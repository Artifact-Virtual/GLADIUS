# GLADIUS Web Interface

A real-time visualization of the GLADIUS AI consciousness as a particle swarm.

## Features

- **Particle Visualization**: 15,000+ particles representing GLADIUS's 71M neural parameters
- **Real-time State Sync**: Connects to GLADIUS backend for live system status
- **Voice Interaction**: Speech-to-text and text-to-speech via Web Speech API
- **Dual Engine Support**: 
  - **GLADIUS Native** (llama.cpp) - Primary
  - **Gemini** (Google) - Fallback

## States

| State | Color | Description |
|-------|-------|-------------|
| SLEEPING | Indigo/Purple | Dormant - particles orbit calmly |
| LEARNING | Cyan/Teal | Active training - particles flow in neural patterns |
| INTERACTING | Orange/Gold | Voice active - particles react to speech |

## Setup

```bash
cd /home/adam/worxpace/gladius/ui/webui
npm install
npm run dev
```

## Configuration

Edit `.env.local`:
```env
VITE_LLAMA_ENDPOINT=http://localhost:8080
VITE_GLADIUS_API_URL=http://localhost:7000
VITE_MODEL_NAME=gladius1.1:71M-native
```

## Integration

The webapp connects to:
- **llama.cpp server** at port 8080 for inference
- **GLADIUS Infra API** at port 7000 for system telemetry
- **Hektor VDB** for vector count metrics

## Metrics HUD

Displays real-time:
- Parameter count (71M)
- Particle/mote count
- Vector database entries
- Training progress, loss, epochs
- CPU/Memory usage
- Active modules (SENTINEL, SYNDICATE, etc.)

## Architecture

```
App.tsx                  # Main React component
├── services/
│   ├── SwarmEngine.ts   # Canvas particle physics
│   ├── LlamaService.ts  # GLADIUS llama.cpp client
│   ├── LiveService.ts   # Gemini WebSocket client
│   ├── GladiusService.ts # System status polling
│   └── AudioEngine.ts   # Ambient sound
└── components/
    ├── Overlay.tsx      # UI overlay with HUD
    └── StateSelector.tsx # State buttons
```
