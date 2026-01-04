# Semantic Routing: Designing a vLLM Intent Router

## Introduction

In hybrid AI architectures combining local small language models (SLMs) with cloud-based frontier LLMs, intelligent routing determines which model handles each request. Poor routing wastes resources—sending simple queries to expensive frontier models increases costs unnecessarily, while routing complex queries to SLMs produces low-quality outputs. Semantic routing solves this by analyzing request characteristics and routing to optimal models.

## Understanding Semantic Routing

Semantic routing examines the **meaning** and **complexity** of requests rather than using simple rule-based matching. Unlike keyword-based routing ("if text contains 'trading' then use model A"), semantic routing:

- Analyzes semantic similarity to known query types
- Evaluates query complexity and ambiguity
- Considers domain-specific requirements
- Assesses confidence levels for different model tiers

## Architecture: Intent Classification Router

```python
class SemanticRouter:
    def __init__(self, embedding_model, slm, frontier_llm):
        self.embedding_model = embedding_model
        self.slm = slm
        self.frontier_llm = frontier_llm
        
        # Intent examples for classification
        self.intent_database = self._build_intent_database()
    
    def route(self, query):
        # Classify query intent
        intent = self.classify_intent(query)
        
        # Determine complexity
        complexity = self.assess_complexity(query, intent)
        
        # Route based on intent + complexity
        if complexity == "simple" and intent in ["classification", "extraction", "summarization"]:
            return self.slm.generate(query)
        elif complexity == "medium":
            # Try SLM with confidence check
            result = self.slm.generate(query)
            if result.confidence >= 0.8:
                return result
            else:
                # Escalate to frontier model
                return self.frontier_llm.generate(query)
        else:  # complex
            return self.frontier_llm.generate(query)
```

## Intent Classification Strategies

### Strategy 1: Embedding-Based Similarity

```python
def classify_intent(self, query):
    # Embed query
    query_embedding = self.embedding_model.encode(query)
    
    # Find most similar intent
    max_similarity = 0
    best_intent = None
    
    for intent_name, intent_examples in self.intent_database.items():
        for example in intent_examples:
            similarity = cosine_similarity(query_embedding, example['embedding'])
            if similarity > max_similarity:
                max_similarity = similarity
                best_intent = intent_name
    
    return {
        'intent': best_intent,
        'confidence': max_similarity
    }
```

### Strategy 2: Lightweight Classification Model

Train a specialized classifier mapping queries to intents:

```python
class IntentClassifier:
    def __init__(self):
        # Small BERT-based classifier
        self.model = load_model('intent_classifier_bert_tiny')
    
    def classify(self, query):
        # Fast inference (~10ms)
        intent_probs = self.model.predict(query)
        
        top_intent = max(intent_probs, key=intent_probs.get)
        confidence = intent_probs[top_intent]
        
        return {
            'intent': top_intent,
            'confidence': confidence,
            'alternatives': sorted(intent_probs.items(), key=lambda x: x[1], reverse=True)[:3]
        }
```

## Complexity Assessment

Queries requiring advanced reasoning should route to frontier models:

```python
def assess_complexity(self, query, intent):
    features = {
        'length': len(query.split()),
        'question_depth': self._count_sub_questions(query),
        'requires_world_knowledge': self._check_world_knowledge(query),
        'involves_reasoning': self._check_reasoning_indicators(query),
        'ambiguity_score': self._measure_ambiguity(query)
    }
    
    # Simple scoring
    complexity_score = 0
    if features['length'] > 100:
        complexity_score += 2
    if features['question_depth'] > 1:
        complexity_score += 3
    if features['requires_world_knowledge']:
        complexity_score += 3
    if features['involves_reasoning']:
        complexity_score += 2
    if features['ambiguity_score'] > 0.5:
        complexity_score += 2
    
    if complexity_score >= 7:
        return "complex"
    elif complexity_score >= 4:
        return "medium"
    else:
        return "simple"
```

## Cost-Aware Routing

Balance accuracy requirements with budget constraints:

```python
class CostAwareRouter(SemanticRouter):
    def __init__(self, *args, daily_budget=1000, **kwargs):
        super().__init__(*args, **kwargs)
        self.daily_budget = daily_budget
        self.daily_spend = 0
        self.reset_date = datetime.now().date()
    
    def route(self, query):
        # Reset budget daily
        if datetime.now().date() != self.reset_date:
            self.daily_spend = 0
            self.reset_date = datetime.now().date()
        
        # Check budget
        if self.daily_spend >= self.daily_budget:
            # Budget exhausted, use SLM only
            return self.slm.generate(query)
        
        # Normal routing with cost tracking
        intent = self.classify_intent(query)
        complexity = self.assess_complexity(query, intent)
        
        if self._should_use_frontier(complexity, intent):
            estimated_cost = self._estimate_cost(query)
            
            if self.daily_spend + estimated_cost <= self.daily_budget:
                result = self.frontier_llm.generate(query)
                self.daily_spend += estimated_cost
                return result
            else:
                # Would exceed budget, use SLM
                return self.slm.generate(query)
        else:
            return self.slm.generate(query)
```

## Adaptive Routing with Feedback

Learn from routing decisions:

```python
class AdaptiveRouter(SemanticRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.routing_history = []
    
    def route_with_feedback(self, query):
        intent = self.classify_intent(query)
        complexity = self.assess_complexity(query, intent)
        
        # Initial routing decision
        if complexity == "simple":
            model = "slm"
            result = self.slm.generate(query)
        else:
            model = "frontier"
            result = self.frontier_llm.generate(query)
        
        # Record decision
        self.routing_history.append({
            'query': query,
            'intent': intent,
            'complexity': complexity,
            'model_used': model,
            'result': result
        })
        
        return result
    
    def update_from_feedback(self, query_id, human_rating):
        # Use human ratings to refine routing thresholds
        record = self.routing_history[query_id]
        
        if record['model_used'] == "slm" and human_rating < 3:
            # SLM produced poor result, should have escalated
            self._adjust_escalation_threshold(record, increase=True)
        elif record['model_used'] == "frontier" and human_rating >= 4:
            # Frontier model worked well, potentially could have used SLM
            self._adjust_escalation_threshold(record, increase=False)
```

## Performance Monitoring

Track routing effectiveness:

```python
class RouterMetrics:
    def __init__(self, router):
        self.router = router
        self.metrics = {
            'slm_requests': 0,
            'frontier_requests': 0,
            'total_cost': 0,
            'escalations': 0,
            'slm_confidence': []
        }
    
    def log_routing_decision(self, query, decision, cost=0):
        if decision == 'slm':
            self.metrics['slm_requests'] += 1
        else:
            self.metrics['frontier_requests'] += 1
            self.metrics['total_cost'] += cost
    
    def get_statistics(self):
        total = self.metrics['slm_requests'] + self.metrics['frontier_requests']
        return {
            'slm_percentage': self.metrics['slm_requests'] / total * 100,
            'frontier_percentage': self.metrics['frontier_requests'] / total * 100,
            'average_cost_per_request': self.metrics['total_cost'] / total,
            'total_cost': self.metrics['total_cost']
        }
```

## Implementation Example

```python
# Initialize models
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
slm = OllamaModel('mistral:7b')
frontier_llm = OpenAIModel('gpt-4-turbo')

# Create router
router = SemanticRouter(
    embedding_model=embedding_model,
    slm=slm,
    frontier_llm=frontier_llm
)

# Route queries
queries = [
    "What is the current price of AAPL?",  # Simple - SLM
    "Analyze the geopolitical implications of recent Fed policy on emerging markets",  # Complex - Frontier
    "Extract company names from this earnings call transcript",  # Simple - SLM
    "Compare and contrast Keynesian and Austrian economic theories"  # Complex - Frontier
]

for query in queries:
    result = router.route(query)
    print(f"Query: {query}\nModel: {result.model_used}\nResponse: {result.text}\n")
```

## Best Practices

**Start Conservative:** Initially route to frontier models; gradually shift more queries to SLMs as confidence grows.

**Monitor Quality:** Track output quality by model tier; identify query types where SLM performance is insufficient.

**Iterate Thresholds:** Continuously refine routing thresholds based on production data.

**Provide Override:** Allow human operators to manually route specific queries when needed.

**Log Extensively:** Capture routing decisions for analysis and model improvement.

## Conclusion

Semantic routing enables hybrid architectures to optimize cost-accuracy-latency tradeoffs. By intelligently routing queries based on intent and complexity, organizations achieve 80-90% cost reduction while maintaining output quality. The key is treating routing not as static configuration but as a continuously optimized component informed by production feedback.
