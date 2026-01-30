import { ipcMain } from 'electron';
import { spawn, ChildProcess } from 'child_process';
import path from 'path';

const LEGION_PATH = path.join(__dirname, '../../../LEGION');

interface LegionResponse {
  success: boolean;
  data?: any;
  error?: string;
}

let runningAgents: Map<string, ChildProcess> = new Map();

export function setupLegionHandlers() {
  // Get LEGION status
  ipcMain.handle('legion:status', async (): Promise<LegionResponse> => {
    try {
      console.log('[LEGION] Checking status...');
      const pythonProcess = spawn('python3', [
        path.join(LEGION_PATH, 'legion_cli.py'),
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
              console.log('[LEGION] Status retrieved successfully');
              resolve({ success: true, data });
            } catch (e) {
              resolve({
                success: true,
                data: {
                  status: 'ready',
                  activeAgents: runningAgents.size,
                  output: stdout
                }
              });
            }
          } else {
            console.error('[LEGION] Status check failed:', stderr);
            resolve({ success: false, error: stderr || 'Status check failed' });
          }
        });
      });
    } catch (error) {
      console.error('[LEGION] Error getting status:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // List available agents
  ipcMain.handle('legion:list-agents', async (): Promise<LegionResponse> => {
    try {
      console.log('[LEGION] Listing agents...');
      const pythonProcess = spawn('python3', [
        path.join(LEGION_PATH, 'legion_cli.py'),
        'list'
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
              console.log('[LEGION] Agents listed successfully');
              resolve({ success: true, data });
            } catch (e) {
              resolve({ success: true, data: { output: stdout } });
            }
          } else {
            console.error('[LEGION] List agents failed:', stderr);
            resolve({ success: false, error: stderr || 'Failed to list agents' });
          }
        });
      });
    } catch (error) {
      console.error('[LEGION] Error listing agents:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // Create new agent
  ipcMain.handle('legion:create-agent', async (_, config: any): Promise<LegionResponse> => {
    try {
      console.log('[LEGION] Creating agent...', config);
      const args = ['create'];
      
      if (config.name) args.push('--name', config.name);
      if (config.type) args.push('--type', config.type);
      if (config.role) args.push('--role', config.role);

      const pythonProcess = spawn('python3', [
        path.join(LEGION_PATH, 'legion_cli.py'),
        ...args
      ]);

      return new Promise((resolve) => {
        let stdout = '';
        let stderr = '';

        pythonProcess.stdout.on('data', (data) => {
          stdout += data.toString();
          console.log('[LEGION] Create output:', data.toString());
        });

        pythonProcess.stderr.on('data', (data) => {
          stderr += data.toString();
        });

        pythonProcess.on('close', (code) => {
          if (code === 0) {
            console.log('[LEGION] Agent created successfully');
            try {
              const data = JSON.parse(stdout);
              resolve({ success: true, data });
            } catch (e) {
              resolve({ success: true, data: { output: stdout } });
            }
          } else {
            console.error('[LEGION] Agent creation failed:', stderr);
            resolve({ success: false, error: stderr || 'Failed to create agent' });
          }
        });
      });
    } catch (error) {
      console.error('[LEGION] Error creating agent:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // Deploy agent
  ipcMain.handle('legion:deploy-agent', async (_, agentId: string, config?: any): Promise<LegionResponse> => {
    try {
      console.log('[LEGION] Deploying agent:', agentId);
      const args = ['deploy', '--agent-id', agentId];
      
      if (config?.target) args.push('--target', config.target);
      if (config?.mode) args.push('--mode', config.mode);

      const pythonProcess = spawn('python3', [
        path.join(LEGION_PATH, 'legion_cli.py'),
        ...args
      ], {
        detached: false,
        stdio: ['pipe', 'pipe', 'pipe']
      });

      const processId = `agent-${agentId}-${Date.now()}`;
      runningAgents.set(processId, pythonProcess);

      pythonProcess.stdout?.on('data', (data) => {
        console.log(`[LEGION][${agentId}]`, data.toString());
      });

      pythonProcess.stderr?.on('data', (data) => {
        console.error(`[LEGION][${agentId}]`, data.toString());
      });

      pythonProcess.on('close', (code) => {
        console.log(`[LEGION] Agent ${agentId} exited with code ${code}`);
        runningAgents.delete(processId);
      });

      // Give it a moment to start
      await new Promise(resolve => setTimeout(resolve, 1000));

      console.log('[LEGION] Agent deployed successfully');
      return {
        success: true,
        data: {
          agentId,
          processId,
          status: 'deployed',
          pid: pythonProcess.pid
        }
      };
    } catch (error) {
      console.error('[LEGION] Error deploying agent:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // Stop agent
  ipcMain.handle('legion:stop-agent', async (_, processId: string): Promise<LegionResponse> => {
    try {
      const process = runningAgents.get(processId);
      
      if (!process || process.killed) {
        console.log('[LEGION] Agent not running:', processId);
        return { success: false, error: 'Agent is not running' };
      }

      console.log('[LEGION] Stopping agent:', processId);
      
      return new Promise((resolve) => {
        const timeout = setTimeout(() => {
          if (process && !process.killed) {
            console.log('[LEGION] Force killing agent');
            process.kill('SIGKILL');
          }
          runningAgents.delete(processId);
          resolve({ success: true, data: { status: 'stopped' } });
        }, 5000);

        process.on('close', () => {
          clearTimeout(timeout);
          runningAgents.delete(processId);
          console.log('[LEGION] Agent stopped successfully');
          resolve({ success: true, data: { status: 'stopped' } });
        });

        process.kill('SIGTERM');
      });
    } catch (error) {
      console.error('[LEGION] Error stopping agent:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  console.log('[LEGION] IPC handlers registered');
}

// Cleanup on app quit
export function cleanupLegion() {
  console.log('[LEGION] Cleaning up running agents...');
  for (const [processId, process] of runningAgents.entries()) {
    if (process && !process.killed) {
      console.log('[LEGION] Stopping agent:', processId);
      process.kill('SIGTERM');
    }
  }
  runningAgents.clear();
}
