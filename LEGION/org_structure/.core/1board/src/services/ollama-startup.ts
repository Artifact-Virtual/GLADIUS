/**
 * Ollama Startup Service
 * Handles the startup, configuration, and health monitoring of Ollama LLM service
 * Provides robust error handling and automatic recovery
 */

import axios from 'axios';
import { ChildProcess, spawn } from 'child_process';

export interface OllamaStartupConfig {
    baseUrl: string;
    port: number;
    model: string;
    autoStart: boolean;
    healthCheckInterval: number; // milliseconds
    maxRetries: number;
    timeout: number;
    logLevel: 'debug' | 'info' | 'warn' | 'error';
}

export interface OllamaHealthStatus {
    isRunning: boolean;
    isResponding: boolean;
    modelLoaded: boolean;
    lastHealthCheck: Date;
    uptime: number;
    memoryUsage?: number;
    errorCount: number;
}

export class OllamaStartupService {
    private config: OllamaStartupConfig;
    private process: ChildProcess | null = null;
    private healthStatus: OllamaHealthStatus;
    private healthCheckTimer: NodeJS.Timeout | null = null;
    private startTime: Date | null = null;
    private errorCount: number = 0;
    private maxErrors: number = 5;
    private isShuttingDown: boolean = false;

    constructor(config: Partial<OllamaStartupConfig> = {}) {
        this.config = {
            baseUrl: 'http://localhost:11434',
            port: 11434,
            model: 'llama3.2',
            autoStart: true,
            healthCheckInterval: 30000, // 30 seconds
            maxRetries: 3,
            timeout: 60000, // 60 seconds
            logLevel: 'info',
            ...config
        };

        this.healthStatus = {
            isRunning: false,
            isResponding: false,
            modelLoaded: false,
            lastHealthCheck: new Date(),
            uptime: 0,
            errorCount: 0
        };
    }

    /**
     * Start Ollama service with comprehensive error handling
     */
    async startOllama(): Promise<boolean> {
        try {
            this.log('info', 'Starting Ollama service...');

            // Check if already running
            if (await this.isOllamaRunning()) {
                this.log('info', 'Ollama is already running');
                await this.ensureModelLoaded();
                this.startHealthChecking();
                return true;
            }

            // Start Ollama process
            const success = await this.spawnOllamaProcess();
            if (!success) {
                this.log('error', 'Failed to start Ollama process');
                return false;
            }

            // Wait for service to be ready
            const ready = await this.waitForOllamaReady();
            if (!ready) {
                this.log('error', 'Ollama service failed to become ready');
                return false;
            }

            // Load the required model
            await this.ensureModelLoaded();
            
            // Start health monitoring
            this.startHealthChecking();
            
            this.log('info', 'Ollama service started successfully');
            return true;

        } catch (error) {
            this.log('error', `Error starting Ollama: ${error}`);
            return false;
        }
    }

    /**
     * Spawn Ollama process
     */
    private async spawnOllamaProcess(): Promise<boolean> {
        return new Promise((resolve) => {
            try {
                // Try to start Ollama serve
                this.process = spawn('ollama', ['serve'], {
                    stdio: ['ignore', 'pipe', 'pipe'],
                    env: { ...process.env, OLLAMA_HOST: `0.0.0.0:${this.config.port}` }
                });

                this.startTime = new Date();

                this.process.stdout?.on('data', (data) => {
                    this.log('debug', `Ollama stdout: ${data}`);
                });

                this.process.stderr?.on('data', (data) => {
                    this.log('debug', `Ollama stderr: ${data}`);
                });

                this.process.on('error', (error) => {
                    this.log('error', `Ollama process error: ${error}`);
                    this.errorCount++;
                    resolve(false);
                });

                this.process.on('exit', (code, signal) => {
                    this.log('warn', `Ollama process exited with code ${code}, signal ${signal}`);
                    this.healthStatus.isRunning = false;
                    
                    if (!this.isShuttingDown && this.errorCount < this.maxErrors) {
                        this.log('info', 'Attempting to restart Ollama...');
                        setTimeout(() => this.startOllama(), 5000);
                    }
                });

                // Give the process time to start
                setTimeout(() => {
                    resolve(true);
                }, 3000);

            } catch (error) {
                this.log('error', `Failed to spawn Ollama process: ${error}`);
                resolve(false);
            }
        });
    }

    /**
     * Wait for Ollama to be ready
     */
    private async waitForOllamaReady(): Promise<boolean> {
        const maxWaitTime = this.config.timeout;
        const checkInterval = 2000;
        let elapsed = 0;

        while (elapsed < maxWaitTime) {
            if (await this.isOllamaRunning()) {
                this.healthStatus.isRunning = true;
                this.healthStatus.isResponding = true;
                return true;
            }
            
            await this.sleep(checkInterval);
            elapsed += checkInterval;
            this.log('debug', `Waiting for Ollama to be ready... (${elapsed}ms)`);
        }

        return false;
    }

    /**
     * Check if Ollama is running and responding
     */
    async isOllamaRunning(): Promise<boolean> {
        try {
            const response = await axios.get(`${this.config.baseUrl}/api/version`, {
                timeout: 5000
            });
            return response.status === 200;
        } catch (error) {
            return false;
        }
    }

    /**
     * Ensure the required model is loaded
     */
    private async ensureModelLoaded(): Promise<boolean> {
        try {
            this.log('info', `Checking if model ${this.config.model} is available...`);

            // First, check if model exists locally
            const modelsResponse = await axios.get(`${this.config.baseUrl}/api/tags`, {
                timeout: 10000
            });

            const modelExists = modelsResponse.data.models?.some((model: any) => 
                model.name.includes(this.config.model)
            );

            if (!modelExists) {
                this.log('info', `Model ${this.config.model} not found, pulling...`);
                await this.pullModel();
            }

            this.healthStatus.modelLoaded = true;
            this.log('info', `Model ${this.config.model} is ready`);
            return true;

        } catch (error) {
            this.log('error', `Error ensuring model is loaded: ${error}`);
            return false;
        }
    }

    /**
     * Pull the required model
     */
    private async pullModel(): Promise<boolean> {
        try {
            this.log('info', `Pulling model ${this.config.model}...`);
            
            const response = await axios.post(`${this.config.baseUrl}/api/pull`, {
                name: this.config.model
            }, {
                timeout: 300000 // 5 minutes for model download
            });

            return response.status === 200;
        } catch (error) {
            this.log('error', `Error pulling model: ${error}`);
            return false;
        }
    }

    /**
     * Start health checking
     */
    private startHealthChecking(): void {
        if (this.healthCheckTimer) {
            clearInterval(this.healthCheckTimer);
        }

        this.healthCheckTimer = setInterval(async () => {
            await this.performHealthCheck();
        }, this.config.healthCheckInterval);

        this.log('info', 'Health checking started');
    }

    /**
     * Perform health check
     */
    private async performHealthCheck(): Promise<void> {
        try {
            const isRunning = await this.isOllamaRunning();
            
            this.healthStatus = {
                ...this.healthStatus,
                isRunning,
                isResponding: isRunning,
                lastHealthCheck: new Date(),
                uptime: this.startTime ? Date.now() - this.startTime.getTime() : 0,
                errorCount: this.errorCount
            };

            if (!isRunning && this.errorCount < this.maxErrors) {
                this.log('warn', 'Ollama health check failed, attempting restart...');
                this.errorCount++;
                await this.startOllama();
            }

        } catch (error) {
            this.log('error', `Health check error: ${error}`);
            this.errorCount++;
        }
    }

    /**
     * Get current health status
     */
    getHealthStatus(): OllamaHealthStatus {
        return { ...this.healthStatus };
    }

    /**
     * Stop Ollama service
     */
    async stopOllama(): Promise<boolean> {
        try {
            this.isShuttingDown = true;
            this.log('info', 'Stopping Ollama service...');

            if (this.healthCheckTimer) {
                clearInterval(this.healthCheckTimer);
                this.healthCheckTimer = null;
            }

            if (this.process) {
                this.process.kill('SIGTERM');
                
                // Wait for graceful shutdown
                await this.sleep(5000);
                
                if (this.process && !this.process.killed) {
                    this.process.kill('SIGKILL');
                }
                
                this.process = null;
            }

            this.healthStatus.isRunning = false;
            this.healthStatus.isResponding = false;
            this.log('info', 'Ollama service stopped');
            return true;

        } catch (error) {
            this.log('error', `Error stopping Ollama: ${error}`);
            return false;
        }
    }

    /**
     * Test Ollama with a simple prompt
     */
    async testOllama(): Promise<boolean> {
        try {
            const response = await axios.post(`${this.config.baseUrl}/api/generate`, {
                model: this.config.model,
                prompt: 'Hello, can you respond?',
                stream: false
            }, {
                timeout: 30000
            });

            return response.status === 200 && response.data.response;
        } catch (error) {
            this.log('error', `Ollama test failed: ${error}`);
            return false;
        }
    }

    /**
     * Utility methods
     */
    private sleep(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    private log(level: string, message: string): void {
        const levels = { debug: 0, info: 1, warn: 2, error: 3 };
        const configLevel = levels[this.config.logLevel] || 1;
        const messageLevel = levels[level as keyof typeof levels] || 1;

        if (messageLevel >= configLevel) {
            const timestamp = new Date().toISOString();
            console.log(`[${timestamp}] [OLLAMA-${level.toUpperCase()}] ${message}`);
        }
    }
}

/**
 * Factory function to create and start Ollama service
 */
export async function createAndStartOllama(config?: Partial<OllamaStartupConfig>): Promise<OllamaStartupService> {
    const service = new OllamaStartupService(config);
    
    if (config?.autoStart !== false) {
        await service.startOllama();
    }
    
    return service;
}
