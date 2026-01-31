import { ipcMain } from 'electron';
import { spawn } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import { getPythonExecutable, sanitizeInput, sanitizeArray, validatePath } from './utils';

const ARTIFACT_PATH = path.join(__dirname, '../../../Artifact');
const PYTHON = getPythonExecutable();

interface ArtifactResponse {
  success: boolean;
  data?: any;
  error?: string;
}

export function setupArtifactHandlers() {
  // Get Artifact status
  ipcMain.handle('artifact:status', async (): Promise<ArtifactResponse> => {
    try {
      console.log('[ARTIFACT] Checking status...');
      const pythonProcess = spawn(PYTHON, [
        path.join(ARTIFACT_PATH, 'artifact_cli.py'),
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
              console.log('[ARTIFACT] Status retrieved successfully');
              resolve({ success: true, data });
            } catch (e) {
              resolve({ success: true, data: { status: 'ready', output: stdout } });
            }
          } else {
            console.error('[ARTIFACT] Status check failed:', stderr);
            resolve({ success: false, error: stderr || 'Status check failed' });
          }
        });
      });
    } catch (error) {
      console.error('[ARTIFACT] Error getting status:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // List artifacts
  ipcMain.handle('artifact:list', async (_, filter?: any): Promise<ArtifactResponse> => {
    try {
      console.log('[ARTIFACT] Listing artifacts...', filter);
      const args = ['list'];
      
      if (filter?.type) args.push('--type', sanitizeInput(filter.type));
      if (filter?.tag) args.push('--tag', sanitizeInput(filter.tag));

      const pythonProcess = spawn(PYTHON, [
        path.join(ARTIFACT_PATH, 'artifact_cli.py'),
        ...args
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
              console.log('[ARTIFACT] Artifacts listed successfully');
              resolve({ success: true, data });
            } catch (e) {
              resolve({ success: true, data: { output: stdout } });
            }
          } else {
            console.error('[ARTIFACT] List failed:', stderr);
            resolve({ success: false, error: stderr || 'Failed to list artifacts' });
          }
        });
      });
    } catch (error) {
      console.error('[ARTIFACT] Error listing artifacts:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // Get artifact details
  ipcMain.handle('artifact:get', async (_, artifactId: string): Promise<ArtifactResponse> => {
    try {
      console.log('[ARTIFACT] Getting artifact:', artifactId);
      const pythonProcess = spawn(PYTHON, [
        path.join(ARTIFACT_PATH, 'artifact_cli.py'),
        'get',
        '--id', sanitizeInput(artifactId)
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
              console.log('[ARTIFACT] Artifact retrieved successfully');
              resolve({ success: true, data });
            } catch (e) {
              resolve({ success: true, data: { output: stdout } });
            }
          } else {
            console.error('[ARTIFACT] Get failed:', stderr);
            resolve({ success: false, error: stderr || 'Failed to get artifact' });
          }
        });
      });
    } catch (error) {
      console.error('[ARTIFACT] Error getting artifact:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // Create/upload artifact
  ipcMain.handle('artifact:create', async (_, config: any): Promise<ArtifactResponse> => {
    try {
      console.log('[ARTIFACT] Creating artifact...', config);
      const args = ['create'];
      
      if (config.name) args.push('--name', sanitizeInput(config.name));
      if (config.type) args.push('--type', sanitizeInput(config.type));
      
      if (config.path) {
        if (!validatePath(config.path)) {
          return { success: false, error: 'Invalid path: path traversal not allowed' };
        }
        args.push('--path', config.path);
      }
      
      if (config.description) args.push('--description', sanitizeInput(config.description));
      if (config.tags) args.push('--tags', sanitizeArray(config.tags).join(','));

      const pythonProcess = spawn(PYTHON, [
        path.join(ARTIFACT_PATH, 'artifact_cli.py'),
        ...args
      ]);

      return new Promise((resolve) => {
        let stdout = '';
        let stderr = '';

        pythonProcess.stdout.on('data', (data) => {
          stdout += data.toString();
          console.log('[ARTIFACT] Create output:', data.toString());
        });

        pythonProcess.stderr.on('data', (data) => {
          stderr += data.toString();
        });

        pythonProcess.on('close', (code) => {
          if (code === 0) {
            try {
              const data = JSON.parse(stdout);
              console.log('[ARTIFACT] Artifact created successfully');
              resolve({ success: true, data });
            } catch (e) {
              resolve({ success: true, data: { output: stdout } });
            }
          } else {
            console.error('[ARTIFACT] Create failed:', stderr);
            resolve({ success: false, error: stderr || 'Failed to create artifact' });
          }
        });
      });
    } catch (error) {
      console.error('[ARTIFACT] Error creating artifact:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // Delete artifact
  ipcMain.handle('artifact:delete', async (_, artifactId: string): Promise<ArtifactResponse> => {
    try {
      console.log('[ARTIFACT] Deleting artifact:', artifactId);
      const pythonProcess = spawn(PYTHON, [
        path.join(ARTIFACT_PATH, 'artifact_cli.py'),
        'delete',
        '--id', sanitizeInput(artifactId)
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
            console.log('[ARTIFACT] Artifact deleted successfully');
            resolve({ success: true, data: { deleted: true, artifactId } });
          } else {
            console.error('[ARTIFACT] Delete failed:', stderr);
            resolve({ success: false, error: stderr || 'Failed to delete artifact' });
          }
        });
      });
    } catch (error) {
      console.error('[ARTIFACT] Error deleting artifact:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // Export artifact
  ipcMain.handle('artifact:export', async (_, artifactId: string, destination: string): Promise<ArtifactResponse> => {
    try {
      if (!validatePath(destination)) {
        return { success: false, error: 'Invalid destination path: path traversal not allowed' };
      }

      console.log('[ARTIFACT] Exporting artifact:', artifactId, 'to:', destination);
      const pythonProcess = spawn(PYTHON, [
        path.join(ARTIFACT_PATH, 'artifact_cli.py'),
        'export',
        '--id', sanitizeInput(artifactId),
        '--destination', destination
      ]);

      return new Promise((resolve) => {
        let stdout = '';
        let stderr = '';

        pythonProcess.stdout.on('data', (data) => {
          stdout += data.toString();
          console.log('[ARTIFACT] Export output:', data.toString());
        });

        pythonProcess.stderr.on('data', (data) => {
          stderr += data.toString();
        });

        pythonProcess.on('close', (code) => {
          if (code === 0) {
            console.log('[ARTIFACT] Artifact exported successfully');
            resolve({ success: true, data: { exported: true, path: destination } });
          } else {
            console.error('[ARTIFACT] Export failed:', stderr);
            resolve({ success: false, error: stderr || 'Failed to export artifact' });
          }
        });
      });
    } catch (error) {
      console.error('[ARTIFACT] Error exporting artifact:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  console.log('[ARTIFACT] IPC handlers registered');
}
