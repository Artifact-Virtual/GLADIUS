import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-loading-screen',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="loading-screen">
      <div class="loading-content">
        <div class="loading-logo">
          <h1 class="logo-text">UniXchange</h1>
          <p class="logo-subtitle">Professional Market Analytics</p>
        </div>
        
        <div class="loading-spinner"></div>
        
        <div class="loading-status">
          <p class="status-text">{{ statusMessage }}</p>
          <div class="progress-bar">
            <div class="progress-fill" [style.width.%]="progress"></div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .loading-screen {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, var(--primary-bg) 0%, var(--secondary-bg) 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 9999;
    }

    .loading-content {
      text-align: center;
      max-width: 400px;
      padding: 2rem;
    }

    .loading-logo {
      margin-bottom: 3rem;
    }

    .logo-text {
      font-size: 3rem;
      font-weight: 700;
      color: var(--accent-blue);
      margin-bottom: 0.5rem;
      letter-spacing: -0.02em;
    }

    .logo-subtitle {
      font-size: 1.1rem;
      color: var(--text-secondary);
      font-weight: 400;
    }

    .loading-spinner {
      width: 60px;
      height: 60px;
      border: 4px solid var(--border-color);
      border-top: 4px solid var(--accent-blue);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 3rem;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .loading-status {
      margin-top: 2rem;
    }

    .status-text {
      color: var(--text-secondary);
      font-size: 0.9rem;
      margin-bottom: 1rem;
    }

    .progress-bar {
      width: 100%;
      height: 4px;
      background: var(--border-color);
      border-radius: 2px;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--accent-blue), var(--accent-green));
      border-radius: 2px;
      transition: width 0.3s ease;
    }
  `]
})
export class LoadingScreenComponent {
  statusMessage = 'Initializing market data connections...';
  progress = 0;

  private statusMessages = [
    'Initializing market data connections...',
    'Establishing secure channels...',
    'Loading market instruments...',
    'Synchronizing real-time feeds...',
    'Preparing trading workspace...',
    'Ready to trade!'
  ];

  constructor() {
    this.animateProgress();
  }

  private animateProgress(): void {
    let messageIndex = 0;
    let currentProgress = 0;

    const interval = setInterval(() => {
      currentProgress += Math.random() * 20;
      
      if (currentProgress >= 100) {
        currentProgress = 100;
        this.progress = currentProgress;
        this.statusMessage = this.statusMessages[this.statusMessages.length - 1];
        clearInterval(interval);
        return;
      }

      this.progress = currentProgress;
      
      if (messageIndex < this.statusMessages.length - 1) {
        this.statusMessage = this.statusMessages[messageIndex];
        messageIndex++;
      }
    }, 400);
  }
}
