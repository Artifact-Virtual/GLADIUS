# Langton's Ant Experiment - Requirements

> **Experiment ID**: EXP-001

---

## System Requirements

### Hardware
- CPU: 4+ cores (dedicated to experiment)
- RAM: 4GB minimum
- Storage: 10GB for full experiment

### Software
- Python 3.10+
- PyTorch (CPU mode)
- NumPy
- Matplotlib (visualization)
- Hektor VDB (for result storage)

---

## Dependencies

```txt
torch>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
pillow>=9.5.0
hektor-vdb>=0.1.0
tqdm>=4.65.0
```

---

## Model Requirements

### GLADIUS 71M Model
- Location: `/home/adam/worxpace/gladius/GLADIUS/models/archive/gladius-71m/`
- Format: GGUF or PyTorch checkpoint
- Mode: Inference only (no training during experiment)

### Model Interface
```python
class LangtonGladiusAnt:
    def __init__(self, model_path: str):
        self.model = load_model(model_path)
    
    def decide(self, state: dict) -> dict:
        """
        Input: {"cell_color": str, "orientation": str, "step": int, "neighborhood": list}
        Output: {"turn": str, "confidence": float}
        """
        pass
```

---

## Data Requirements

### Input Data
- Initial grid state (optional, default: all white)
- Starting position (default: center)
- Starting orientation (default: North)

### Output Data
- Grid snapshots (every N steps)
- Decision log (every step)
- Performance metrics
- Emergence indicators

---

## Integration Requirements

### Hektor VDB
- Store decision embeddings
- Enable pattern retrieval
- Support similarity search for recurring patterns

### Auto-Study Teams
- Observer: Read-only access to experiment state
- Analyst: Access to decision logs
- Reporter: Write access to reports directory

---

## Containerization (Optional)

```dockerfile
FROM python:3.10-slim

WORKDIR /experiment

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV EXPERIMENT_ID=EXP-001
ENV MODEL_PATH=/models/gladius-71m

CMD ["python", "src/main.py"]
```

---

## Environment Variables

```bash
EXPERIMENT_ID=EXP-001
MODEL_PATH=/home/adam/worxpace/gladius/GLADIUS/models/archive/gladius-71m
GRID_SIZE=1000
MAX_STEPS=1000000
CHECKPOINT_INTERVAL=10000
HEKTOR_URL=http://localhost:8765
LOG_LEVEL=INFO
```

---

## Validation Checklist

- [ ] Model loads successfully
- [ ] Grid initializes correctly
- [ ] Single step executes without error
- [ ] Decision logging works
- [ ] Checkpoint saving/loading works
- [ ] Auto-study connection established
- [ ] Hektor integration functional

---

*"Requirements are the foundation of reproducible science."*
