import { platform } from 'os';

/**
 * Get the appropriate Python executable for the current platform
 */
export function getPythonExecutable(): string {
  return platform() === 'win32' ? 'python' : 'python3';
}

/**
 * Sanitize string input to prevent command injection
 */
export function sanitizeInput(input: string): string {
  // Remove potentially dangerous characters
  return input.replace(/[;&|`$(){}[\]<>]/g, '');
}

/**
 * Validate that a string is a safe filename (no path traversal)
 */
export function validateFilename(filename: string): boolean {
  // Check for path traversal attempts and only allow safe characters
  return !/[\/\\.]/.test(filename) && /^[a-zA-Z0-9_-]+\.log$/.test(filename);
}

/**
 * Validate numeric input
 */
export function validateNumber(value: any, min?: number, max?: number): number | null {
  const num = Number(value);
  if (isNaN(num)) return null;
  if (min !== undefined && num < min) return null;
  if (max !== undefined && num > max) return null;
  return num;
}

/**
 * Validate agent ID format
 */
export function validateAgentId(id: string): boolean {
  // Only allow alphanumeric, dash, and underscore
  return /^[a-zA-Z0-9_-]+$/.test(id);
}

/**
 * Validate path to prevent traversal attacks
 */
export function validatePath(path: string): boolean {
  // Reject paths with parent directory references
  return !path.includes('..') && !path.includes('~');
}

/**
 * Sanitize array of strings
 */
export function sanitizeArray(arr: string[]): string[] {
  return arr.map(item => sanitizeInput(item));
}
