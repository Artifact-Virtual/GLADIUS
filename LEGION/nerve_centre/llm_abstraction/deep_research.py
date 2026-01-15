import logging
import re
import asyncio
from functools import partial
from typing import Dict, List, Optional, Generator, Any
from dataclasses import dataclass
from enum import Enum

from agentic_reasoning.prompts import (
    BEGIN_SEARCH_QUERY, BEGIN_SEARCH_RESULT, END_SEARCH_RESULT, 
    MAX_SEARCH_LIMIT, END_SEARCH_QUERY, REASON_PROMPT, RELEVANT_EXTRACTION_PROMPT
)
from api.db.services.llm_service import LLMBundle
from rag.nlp import extract_between
from rag.prompts import kb_prompt
from rag.utils.tavily_conn import Tavily


class SearchStatus(Enum):
    REASONING = "reasoning"
    SEARCHING = "searching"
    EXTRACTING = "extracting"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class SearchResult:
    query: str
    sources: List[Dict[str, Any]]
    summary: str
    confidence: float
    timestamp: float


@dataclass
class ReasoningStep:
    step_id: int
    content: str
    queries: List[str]
    results: List[SearchResult]
    status: SearchStatus


class DeepResearcher:
    def __init__(
        self,
        chat_mdl: LLMBundle,
        prompt_config: dict,
        kb_retrieve: Optional[partial] = None,
        kg_retrieve: Optional[partial] = None,
        max_reasoning_steps: int = 10,
        max_queries_per_step: int = 3,
        min_confidence_threshold: float = 0.7
    ):
        self.chat_mdl = chat_mdl
        self.prompt_config = prompt_config
        self._kb_retrieve = kb_retrieve
        self._kg_retrieve = kg_retrieve
        self.max_reasoning_steps = max_reasoning_steps
        self.max_queries_per_step = max_queries_per_step
        self.min_confidence_threshold = min_confidence_threshold
        
        # Enhanced state tracking
        self._executed_queries = set()
        self._reasoning_history: List[ReasoningStep] = []
        self._query_cache: Dict[str, SearchResult] = {}
        
        # Performance metrics
        self._metrics = {
            "total_queries": 0,
            "cache_hits": 0,
            "failed_retrievals": 0,
            "avg_confidence": 0.0
        }

    @staticmethod
    def _remove_tags(text: str, start_tag: str, end_tag: str) -> str:
        """Improved tag removal with better regex handling"""
        if not text or not start_tag or not end_tag:
            return text
        
        pattern = re.escape(start_tag) + r"(.*?)" + re.escape(end_tag)
        return re.sub(pattern, "", text, flags=re.DOTALL)

    @staticmethod
    def _remove_query_tags(text: str) -> str:
        """Remove Query Tags"""
        return DeepResearcher._remove_tags(text, BEGIN_SEARCH_QUERY, END_SEARCH_QUERY)

    @staticmethod
    def _remove_result_tags(text: str) -> str:
        """Remove Result Tags"""
        return DeepResearcher._remove_tags(text, BEGIN_SEARCH_RESULT, END_SEARCH_RESULT)

    def _calculate_query_similarity(self, query1: str, query2: str) -> float:
        """Calculate semantic similarity between queries to avoid redundant searches"""
        # Simple implementation - could be enhanced with embeddings
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0

    def _is_query_redundant(self, query: str, threshold: float = 0.8) -> bool:
        """Check if a query is too similar to previously executed queries"""
        for executed_query in self._executed_queries:
            if self._calculate_query_similarity(query, executed_query) > threshold:
                return True
        return False

    def _generate_reasoning(self, msg_history: List[Dict[str, str]]) -> Generator[str, None, str]:
        """Enhanced reasoning generation with better error handling"""
        try:
            if not msg_history:
                msg_history = [{"role": "user", "content": "Please begin your reasoning process."}]
            
            # Ensure proper message structure
            if msg_history[-1]["role"] != "user":
                msg_history.append({
                    "role": "user", 
                    "content": "Continue reasoning with the new information.\n"
                })
            else:
                msg_history[-1]["content"] += "\n\nContinue reasoning with the new information.\n"
            
            query_think = ""
            token_count = 0
            
            for ans in self.chat_mdl.chat_streamly(
                REASON_PROMPT, 
                msg_history, 
                {"temperature": 0.7, "max_tokens": 2048}
            ):
                ans = re.sub(r"^.*</think>", "", ans, flags=re.DOTALL)
                if not ans:
                    continue
                
                query_think = ans
                token_count += len(ans.split())
                
                # Prevent excessively long reasoning
                if token_count > 1500:
                    query_think += "\n[Reasoning truncated for length]"
                    break
                    
                yield query_think
                
            return query_think
            
        except Exception as e:
            logging.error(f"Error in reasoning generation: {e}")
            return "Error occurred during reasoning. Proceeding with basic analysis."

    def _extract_and_validate_queries(self, reasoning_text: str, question: str, step_index: int) -> List[str]:
        """Enhanced query extraction with validation and deduplication"""
        queries = extract_between(reasoning_text, BEGIN_SEARCH_QUERY, END_SEARCH_QUERY)
        
        # Fallback for first step
        if not queries and step_index == 0:
            queries = [question]
        
        # Clean and validate queries
        validated_queries = []
        for query in queries[:self.max_queries_per_step]:
            query = query.strip()
            
            # Skip empty or too short queries
            if len(query) < 3:
                continue
                
            # Skip redundant queries
            if self._is_query_redundant(query):
                logging.info(f"Skipping redundant query: {query}")
                continue
                
            validated_queries.append(query)
        
        return validated_queries

    def _retrieve_with_fallback(self, search_query: str) -> Dict[str, Any]:
        """Enhanced retrieval with fallback mechanisms and error recovery"""
        kbinfos = {"chunks": [], "doc_aggs": []}
        retrieval_errors = []
        
        # 1. Knowledge base retrieval with retry
        for attempt in range(2):
            try:
                if self._kb_retrieve:
                    kb_result = self._kb_retrieve(question=search_query)
                    if kb_result and isinstance(kb_result, dict):
                        kbinfos.update(kb_result)
                        break
            except Exception as e:
                retrieval_errors.append(f"KB retrieval attempt {attempt + 1}: {e}")
                if attempt == 1:
                    logging.error(f"Knowledge base retrieval failed: {e}")

        # 2. Web retrieval with enhanced error handling
        if self.prompt_config.get("tavily_api_key"):
            try:
                tav = Tavily(self.prompt_config["tavily_api_key"])
                tav_res = tav.retrieve_chunks(search_query)
                
                if tav_res and isinstance(tav_res, dict):
                    kbinfos["chunks"].extend(tav_res.get("chunks", []))
                    kbinfos["doc_aggs"].extend(tav_res.get("doc_aggs", []))
                    
            except Exception as e:
                retrieval_errors.append(f"Web retrieval: {e}")
                logging.error(f"Web retrieval error: {e}")

        # 3. Knowledge graph retrieval
        if self.prompt_config.get("use_kg") and self._kg_retrieve:
            try:
                kg_result = self._kg_retrieve(question=search_query)
                if kg_result and kg_result.get("content_with_weight"):
                    kbinfos["chunks"].insert(0, kg_result)
            except Exception as e:
                retrieval_errors.append(f"KG retrieval: {e}")
                logging.error(f"Knowledge graph retrieval error: {e}")

        # Update metrics
        self._metrics["total_queries"] += 1
        if retrieval_errors:
            self._metrics["failed_retrievals"] += 1

        return kbinfos

    def _calculate_content_confidence(self, content: str, query: str) -> float:
        """Calculate confidence score for retrieved content"""
        if not content or not query:
            return 0.0
        
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        # Simple relevance scoring - could be enhanced with embeddings
        overlap = len(query_words.intersection(content_words))
        query_coverage = overlap / len(query_words) if query_words else 0.0
        
        # Boost score based on content length (more content = potentially more informative)
        length_factor = min(len(content) / 1000, 1.0)
        
        return min(query_coverage + (length_factor * 0.3), 1.0)

    def _smart_chunk_merging(self, chunk_info: Dict[str, Any], new_info: Dict[str, Any]) -> None:
        """Intelligent chunk merging with deduplication and ranking"""
        if not chunk_info.get("chunks"):
            chunk_info.update(new_info)
            return

        # Create lookup sets for efficient deduplication
        existing_chunk_ids = {c.get("chunk_id") for c in chunk_info["chunks"]}
        existing_doc_ids = {d.get("doc_id") for d in chunk_info["doc_aggs"]}

        # Merge chunks with confidence scoring
        for chunk in new_info.get("chunks", []):
            if chunk.get("chunk_id") not in existing_chunk_ids:
                # Add confidence score to chunk
                chunk["confidence"] = self._calculate_content_confidence(
                    chunk.get("content", ""), 
                    chunk.get("query", "")
                )
                chunk_info["chunks"].append(chunk)

        # Merge document aggregations
        for doc in new_info.get("doc_aggs", []):
            if doc.get("doc_id") not in existing_doc_ids:
                chunk_info["doc_aggs"].append(doc)

        # Sort chunks by confidence score
        chunk_info["chunks"].sort(key=lambda x: x.get("confidence", 0.0), reverse=True)

    def _adaptive_context_truncation(self, reasoning_steps: List[ReasoningStep], max_tokens: int = 4000) -> str:
        """Adaptive context truncation based on relevance and recency"""
        if not reasoning_steps:
            return ""

        truncated_reasoning = ""
        token_count = 0
        
        # Always include the most recent steps
        recent_steps = reasoning_steps[-3:] if len(reasoning_steps) > 3 else reasoning_steps
        
        # Include high-confidence search results from earlier steps
        important_steps = [
            step for step in reasoning_steps[:-3] 
            if any(result.confidence > self.min_confidence_threshold for result in step.results)
        ]
        
        # Combine and format
        for i, step in enumerate(important_steps + recent_steps):
            step_text = f"Step {step.step_id}: {step.content}\n"
            
            # Add search results summary
            if step.results:
                step_text += "Key findings:\n"
                for result in step.results[:2]:  # Top 2 results
                    step_text += f"- {result.summary[:200]}...\n"
            
            step_text += "\n"
            
            # Check token limit (rough estimation)
            if token_count + len(step_text.split()) > max_tokens:
                break
                
            truncated_reasoning += step_text
            token_count += len(step_text.split())

        return truncated_reasoning.strip()

    def thinking(
        self, 
        chunk_info: dict, 
        question: str, 
        stream_callback: Optional[callable] = None
    ) -> Generator[Dict[str, Any], None, str]:
        """Enhanced thinking process with better state management and error recovery"""
        
        try:
            msg_history = [{"role": "user", "content": f'Question: "{question}"\n'}]
            think = "<think>"
            
            for step_index in range(self.max_reasoning_steps):
                current_step = ReasoningStep(
                    step_id=step_index + 1,
                    content="",
                    queries=[],
                    results=[],
                    status=SearchStatus.REASONING
                )
                
                # Check search limit
                if step_index >= MAX_SEARCH_LIMIT - 1:
                    summary = f"\n{BEGIN_SEARCH_RESULT}\nMaximum search limit reached. Concluding analysis.\n{END_SEARCH_RESULT}\n"
                    current_step.status = SearchStatus.COMPLETED
                    yield {"answer": think + summary + "</think>", "reference": chunk_info, "audio_binary": None}
                    break

                # Generate reasoning
                current_step.status = SearchStatus.REASONING
                reasoning_content = ""
                
                for reasoning_chunk in self._generate_reasoning(msg_history):
                    reasoning_content = reasoning_chunk
                    clean_reasoning = self._remove_query_tags(reasoning_content)
                    yield {
                        "answer": think + clean_reasoning + "</think>", 
                        "reference": chunk_info, 
                        "audio_binary": None,
                        "status": current_step.status.value
                    }

                current_step.content = reasoning_content
                think += self._remove_query_tags(reasoning_content)

                # Extract and validate queries
                queries = self._extract_and_validate_queries(reasoning_content, question, step_index)
                current_step.queries = queries
                
                if not queries and step_index > 0:
                    current_step.status = SearchStatus.COMPLETED
                    break

                # Process each query
                for query_idx, search_query in enumerate(queries):
                    logging.info(f"[STEP {step_index + 1}] Processing query {query_idx + 1}: {search_query}")
                    
                    current_step.status = SearchStatus.SEARCHING
                    msg_history.append({"role": "assistant", "content": search_query})
                    think += f"\n\n> {step_index + 1}.{query_idx + 1} {search_query}\n\n"
                    
                    yield {
                        "answer": think + "</think>", 
                        "reference": chunk_info, 
                        "audio_binary": None,
                        "status": current_step.status.value
                    }

                    # Check query cache
                    if search_query in self._query_cache:
                        cached_result = self._query_cache[search_query]
                        current_step.results.append(cached_result)
                        self._metrics["cache_hits"] += 1
                        
                        summary = f"\n{BEGIN_SEARCH_RESULT}\nUsing cached result for: {search_query}\n{cached_result.summary}\n{END_SEARCH_RESULT}\n"
                        think += summary
                        continue

                    self._executed_queries.add(search_query)
                    
                    # Retrieve information
                    kbinfos = self._retrieve_with_fallback(search_query)
                    self._smart_chunk_merging(chunk_info, kbinfos)
                    
                    # Extract relevant information
                    current_step.status = SearchStatus.EXTRACTING
                    truncated_context = self._adaptive_context_truncation(self._reasoning_history)
                    
                    summary_content = ""
                    for summary_chunk in self._extract_relevant_info(truncated_context, search_query, kbinfos):
                        summary_content = summary_chunk
                        clean_summary = self._remove_result_tags(summary_content)
                        yield {
                            "answer": think + "\n\n" + clean_summary + "</think>", 
                            "reference": chunk_info, 
                            "audio_binary": None,
                            "status": current_step.status.value
                        }

                    # Create search result
                    confidence = self._calculate_content_confidence(summary_content, search_query)
                    search_result = SearchResult(
                        query=search_query,
                        sources=kbinfos.get("chunks", [])[:5],  # Top 5 sources
                        summary=summary_content,
                        confidence=confidence,
                        timestamp=step_index
                    )
                    
                    current_step.results.append(search_result)
                    self._query_cache[search_query] = search_result
                    
                    # Update message history and thinking
                    msg_history.append({
                        "role": "user", 
                        "content": f"\n\n{BEGIN_SEARCH_RESULT}{summary_content}{END_SEARCH_RESULT}\n\n"
                    })
                    think += self._remove_result_tags(summary_content)

                current_step.status = SearchStatus.COMPLETED
                self._reasoning_history.append(current_step)

            # Calculate final metrics
            if self._reasoning_history:
                all_confidences = [
                    result.confidence 
                    for step in self._reasoning_history 
                    for result in step.results
                ]
                self._metrics["avg_confidence"] = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0

            final_response = think + "</think>"
            
            # Add metadata
            metadata = {
                "reasoning_steps": len(self._reasoning_history),
                "total_queries": len(self._executed_queries),
                "metrics": self._metrics
            }
            
            yield {
                "answer": final_response,
                "reference": chunk_info,
                "audio_binary": None,
                "metadata": metadata,
                "status": "completed"
            }
            
            return final_response
            
        except Exception as e:
            logging.error(f"Critical error in thinking process: {e}")
            error_response = think + f"\n\nError occurred during reasoning: {str(e)}</think>"
            yield {
                "answer": error_response,
                "reference": chunk_info,
                "audio_binary": None,
                "status": "error",
                "error": str(e)
            }
            return error_response

    def _extract_relevant_info(self, context: str, query: str, kbinfos: Dict[str, Any]) -> Generator[str, None, str]:
        """Enhanced information extraction with better prompting"""
        try:
            documents = "\n".join(kb_prompt(kbinfos, 4096))
            
            if not documents.strip():
                return "No relevant information found for this query."
            
            enhanced_prompt = RELEVANT_EXTRACTION_PROMPT.format(
                prev_reasoning=context,
                search_query=query,
                document=documents
            )
            
            messages = [{
                "role": "user",
                "content": f'Analyze the retrieved information for query: "{query}". Focus on accuracy, relevance, and provide specific details with source attribution where possible.'
            }]
            
            summary_content = ""
            for chunk in self.chat_mdl.chat_streamly(enhanced_prompt, messages, {"temperature": 0.5}):
                chunk = re.sub(r"^.*</think>", "", chunk, flags=re.DOTALL)
                if chunk:
                    summary_content = chunk
                    yield summary_content
                    
            return summary_content
            
        except Exception as e:
            logging.error(f"Error in information extraction: {e}")
            return f"Error extracting information: {str(e)}"

    def get_research_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the research process"""
        return {
            "total_steps": len(self._reasoning_history),
            "total_queries": len(self._executed_queries),
            "executed_queries": list(self._executed_queries),
            "metrics": self._metrics,
            "high_confidence_results": [
                {
                    "query": result.query,
                    "summary": result.summary[:200] + "...",
                    "confidence": result.confidence
                }
                for step in self._reasoning_history
                for result in step.results
                if result.confidence > self.min_confidence_threshold
            ]
        }
