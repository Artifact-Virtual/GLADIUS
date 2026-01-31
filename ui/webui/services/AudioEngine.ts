
import { SwarmState } from '../types';

class AudioEngine {
  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private currentOscillators: (OscillatorNode | BiquadFilterNode)[] = [];
  private state: SwarmState = SwarmState.SLEEPING;
  private initialized = false;

  constructor() {}

  public init() {
    if (this.initialized) return;
    this.ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
    this.masterGain = this.ctx.createGain();
    this.masterGain.gain.value = 0.2;
    this.masterGain.connect(this.ctx.destination);
    this.initialized = true;
    this.updateState(SwarmState.SLEEPING);
  }

  public updateState(state: SwarmState) {
    if (!this.ctx || !this.masterGain) return;
    this.state = state;
    this.clearNodes();

    switch (state) {
      case SwarmState.SLEEPING:
        this.playSleepingDrone();
        break;
      case SwarmState.LEARNING:
        this.playLearningGlitches();
        break;
      case SwarmState.INTERACTING:
        this.playInteractingPads();
        break;
    }
  }

  private clearNodes() {
    this.currentOscillators.forEach(node => {
      try {
        if ('stop' in node) node.stop();
        node.disconnect();
      } catch (e) {}
    });
    this.currentOscillators = [];
  }

  private playSleepingDrone() {
    if (!this.ctx || !this.masterGain) return;
    
    // Deep sub-bass drone
    const osc = this.ctx.createOscillator();
    const lfo = this.ctx.createOscillator();
    const lfoGain = this.ctx.createGain();
    const filter = this.ctx.createBiquadFilter();

    osc.type = 'sine';
    osc.frequency.value = 40;
    
    lfo.type = 'sine';
    lfo.frequency.value = 0.2; // Slow pulse
    lfoGain.gain.value = 20;

    filter.type = 'lowpass';
    filter.frequency.value = 200;

    lfo.connect(lfoGain);
    lfoGain.connect(osc.frequency);
    osc.connect(filter);
    filter.connect(this.masterGain);

    osc.start();
    lfo.start();
    this.currentOscillators.push(osc, filter);
  }

  private playLearningGlitches() {
    if (!this.ctx || !this.masterGain) return;

    const interval = setInterval(() => {
      if (this.state !== SwarmState.LEARNING || !this.ctx || !this.masterGain) {
        clearInterval(interval);
        return;
      }

      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      
      osc.type = Math.random() > 0.5 ? 'square' : 'sawtooth';
      osc.frequency.setValueAtTime(440 + Math.random() * 2000, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(100, this.ctx.currentTime + 0.1);
      
      gain.gain.setValueAtTime(0.1, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + 0.1);

      osc.connect(gain);
      gain.connect(this.masterGain);

      osc.start();
      osc.stop(this.ctx.currentTime + 0.1);
    }, 150);
  }

  private playInteractingPads() {
    if (!this.ctx || !this.masterGain) return;

    const frequencies = [261.63, 329.63, 392.00, 523.25]; // C Major Chord
    frequencies.forEach(freq => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      const lfo = this.ctx.createOscillator();
      const lfoGain = this.ctx.createGain();

      osc.type = 'sine';
      osc.frequency.value = freq;
      
      lfo.type = 'sine';
      lfo.frequency.value = 0.5 + Math.random();
      lfoGain.gain.value = 0.05;

      gain.gain.value = 0.05;

      lfo.connect(lfoGain);
      lfoGain.connect(gain.gain);
      osc.connect(gain);
      gain.connect(this.masterGain);

      osc.start();
      this.currentOscillators.push(osc);
    });
  }

  public setVolume(val: number) {
    if (this.masterGain) {
      this.masterGain.gain.setTargetAtTime(val, this.ctx?.currentTime || 0, 0.1);
    }
  }

  public stop() {
    this.clearNodes();
  }
}

export const audioEngine = new AudioEngine();
