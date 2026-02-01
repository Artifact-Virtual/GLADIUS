# GLADIUS v2.0 Migration Summary

> **Date**: 2026-02-01  
> **Migration**: v1.1 (71M monolithic) → v2.0 (Modular Specialist Network)

---

## What Changed

### Architecture Shift

| Aspect | v1.1 (Old) | v2.0 (New) |
|--------|------------|------------|
| Architecture | Single 71M parameter model | Modular Specialist Network (~30M total) |
| Training | Monolithic fine-tuning | Per-specialist training |
| Routing | Direct inference | Central Nexus orchestration |
| Emergence | Unlikely at 71M | Designed for emergence |

### File Structure

```
GLADIUS/
├── docs/
│   ├── archive/              # OLD: v1.1 documentation
│   │   ├── ARCHITECTURE.md
│   │   ├── BLUEPRINT.md
│   │   └── MODEL_CARD.md
│   ├── ARCHITECTURE_V2.md    # NEW: v2.0 architecture
│   └── SPECIALIST_SPECS.md   # NEW: Specialist specifications
├── models/
│   ├── archive/              # OLD: v1.1 models (for experiments)
│   │   ├── base/
│   │   ├── gladius_primary/
│   │   ├── native/
│   │   ├── production/
│   │   └── staging/
│   └── [new v2.0 structure to be created]
└── ...
```

---

## Archived Components

### Models (kept for experiments like Langton's Ant)
- `gladius_primary/` - Main 71M model
- `native/` - Native GGUF export
- `base/` - Base model
- `production/` - Production checkpoint
- `staging/` - Staging checkpoint

### Documentation
- `ARCHITECTURE.md` - v1.1 architecture
- `BLUEPRINT.md` - v1.1 blueprint
- `MODEL_CARD.md` - v1.1 model card

---

## HuggingFace Status

Repository: https://huggingface.co/amuzetnoM/Gladius

Current content:
- v1.1 71M GGUF files (archived, available for Langton's Ant experiment)
- Model card (to be updated for v2.0)

Future:
- v2.0 specialist models when trained
- Updated model card with MSN architecture

---

## Experiments Module

New experiments directory created at `/home/adam/worxpace/gladius/experiments/`:

### Active Experiments

| ID | Name | Description | Model |
|----|------|-------------|-------|
| EXP-001 | langtons_ant | GLADIUS IS the ant | v1.1 71M |

### Auto-Study Teams

- **Observer**: Watches experiments, logs events
- **Analyst**: Processes data, detects patterns
- **Reporter**: Generates human-readable reports

---

## Next Steps

1. **Implement v2.0 Specialists**
   - Create specialist model scaffolding
   - Set up per-specialist training pipelines
   - Implement Central Nexus routing

2. **Run Langton's Ant Experiment**
   - Use archived 71M model
   - Validate experiment infrastructure
   - Test auto-study teams

3. **Train v2.0 System**
   - Train individual specialists
   - Train nexus routing
   - Joint fine-tuning

4. **Update HuggingFace**
   - Upload v2.0 specialists
   - Update model card
   - Keep v1.1 archived for reference

---

## Backward Compatibility

The v1.1 71M model remains available at:
```
/home/adam/worxpace/gladius/GLADIUS/models/archive/gladius_primary/
/home/adam/worxpace/gladius/GLADIUS/models/archive/native/
```

This allows:
- Langton's Ant experiment to run
- Comparisons between v1.1 and v2.0
- Fallback if v2.0 training fails

---

*"Evolution requires preserving what works while building what's better."*
