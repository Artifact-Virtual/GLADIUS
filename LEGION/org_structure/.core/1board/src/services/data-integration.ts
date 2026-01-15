/**
 * Data Integration Service for Board Governance System
 * Comprehensive integration with W:\artifactvirtual\data folder
 * Provides data context, persistence, and analytics for board operations
 */

import fs from 'fs';
import path from 'path';
import { BehaviorSubject, Observable } from 'rxjs';
import sqlite3 from 'sqlite3';

import { PerformanceMetrics } from '../models/governance-metrics';

export interface DataIntegrationConfig {
    dataRoot: string;
    databasePath: string;
    researchDataPath: string;
    enterpriseDataPath: string;
    daoDataPath: string;
    backupPath: string;
    monitoringInterval: number;
}

export interface WorkspaceDataContext {
    databases: Map<string, sqlite3.Database>;
    researchFiles: Map<string, any>;
    enterpriseData: Map<string, any>;
    daoData: Map<string, any>;
    systemMetrics: Map<string, any>;
    lastUpdated: Date;
}

/**
 * Data Integration Service
 * Manages all data interactions for the board governance system
 */
export class DataIntegrationService {
    private readonly config: DataIntegrationConfig;
    private readonly dataContext: WorkspaceDataContext;
    private readonly dataStream$ = new BehaviorSubject<WorkspaceDataContext>({} as WorkspaceDataContext);
    private isInitialized = false;

    constructor(config?: Partial<DataIntegrationConfig>) {
        this.config = {
            dataRoot: 'W:\\artifactvirtual\\data',
            databasePath: 'W:\\artifactvirtual\\data',
            researchDataPath: 'W:\\artifactvirtual\\data\\real_research',
            enterpriseDataPath: 'W:\\artifactvirtual\\data\\enterprise',
            daoDataPath: 'W:\\artifactvirtual\\data\\dao',
            backupPath: 'W:\\artifactvirtual\\data\\backups',
            monitoringInterval: 30000, // 30 seconds
            ...config
        };

        this.dataContext = {
            databases: new Map(),
            researchFiles: new Map(),
            enterpriseData: new Map(),
            daoData: new Map(),
            systemMetrics: new Map(),
            lastUpdated: new Date()
        };
    }

    /**
     * Initialize the data integration service
     */
    public async initialize(): Promise<void> {
        console.log(`[DataIntegration] Initializing with data root: ${this.config.dataRoot}`);
        
        try {
            // Ensure data directories exist
            await this.ensureDirectories();
            
            // Connect to databases
            await this.connectDatabases();
            
            // Load research data
            await this.loadResearchData();
            
            // Load enterprise data
            await this.loadEnterpriseData();
            
            // Load DAO data
            await this.loadDaoData();
            
            // Start monitoring
            this.startDataMonitoring();
            
            this.isInitialized = true;
            console.log('[DataIntegration] Successfully initialized');
            
        } catch (error) {
            console.error('[DataIntegration] Initialization failed:', error);
            throw error;
        }
    }

    /**
     * Get the current data context
     */
    public getDataContext(): WorkspaceDataContext {
        return this.dataContext;
    }

    /**
     * Get data stream observable
     */
    public getDataStream(): Observable<WorkspaceDataContext> {
        return this.dataStream$.asObservable();
    }

    /**
     * Ensure all required directories exist
     */
    private async ensureDirectories(): Promise<void> {
        const directories = [
            this.config.dataRoot,
            this.config.researchDataPath,
            this.config.enterpriseDataPath,
            this.config.daoDataPath,
            this.config.backupPath
        ];

        for (const dir of directories) {
            if (!fs.existsSync(dir)) {
                console.log(`[DataIntegration] Creating directory: ${dir}`);
                fs.mkdirSync(dir, { recursive: true });
            }
        }
    }

    /**
     * Connect to all available databases
     */
    private async connectDatabases(): Promise<void> {
        const databaseFiles = [
            'automation_orchestrator.db',
            'backup_system.db',
            'e2e_test.db',
            'integration_test.db',
            'monitoring.db',
            'production_crew.db',
            'research_lab.db',
            'test_framework.db'
        ];

        for (const dbFile of databaseFiles) {
            const dbPath = path.join(this.config.databasePath, dbFile);
            if (fs.existsSync(dbPath)) {
                try {
                    const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY);
                    this.dataContext.databases.set(dbFile.replace('.db', ''), db);
                    console.log(`[DataIntegration] Connected to database: ${dbFile}`);
                } catch (error) {
                    console.warn(`[DataIntegration] Failed to connect to ${dbFile}:`, error);
                }
            }
        }
    }

    /**
     * Load research data from the research directory
     */
    private async loadResearchData(): Promise<void> {
        console.log(`[DataIntegration] Loading research data from: ${this.config.researchDataPath}`);
        
        if (!fs.existsSync(this.config.researchDataPath)) {
            console.warn(`[DataIntegration] Research data path does not exist: ${this.config.researchDataPath}`);
            return;
        }

        try {
            const files = fs.readdirSync(this.config.researchDataPath);
            
            for (const file of files) {
                const filePath = path.join(this.config.researchDataPath, file);
                const stats = fs.statSync(filePath);
                
                if (stats.isFile() && file.endsWith('.json')) {
                    try {
                        const content = JSON.parse(fs.readFileSync(filePath, 'utf8'));
                        this.dataContext.researchFiles.set(file, {
                            ...content,
                            filePath,
                            lastModified: stats.mtime,
                            size: stats.size
                        });
                        console.log(`[DataIntegration] Loaded research file: ${file}`);
                    } catch (error) {
                        console.warn(`[DataIntegration] Failed to parse research file ${file}:`, error);
                    }
                }
            }
            
            console.log(`[DataIntegration] Loaded ${this.dataContext.researchFiles.size} research files`);
            
        } catch (error) {
            console.error('[DataIntegration] Error loading research data:', error);
        }
    }

    /**
     * Load enterprise data
     */
    private async loadEnterpriseData(): Promise<void> {
        console.log(`[DataIntegration] Loading enterprise data from: ${this.config.enterpriseDataPath}`);
        
        if (!fs.existsSync(this.config.enterpriseDataPath)) {
            console.warn(`[DataIntegration] Enterprise data path does not exist: ${this.config.enterpriseDataPath}`);
            return;
        }

        try {
            // Load any enterprise-specific data files
            const files = fs.readdirSync(this.config.enterpriseDataPath);
            
            for (const file of files) {
                const filePath = path.join(this.config.enterpriseDataPath, file);
                const stats = fs.statSync(filePath);
                
                if (stats.isFile()) {
                    try {
                        let content;
                        if (file.endsWith('.json')) {
                            content = JSON.parse(fs.readFileSync(filePath, 'utf8'));
                        } else {
                            content = fs.readFileSync(filePath, 'utf8');
                        }
                        
                        this.dataContext.enterpriseData.set(file, {
                            content,
                            filePath,
                            lastModified: stats.mtime,
                            size: stats.size
                        });
                        console.log(`[DataIntegration] Loaded enterprise file: ${file}`);
                    } catch (error) {
                        console.warn(`[DataIntegration] Failed to load enterprise file ${file}:`, error);
                    }
                }
            }
            
        } catch (error) {
            console.error('[DataIntegration] Error loading enterprise data:', error);
        }
    }

    /**
     * Load DAO data
     */
    private async loadDaoData(): Promise<void> {
        console.log(`[DataIntegration] Loading DAO data from: ${this.config.daoDataPath}`);
        
        if (!fs.existsSync(this.config.daoDataPath)) {
            console.warn(`[DataIntegration] DAO data path does not exist: ${this.config.daoDataPath}`);
            return;
        }

        try {
            // Load any DAO-specific data files
            const files = fs.readdirSync(this.config.daoDataPath);
            
            for (const file of files) {
                const filePath = path.join(this.config.daoDataPath, file);
                const stats = fs.statSync(filePath);
                
                if (stats.isFile()) {
                    try {
                        let content;
                        if (file.endsWith('.json')) {
                            content = JSON.parse(fs.readFileSync(filePath, 'utf8'));
                        } else {
                            content = fs.readFileSync(filePath, 'utf8');
                        }
                        
                        this.dataContext.daoData.set(file, {
                            content,
                            filePath,
                            lastModified: stats.mtime,
                            size: stats.size
                        });
                        console.log(`[DataIntegration] Loaded DAO file: ${file}`);
                    } catch (error) {
                        console.warn(`[DataIntegration] Failed to load DAO file ${file}:`, error);
                    }
                }
            }
            
        } catch (error) {
            console.error('[DataIntegration] Error loading DAO data:', error);
        }
    }

    /**
     * Start continuous data monitoring
     */
    private startDataMonitoring(): void {
        console.log(`[DataIntegration] Starting data monitoring (interval: ${this.config.monitoringInterval}ms)`);
        
        setInterval(async () => {
            try {
                await this.refreshDataContext();
                this.dataStream$.next(this.dataContext);
            } catch (error) {
                console.error('[DataIntegration] Error during data monitoring:', error);
            }
        }, this.config.monitoringInterval);
    }

    /**
     * Refresh the data context
     */
    private async refreshDataContext(): Promise<void> {
        // Update system metrics
        this.dataContext.systemMetrics.set('workspace_stats', await this.gatherWorkspaceStats());
        this.dataContext.systemMetrics.set('database_stats', await this.gatherDatabaseStats());
        this.dataContext.systemMetrics.set('research_stats', await this.gatherResearchStats());
        
        this.dataContext.lastUpdated = new Date();
    }

    /**
     * Gather workspace statistics
     */
    private async gatherWorkspaceStats(): Promise<any> {
        try {
            const stats = {
                dataDirectorySize: this.getDirectorySize(this.config.dataRoot),
                totalDatabases: this.dataContext.databases.size,
                totalResearchFiles: this.dataContext.researchFiles.size,
                totalEnterpriseFiles: this.dataContext.enterpriseData.size,
                totalDaoFiles: this.dataContext.daoData.size,
                lastUpdated: new Date()
            };
            
            return stats;
        } catch (error) {
            console.error('[DataIntegration] Error gathering workspace stats:', error);
            return {};
        }
    }

    /**
     * Gather database statistics
     */
    private async gatherDatabaseStats(): Promise<any> {
        const dbStats: any = {};
        
        for (const [dbName, db] of this.dataContext.databases) {
            try {
                // Get table count and other basic stats
                // This is a simplified version - could be expanded based on specific database schemas
                dbStats[dbName] = {
                    connected: true,
                    lastAccessed: new Date()
                };
            } catch (error) {
                console.warn(`[DataIntegration] Error getting stats for database ${dbName}:`, error);
                dbStats[dbName] = {
                    connected: false,
                    error: error.message
                };
            }
        }
        
        return dbStats;
    }

    /**
     * Gather research statistics
     */
    private async gatherResearchStats(): Promise<any> {
        try {
            const researchStats = {
                totalFiles: this.dataContext.researchFiles.size,
                totalDataSize: 0,
                fileTypes: new Map(),
                lastModified: new Date(0)
            };

            for (const [fileName, fileData] of this.dataContext.researchFiles) {
                researchStats.totalDataSize += fileData.size || 0;
                
                const extension = path.extname(fileName);
                const count = researchStats.fileTypes.get(extension) || 0;
                researchStats.fileTypes.set(extension, count + 1);
                
                if (fileData.lastModified > researchStats.lastModified) {
                    researchStats.lastModified = fileData.lastModified;
                }
            }

            return {
                ...researchStats,
                fileTypes: Object.fromEntries(researchStats.fileTypes)
            };
        } catch (error) {
            console.error('[DataIntegration] Error gathering research stats:', error);
            return {};
        }
    }

    /**
     * Get directory size recursively
     */
    private getDirectorySize(dirPath: string): number {
        try {
            let totalSize = 0;
            const files = fs.readdirSync(dirPath);
            
            for (const file of files) {
                const filePath = path.join(dirPath, file);
                const stats = fs.statSync(filePath);
                
                if (stats.isDirectory()) {
                    totalSize += this.getDirectorySize(filePath);
                } else {
                    totalSize += stats.size;
                }
            }
            
            return totalSize;
        } catch (error) {
            console.warn(`[DataIntegration] Error calculating directory size for ${dirPath}:`, error);
            return 0;
        }
    }

    /**
     * Save board decision to data store
     */
    public async saveDecisionRecord(decision: any): Promise<void> {
        try {
            const decisionFile = path.join(this.config.enterpriseDataPath, 'board-decisions.json');
            let decisions = [];
            
            if (fs.existsSync(decisionFile)) {
                decisions = JSON.parse(fs.readFileSync(decisionFile, 'utf8'));
            }
            
            decisions.push({
                ...decision,
                timestamp: new Date(),
                id: `decision_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
            });
            
            fs.writeFileSync(decisionFile, JSON.stringify(decisions, null, 2));
            console.log('[DataIntegration] Saved board decision record');
            
        } catch (error) {
            console.error('[DataIntegration] Error saving decision record:', error);
        }
    }

    /**
     * Get historical board performance data
     */
    public async getBoardPerformanceHistory(): Promise<any[]> {
        try {
            const performanceFile = path.join(this.config.enterpriseDataPath, 'board-performance.json');
            
            if (fs.existsSync(performanceFile)) {
                return JSON.parse(fs.readFileSync(performanceFile, 'utf8'));
            }
            
            return [];
        } catch (error) {
            console.error('[DataIntegration] Error loading board performance history:', error);
            return [];
        }
    }

    /**
     * Save board performance metrics
     */
    public async saveBoardPerformanceMetrics(metrics: PerformanceMetrics): Promise<void> {
        try {
            const performanceFile = path.join(this.config.enterpriseDataPath, 'board-performance.json');
            let history = [];
            
            if (fs.existsSync(performanceFile)) {
                history = JSON.parse(fs.readFileSync(performanceFile, 'utf8'));
            }
            
            history.push({
                ...metrics,
                recordedAt: new Date(),
                id: `performance_${Date.now()}`
            });
            
            // Keep only last 1000 records to prevent file from growing too large
            if (history.length > 1000) {
                history = history.slice(-1000);
            }
            
            fs.writeFileSync(performanceFile, JSON.stringify(history, null, 2));
            console.log('[DataIntegration] Saved board performance metrics');
            
        } catch (error) {
            console.error('[DataIntegration] Error saving performance metrics:', error);
        }
    }

    /**
     * Clean up resources
     */
    public async cleanup(): Promise<void> {
        console.log('[DataIntegration] Cleaning up resources...');
        
        // Close database connections
        for (const [dbName, db] of this.dataContext.databases) {
            try {
                db.close();
                console.log(`[DataIntegration] Closed database: ${dbName}`);
            } catch (error) {
                console.warn(`[DataIntegration] Error closing database ${dbName}:`, error);
            }
        }
        
        this.dataContext.databases.clear();
        this.isInitialized = false;
    }
}
