import { ipcMain } from 'electron';
import { spawn, ChildProcess } from 'child_process';
import path from 'path';
import { getPythonExecutable, sanitizeInput, validateNumber } from './utils';

const SENTINEL_PATH = path.join(__dirname, '../../../SENTINEL');
const PYTHON = getPythonExecutable();

interface SentinelResponse {
  success: boolean;
  data?: any;
  error?: string;
}

let sentinelProcess: ChildProcess | null = null;

export function setupSentinelHandlers() {
  // Get SENTINEL status
  ipcMain.handle('sentinel:status', async (): Promise<SentinelResponse> => {
    try {
      console.log('[SENTINEL] Checking status...');
      
      const isRunning = sentinelProcess !== null && !sentinelProcess.killed;
      
      if (!isRunning) {
        return {
          success: true,
          data: {
            status: 'stopped',
            running: false
          }
        };
      }

      return {
        success: true,
        data: {
          status: 'running',
          running: true,
          pid: sentinelProcess?.pid
        }
      };
    } catch (error) {
      console.error('[SENTINEL] Error getting status:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // Start SENTINEL
  ipcMain.handle('sentinel:start', async (_, config?: any): Promise<SentinelResponse> => {
    try {
      if (sentinelProcess && !sentinelProcess.killed) {
        console.log('[SENTINEL] Already running');
        return { success: false, error: 'SENTINEL is already running' };
      }

      console.log('[SENTINEL] Starting...', config);
      const args = ['start'];
      
      const port = validateNumber(config?.port, 1024, 65535);
      if (port) args.push('--port', port.toString());
      
      if (config?.logLevel) args.push('--log-level', sanitizeInput(config.logLevel));

      sentinelProcess = spawn(PYTHON, [
        path.join(SENTINEL_PATH, 'sentinel_cli.py'),
        ...args
      ], {
        detached: false,
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let stdout = '';
      let stderr = '';

      sentinelProcess.stdout?.on('data', (data) => {
        stdout += data.toString();
        console.log('[SENTINEL]', data.toString());
      });

      sentinelProcess.stderr?.on('data', (data) => {
        stderr += data.toString();
        console.error('[SENTINEL]', data.toString());
      });

      sentinelProcess.on('close', (code) => {
        console.log(`[SENTINEL] Process exited with code ${code}`);
        sentinelProcess = null;
      });

      sentinelProcess.on('error', (error) => {
        console.error('[SENTINEL] Process error:', error);
        sentinelProcess = null;
      });

      // Give it a moment to start
      await new Promise(resolve => setTimeout(resolve, 1000));

      if (sentinelProcess && !sentinelProcess.killed) {
        console.log('[SENTINEL] Started successfully');
        return {
          success: true,
          data: {
            status: 'running',
            pid: sentinelProcess.pid
          }
        };
      } else {
        return { success: false, error: 'Failed to start SENTINEL' };
      }
    } catch (error) {
      console.error('[SENTINEL] Error starting:', error);
      sentinelProcess = null;
      return { success: false, error: (error as Error).message };
    }
  });

  // Stop SENTINEL
  ipcMain.handle('sentinel:stop', async (): Promise<SentinelResponse> => {
    try {
      if (!sentinelProcess || sentinelProcess.killed) {
        console.log('[SENTINEL] Not running');
        return { success: false, error: 'SENTINEL is not running' };
      }

      console.log('[SENTINEL] Stopping...');
      
      return new Promise((resolve) => {
        const timeout = setTimeout(() => {
          if (sentinelProcess && !sentinelProcess.killed) {
            console.log('[SENTINEL] Force killing process');
            sentinelProcess.kill('SIGKILL');
          }
          sentinelProcess = null;
          resolve({ success: true, data: { status: 'stopped' } });
        }, 5000);

        sentinelProcess!.on('close', () => {
          clearTimeout(timeout);
          sentinelProcess = null;
          console.log('[SENTINEL] Stopped successfully');
          resolve({ success: true, data: { status: 'stopped' } });
        });

        sentinelProcess!.kill('SIGTERM');
      });
    } catch (error) {
      console.error('[SENTINEL] Error stopping:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // Run scan
  ipcMain.handle('sentinel:scan', async (_, target: string, options?: any): Promise<SentinelResponse> => {
    try {
      console.log('[SENTINEL] Starting scan on:', target);
      const args = ['scan', '--target', sanitizeInput(target)];
      
      const depth = validateNumber(options?.depth, 1, 10);
      if (depth) args.push('--depth', depth.toString());
      
      if (options?.profile) args.push('--profile', sanitizeInput(options.profile));

      const pythonProcess = spawn(PYTHON, [
        path.join(SENTINEL_PATH, 'sentinel_cli.py'),
        ...args
      ]);

      return new Promise((resolve) => {
        let stdout = '';
        let stderr = '';

        pythonProcess.stdout.on('data', (data) => {
          stdout += data.toString();
          console.log('[SENTINEL] Scan output:', data.toString());
        });

        pythonProcess.stderr.on('data', (data) => {
          stderr += data.toString();
        });

        pythonProcess.on('close', (code) => {
          if (code === 0) {
            console.log('[SENTINEL] Scan completed successfully');
            try {
              const data = JSON.parse(stdout);
              resolve({ success: true, data });
            } catch (e) {
              resolve({ success: true, data: { output: stdout } });
            }
          } else {
            console.error('[SENTINEL] Scan failed:', stderr);
            resolve({ success: false, error: stderr || 'Scan failed' });
          }
        });
      });
    } catch (error) {
      console.error('[SENTINEL] Error running scan:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  console.log('[SENTINEL] IPC handlers registered');
}

// Cleanup on app quit
export function cleanupSentinel() {
  if (sentinelProcess && !sentinelProcess.killed) {
    console.log('[SENTINEL] Cleaning up...');
    sentinelProcess.kill('SIGTERM');
    sentinelProcess = null;
  }
}
