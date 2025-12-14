# Best Practices for Local SLM Deployment and Monitoring

## Introduction

Deploying small language models (SLMs) locally transforms the economics and performance of AI systems in financial services. However, the transition from cloud-based APIs to self-managed infrastructure introduces operational responsibilities that many organizations underestimate. This guide provides comprehensive best practices for deploying, operating, and monitoring local SLM infrastructure in production environments.

## Infrastructure Planning

### Hardware Selection

**CPU-Based Deployment:**
- **Minimum:** 8-core CPU, 16GB RAM
- **Recommended:** 16-core CPU, 32GB RAM
- **Optimal:** 32-core CPU, 64GB RAM
- **Use Case:** Development, low-throughput production (< 10 req/sec)

**GPU-Based Deployment:**
- **Entry:** NVIDIA RTX 4090 (24GB VRAM) - $1,500-2,000
- **Production:** NVIDIA A10G (24GB VRAM) - Cloud $1.00/hour
- **High-Performance:** NVIDIA A100 (40GB/80GB VRAM) - Cloud $3-5/hour
- **Use Case:** Production workloads requiring sub-100ms latency

**Capacity Planning Formula:**
```
Required VRAM (GB) = Model Size (B params) × Quantization Factor
- Q4: 0.5-0.6 GB per billion parameters
- Q5: 0.65-0.75 GB per billion parameters
- Q8: 1.0-1.1 GB per billion parameters
- FP16: 2.0 GB per billion parameters

Example: Mistral 7B Q4_K_M = 7B × 0.55 = 3.85 GB VRAM
Add 2GB overhead for KV cache and operations = 6GB total
```

### Software Stack

**Option 1: Ollama (Recommended for Most)**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Configure for production
sudo systemctl enable ollama
sudo systemctl start ollama

# Set environment variables
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_MAX_LOADED_MODELS=2
```

**Option 2: vLLM (High-Throughput GPU)**
```bash
# Install vLLM
pip install vllm

# Run server
python -m vllm.entrypoints.openai.api_server \
  --model mistralai/Mistral-7B-Instruct-v0.2 \
  --dtype float16 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.95
```

**Option 3: llama.cpp (CPU Optimization)**
```bash
# Build llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# Run server
./server -m models/mistral-7b-q4_k_m.gguf \
  -c 4096 \
  -ngl 32 \
  --host 0.0.0.0 \
  --port 8080 \
  -t 8
```

## Deployment Architecture

### Single Instance Setup (Small Scale)

```
┌─────────────────┐
│  Load Balancer  │
│   (nginx/HAProxy)│
└────────┬────────┘
         │
┌────────▼────────┐
│   SLM Server    │
│   Ollama/vLLM   │
│   Model: 7B     │
└─────────────────┘
```

**Configuration:**
```nginx
# nginx load balancer config
upstream slm_backend {
    server localhost:11434;
}

server {
    listen 8000;
    
    location / {
        proxy_pass http://slm_backend;
        proxy_read_timeout 120s;
        proxy_connect_timeout 10s;
    }
}
```

### Multi-Instance Setup (Production Scale)

```
                ┌─────────────────┐
                │  Load Balancer  │
                │   (nginx/HAProxy)│
                └────────┬────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
┌────────▼────────┐ ┌───▼────────┐ ┌───▼────────┐
│   SLM Server 1  │ │ SLM Server 2│ │ SLM Server 3│
│   Mistral 7B    │ │ Mistral 7B  │ │ Mistral 7B  │
└─────────────────┘ └─────────────┘ └─────────────┘
```

**Load Balancing Strategy:**
```python
# Health check endpoint
@app.get("/health")
def health_check():
    try:
        # Test inference
        result = model.generate("test", max_tokens=5)
        return {
            "status": "healthy",
            "model_loaded": True,
            "response_time_ms": result.latency
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 503
```

## Model Management

### Model Storage and Versioning

```bash
# Directory structure
/opt/models/
├── mistral-7b/
│   ├── v2.0/
│   │   ├── model-q4_k_m.gguf
│   │   ├── model-q5_k_m.gguf
│   │   └── metadata.json
│   ├── v2.1/
│   │   └── model-q4_k_m.gguf
│   └── current -> v2.1
├── llama-3-8b/
│   └── v1.0/
│       └── model-q4_k_m.gguf
└── registry.json
```

**Model Registry:**
```json
{
  "models": [
    {
      "name": "mistral-7b",
      "version": "v2.1",
      "quantization": "Q4_K_M",
      "size_gb": 3.8,
      "checksum": "sha256:abc123...",
      "deployed_date": "2024-03-15",
      "performance_metrics": {
        "avg_latency_ms": 45,
        "throughput_tps": 38,
        "quality_score": 0.94
      }
    }
  ]
}
```

### Hot-Swapping Models

```python
class ModelManager:
    def __init__(self):
        self.current_model = None
        self.loading_lock = threading.Lock()
    
    def swap_model(self, new_model_path):
        """Zero-downtime model swap"""
        with self.loading_lock:
            # Load new model
            new_model = self._load_model(new_model_path)
            
            # Atomic swap
            old_model = self.current_model
            self.current_model = new_model
            
            # Cleanup old model (after grace period)
            time.sleep(10)  # Allow in-flight requests to complete
            if old_model:
                old_model.unload()
    
    def _load_model(self, path):
        # Validate model before loading
        self._validate_model(path)
        return Model.load(path)
```

## Monitoring and Observability

### Key Metrics

**Infrastructure Metrics:**
- CPU utilization (target: < 80% average)
- Memory usage (should not exceed 90%)
- GPU utilization (target: 70-90% for cost efficiency)
- GPU memory usage
- Disk I/O for model loading

**Application Metrics:**
- Requests per second
- Time to first token (TTFT) - P50, P95, P99
- Tokens per second (throughput)
- Request queue depth
- Active concurrent requests

**Quality Metrics:**
- Response confidence scores
- Escalation rate to frontier models
- Error rate by error type
- Model accuracy on validation set

### Prometheus Integration

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
inference_requests = Counter(
    'slm_inference_requests_total',
    'Total inference requests',
    ['model', 'status']
)

inference_latency = Histogram(
    'slm_inference_latency_seconds',
    'Inference latency in seconds',
    ['model'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

tokens_per_second = Gauge(
    'slm_tokens_per_second',
    'Current generation speed',
    ['model']
)

gpu_memory_usage = Gauge(
    'slm_gpu_memory_bytes',
    'GPU memory usage in bytes'
)

# Instrument inference
def generate_with_metrics(model_name, prompt):
    start = time.time()
    try:
        result = model.generate(prompt)
        
        # Record success
        inference_requests.labels(model=model_name, status='success').inc()
        
        # Record latency
        latency = time.time() - start
        inference_latency.labels(model=model_name).observe(latency)
        
        # Record throughput
        tps = len(result.tokens) / latency
        tokens_per_second.labels(model=model_name).set(tps)
        
        return result
    
    except Exception as e:
        inference_requests.labels(model=model_name, status='error').inc()
        raise

# Start metrics server
start_http_server(9090)
```

### Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "title": "SLM Production Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [{
          "expr": "rate(slm_inference_requests_total[5m])"
        }]
      },
      {
        "title": "P95 Latency",
        "targets": [{
          "expr": "histogram_quantile(0.95, slm_inference_latency_seconds_bucket)"
        }]
      },
      {
        "title": "Tokens per Second",
        "targets": [{
          "expr": "slm_tokens_per_second"
        }]
      },
      {
        "title": "GPU Memory Usage",
        "targets": [{
          "expr": "slm_gpu_memory_bytes / (1024^3)"
        }]
      }
    ]
  }
}
```

### Alerting Rules

```yaml
groups:
  - name: slm_alerts
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, slm_inference_latency_seconds_bucket) > 1.0
        for: 5m
        annotations:
          summary: "High inference latency detected"
          description: "P95 latency is {{ $value }}s"
      
      - alert: HighErrorRate
        expr: rate(slm_inference_requests_total{status="error"}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"
      
      - alert: GPUMemoryHigh
        expr: slm_gpu_memory_bytes / gpu_memory_total_bytes > 0.95
        for: 10m
        annotations:
          summary: "GPU memory usage above 95%"
      
      - alert: ModelNotResponding
        expr: up{job="slm_server"} == 0
        for: 1m
        annotations:
          summary: "SLM server is down"
```

## Performance Optimization

### Batch Processing

```python
class BatchInferenceServer:
    def __init__(self, max_batch_size=32, max_wait_ms=50):
        self.max_batch_size = max_batch_size
        self.max_wait_ms = max_wait_ms
        self.pending_requests = []
        self.batch_lock = threading.Lock()
    
    async def generate(self, prompt):
        # Add to batch
        future = asyncio.Future()
        with self.batch_lock:
            self.pending_requests.append((prompt, future))
            
            if len(self.pending_requests) >= self.max_batch_size:
                asyncio.create_task(self._process_batch())
        
        # Wait for result
        return await future
    
    async def _process_batch(self):
        with self.batch_lock:
            if not self.pending_requests:
                return
            
            batch = self.pending_requests[:self.max_batch_size]
            self.pending_requests = self.pending_requests[self.max_batch_size:]
        
        # Process batch
        prompts = [p for p, _ in batch]
        results = model.generate_batch(prompts)
        
        # Return results
        for (_, future), result in zip(batch, results):
            future.set_result(result)
```

### KV Cache Optimization

```python
# Configure KV cache for optimal performance
model_config = {
    "n_ctx": 4096,  # Context window
    "n_batch": 512,  # Batch size for prompt processing
    "n_gpu_layers": 32,  # Offload layers to GPU
    "use_mlock": True,  # Keep model in RAM
    "use_mmap": True,  # Memory map model file
}
```

### Quantization Selection

```python
def select_quantization(requirements):
    """Choose optimal quantization level"""
    if requirements["quality"] == "maximum":
        return "Q8_0"  # Minimal quality loss
    elif requirements["quality"] == "high":
        return "Q5_K_M"  # Good balance
    elif requirements["quality"] == "balanced":
        return "Q4_K_M"  # Recommended default
    elif requirements["quality"] == "fast":
        return "Q4_0"  # Maximum speed
    else:
        return "Q2_K"  # Extreme compression
```

## Security Best Practices

### Access Control

```python
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if not validate_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

@app.post("/generate")
async def generate(request: GenerateRequest, token: str = Depends(verify_token)):
    # Only accessible with valid token
    return model.generate(request.prompt)
```

### Input Validation

```python
def sanitize_input(prompt: str, max_length: int = 4096) -> str:
    """Sanitize and validate user input"""
    # Length check
    if len(prompt) > max_length:
        raise ValueError(f"Prompt exceeds maximum length of {max_length}")
    
    # Content filtering
    if contains_malicious_patterns(prompt):
        raise ValueError("Prompt contains prohibited content")
    
    # Normalize whitespace
    prompt = " ".join(prompt.split())
    
    return prompt
```

### Rate Limiting

```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@app.post("/generate")
@limiter.limit("100/minute")
async def generate(request: GenerateRequest):
    return model.generate(request.prompt)
```

## Operational Runbook

### Deployment Checklist

- [ ] Hardware provisioned and validated
- [ ] Software stack installed (Ollama/vLLM/llama.cpp)
- [ ] Models downloaded and verified (checksums)
- [ ] Load balancer configured
- [ ] Health checks operational
- [ ] Monitoring dashboards created
- [ ] Alerting rules configured
- [ ] Backup models available
- [ ] Rollback procedure documented
- [ ] On-call rotation established

### Common Issues and Resolutions

**Issue: High latency spikes**
- Check GPU temperature and throttling
- Verify no CPU contention from other processes
- Check batch size configuration
- Review request queue depth

**Issue: Out of memory errors**
- Reduce context window size
- Switch to smaller model or higher quantization
- Limit concurrent requests
- Check for memory leaks

**Issue: Model quality degradation**
- Validate model file integrity
- Check quantization level
- Review input preprocessing
- Compare against baseline metrics

**Issue: Server unresponsive**
- Check process is running
- Verify GPU is accessible
- Review system logs
- Restart service if needed

### Backup and Disaster Recovery

```bash
#!/bin/bash
# Backup script
backup_models() {
    DATE=$(date +%Y%m%d)
    BACKUP_DIR="/backup/models-$DATE"
    
    mkdir -p $BACKUP_DIR
    
    # Backup model files
    rsync -av /opt/models/ $BACKUP_DIR/
    
    # Backup configuration
    cp /etc/ollama/* $BACKUP_DIR/config/
    
    # Upload to S3
    aws s3 sync $BACKUP_DIR s3://model-backups/$DATE/
}
```

## Conclusion

Successful local SLM deployment requires treating model serving as production infrastructure with appropriate operational rigor. Monitoring, alerting, capacity planning, and disaster recovery are not optional—they are prerequisites for reliable operation. Organizations that implement these best practices achieve 99.9% uptime with predictable performance and manageable operational overhead.

The investment in proper deployment infrastructure pays dividends in reduced costs, improved latency, and operational confidence. Start with conservative configurations, monitor extensively, and optimize based on production data.
