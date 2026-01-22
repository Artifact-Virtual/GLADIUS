# llama.cpp Setup Guide

This guide will help you set up llama.cpp as the primary adapter for nanocode v4.

## Why llama.cpp?

- **Local & Private**: No data sent to external APIs
- **Fast**: Optimized C++ implementation
- **Free**: No API costs
- **Open Source**: Full control over your models
- **Flexible**: Works with any GGUF model

## Quick Start

### 1. Install llama.cpp

```bash
# Clone llama.cpp repository
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# Build (with GPU support if available)
make

# Or with CUDA for NVIDIA GPUs:
make LLAMA_CUBLAS=1

# Or with Metal for Mac M1/M2:
make LLAMA_METAL=1
```

### 2. Download a Model

Download a GGUF format model. Recommended models:

**Small & Fast (recommended for testing):**
- **Llama-3.2-3B-Instruct** (~2GB)
- **Phi-3-mini** (~2.4GB)

**Medium (good balance):**
- **Llama-3.1-8B-Instruct** (~4.7GB)
- **Mistral-7B-Instruct** (~4.1GB)

**Large (best quality):**
- **Llama-3.1-70B-Instruct** (~40GB, needs powerful GPU)

Download from Hugging Face:
```bash
# Example: Download Llama-3.2-3B-Instruct
huggingface-cli download bartowski/Llama-3.2-3B-Instruct-GGUF \
  Llama-3.2-3B-Instruct-Q4_K_M.gguf \
  --local-dir ./models
```

Or manually from: https://huggingface.co/models?library=gguf

### 3. Start llama.cpp Server

```bash
# Basic server (CPU only)
./server -m ./models/Llama-3.2-3B-Instruct-Q4_K_M.gguf \
  --port 8080 \
  --ctx-size 4096 \
  --n-gpu-layers 0

# With GPU acceleration (recommended)
./server -m ./models/Llama-3.2-3B-Instruct-Q4_K_M.gguf \
  --port 8080 \
  --ctx-size 4096 \
  --n-gpu-layers 35

# Advanced: With more options
./server -m ./models/Llama-3.2-3B-Instruct-Q4_K_M.gguf \
  --port 8080 \
  --ctx-size 8192 \
  --n-gpu-layers 35 \
  --threads 8 \
  --batch-size 512
```

**Server Options Explained:**
- `--port 8080`: Port to listen on (must match LLAMA_SERVER_URL)
- `--ctx-size 4096`: Context window size in tokens
- `--n-gpu-layers 35`: Number of layers to offload to GPU (0 = CPU only)
- `--threads 8`: Number of CPU threads to use
- `--batch-size 512`: Batch size for prompt processing

### 4. Configure nanocode

Create or edit `.env` file:
```bash
# Primary adapter
ADAPTER_TYPE=llamacpp

# Server configuration
LLAMA_SERVER_URL=http://localhost:8080
LLAMA_MAX_TOKENS=2048
LLAMA_TEMPERATURE=0.7
LLAMA_TIMEOUT=120
```

### 5. Run nanocode

```bash
python run.py
```

## Verification

Test if llama.cpp server is running:
```bash
# Check health endpoint
curl http://localhost:8080/health

# Check models endpoint
curl http://localhost:8080/v1/models

# Test completion
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }'
```

## Troubleshooting

### Server won't start
- **Problem**: Model file not found
  - **Solution**: Check the path to your .gguf file
  
- **Problem**: Port already in use
  - **Solution**: Use a different port: `--port 8081`
  
- **Problem**: Out of memory
  - **Solution**: Use a smaller model or reduce `--ctx-size`

### Connection errors
- **Problem**: "Connection refused"
  - **Solution**: Make sure server is running: `ps aux | grep server`
  
- **Problem**: "Connection timeout"
  - **Solution**: Increase `LLAMA_TIMEOUT` in `.env`
  
- **Problem**: Wrong URL
  - **Solution**: Verify `LLAMA_SERVER_URL` matches server port

### Slow performance
- **Problem**: Slow generation
  - **Solution**: Enable GPU layers: `--n-gpu-layers 35`
  
- **Problem**: Still slow
  - **Solution**: Use a smaller/quantized model (Q4_K_M)
  
- **Problem**: High memory usage
  - **Solution**: Reduce `--ctx-size` or use smaller model

## Remote Server Setup

To use llama.cpp on a remote server:

1. **Start server on remote machine:**
```bash
./server -m model.gguf --host 0.0.0.0 --port 8080
```

2. **Configure nanocode:**
```bash
export LLAMA_SERVER_URL=http://your-server-ip:8080
```

## Advanced Configuration

### Multiple Models

Run multiple servers on different ports:
```bash
# Small model for quick tasks
./server -m small-model.gguf --port 8080

# Large model for complex tasks
./server -m large-model.gguf --port 8081
```

Then switch between them:
```bash
export LLAMA_SERVER_URL=http://localhost:8080  # Use small model
# or
export LLAMA_SERVER_URL=http://localhost:8081  # Use large model
```

### Docker Setup

Run llama.cpp in Docker:
```bash
docker run -d \
  --name llamacpp \
  -p 8080:8080 \
  -v /path/to/models:/models \
  ghcr.io/ggerganov/llama.cpp:server \
  -m /models/your-model.gguf \
  --port 8080 \
  --host 0.0.0.0
```

## Model Recommendations by Use Case

### Code Analysis (nanocode's primary use)
- **Best**: Llama-3.1-8B-Instruct or CodeLlama-7B
- **Why**: Good balance of speed and code understanding

### General Tasks
- **Best**: Llama-3.2-3B-Instruct or Phi-3-mini
- **Why**: Fast, efficient, good for most tasks

### Complex Reasoning
- **Best**: Llama-3.1-70B-Instruct (if you have GPU)
- **Why**: Best quality, deeper understanding

### Resource Constrained
- **Best**: Llama-3.2-1B or TinyLlama
- **Why**: Run on CPU, minimal memory

## Performance Tips

1. **Use quantized models**: Q4_K_M is sweet spot (quality vs. size)
2. **Enable GPU**: `--n-gpu-layers 35` (or more)
3. **Increase batch size**: `--batch-size 512` for faster prompt processing
4. **Optimize context**: Don't use more `--ctx-size` than needed
5. **Use cache**: llama.cpp caches KV data for speed

## Resources

- **llama.cpp GitHub**: https://github.com/ggerganov/llama.cpp
- **Model Repository**: https://huggingface.co/models?library=gguf
- **Quantization Guide**: https://github.com/ggerganov/llama.cpp/blob/master/examples/quantize/README.md
- **Server API Docs**: https://github.com/ggerganov/llama.cpp/blob/master/examples/server/README.md

## Example: Complete Setup (Ubuntu/Linux)

```bash
# 1. Install dependencies
sudo apt-get update
sudo apt-get install build-essential git curl

# 2. Clone and build llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make -j$(nproc)

# 3. Download model
mkdir models
cd models
wget https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf
cd ..

# 4. Start server
./server -m ./models/Llama-3.2-3B-Instruct-Q4_K_M.gguf \
  --port 8080 \
  --ctx-size 4096 \
  --n-gpu-layers 0 &

# 5. Configure nanocode
cd /path/to/nanocode
echo "ADAPTER_TYPE=llamacpp" > .env
echo "LLAMA_SERVER_URL=http://localhost:8080" >> .env

# 6. Run nanocode
python run.py
```

## Next Steps

Once llama.cpp is running:
1. Test with mock adapter first: `export ADAPTER_TYPE=mock`
2. Verify llama.cpp server: `curl http://localhost:8080/health`
3. Switch to llama.cpp: `export ADAPTER_TYPE=llamacpp`
4. Run nanocode and monitor performance

Enjoy local, private, and fast AI-powered coding assistance!
