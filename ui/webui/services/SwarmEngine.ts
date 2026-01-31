
import { Particle, SwarmState, SwarmParams } from '../types';

// Dynamic particle count - can be updated based on model params
// 71M params = 15000 particles (scaled for performance)
// Ratio: 1 particle per ~4733 parameters
let PARTICLE_COUNT = 15000;
const MAX_VELOCITY = 15;

export class SwarmEngine {
  private particles: Particle[] = [];
  private ctx: CanvasRenderingContext2D;
  private width: number = 0;
  private height: number = 0;
  private state: SwarmState = SwarmState.SLEEPING;
  private mouseX: number = -1000;
  private mouseY: number = -1000;
  private targetParticleCount: number = PARTICLE_COUNT;
  
  private currentParams: SwarmParams = {
    drag: 0.95,
    cohesion: 0.02,
    speed: 0.5,
    turbulence: 0.1,
    mouseForce: -1,
    bloom: 0.5,
    thinkingEnergy: 0,
    audioAmplitude: 0
  };

  private targetParams: SwarmParams = { ...this.currentParams };

  // Metrics tracking for UI display
  public metrics = {
    particleCount: PARTICLE_COUNT,
    avgVelocity: 0,
    centerMass: { x: 0, y: 0 },
    entropy: 0,
    frameTime: 0
  };

  constructor(canvas: HTMLCanvasElement) {
    this.ctx = canvas.getContext('2d', { alpha: false })!;
    this.resize(window.innerWidth, window.innerHeight);
    this.initParticles();
  }

  /**
   * Set particle count based on model parameters
   * @param modelParams - Number of model parameters (e.g., 71000000 for 71M)
   * @param scaleFactor - Scale factor (default 4733 = 1 particle per 4733 params)
   */
  public setParticleCountFromModel(modelParams: number, scaleFactor: number = 4733) {
    const targetCount = Math.floor(modelParams / scaleFactor);
    // Clamp between 5000 and 100000 for performance
    this.targetParticleCount = Math.max(5000, Math.min(100000, targetCount));
    
    // Gradually adjust particle count
    if (this.particles.length < this.targetParticleCount) {
      this.addParticles(this.targetParticleCount - this.particles.length);
    } else if (this.particles.length > this.targetParticleCount) {
      this.removeParticles(this.particles.length - this.targetParticleCount);
    }
    
    this.metrics.particleCount = this.particles.length;
  }

  private addParticles(count: number) {
    for (let i = 0; i < count; i++) {
      this.particles.push({
        x: Math.random() * this.width,
        y: Math.random() * this.height,
        vx: (Math.random() - 0.5) * 2,
        vy: (Math.random() - 0.5) * 2,
        ax: 0,
        ay: 0,
        size: Math.random() * 1.5 + 0.5,
        color: 'rgba(255, 255, 255, 0.8)',
        originalColor: { r: 100, g: 100, b: 255 },
        life: Math.random()
      });
    }
  }

  private removeParticles(count: number) {
    this.particles.splice(0, count);
  }

  private initParticles() {
    this.particles = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      this.particles.push({
        x: Math.random() * this.width,
        y: Math.random() * this.height,
        vx: (Math.random() - 0.5) * 2,
        vy: (Math.random() - 0.5) * 2,
        ax: 0,
        ay: 0,
        size: Math.random() * 1.5 + 0.5,
        color: 'rgba(255, 255, 255, 0.8)',
        originalColor: { r: 100, g: 100, b: 255 },
        life: Math.random()
      });
    }
    this.metrics.particleCount = this.particles.length;
  }

  public resize(w: number, h: number) {
    this.width = w;
    this.height = h;
    this.ctx.canvas.width = w;
    this.ctx.canvas.height = h;
  }

  public setAIActivity(thinking: boolean, amplitude: number) {
    this.targetParams.thinkingEnergy = thinking ? 1.0 : 0.0;
    this.targetParams.audioAmplitude = amplitude;
  }

  public setState(state: SwarmState) {
    this.state = state;
    switch (state) {
      case SwarmState.SLEEPING:
        this.targetParams = {
          ...this.targetParams,
          drag: 0.92,
          cohesion: 0.05,
          speed: 0.2,
          turbulence: 0.05,
          mouseForce: -2.0,
          bloom: 0.3
        };
        break;
      case SwarmState.LEARNING:
        this.targetParams = {
          ...this.targetParams,
          drag: 0.85,
          cohesion: 0.01,
          speed: 2.5,
          turbulence: 0.1,
          mouseForce: 1.5,
          bloom: 0.6
        };
        break;
      case SwarmState.INTERACTING:
        this.targetParams = {
          ...this.targetParams,
          drag: 0.96,
          cohesion: 0.005,
          speed: 1.8,
          turbulence: 0.5,
          mouseForce: 4.0,
          bloom: 0.8
        };
        break;
    }
  }

  public setMouse(x: number, y: number) {
    this.mouseX = x;
    this.mouseY = y;
  }

  private updateColors(p: Particle) {
    let r, g, b;
    const { thinkingEnergy, audioAmplitude } = this.currentParams;

    if (this.state === SwarmState.SLEEPING) {
      // Deep indigo/purple - dormant neural state
      r = 40 + Math.sin(p.life * 10) * 20;
      g = 20 + Math.cos(p.life * 5) * 50;
      b = 180 + Math.sin(p.life * 2) * 75;
    } else if (this.state === SwarmState.LEARNING) {
      // Cyan/teal - active learning, neural plasticity
      r = 20 + thinkingEnergy * 50;
      g = 200 + Math.sin(p.life * 5) * 55;
      b = 255;
      
      // Pulse brighter during active learning
      const pulse = Math.sin(Date.now() * 0.003 + p.life * 10) * 0.3 + 0.7;
      r *= pulse;
      g *= pulse;
      b *= pulse;
    } else {
      // INTERACTING - Orange/Gold with reactive elements
      r = 255;
      g = 100 + Math.sin(p.life * 10) * 100;
      b = 50 + Math.cos(p.life * 5) * 50;

      // React to Thinking (Shift to White/Blue electric)
      if (thinkingEnergy > 0.1) {
        r = r * (1 - thinkingEnergy) + 200 * thinkingEnergy;
        g = g * (1 - thinkingEnergy) + 230 * thinkingEnergy;
        b = b * (1 - thinkingEnergy) + 255 * thinkingEnergy;
      }
      
      // React to Audio Amplitude (Brighten)
      const bright = 1 + audioAmplitude * 2;
      r = Math.min(255, r * bright);
      g = Math.min(255, g * bright);
      b = Math.min(255, b * bright);
    }

    p.originalColor.r += (r - p.originalColor.r) * 0.1;
    p.originalColor.g += (g - p.originalColor.g) * 0.1;
    p.originalColor.b += (b - p.originalColor.b) * 0.1;

    p.color = `rgb(${Math.floor(p.originalColor.r)}, ${Math.floor(p.originalColor.g)}, ${Math.floor(p.originalColor.b)})`;
  }

  private lerpParams() {
    const keys = Object.keys(this.currentParams) as (keyof SwarmParams)[];
    keys.forEach(k => {
      const speed = (k === 'audioAmplitude' || k === 'thinkingEnergy') ? 0.2 : 0.01;
      this.currentParams[k] += (this.targetParams[k] - this.currentParams[k]) * speed;
    });
  }

  public update() {
    const startTime = performance.now();
    
    this.lerpParams();
    const centerX = this.width / 2;
    const centerY = this.height / 2;
    const time = Date.now() * 0.001;
    const { thinkingEnergy, audioAmplitude, speed: baseSpeed, turbulence: baseTurbulence } = this.currentParams;

    let totalVelocity = 0;
    let sumX = 0, sumY = 0;

    for (let i = 0; i < this.particles.length; i++) {
      const p = this.particles[i];
      p.ax = 0;
      p.ay = 0;

      if (this.state === SwarmState.SLEEPING) {
        // Orbital formation - calm, collected swarm
        const dx = centerX - p.x;
        const dy = centerY - p.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const targetRadius = 150 + Math.sin(time + i * 0.001) * 20;
        const force = (dist - targetRadius) * this.currentParams.cohesion;
        p.ax += (dx / dist) * force;
        p.ay += (dy / dist) * force;
        // Orbital motion
        p.ax += (dy / dist) * 0.5;
        p.ay -= (dx / dist) * 0.5;
      } else if (this.state === SwarmState.LEARNING) {
        // Flow field - neural pathways forming
        const angle = (Math.sin(p.x * 0.01 + time * 0.5) + Math.cos(p.y * 0.01 + time * 0.3)) * Math.PI;
        p.ax += Math.cos(angle) * baseSpeed;
        p.ay += Math.sin(angle) * baseSpeed;
        
        // Add some chaotic exploration
        p.ax += (Math.random() - 0.5) * baseTurbulence;
        p.ay += (Math.random() - 0.5) * baseTurbulence;
      } else if (this.state === SwarmState.INTERACTING) {
        // Voice/thought reactive expansion
        const dx = p.x - centerX;
        const dy = p.y - centerY;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const voiceForce = audioAmplitude * 5;
        p.ax += (dx / dist) * voiceForce;
        p.ay += (dy / dist) * voiceForce;

        // Thinking causes jittery turbulence
        const jitter = baseTurbulence + thinkingEnergy * 2.0;
        p.ax += (Math.random() - 0.5) * jitter;
        p.ay += (Math.random() - 0.5) * jitter;
      }

      // Mouse interaction
      const mdx = this.mouseX - p.x;
      const mdy = this.mouseY - p.y;
      const mdist = Math.sqrt(mdx * mdx + mdy * mdy) || 1;
      if (mdist < 300) {
        const mForce = (1 - mdist / 300) * this.currentParams.mouseForce;
        p.ax += (mdx / mdist) * mForce;
        p.ay += (mdy / mdist) * mForce;
      }

      // Apply physics
      p.vx += p.ax;
      p.vy += p.ay;
      p.vx *= this.currentParams.drag;
      p.vy *= this.currentParams.drag;

      const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
      if (speed > MAX_VELOCITY) {
        p.vx = (p.vx / speed) * MAX_VELOCITY;
        p.vy = (p.vy / speed) * MAX_VELOCITY;
      }

      p.x += p.vx;
      p.y += p.vy;

      // Wrap around screen
      if (p.x < 0) p.x = this.width;
      if (p.x > this.width) p.x = 0;
      if (p.y < 0) p.y = this.height;
      if (p.y > this.height) p.y = 0;

      this.updateColors(p);

      // Metrics
      totalVelocity += speed;
      sumX += p.x;
      sumY += p.y;
    }

    // Update metrics
    this.metrics.avgVelocity = totalVelocity / this.particles.length;
    this.metrics.centerMass = { 
      x: sumX / this.particles.length, 
      y: sumY / this.particles.length 
    };
    this.metrics.frameTime = performance.now() - startTime;
  }

  public draw() {
    this.ctx.fillStyle = '#000';
    this.ctx.fillRect(0, 0, this.width, this.height);
    this.ctx.globalCompositeOperation = 'lighter';
    
    const bloomScale = this.currentParams.bloom + this.currentParams.audioAmplitude;

    for (let i = 0; i < this.particles.length; i++) {
      const p = this.particles[i];
      this.ctx.fillStyle = p.color;
      
      // Bloom effect on every 15th particle
      if (i % 15 === 0) {
        this.ctx.globalAlpha = 0.1 * bloomScale;
        this.ctx.beginPath();
        this.ctx.arc(p.x, p.y, p.size * 5, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.globalAlpha = 1;
      }
      
      const drawSize = p.size * (1 + this.currentParams.audioAmplitude * 2);
      this.ctx.fillRect(p.x, p.y, drawSize, drawSize);
    }
    
    this.ctx.globalCompositeOperation = 'source-over';
  }

  public getMetrics() {
    return { ...this.metrics };
  }
}
