import { app, BrowserWindow, ipcMain } from 'electron';
import * as path from 'path';
import { setupGladiusHandlers } from './ipc/gladius';
import { setupSentinelHandlers, cleanupSentinel } from './ipc/sentinel';
import { setupLegionHandlers, cleanupLegion } from './ipc/legion';
import { setupLogHandlers, cleanupLogs } from './ipc/logs';
import { setupArtifactHandlers } from './ipc/artifact';

let mainWindow: BrowserWindow | null = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1920,
    height: 1080,
    minWidth: 1280,
    minHeight: 720,
    backgroundColor: '#0A0E27',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    titleBarStyle: 'hidden',
    titleBarOverlay: {
      color: '#0A0E27',
      symbolColor: '#E4E7EB',
    },
  });

  // Load app
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Security: Set Content Security Policy
app.on('web-contents-created', (event, contents) => {
  contents.session.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [
          "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        ]
      }
    });
  });
});

app.whenReady().then(() => {
  createWindow();

  // Setup IPC handlers
  setupGladiusHandlers();
  setupSentinelHandlers();
  setupLegionHandlers();
  setupArtifactHandlers();
  
  if (mainWindow) {
    setupLogHandlers(mainWindow);
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  // Cleanup
  cleanupSentinel();
  cleanupLegion();
  cleanupLogs();
  
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
