/**
 * Research Data Ingestion Service
 * Ingests research data from the research library and feeds it to the board governance system
 * Converts research papers, debates, and other data into SystemState and EnvironmentalEvents
 */

import fs from 'fs';
import path from 'path';
import { Observable, Subject } from 'rxjs';
import sqlite3 from 'sqlite3';


import {
    EnvironmentalEvent,
    EventImpact,
    EventSeverity,
    EventSource,
    EventType,
    SystemState
} from '../models/core-types';

/**
 * Research Data Types
 */
export interface ResearchPaper {
    title: string;
    abstract: string;
    content: string;
    topics: string[];
    confidence: number;
    date: Date;
}

export interface DebateSummary {
    topic: string;
    synthesis: string;
    key_evidence: string[];
    consensus_points: string[];
    contentious_points: string[];
    actionable_insights: string[];
    confidence_score: number;
    research_basis: number;
    generated: string;
}

export interface ResearchEntry {
    id: string;
    title: string;
    category: string;
    classification: string;
    file_path: string;
    metadata: Record<string, any>;
}

/**
 * Research Ingestion Service
 * Reads research data from various sources and converts it into system events
 */
export class ResearchIngestionService {
    private eventSubject: Subject<EnvironmentalEvent> = new Subject<EnvironmentalEvent>();
    private stateSubject: Subject<Partial<SystemState>> = new Subject<Partial<SystemState>>();

    /**
     * Get observable streams of events and state updates
     */
    public getEvents(): Observable<EnvironmentalEvent> {
        return this.eventSubject.asObservable();
    }
    
    public getStateUpdates(): Observable<Partial<SystemState>> {
        return this.stateSubject.asObservable();
    }

    /**
     * Ingest all research data from specified paths
     */
    public async ingestAllResearch(): Promise<void> {
        console.log("Starting comprehensive research data ingestion...");
        
        // Ingest automated papers
        await this.ingestAutomatedPapers();
        
        // Ingest debates
        await this.ingestDebates();
        
        // Ingest research library data
        await this.ingestResearchLibrary();
        
        console.log("Research data ingestion complete.");
    }

    /**
     * Ingest automated papers from the specified directory
     */
    private async ingestAutomatedPapers(): Promise<void> {
        const papersDir = 'W:/artifactvirtual/research/automated_papers';
        console.log(`Ingesting automated papers from ${papersDir}...`);
        
        try {
            const files = fs.readdirSync(papersDir);
            for (const file of files) {
                if (file.endsWith('.md')) {
                    const filePath = path.join(papersDir, file);
                    const content = fs.readFileSync(filePath, 'utf8');
                    
                    // Extract title and abstract from markdown
                    const titleMatch = content.match(/^# (.+)$/m);
                    const title = titleMatch ? titleMatch[1] : path.basename(file, '.md').replace(/_/g, ' ');
                    
                    // Extract abstract if available
                    const abstractMatch = content.match(/## Abstract\s+([\s\S]+?)(?=##|$)/);
                    const abstract = abstractMatch ? abstractMatch[1].trim() : '';
                    
                    // Create research paper object
                    const paper: ResearchPaper = {
                        title,
                        abstract,
                        content,
                        topics: this.extractTopics(content),
                        confidence: 0.85, // Default confidence
                        date: new Date()
                    };
                    
                    // Convert to event and emit
                    this.emitResearchPaperEvent(paper);
                }
            }
            console.log(`Processed ${files.length} papers.`);
        } catch (error) {
            console.error('Error ingesting automated papers:', error);
        }
    }

    /**
     * Ingest debate summaries and data
     */
    private async ingestDebates(): Promise<void> {
        const debatesDir = 'W:/artifactvirtual/debates';
        console.log(`Ingesting debates from ${debatesDir}...`);
        
        try {
            const files = fs.readdirSync(debatesDir);
            for (const file of files) {
                if (file.startsWith('summary_') && file.endsWith('.json')) {
                    const filePath = path.join(debatesDir, file);
                    const content = fs.readFileSync(filePath, 'utf8');
                    const debate = JSON.parse(content) as DebateSummary;
                    
                    // Emit event
                    this.emitDebateEvent(debate);
                }
            }
            console.log(`Processed ${files.filter(f => f.startsWith('summary_')).length} debate summaries.`);
        } catch (error) {
            console.error('Error ingesting debates:', error);
        }
    }

    /**
     * Ingest research library data from SQLite database
     */
    private async ingestResearchLibrary(): Promise<void> {
        const dbPath = 'W:/artifactvirtual/research/research_lib/research_data.db';
        console.log(`Ingesting research library data from ${dbPath}...`);
        
        return new Promise((resolve, reject) => {
            if (!fs.existsSync(dbPath)) {
                console.warn(`Research database not found at ${dbPath}`);
                resolve();
                return;
            }
            
            const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err) => {
                if (err) {
                    console.error('Error opening research database:', err);
                    reject(err);
                    return;
                }
                
                db.all("SELECT * FROM research_entries", [], (err, rows) => {
                    if (err) {
                        console.error('Error querying research database:', err);
                        db.close();
                        reject(err);
                        return;
                    }
                    
                    console.log(`Retrieved ${rows.length} research entries from database.`);
                    
                    for (const row of rows) {
                        const entry: ResearchEntry = {
                            id: row.id,
                            title: row.title,
                            category: row.category,
                            classification: row.classification,
                            file_path: row.file_path,
                            metadata: JSON.parse(row.metadata || '{}')
                        };
                        
                        this.emitResearchEntryEvent(entry);
                    }
                    
                    db.close();
                    resolve();
                });
            });
        });
    }

    /**
     * Extract topics from paper content using simple keyword analysis
     */
    private extractTopics(content: string): string[] {
        // Simplified topic extraction - would be more sophisticated in production
        const keywords = [
            'consciousness', 'quantum', 'governance', 'artificial intelligence', 
            'ethics', 'research', 'technology', 'systems', 'theory', 'uncertainty',
            'blockchain', 'autonomous', 'simulation', 'cognition', 'decision-making'
        ];
        
        return keywords.filter(keyword => 
            content.toLowerCase().includes(keyword.toLowerCase())
        );
    }

    /**
     * Convert research paper to environmental event and emit
     */    private emitResearchPaperEvent(paper: ResearchPaper): void {
        const event: EnvironmentalEvent = {
            eventId: `paper-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
            type: EventType.RESEARCH_BREAKTHROUGH,
            severity: EventSeverity.INFORMATIONAL,
            source: EventSource.RESEARCH_LAB,
            description: `Research Paper: ${paper.title}`,
            impact: {
                severity: 0.7,
                scope: ['research', 'strategic'],
                duration: 30,
                consequences: ['Research advancement', 'Strategic positioning'],
                mitigation: ['Monitor implementation', 'Risk assessment']
            },
            timestamp: new Date(),
            metadata: {
                paper: {
                    title: paper.title,
                    abstract: paper.abstract,
                    topics: paper.topics,
                    confidence: paper.confidence
                }
            }
        };
        
        this.eventSubject.next(event);
        
        // Also update system state for research
        this.stateSubject.next({
            research: {
                researchProgress: 0.7,
                innovationPipeline: 0.72,
                intellectualProperty: 0.65,
                collaborationIndex: 0.6,
                breakthroughProbability: 0.5
            },
            timestamp: new Date()
        });
    }

    /**
     * Convert debate summary to environmental event and emit
     */
    private emitDebateEvent(debate: DebateSummary): void {
        const event: EnvironmentalEvent = {
            eventId: `debate-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
            type: EventType.STRATEGIC_OPPORTUNITY,
            severity: EventSeverity.INFORMATIONAL,
            source: EventSource.ENTERPRISE,
            description: `Debate Summary: ${debate.topic}`,            impact: {
                severity: 0.8,
                scope: ['enterprise', 'strategic'],
                duration: 45,
                consequences: ['Strategic opportunity', 'Enterprise enhancement'],
                mitigation: ['Review recommendations', 'Implementation planning']
            },
            timestamp: new Date(debate.generated),
            metadata: {
                debate: {
                    topic: debate.topic,
                    synthesis: debate.synthesis,
                    consensus_points: debate.consensus_points,
                    actionable_insights: debate.actionable_insights,
                    confidence_score: debate.confidence_score
                }
            }
        };
        
        this.eventSubject.next(event);
          // Update strategic state
        this.stateSubject.next({
            strategic: {
                marketPosition: 0.68,
                competitiveAdvantage: 0.72,
                innovationIndex: 0.65,
                brandValue: 0.7,
                strategicAlignment: 0.75
            },
            timestamp: new Date()
        });
    }

    /**
     * Convert research entry to environmental event and emit
     */
    private emitResearchEntryEvent(entry: ResearchEntry): void {
        const event: EnvironmentalEvent = {
            eventId: `research-${entry.id}`,
            type: EventType.RESEARCH_BREAKTHROUGH,
            severity: this.getResearchSeverity(entry),
            source: EventSource.RESEARCH_LAB,
            description: `Research Entry: ${entry.title}`,
            impact: this.getResearchImpact(entry),
            timestamp: new Date(),
            metadata: {
                research_entry: {
                    id: entry.id,
                    title: entry.title,
                    category: entry.category,
                    classification: entry.classification,
                    metadata: entry.metadata
                }
            }
        };
        
        this.eventSubject.next(event);
    }

    /**
     * Determine severity based on research entry classification
     */
    private getResearchSeverity(entry: ResearchEntry): EventSeverity {
        switch (entry.classification) {
            case 'top_secret':
                return EventSeverity.CRITICAL;
            case 'secret':
                return EventSeverity.HIGH;
            case 'confidential':
                return EventSeverity.MEDIUM;
            case 'internal':
                return EventSeverity.LOW;
            default:
                return EventSeverity.INFORMATIONAL;
        }
    }

    /**
     * Determine impact based on research entry category and metadata
     */    private getResearchImpact(entry: ResearchEntry): EventImpact {
        // Adjust based on category
        switch (entry.category) {
            case 'cognitive_models':
                return {
                    severity: 0.8,
                    scope: ['research', 'strategic'],
                    duration: 45,
                    consequences: ['Cognitive model advancement', 'Strategic enhancement'],
                    mitigation: ['Monitor implementation', 'Risk assessment']
                };
            case 'analysis_results':
                return {
                    severity: 0.7,
                    scope: ['research', 'operational'],
                    duration: 30,
                    consequences: ['Analysis improvement', 'Operational insights'],
                    mitigation: ['Validate results', 'Monitor application']
                };
            case 'visualizations':
                return {
                    severity: 0.6,
                    scope: ['research', 'presentation'],
                    duration: 20,
                    consequences: ['Visualization enhancement', 'Data presentation'],
                    mitigation: ['Review presentation', 'Update documentation']
                };
            case 'encrypted_data':
                return {
                    severity: 0.9,
                    scope: ['research', 'security'],
                    duration: 60,
                    consequences: ['Encrypted data advancement', 'Security enhancement'],
                    mitigation: ['Security audit', 'Access control review']
                };
            default:
                return {
                    severity: 0.5,
                    scope: ['research'],
                    duration: 30,
                    consequences: ['Research advancement'],
                    mitigation: ['Monitor progress']
                };
        }
    }
}
