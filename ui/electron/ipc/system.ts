import { ipcMain } from 'electron';
import { spawn, ChildProcess } from 'child_process';
import path from 'path';
import fs from 'fs';
import { getPythonExecutable, sanitizeInput } from './utils';

const GLADIUS_PATH = path.join(__dirname, '../../../GLADIUS');
const CONFIG_PATH = path.join(__dirname, '../../../config.json');
const PYTHON = getPythonExecutable();

interface SystemResponse {
  success: boolean;
  data?: any;
  error?: string;
}

export function setupSystemHandlers() {
  // Get system configuration
  ipcMain.handle('system:config:get', async (): Promise<SystemResponse> => {
    try {
      if (fs.existsSync(CONFIG_PATH)) {
        const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
        return { success: true, data: config };
      }
      return { success: true, data: {} };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  // Update system configuration
  ipcMain.handle('system:config:set', async (_, updates: Record<string, any>): Promise<SystemResponse> => {
    try {
      let config = {};
      if (fs.existsSync(CONFIG_PATH)) {
        config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
      }
      
      const newConfig = { ...config, ...updates };
      fs.writeFileSync(CONFIG_PATH, JSON.stringify(newConfig, null, 2));
      
      return { success: true, data: newConfig };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  // Check GPU availability
  ipcMain.handle('system:gpu:check', async (): Promise<SystemResponse> => {
    try {
      const pythonProcess = spawn(PYTHON, ['-c', `
import torch
import json
result = {
    'cuda_available': torch.cuda.is_available(),
    'device_count': torch.cuda.device_count() if torch.cuda.is_available() else 0,
    'device_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    'memory_total': torch.cuda.get_device_properties(0).total_memory if torch.cuda.is_available() else 0
}
print(json.dumps(result))
      `]);

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
              resolve({ success: true, data });
            } catch (e) {
              resolve({ success: true, data: { cuda_available: false } });
            }
          } else {
            resolve({ success: true, data: { cuda_available: false } });
          }
        });
      });
    } catch (error) {
      return { success: true, data: { cuda_available: false } };
    }
  });

  // Get system stats
  ipcMain.handle('system:stats', async (): Promise<SystemResponse> => {
    try {
      const os = require('os');
      
      const stats = {
        platform: os.platform(),
        arch: os.arch(),
        cpus: os.cpus().length,
        totalMemory: os.totalmem(),
        freeMemory: os.freemem(),
        uptime: os.uptime(),
        hostname: os.hostname(),
        nodeVersion: process.version,
      };
      
      return { success: true, data: stats };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  // Start all services
  ipcMain.handle('system:start-all', async (): Promise<SystemResponse> => {
    try {
      console.log('[SYSTEM] Starting all services...');
      
      const script = path.join(__dirname, '../../../gladius.sh');
      const process = spawn('bash', [script, 'start'], {
        cwd: path.join(__dirname, '../../..'),
        detached: true
      });
      
      process.unref();
      
      return { success: true, data: { message: 'All services starting' } };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  // Stop all services
  ipcMain.handle('system:stop-all', async (): Promise<SystemResponse> => {
    try {
      console.log('[SYSTEM] Stopping all services...');
      
      const script = path.join(__dirname, '../../../gladius.sh');
      const process = spawn('bash', [script, 'stop'], {
        cwd: path.join(__dirname, '../../..')
      });

      return new Promise((resolve) => {
        process.on('close', (code) => {
          resolve({ success: code === 0, data: { message: 'All services stopped' } });
        });
      });
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  // Get overall system status
  ipcMain.handle('system:status', async (): Promise<SystemResponse> => {
    try {
      const pidFiles = [
        { name: 'gladius', file: 'gladius.pid' },
        { name: 'sentinel', file: 'sentinel.pid' },
        { name: 'legion', file: 'legion.pid' },
        { name: 'syndicate', file: 'syndicate.pid' },
      ];
      
      const status: Record<string, any> = {};
      
      for (const { name, file } of pidFiles) {
        const pidPath = path.join(__dirname, '../../..', file);
        if (fs.existsSync(pidPath)) {
          const pid = parseInt(fs.readFileSync(pidPath, 'utf-8').trim());
          try {
            process.kill(pid, 0); // Check if process exists
            status[name] = { running: true, pid };
          } catch {
            status[name] = { running: false };
          }
        } else {
          status[name] = { running: false };
        }
      }
      
      return { success: true, data: status };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  console.log('[SYSTEM] IPC handlers registered');
}
