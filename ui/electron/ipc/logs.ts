import { ipcMain, BrowserWindow } from 'electron';
import { spawn } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import { Tail } from 'tail';

const PROJECT_ROOT = path.join(__dirname, '../../..');
const LOGS_PATH = path.join(PROJECT_ROOT, 'logs');

interface LogResponse {
  success: boolean;
  data?: any;
  error?: string;
}

let activeTails: Map<string, any> = new Map();

export function setupLogHandlers(mainWindow: BrowserWindow) {
  // Get available log files
  ipcMain.handle('logs:list', async (): Promise<LogResponse> => {
    try {
      console.log('[LOGS] Listing log files...');
      
      // Ensure logs directory exists
      if (!fs.existsSync(LOGS_PATH)) {
        fs.mkdirSync(LOGS_PATH, { recursive: true });
        return { success: true, data: { logs: [] } };
      }

      const files = fs.readdirSync(LOGS_PATH);
      const logFiles = files
        .filter(file => file.endsWith('.log'))
        .map(file => {
          const filePath = path.join(LOGS_PATH, file);
          const stats = fs.statSync(filePath);
          return {
            name: file,
            path: filePath,
            size: stats.size,
            modified: stats.mtime
          };
        })
        .sort((a, b) => b.modified.getTime() - a.modified.getTime());

      console.log(`[LOGS] Found ${logFiles.length} log files`);
      return { success: true, data: { logs: logFiles } };
    } catch (error) {
      console.error('[LOGS] Error listing logs:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // Read log file content
  ipcMain.handle('logs:read', async (_, logName: string, lines?: number): Promise<LogResponse> => {
    try {
      console.log('[LOGS] Reading log:', logName);
      const logPath = path.join(LOGS_PATH, logName);

      if (!fs.existsSync(logPath)) {
        return { success: false, error: 'Log file not found' };
      }

      return new Promise((resolve) => {
        const tailProcess = spawn('tail', lines ? ['-n', lines.toString(), logPath] : [logPath]);
        let stdout = '';
        let stderr = '';

        tailProcess.stdout.on('data', (data) => {
          stdout += data.toString();
        });

        tailProcess.stderr.on('data', (data) => {
          stderr += data.toString();
        });

        tailProcess.on('close', (code) => {
          if (code === 0) {
            console.log(`[LOGS] Read ${stdout.split('\n').length} lines from ${logName}`);
            resolve({ success: true, data: { content: stdout, lines: stdout.split('\n') } });
          } else {
            console.error('[LOGS] Failed to read log:', stderr);
            resolve({ success: false, error: stderr || 'Failed to read log' });
          }
        });
      });
    } catch (error) {
      console.error('[LOGS] Error reading log:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // Start streaming a log file
  ipcMain.handle('logs:stream-start', async (_, logName: string): Promise<LogResponse> => {
    try {
      console.log('[LOGS] Starting stream for:', logName);
      const logPath = path.join(LOGS_PATH, logName);

      // Stop existing stream if any
      if (activeTails.has(logName)) {
        const existingTail = activeTails.get(logName);
        existingTail.unwatch();
        activeTails.delete(logName);
      }

      if (!fs.existsSync(logPath)) {
        // Create the file if it doesn't exist
        fs.writeFileSync(logPath, '');
      }

      const tail = new Tail(logPath, {
        follow: true,
        useWatchFile: true
      });

      tail.on('line', (line: string) => {
        mainWindow.webContents.send('logs:stream-data', {
          logName,
          line,
          timestamp: new Date().toISOString()
        });
      });

      tail.on('error', (error: Error) => {
        console.error(`[LOGS] Stream error for ${logName}:`, error);
        mainWindow.webContents.send('logs:stream-error', {
          logName,
          error: error.message
        });
      });

      activeTails.set(logName, tail);
      console.log(`[LOGS] Stream started for ${logName}`);
      
      return { success: true, data: { streaming: true, logName } };
    } catch (error) {
      console.error('[LOGS] Error starting stream:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // Stop streaming a log file
  ipcMain.handle('logs:stream-stop', async (_, logName: string): Promise<LogResponse> => {
    try {
      console.log('[LOGS] Stopping stream for:', logName);
      
      if (activeTails.has(logName)) {
        const tail = activeTails.get(logName);
        tail.unwatch();
        activeTails.delete(logName);
        console.log(`[LOGS] Stream stopped for ${logName}`);
        return { success: true, data: { streaming: false, logName } };
      } else {
        return { success: false, error: 'Stream not found' };
      }
    } catch (error) {
      console.error('[LOGS] Error stopping stream:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // Clear log file
  ipcMain.handle('logs:clear', async (_, logName: string): Promise<LogResponse> => {
    try {
      console.log('[LOGS] Clearing log:', logName);
      const logPath = path.join(LOGS_PATH, logName);

      if (!fs.existsSync(logPath)) {
        return { success: false, error: 'Log file not found' };
      }

      fs.writeFileSync(logPath, '');
      console.log(`[LOGS] Cleared ${logName}`);
      
      return { success: true, data: { cleared: true, logName } };
    } catch (error) {
      console.error('[LOGS] Error clearing log:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  console.log('[LOGS] IPC handlers registered');
}

// Cleanup on app quit
export function cleanupLogs() {
  console.log('[LOGS] Cleaning up active log streams...');
  for (const [logName, tail] of activeTails.entries()) {
    console.log('[LOGS] Stopping stream:', logName);
    tail.unwatch();
  }
  activeTails.clear();
}
