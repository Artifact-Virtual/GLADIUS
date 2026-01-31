import { ipcMain, BrowserWindow } from 'electron';
import { spawn, ChildProcess } from 'child_process';
import path from 'path';
import { getPythonExecutable, validateNumber } from './utils';

const GLADIUS_PATH = path.join(__dirname, '../../../GLADIUS');
const PYTHON = getPythonExecutable();

interface TrainingResponse {
  success: boolean;
  data?: any;
  error?: string;
}

let trainingProcess: ChildProcess | null = null;
let mainWindowRef: BrowserWindow | null = null;

export function setupTrainingHandlers(mainWindow?: BrowserWindow) {
  if (mainWindow) {
    mainWindowRef = mainWindow;
  }

  // Get training status
  ipcMain.handle('training:status', async (): Promise<TrainingResponse> => {
    try {
      const isRunning = trainingProcess !== null && !trainingProcess.killed;
      return {
        success: true,
        data: {
          running: isRunning,
          pid: trainingProcess?.pid
        }
      };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  // Start training
  ipcMain.handle('training:start', async (_, config: any): Promise<TrainingResponse> => {
    try {
      if (trainingProcess && !trainingProcess.killed) {
        return { success: false, error: 'Training is already running' };
      }

      console.log('[TRAINING] Starting training...', config);
      
      // Determine which trainer to use based on GPU availability
      const trainerScript = config.useGpu 
        ? 'train_gpu.py'
        : 'train_cpu.py';

      const args: string[] = [];
      
      const epochs = validateNumber(config.epochs, 1, 10000);
      if (epochs) args.push('--epochs', epochs.toString());
      
      const batchSize = validateNumber(config.batchSize, 1, 1024);
      if (batchSize) args.push('--batch-size', batchSize.toString());
      
      const lr = config.learningRate;
      if (lr) args.push('--learning-rate', lr.toString());

      if (config.resumeFromCheckpoint) {
        args.push('--resume');
      }

      trainingProcess = spawn(PYTHON, [
        path.join(GLADIUS_PATH, trainerScript),
        ...args
      ], {
        cwd: GLADIUS_PATH,
        env: { ...process.env, PYTHONUNBUFFERED: '1' }
      });

      // Stream output to renderer
      trainingProcess.stdout?.on('data', (data) => {
        const output = data.toString();
        console.log('[TRAINING]', output);
        if (mainWindowRef && !mainWindowRef.isDestroyed()) {
          mainWindowRef.webContents.send('training:output', { type: 'stdout', data: output });
        }
      });

      trainingProcess.stderr?.on('data', (data) => {
        const output = data.toString();
        console.error('[TRAINING]', output);
        if (mainWindowRef && !mainWindowRef.isDestroyed()) {
          mainWindowRef.webContents.send('training:output', { type: 'stderr', data: output });
        }
      });

      trainingProcess.on('close', (code) => {
        console.log(`[TRAINING] Process exited with code ${code}`);
        if (mainWindowRef && !mainWindowRef.isDestroyed()) {
          mainWindowRef.webContents.send('training:complete', { code });
        }
        trainingProcess = null;
      });

      trainingProcess.on('error', (error) => {
        console.error('[TRAINING] Process error:', error);
        if (mainWindowRef && !mainWindowRef.isDestroyed()) {
          mainWindowRef.webContents.send('training:error', { error: error.message });
        }
        trainingProcess = null;
      });

      return {
        success: true,
        data: {
          status: 'started',
          pid: trainingProcess.pid,
          config
        }
      };
    } catch (error) {
      console.error('[TRAINING] Error starting:', error);
      trainingProcess = null;
      return { success: false, error: (error as Error).message };
    }
  });

  // Stop training
  ipcMain.handle('training:stop', async (): Promise<TrainingResponse> => {
    try {
      if (!trainingProcess || trainingProcess.killed) {
        return { success: false, error: 'Training is not running' };
      }

      console.log('[TRAINING] Stopping...');
      
      return new Promise((resolve) => {
        const timeout = setTimeout(() => {
          if (trainingProcess && !trainingProcess.killed) {
            console.log('[TRAINING] Force killing process');
            trainingProcess.kill('SIGKILL');
          }
          trainingProcess = null;
          resolve({ success: true, data: { status: 'stopped', forced: true } });
        }, 10000);

        trainingProcess!.on('close', () => {
          clearTimeout(timeout);
          trainingProcess = null;
          console.log('[TRAINING] Stopped gracefully');
          resolve({ success: true, data: { status: 'stopped', forced: false } });
        });

        // Send SIGINT first for graceful shutdown (saves checkpoint)
        trainingProcess!.kill('SIGINT');
      });
    } catch (error) {
      console.error('[TRAINING] Error stopping:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // Pause training (if supported)
  ipcMain.handle('training:pause', async (): Promise<TrainingResponse> => {
    try {
      if (!trainingProcess || trainingProcess.killed) {
        return { success: false, error: 'Training is not running' };
      }

      console.log('[TRAINING] Pausing...');
      trainingProcess.kill('SIGSTOP');
      
      return { success: true, data: { status: 'paused' } };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  // Resume training
  ipcMain.handle('training:resume', async (): Promise<TrainingResponse> => {
    try {
      if (!trainingProcess || trainingProcess.killed) {
        return { success: false, error: 'Training is not running' };
      }

      console.log('[TRAINING] Resuming...');
      trainingProcess.kill('SIGCONT');
      
      return { success: true, data: { status: 'running' } };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  // Get training metrics
  ipcMain.handle('training:metrics', async (): Promise<TrainingResponse> => {
    try {
      const metricsFile = path.join(GLADIUS_PATH, 'checkpoints', 'metrics.json');
      const fs = require('fs');
      
      if (fs.existsSync(metricsFile)) {
        const data = JSON.parse(fs.readFileSync(metricsFile, 'utf-8'));
        return { success: true, data };
      }
      
      return { success: true, data: { message: 'No metrics available yet' } };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  console.log('[TRAINING] IPC handlers registered');
}

export function cleanupTraining() {
  if (trainingProcess && !trainingProcess.killed) {
    console.log('[TRAINING] Cleaning up...');
    trainingProcess.kill('SIGTERM');
    trainingProcess = null;
  }
}
