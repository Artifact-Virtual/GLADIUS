import winston from 'winston';
import DailyRotateFile from 'winston-daily-rotate-file';
import path from 'path';
import { fileURLToPath } from 'url';
import { mkdirSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Ensure logs directory exists
const logDir = process.env.LOG_DIR || path.join(path.dirname(path.dirname(__dirname)), 'logs');
try {
  mkdirSync(logDir, { recursive: true });
} catch (error) {
  console.error('Failed to create logs directory:', error);
}

// Define log format
const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.printf(({ timestamp, level, message, stack }) => {
    if (stack) {
      return `${timestamp} [${level.toUpperCase()}]: ${message}\n${stack}`;
    }
    return `${timestamp} [${level.toUpperCase()}]: ${message}`;
  })
);

// Create logger
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: logFormat,
  transports: [
    // Console transport
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        logFormat
      )
    }),
    // File transport - all logs
    new DailyRotateFile({
      filename: path.join(logDir, 'combined-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      maxFiles: '14d',
      maxSize: '20m',
      format: logFormat
    }),
    // File transport - errors only
    new DailyRotateFile({
      filename: path.join(logDir, 'error-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      level: 'error',
      maxFiles: '30d',
      maxSize: '20m',
      format: logFormat
    }),
    // File transport - commands
    new DailyRotateFile({
      filename: path.join(logDir, 'commands-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      maxFiles: '7d',
      maxSize: '20m',
      format: logFormat,
      level: 'info'
    })
  ]
});

// Add custom logging methods
logger.command = (user, guild, command, args) => {
  logger.info(`Command executed: ${command} | User: ${user?.tag || 'Unknown'} (${user?.id || 'N/A'}) | Guild: ${guild?.name || 'DM'} (${guild?.id || 'N/A'}) | Args: ${args?.join(' ') || 'none'}`);
};

logger.moderation = (moderator, target, action, reason) => {
  logger.warn(`Moderation: ${action} | Moderator: ${moderator?.tag || 'Unknown'} (${moderator?.id || 'N/A'}) | Target: ${target?.tag || 'Unknown'} (${target?.id || 'N/A'}) | Reason: ${reason || 'No reason provided'}`);
};

export default logger;
