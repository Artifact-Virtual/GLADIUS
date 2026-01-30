import { ipcMain } from 'electron';
import { spawn, ChildProcess } from 'child_process';
import path from 'path';
import { getPythonExecutable, sanitizeInput, validateNumber } from './utils';

const GLADIUS_PATH = path.join(__dirname, '../../../GLADIUS');
const PYTHON = getPythonExecutable();

interface GladiusResponse {
  success: boolean;
  data?: any;
  error?: string;
}

let runningProcesses: Map<string, ChildProcess> = new Map();

export function setupGladiusHandlers() {
  // Get GLADIUS status
  ipcMain.handle('gladius:status', async (): Promise<GladiusResponse> => {
    try {
      console.log('[GLADIUS] Checking status...');
      const pythonProcess = spawn(PYTHON, [
        path.join(GLADIUS_PATH, 'gladius_cli.py'),
        'status'
      ]);

      return new Promise((resolve) => {
        let stdout = '';
        let stderr = '';

        pythonProcess.stdout.on('data', (data) => {
          stdout += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
          stderr += data.toString();
        });

        pythonProcess.on('close', (code) => {
          if (code === 0) {
            try {
              const data = JSON.parse(stdout);
              console.log('[GLADIUS] Status retrieved successfully');
              resolve({ success: true, data });
            } catch (e) {
              resolve({ success: true, data: { status: 'ready', output: stdout } });
            }
          } else {
            console.error('[GLADIUS] Status check failed:', stderr);
            resolve({ success: false, error: stderr || 'Status check failed' });
          }
        });
      });
    } catch (error) {
      console.error('[GLADIUS] Error getting status:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // Run benchmark
  ipcMain.handle('gladius:benchmark', async (_, config: any): Promise<GladiusResponse> => {
    try {
      console.log('[GLADIUS] Starting benchmark...', config);
      const args = ['benchmark'];
      
      if (config.dataset) args.push('--dataset', sanitizeInput(config.dataset));
      if (config.metric) args.push('--metric', sanitizeInput(config.metric));

      const pythonProcess = spawn(PYTHON, [
        path.join(GLADIUS_PATH, 'gladius_cli.py'),
        ...args
      ]);

      const processId = `benchmark-${Date.now()}`;
      runningProcesses.set(processId, pythonProcess);

      return new Promise((resolve) => {
        let stdout = '';
        let stderr = '';

        pythonProcess.stdout.on('data', (data) => {
          stdout += data.toString();
          console.log('[GLADIUS] Benchmark output:', data.toString());
        });

        pythonProcess.stderr.on('data', (data) => {
          stderr += data.toString();
        });

        pythonProcess.on('close', (code) => {
          runningProcesses.delete(processId);
          if (code === 0) {
            console.log('[GLADIUS] Benchmark completed successfully');
            try {
              const data = JSON.parse(stdout);
              resolve({ success: true, data });
            } catch (e) {
              resolve({ success: true, data: { output: stdout } });
            }
          } else {
            console.error('[GLADIUS] Benchmark failed:', stderr);
            resolve({ success: false, error: stderr || 'Benchmark failed' });
          }
        });
      });
    } catch (error) {
      console.error('[GLADIUS] Error running benchmark:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // Train model
  ipcMain.handle('gladius:train', async (_, config: any): Promise<GladiusResponse> => {
    try {
      console.log('[GLADIUS] Starting training...', config);
      const args = ['train'];
      
      if (config.dataset) args.push('--dataset', sanitizeInput(config.dataset));
      
      const epochs = validateNumber(config.epochs, 1, 1000);
      if (epochs) args.push('--epochs', epochs.toString());
      
      const batchSize = validateNumber(config.batchSize, 1, 1024);
      if (batchSize) args.push('--batch-size', batchSize.toString());

      const pythonProcess = spawn(PYTHON, [
        path.join(GLADIUS_PATH, 'gladius_cli.py'),
        ...args
      ]);

      const processId = `train-${Date.now()}`;
      runningProcesses.set(processId, pythonProcess);

      return new Promise((resolve) => {
        let stdout = '';
        let stderr = '';

        pythonProcess.stdout.on('data', (data) => {
          stdout += data.toString();
          console.log('[GLADIUS] Training output:', data.toString());
        });

        pythonProcess.stderr.on('data', (data) => {
          stderr += data.toString();
        });

        pythonProcess.on('close', (code) => {
          runningProcesses.delete(processId);
          if (code === 0) {
            console.log('[GLADIUS] Training completed successfully');
            try {
              const data = JSON.parse(stdout);
              resolve({ success: true, data });
            } catch (e) {
              resolve({ success: true, data: { output: stdout } });
            }
          } else {
            console.error('[GLADIUS] Training failed:', stderr);
            resolve({ success: false, error: stderr || 'Training failed' });
          }
        });
      });
    } catch (error) {
      console.error('[GLADIUS] Error starting training:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // Interact with model
  ipcMain.handle('gladius:interact', async (_, message: string): Promise<GladiusResponse> => {
    try {
      console.log('[GLADIUS] Sending interaction:', message);
      const pythonProcess = spawn(PYTHON, [
        path.join(GLADIUS_PATH, 'gladius_cli.py'),
        'interact',
        '--message', sanitizeInput(message)
      ]);

      return new Promise((resolve) => {
        let stdout = '';
        let stderr = '';

        pythonProcess.stdout.on('data', (data) => {
          stdout += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
          stderr += data.toString();
        });

        pythonProcess.on('close', (code) => {
          if (code === 0) {
            console.log('[GLADIUS] Interaction completed successfully');
            try {
              const data = JSON.parse(stdout);
              resolve({ success: true, data });
            } catch (e) {
              resolve({ success: true, data: { response: stdout } });
            }
          } else {
            console.error('[GLADIUS] Interaction failed:', stderr);
            resolve({ success: false, error: stderr || 'Interaction failed' });
          }
        });
      });
    } catch (error) {
      console.error('[GLADIUS] Error during interaction:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  console.log('[GLADIUS] IPC handlers registered');
}
