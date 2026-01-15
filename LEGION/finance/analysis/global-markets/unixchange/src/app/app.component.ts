import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterModule } from '@angular/router';
import { HeaderComponent } from './components/layout/header.component';
import { SidebarComponent } from './components/layout/sidebar.component';
import { LoadingScreenComponent } from './components/ui/loading-screen.component';
import { MarketDataService } from './services/market-data.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterModule,
    HeaderComponent,
    SidebarComponent,
    LoadingScreenComponent
  ],
  template: `
    <div class="app-container">
      <app-loading-screen *ngIf="isLoading"></app-loading-screen>
      
      <app-header class="header-section"></app-header>
      
      <div class="main-content">
        <app-sidebar class="sidebar-section"></app-sidebar>
        <main class="workspace-section">
          <router-outlet></router-outlet>
        </main>
      </div>
    </div>
  `,
  styles: [`
    .app-container {
      height: 100vh;
      overflow: hidden;
    }
    
    .header-section {
      flex-shrink: 0;
      z-index: 100;
    }
    
    .main-content {
      flex: 1;
      overflow: hidden;
    }
    
    .sidebar-section {
      flex-shrink: 0;
      z-index: 50;
    }
    
    .workspace-section {
      overflow: hidden;
    }
  `]
})
export class AppComponent {
  title = 'UniXchange - Professional Market Analytics';
  isLoading = true;

  constructor(private marketDataService: MarketDataService) {
    this.initializeApp();
  }

  private async initializeApp(): Promise<void> {
    try {
      // Initialize market data service
      await this.marketDataService.initialize();
      
      // Simulate initialization time for professional loading experience
      setTimeout(() => {
        this.isLoading = false;
      }, 2000);
    } catch (error) {
      console.error('Failed to initialize application:', error);
      this.isLoading = false;
    }
  }
}
