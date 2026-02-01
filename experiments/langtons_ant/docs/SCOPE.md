# Langton's Ant Experiment - Scope

> **Experiment ID**: EXP-001  
> **Created**: 2026-02-01  
> **Status**: Active

---

## Overview

**Langton's Ant** is a two-dimensional cellular automaton with simple rules that produces complex emergent behavior. In this experiment, the **GLADIUS 71M model IS the ant** - it makes decisions at each step based on its current cell state.

---

## The Rules (Classic Langton's Ant)

1. At a **white** square: turn 90° clockwise, flip color, move forward
2. At a **black** square: turn 90° counter-clockwise, flip color, move forward

---

## GLADIUS as the Ant

Instead of hardcoded rules, GLADIUS-71M will:

1. **Perceive**: Receive current cell state (color) and orientation
2. **Decide**: Choose direction based on learned patterns
3. **Act**: Move and flip cell

### Input to Model
```json
{
  "cell_color": "white" | "black",
  "orientation": "N" | "E" | "S" | "W",
  "step": 12345,
  "local_neighborhood": [[0,1,0], [1,X,1], [0,0,1]]
}
```

### Expected Output
```json
{
  "turn": "clockwise" | "counter_clockwise" | "straight" | "reverse",
  "confidence": 0.95
}
```

---

## Hypothesis

1. **Phase 1**: GLADIUS will learn the classic rules through reinforcement
2. **Phase 2**: GLADIUS may discover variations or optimizations
3. **Phase 3**: Emergent behaviors may differ from classic Langton's Ant
4. **Phase 4**: Potential for novel pattern discovery

---

## Success Criteria

1. ✅ GLADIUS can replicate classic Langton's Ant behavior
2. ⏳ GLADIUS demonstrates learning (improves over iterations)
3. ⏳ GLADIUS shows emergent behavior after ~10,000 steps
4. ⏳ Auto-study team documents any deviations from expected

---

## Boundaries

- Grid size: 1000 x 1000 (expandable)
- Max steps: 1,000,000
- Checkpoint interval: Every 10,000 steps
- Model inference: CPU mode (to allow continuous running)

---

## Timeline

| Phase | Duration | Objective |
|-------|----------|-----------|
| Setup | 1 day | Environment, baseline |
| Training | 3 days | Learn classic rules |
| Free Run | 7 days | Observe emergence |
| Analysis | 3 days | Document findings |

---

## Resources

- Model: GLADIUS 71M (archived version)
- Compute: CPU mode (background)
- Storage: ~1GB for grid states
- Vectorization: Results → Hektor

---

*"From simple rules, complexity emerges."*
