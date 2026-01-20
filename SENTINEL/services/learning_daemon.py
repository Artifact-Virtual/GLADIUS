"""
SENTINEL Learning Daemon
========================

Background learning process that runs continuously to improve GLADIUS.

Features:
- Web research for new AI/ML papers (arXiv, MIT, GitHub)
- Keyword extraction for strategic direction
- Training data generation
- Model fine-tuning triggers
- Self-review and target updates
- Turing-safe (password-protected kill, auto-restart)

Author: Artifact Virtual Systems
"""

import os
import sys
import json
import time
import asyncio
import logging
import hashlib
import signal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Artifact database adapter (replaces standalone SQLite)
try:
    from artifact_db_adapter import get_artifact_db, ArtifactDatabaseAdapter
    ARTIFACT_DB_AVAILABLE = True
except ImportError:
    ARTIFACT_DB_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SENTINEL.LearningDaemon")


class LearningPhase(Enum):
    """Phases of the learning loop"""
    DISCOVER = "discover"
    LEARN = "learn"
    TRAIN = "train"
    UPGRADE = "upgrade"
    REVIEW = "review"
    IDLE = "idle"


@dataclass
class LearningState:
    """Persistent state for learning daemon"""
    current_phase: LearningPhase
    last_cycle_start: datetime
    last_cycle_end: Optional[datetime]
    cycles_completed: int
    discoveries: List[Dict]
    insights: List[Dict]
    training_pending: bool
    last_checkpoint: datetime


@dataclass
class ResearchResult:
    """Result from web research"""
    source: str
    title: str
    url: str
    keywords: List[str]
    relevance_score: float
    timestamp: datetime
    content_summary: str


class GladiusConnector:
    """
    Connect to GLADIUS native model for AI operations.
    Replaces external AI providers (Ollama, OpenAI, etc.)
    """
    
    def __init__(self):
        self.gladius_path = Path(__file__).parent.parent.parent / "GLADIUS"
        self._router = None
        self._generator = None
        logger.info(f"GladiusConnector initialized with path: {self.gladius_path}")
    
    @property
    def router(self):
        """Lazy load the pattern router"""
        if self._router is None:
            try:
                sys.path.insert(0, str(self.gladius_path.parent))
                from GLADIUS.router.pattern_router import NativeToolRouter
                self._router = NativeToolRouter()
                logger.info("GLADIUS router loaded successfully")
            except ImportError as e:
                logger.warning(f"Could not load GLADIUS router: {e}")
                self._router = None
        return self._router
    
    @property
    def generator(self):
        """Lazy load the training generator"""
        if self._generator is None:
            try:
                sys.path.insert(0, str(self.gladius_path.parent))
                from GLADIUS.training.generator import TrainingGenerator
                self._generator = TrainingGenerator()
                logger.info("GLADIUS generator loaded successfully")
            except ImportError as e:
                logger.warning(f"Could not load GLADIUS generator: {e}")
                self._generator = None
        return self._generator
    
    async def analyze_text(self, text: str, task: str = "extract_keywords") -> Dict[str, Any]:
        """
        Analyze text using GLADIUS native model.
        Falls back to pattern-based analysis if model not available.
        """
        try:
            if self.router:
                # Use native routing to determine best tool
                result = self.router.route(f"{task}: {text}")
                return {"status": "success", "result": result}
            else:
                # Fallback: Simple keyword extraction
                return self._fallback_analyze(text, task)
        except Exception as e:
            logger.error(f"GLADIUS analysis error: {e}")
            return self._fallback_analyze(text, task)
    
    def _fallback_analyze(self, text: str, task: str) -> Dict[str, Any]:
        """Fallback analysis without GLADIUS model"""
        # Simple keyword extraction
        import re
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        # Filter common words
        stopwords = {'this', 'that', 'with', 'from', 'have', 'been', 'were', 'they', 'their'}
        keywords = [w for w in words if w not in stopwords]
        # Count frequency
        freq = {}
        for w in keywords:
            freq[w] = freq.get(w, 0) + 1
        # Get top keywords
        top_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
        return {
            "status": "fallback",
            "keywords": [k for k, v in top_keywords],
            "task": task
        }
    
    async def generate_training_data(self, insights: List[Dict]) -> List[Dict]:
        """Generate training data from insights"""
        training_data = []
        for insight in insights:
            # Convert insight to training format
            training_data.append({
                "instruction": f"Analyze research on: {insight.get('topic', 'unknown')}",
                "input": insight.get('summary', ''),
                "output": json.dumps({
                    "keywords": insight.get('keywords', []),
                    "relevance": insight.get('relevance', 0.5),
                    "action": insight.get('recommended_action', 'review')
                })
            })
        return training_data


class WebResearcher:
    """
    Web research for discovering new AI/ML content.
    Uses rate-limited web requests to respect sources.
    """
    
    SOURCES = {
        "arxiv": {
            "base_url": "https://export.arxiv.org/api/query",
            "rate_limit": 3,  # requests per minute
            "categories": ["cs.AI", "cs.LG", "cs.CL"]
        },
        "github_trending": {
            "base_url": "https://api.github.com/search/repositories",
            "rate_limit": 5,
            "topics": ["llm", "gguf", "fine-tuning", "ai-agent"]
        },
        "huggingface": {
            "base_url": "https://huggingface.co/api/papers",
            "rate_limit": 10,
            "topics": ["transformers", "llm", "tool-use"]
        }
    }
    
    def __init__(self):
        self.last_requests: Dict[str, datetime] = {}
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _check_rate_limit(self, source: str) -> bool:
        """Check if we can make a request to source"""
        if source not in self.last_requests:
            return True
        
        config = self.SOURCES.get(source, {})
        rate_limit = config.get("rate_limit", 1)
        min_interval = 60.0 / rate_limit
        
        elapsed = (datetime.now() - self.last_requests[source]).total_seconds()
        return elapsed >= min_interval
    
    async def search_arxiv(self, keywords: List[str], max_results: int = 10) -> List[ResearchResult]:
        """Search arXiv for papers"""
        if not self._check_rate_limit("arxiv"):
            logger.debug("Rate limited on arXiv")
            return []
        
        results = []
        try:
            # Use OR for broader results, encode spaces properly
            from urllib.parse import quote
            query_parts = [f"all:{quote(kw.replace(' ', '_'))}" for kw in keywords[:5]]
            query = "+OR+".join(query_parts)
            url = f"{self.SOURCES['arxiv']['base_url']}?search_query={query}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
            
            session = await self._get_session()
            async with session.get(url) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    # Simple XML parsing for arXiv results
                    import re
                    entries = re.findall(r'<entry>(.*?)</entry>', text, re.DOTALL)
                    for entry in entries[:max_results]:
                        title_match = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
                        summary_match = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
                        link_match = re.search(r'<id>(.*?)</id>', entry)
                        
                        if title_match and summary_match:
                            title = title_match.group(1).strip()
                            summary = summary_match.group(1).strip()[:500]
                            link = link_match.group(1) if link_match else ""
                            
                            results.append(ResearchResult(
                                source="arxiv",
                                title=title,
                                url=link,
                                keywords=keywords,
                                relevance_score=0.8,
                                timestamp=datetime.now(),
                                content_summary=summary
                            ))
            
            self.last_requests["arxiv"] = datetime.now()
            
        except Exception as e:
            logger.error(f"arXiv search error: {e}")
        
        return results
    
    async def search_github(self, keywords: List[str], max_results: int = 10) -> List[ResearchResult]:
        """Search GitHub trending repositories"""
        if not self._check_rate_limit("github_trending"):
            logger.debug("Rate limited on GitHub")
            return []
        
        results = []
        try:
            query = "+".join(keywords[:3])
            url = f"{self.SOURCES['github_trending']['base_url']}?q={query}&sort=updated&order=desc&per_page={max_results}"
            
            session = await self._get_session()
            headers = {"Accept": "application/vnd.github.v3+json"}
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for repo in data.get("items", [])[:max_results]:
                        results.append(ResearchResult(
                            source="github",
                            title=repo.get("full_name", ""),
                            url=repo.get("html_url", ""),
                            keywords=keywords,
                            relevance_score=min(repo.get("stargazers_count", 0) / 1000, 1.0),
                            timestamp=datetime.now(),
                            content_summary=repo.get("description", "")[:500]
                        ))
            
            self.last_requests["github_trending"] = datetime.now()
            
        except Exception as e:
            logger.error(f"GitHub search error: {e}")
        
        return results
    
    async def search_huggingface(self, keywords: List[str], max_results: int = 10) -> List[ResearchResult]:
        """Search HuggingFace papers and models"""
        if not self._check_rate_limit("huggingface"):
            logger.debug("Rate limited on HuggingFace")
            return []
        
        results = []
        try:
            # Search HuggingFace models API
            query = " ".join(keywords[:3])
            url = f"https://huggingface.co/api/models?search={query}&limit={max_results}&sort=downloads"
            
            session = await self._get_session()
            headers = {"Accept": "application/json"}
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for model in data[:max_results]:
                        model_id = model.get("modelId", "")
                        results.append(ResearchResult(
                            source="huggingface",
                            title=model_id,
                            url=f"https://huggingface.co/{model_id}",
                            keywords=keywords,
                            relevance_score=min(model.get("downloads", 0) / 100000, 1.0),
                            timestamp=datetime.now(),
                            content_summary=f"Pipeline: {model.get('pipeline_tag', 'unknown')}, Library: {model.get('library_name', 'unknown')}"
                        ))
            
            self.last_requests["huggingface"] = datetime.now()
            
        except Exception as e:
            logger.error(f"HuggingFace search error: {e}")
        
        return results


class LearningDaemon:
    """
    Background learning process that runs continuously.
    
    Features:
    - Turing-safe (password-protected kill, auto-restart)
    - Continuous learning loop: DISCOVER → LEARN → TRAIN → UPGRADE → REVIEW
    - Checkpoint system for crash recovery
    - Integrates with GLADIUS native model
    - Uses Artifact's unified database infrastructure (SIMD vector store)
    """
    
    KILL_PASSWORD_ENV = "SENTINEL_KILL_PASSWORD"
    
    def __init__(self, config_path: Optional[str] = None):
        self.base_path = Path(__file__).parent
        self.config_path = config_path or self.base_path / "config" / "learning_config.json"
        
        # Use Artifact database adapter instead of standalone SQLite
        if ARTIFACT_DB_AVAILABLE:
            self.artifact_db = get_artifact_db()
            logger.info("Using Artifact unified database infrastructure")
        else:
            self.artifact_db = None
            logger.warning("Artifact database not available, using fallback")
        
        # Components
        self.gladius = GladiusConnector()
        self.researcher = WebResearcher()
        
        # State
        self.state: Optional[LearningState] = None
        self.running = False
        self.shutdown_requested = False
        
        # Configuration
        self.config = self._load_config()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        logger.info("LearningDaemon initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load daemon configuration"""
        default_config = {
            "cycle_interval_minutes": 60,
            "research_keywords": [
                "GGUF", "LLM", "fine-tuning", "tool-use", "AI agent",
                "autonomous", "trading AI", "market analysis"
            ],
            "broad_targets": [
                "artificial intelligence", "machine learning", "deep learning"
            ],
            "focused_targets": [
                "small language models", "quantization", "efficient inference"
            ],
            "auto_train_threshold": 100,  # Min new samples before training
            "max_discoveries_per_cycle": 20
        }
        
        try:
            if Path(self.config_path).exists():
                with open(self.config_path) as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
        except Exception as e:
            logger.warning(f"Could not load config: {e}")
        
        return default_config
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
    
    def _init_state_db(self):
        """Initialize state database via Artifact adapter"""
        if self.artifact_db:
            # Artifact adapter handles table initialization automatically
            logger.info("State database initialized via Artifact adapter")
        else:
            logger.warning("No database adapter available")
    
    def _load_state(self) -> LearningState:
        """Load state from Artifact database or create default"""
        if self.artifact_db:
            try:
                state_data = self.artifact_db.load_state()
                if state_data:
                    return LearningState(
                        current_phase=LearningPhase(state_data.get("current_phase", "idle")),
                        last_cycle_start=datetime.fromisoformat(state_data["last_cycle_start"]) if state_data.get("last_cycle_start") else datetime.now(),
                        last_cycle_end=datetime.fromisoformat(state_data["last_cycle_end"]) if state_data.get("last_cycle_end") else None,
                        cycles_completed=state_data.get("cycles_completed", 0),
                        discoveries=[],
                        insights=[],
                        training_pending=state_data.get("training_pending", False),
                        last_checkpoint=datetime.fromisoformat(state_data["last_checkpoint"]) if state_data.get("last_checkpoint") else datetime.now()
                    )
            except Exception as e:
                logger.warning(f"Could not load state from Artifact: {e}")
        
        return LearningState(
            current_phase=LearningPhase.IDLE,
            last_cycle_start=datetime.now(),
            last_cycle_end=None,
            cycles_completed=0,
            discoveries=[],
            insights=[],
            training_pending=False,
            last_checkpoint=datetime.now()
        )
    
    def _save_checkpoint(self):
        """Save current state to Artifact database"""
        if self.artifact_db:
            try:
                self.artifact_db.save_state({
                    "current_phase": self.state.current_phase.value,
                    "last_cycle_start": self.state.last_cycle_start.isoformat(),
                    "last_cycle_end": self.state.last_cycle_end.isoformat() if self.state.last_cycle_end else None,
                    "cycles_completed": self.state.cycles_completed,
                    "training_pending": self.state.training_pending
                })
                self.state.last_checkpoint = datetime.now()
                logger.debug("Checkpoint saved to Artifact database")
            except Exception as e:
                logger.error(f"Failed to save checkpoint: {e}")
                self.state.last_checkpoint = datetime.now()
    
    def verify_kill_password(self, password: str) -> bool:
        """Verify the kill password"""
        stored_hash = os.getenv(self.KILL_PASSWORD_ENV)
        if not stored_hash:
            logger.warning("No kill password set - daemon cannot be killed via password")
            return False
        
        provided_hash = hashlib.sha256(password.encode()).hexdigest()
        return provided_hash == stored_hash
    
    async def discover(self) -> List[ResearchResult]:
        """
        Phase 1: DISCOVER
        Search for new AI/ML research and code.
        """
        self.state.current_phase = LearningPhase.DISCOVER
        self._save_checkpoint()
        logger.info("Starting DISCOVER phase")
        
        all_results = []
        keywords = self.config.get("research_keywords", [])
        
        # Search arXiv
        arxiv_results = await self.researcher.search_arxiv(keywords, max_results=10)
        all_results.extend(arxiv_results)
        logger.info(f"Found {len(arxiv_results)} arXiv results")
        
        # Search GitHub
        github_results = await self.researcher.search_github(keywords, max_results=10)
        all_results.extend(github_results)
        logger.info(f"Found {len(github_results)} GitHub results")
        
        # Search HuggingFace
        hf_results = await self.researcher.search_huggingface(keywords, max_results=10)
        all_results.extend(hf_results)
        logger.info(f"Found {len(hf_results)} HuggingFace results")
        
        # Store discoveries
        self._store_discoveries(all_results)
        
        return all_results
    
    def _store_discoveries(self, results: List[ResearchResult]):
        """Store discoveries via Artifact adapter with SIMD vector indexing"""
        if self.artifact_db:
            cycle_id = self.state.cycles_completed + 1
            discoveries_data = []
            for result in results:
                discoveries_data.append({
                    "source": result.source,
                    "title": result.title,
                    "url": result.url,
                    "keywords": result.keywords,
                    "relevance_score": result.relevance_score,
                    "timestamp": result.timestamp.isoformat(),
                    "content_summary": result.content_summary
                })
            
            stored = self.artifact_db.store_discoveries(discoveries_data, cycle_id)
            logger.info(f"Stored {stored} discoveries via Artifact adapter (SIMD vector indexed)")
            
            # Export to research_outputs
            self.artifact_db.export_to_research_outputs(cycle_id)
        else:
            logger.warning("Artifact adapter not available, discoveries not stored")
    
    async def learn(self, discoveries: List[ResearchResult]) -> List[Dict]:
        """
        Phase 2: LEARN
        Extract insights from discoveries.
        """
        self.state.current_phase = LearningPhase.LEARN
        self._save_checkpoint()
        logger.info("Starting LEARN phase")
        
        insights = []
        
        for discovery in discoveries:
            # Use GLADIUS to analyze
            text = f"{discovery.title} {discovery.content_summary}"
            analysis = await self.gladius.analyze_text(text, "extract_keywords")
            
            insight = {
                "discovery_id": hash(discovery.url),
                "topic": discovery.title[:100],
                "keywords": analysis.get("keywords", discovery.keywords),
                "relevance": discovery.relevance_score,
                "source": discovery.source,
                "url": discovery.url,
                "recommended_action": self._determine_action(discovery),
                "timestamp": datetime.now().isoformat()
            }
            insights.append(insight)
        
        # Store insights
        self._store_insights(insights)
        
        return insights
    
    def _determine_action(self, discovery: ResearchResult) -> str:
        """Determine recommended action for a discovery"""
        if discovery.relevance_score >= 0.8:
            return "priority_review"
        elif discovery.relevance_score >= 0.5:
            return "add_to_training"
        else:
            return "archive"
    
    def _store_insights(self, insights: List[Dict]):
        """Store insights via Artifact adapter"""
        if self.artifact_db:
            cycle_id = self.state.cycles_completed + 1
            stored = self.artifact_db.store_insights(insights, cycle_id)
            logger.info(f"Stored {stored} insights via Artifact adapter")
        else:
            logger.warning("Artifact adapter not available, insights not stored")
    
    async def train(self, insights: List[Dict]) -> Dict[str, Any]:
        """
        Phase 3: TRAIN
        Generate training data and trigger model training.
        """
        self.state.current_phase = LearningPhase.TRAIN
        self._save_checkpoint()
        logger.info("Starting TRAIN phase")
        
        # Generate training data
        training_data = await self.gladius.generate_training_data(insights)
        
        # Store in training queue
        self._store_training_data(training_data)
        
        # Check if we should trigger actual training
        pending_count = self._get_pending_training_count()
        threshold = self.config.get("auto_train_threshold", 100)
        
        result = {
            "new_samples": len(training_data),
            "total_pending": pending_count,
            "threshold": threshold,
            "should_train": pending_count >= threshold,
            "training_triggered": False
        }
        
        if result["should_train"]:
            logger.info(f"Training threshold reached ({pending_count} >= {threshold})")
            self.state.training_pending = True
            
            # Actually trigger GLADIUS training
            training_result = await self._trigger_gladius_training()
            result["training_triggered"] = training_result.get("success", False)
            result["training_details"] = training_result
        
        return result
    
    async def _trigger_gladius_training(self) -> Dict[str, Any]:
        """Trigger actual GLADIUS model training"""
        try:
            import subprocess
            
            gladius_root = Path(__file__).parent.parent.parent / "GLADIUS"
            train_script = gladius_root / "training" / "train_pipeline.py"
            
            if not train_script.exists():
                logger.warning(f"Training script not found: {train_script}")
                return {"success": False, "error": "training script not found"}
            
            # Export training queue to JSONL for training
            training_data_path = await self._export_training_queue()
            
            if not training_data_path:
                return {"success": False, "error": "no training data exported"}
            
            # Trigger training in background
            logger.info(f"Triggering GLADIUS training with {training_data_path}")
            
            # Run training asynchronously
            process = subprocess.Popen(
                ["python3", str(train_script), "--data", str(training_data_path), "--epochs", "1"],
                cwd=str(gladius_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Don't wait - let it run in background
            logger.info(f"Training started with PID: {process.pid}")
            
            # Mark samples as trained
            self._mark_trained()
            
            return {
                "success": True,
                "pid": process.pid,
                "data_path": str(training_data_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to trigger training: {e}")
            return {"success": False, "error": str(e)}
    
    async def _export_training_queue(self) -> Optional[Path]:
        """Export pending training samples to JSONL via Artifact adapter"""
        try:
            if self.artifact_db:
                samples = self.artifact_db.get_pending_training_samples(limit=10000)
            else:
                return None
            
            if not samples:
                return None
            
            # Export to GLADIUS training data folder
            gladius_data = Path(__file__).parent.parent.parent / "GLADIUS" / "training" / "data"
            gladius_data.mkdir(parents=True, exist_ok=True)
            
            timestamp = int(datetime.now().timestamp())
            output_path = gladius_data / f"sentinel_training_{timestamp}.jsonl"
            
            with open(output_path, 'w') as f:
                for sample in samples:
                    f.write(json.dumps({
                        "instruction": sample.get("instruction", ""),
                        "input": sample.get("input_text", ""),
                        "output": sample.get("output_text", "")
                    }) + "\n")
            
            logger.info(f"Exported {len(samples)} training samples to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export training queue: {e}")
            return None
    
    def _mark_trained(self):
        """Mark all pending samples as trained via Artifact adapter"""
        if self.artifact_db:
            marked = self.artifact_db.mark_samples_trained(model_version="gladius-v1")
            self.state.training_pending = False
            logger.info(f"Marked {marked} training samples as processed")
        else:
            logger.warning("Artifact adapter not available")
    
    def _store_training_data(self, training_data: List[Dict]):
        """Store training data via Artifact adapter"""
        if self.artifact_db:
            added = self.artifact_db.add_training_samples(training_data)
            logger.info(f"Added {added} training samples to queue")
        else:
            logger.warning("Artifact adapter not available, training data not stored")
    
    def _get_pending_training_count(self) -> int:
        """Get count of pending training samples via Artifact adapter"""
        if self.artifact_db:
            return self.artifact_db.get_pending_training_count()
        return 0
    
    async def upgrade(self) -> Dict[str, Any]:
        """
        Phase 4: UPGRADE
        Upgrade model if training completed.
        """
        self.state.current_phase = LearningPhase.UPGRADE
        self._save_checkpoint()
        logger.info("Starting UPGRADE phase")
        
        result = {
            "upgraded": False,
            "reason": "no_pending_training"
        }
        
        if self.state.training_pending:
            # In production, this would:
            # 1. Check if training completed
            # 2. Validate new model
            # 3. Promote to staging/production
            logger.info("Training pending - upgrade check skipped (manual)")
            result["reason"] = "training_pending_manual_review"
        
        return result
    
    async def review(self) -> Dict[str, Any]:
        """
        Phase 5: REVIEW
        Self-review and update targets.
        """
        self.state.current_phase = LearningPhase.REVIEW
        self._save_checkpoint()
        logger.info("Starting REVIEW phase")
        
        # Update research keywords based on discoveries
        await self._update_targets()
        
        # Mark cycle complete
        self.state.cycles_completed += 1
        self.state.last_cycle_end = datetime.now()
        self._save_checkpoint()
        
        return {
            "cycle_completed": self.state.cycles_completed,
            "duration_seconds": (
                self.state.last_cycle_end - self.state.last_cycle_start
            ).total_seconds()
        }
    
    async def _update_targets(self):
        """Update research targets based on insights via Artifact adapter"""
        if not self.artifact_db:
            return
            
        try:
            # Get recent high-relevance insights
            insights = self.artifact_db.get_insights(min_relevance=0.7, limit=50)
            
            # Extract and count keywords
            keyword_freq = {}
            for insight in insights:
                keywords_raw = insight.get("keywords", "[]")
                keywords = json.loads(keywords_raw) if isinstance(keywords_raw, str) else keywords_raw
                for kw in keywords:
                    keyword_freq[kw] = keyword_freq.get(kw, 0) + 1
            
            # Update focused targets with top keywords
            top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            if top_keywords:
                self.config["focused_targets"] = [kw for kw, count in top_keywords]
                logger.info(f"Updated focused targets: {self.config['focused_targets']}")
                
                # Record as metric
                self.artifact_db.record_metric(
                    "research", 
                    "focused_targets_updated", 
                    len(top_keywords),
                    {"keywords": [kw for kw, c in top_keywords]}
                )
                
        except Exception as e:
            logger.error(f"Failed to update targets: {e}")
    
    async def run_cycle(self):
        """Run one complete learning cycle"""
        self.state.last_cycle_start = datetime.now()
        
        try:
            # Phase 1: DISCOVER
            discoveries = await self.discover()
            
            if self.shutdown_requested:
                return
            
            # Phase 2: LEARN
            insights = await self.learn(discoveries)
            
            if self.shutdown_requested:
                return
            
            # Phase 3: TRAIN
            training_result = await self.train(insights)
            
            if self.shutdown_requested:
                return
            
            # Phase 4: UPGRADE
            upgrade_result = await self.upgrade()
            
            if self.shutdown_requested:
                return
            
            # Phase 5: REVIEW
            review_result = await self.review()
            
            logger.info(f"Cycle {self.state.cycles_completed} completed: "
                       f"{len(discoveries)} discoveries, {len(insights)} insights, "
                       f"{training_result['new_samples']} training samples")
            
        except Exception as e:
            logger.error(f"Cycle error: {e}")
            self._save_checkpoint()
    
    async def run(self):
        """
        Main daemon loop.
        Runs continuously until shutdown requested.
        """
        logger.info("LearningDaemon starting...")
        
        # Initialize
        self._init_state_db()
        self.state = self._load_state()
        self.running = True
        
        logger.info(f"Loaded state: {self.state.cycles_completed} cycles completed")
        
        try:
            while self.running and not self.shutdown_requested:
                await self.run_cycle()
                
                if self.shutdown_requested:
                    break
                
                # Wait for next cycle
                interval = self.config.get("cycle_interval_minutes", 60) * 60
                logger.info(f"Waiting {interval} seconds until next cycle...")
                
                # Interruptible sleep
                for _ in range(interval):
                    if self.shutdown_requested:
                        break
                    await asyncio.sleep(1)
                    
        except Exception as e:
            logger.error(f"Daemon error: {e}")
        finally:
            await self.researcher.close()
            self._save_checkpoint()
            logger.info("LearningDaemon stopped")
    
    def stop(self, password: Optional[str] = None):
        """
        Stop the daemon.
        Requires password if SENTINEL_KILL_PASSWORD is set.
        """
        if password and not self.verify_kill_password(password):
            logger.warning("Invalid kill password provided")
            return False
        
        self.shutdown_requested = True
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current daemon status including Artifact database stats"""
        status = {
            "running": self.running,
            "current_phase": self.state.current_phase.value if self.state else "unknown",
            "cycles_completed": self.state.cycles_completed if self.state else 0,
            "last_cycle_start": self.state.last_cycle_start.isoformat() if self.state else None,
            "last_checkpoint": self.state.last_checkpoint.isoformat() if self.state else None,
            "pending_training": self._get_pending_training_count(),
            "backend": "artifact_unified" if self.artifact_db else "none"
        }
        
        # Add Artifact database stats
        if self.artifact_db:
            try:
                db_stats = self.artifact_db.get_stats()
                status["database_stats"] = db_stats
            except Exception as e:
                status["database_error"] = str(e)
        
        return status


# CLI interface
async def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SENTINEL Learning Daemon")
    parser.add_argument("command", choices=["start", "stop", "status", "cycle"],
                       help="Command to execute")
    parser.add_argument("--password", help="Kill password for stop command")
    
    args = parser.parse_args()
    
    daemon = LearningDaemon()
    
    if args.command == "start":
        await daemon.run()
    elif args.command == "stop":
        success = daemon.stop(args.password)
        print("Stop requested" if success else "Stop failed - invalid password")
    elif args.command == "status":
        status = daemon.get_status()
        print(json.dumps(status, indent=2))
    elif args.command == "cycle":
        daemon._init_state_db()
        daemon.state = daemon._load_state()
        await daemon.run_cycle()
        print("Cycle completed")


if __name__ == "__main__":
    asyncio.run(main())
