/**
 * Logger utility
 * Simple console logger with timestamps
 */

const fs = require('fs');
const path = require('path');

class Logger {
  constructor() {
    this.logDir = path.join(__dirname, '../../logs');
    this.ensureLogDir();
  }

  ensureLogDir() {
    if (!fs.existsSync(this.logDir)) {
      fs.mkdirSync(this.logDir, { recursive: true });
    }
  }

  getLogFile() {
    const date = new Date().toISOString().split('T')[0];
    return path.join(this.logDir, `research-${date}.log`);
  }

  formatMessage(level, ...args) {
    const timestamp = new Date().toISOString();
    const message = args.map(arg => 
      typeof arg === 'object' ? JSON.stringify(arg, null, 2) : arg
    ).join(' ');
    return `[${timestamp}] [${level}] ${message}`;
  }

  writeToFile(message) {
    try {
      fs.appendFileSync(this.getLogFile(), message + '\n');
    } catch (error) {
      console.error('Failed to write to log file:', error);
    }
  }

  info(...args) {
    const message = this.formatMessage('INFO', ...args);
    console.log(...args);
    this.writeToFile(message);
  }

  warn(...args) {
    const message = this.formatMessage('WARN', ...args);
    console.warn(...args);
    this.writeToFile(message);
  }

  error(...args) {
    const message = this.formatMessage('ERROR', ...args);
    console.error(...args);
    this.writeToFile(message);
  }

  debug(...args) {
    const message = this.formatMessage('DEBUG', ...args);
    console.log(...args);
    this.writeToFile(message);
  }
}

module.exports = new Logger();
