# Langton's Ant - GLADIUS Neural Simulation

GLADIUS IS THE ANT - Watch emergent behavior unfold.

## Versions

### 2D Version (`animated.py`)
Classic Langton's Ant with fluid terminal animation.

### 3D Version (`animated_3d.py`)
Extended to cubic lattice with 6 directions and isometric rendering.

## Quick Start

```bash
# Run 2D animated version
python3 src/animated.py --model /path/to/gladius/models

# Run 3D animated version  
python3 src/animated_3d.py --model /path/to/gladius/models

# With custom grid size
python3 src/animated.py --grid 1000      # 2D
python3 src/animated_3d.py --grid 100    # 3D (smaller due to memory)
```

## Controls

| Key | Action |
|-----|--------|
| SPACE | Pause/Resume |
| ↑/↓ | Speed up/down |
| F | Toggle follow ant |
| R | Reset |
| Q | Quit |
| V | Cycle views (3D only) |

## 3D View Modes

1. **Isometric**: Stacked layers with diagonal offset
2. **Layers**: Side-by-side Z slices (Z-1, Z=0, Z+1)
3. **Cross-Section**: XZ and YZ planes through ant position

## The Rules

### 2D (Classic)
- On white: turn 90° clockwise, flip cell, move forward
- On black: turn 90° counter-clockwise, flip cell, move forward

### 3D (Extended)
- Same rules extended to 6 directions in cubic space
- Rotations occur in the plane perpendicular to movement

## Emergence

After ~10,000 steps, chaotic behavior gives way to "highway" construction - 
ordered diagonal patterns. This emergence from simple rules is what GLADIUS 
studies to develop understanding of complex systems.
