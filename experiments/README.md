# GLADIUS Experiments Module

**Purpose**: Provide GLADIUS with a controlled space to design, run, and document experiments across any domain.

## Architecture

```
experiments/
├── auto_study/           # Automated documentation and observation system
│   ├── observer.py       # Watches containers and logs observations
│   ├── note_taker.py     # Generates structured notes from events
│   ├── study_generator.py # Creates research studies from data
│   └── reports/          # Generated reports and observations
├── containers/           # Docker experiment environments
│   ├── container_a/      # Isolated experiment A
│   └── container_b/      # Isolated experiment B (for A/B testing)
├── studies/              # Completed studies and findings
└── architecture_designs/ # New architecture blueprints
```

## Auto-Study System

The auto-study team operates **parallel to the main system**, observing without interference:

1. **Observer** - Monitors container logs, metrics, state changes
2. **Note Taker** - Converts observations into structured notes
3. **Study Generator** - Synthesizes notes into research documents

All data is vectorized and available in Hektor for GLADIUS to query.

## Container Isolation

Each experiment runs in a fully isolated Docker container with:
- Own filesystem
- Own network namespace
- Resource limits (CPU, memory)
- Auto-study team watching from outside

## Usage

```bash
# Create new experiment
./gladius.sh experiment create my_experiment

# Run experiment in container
./gladius.sh experiment run my_experiment

# View auto-study observations
./gladius.sh experiment observe my_experiment

# Generate study report
./gladius.sh experiment report my_experiment
```

## Experiment Types

GLADIUS can design experiments across all domains:
- **Technological**: Testing new algorithms, architectures
- **Psychological**: Studying agent behaviors
- **Ethical**: Exploring decision-making boundaries
- **Mathematical**: Proving theorems, exploring patterns
- **Logical**: Testing reasoning capabilities
- **Architectural**: Designing system structures
- **Emotional**: Understanding sentiment and response
- **Physical**: Simulating real-world physics (when applicable)
