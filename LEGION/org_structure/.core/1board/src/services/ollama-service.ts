/**
 * Ollama Integration Service
 * Provides LLM-powered insights and actionable recommendations
 * using the converted workspace context
 */

import axios from 'axios';
import { ActionableItem, LLMContext } from './llm-context-converter';

export interface OllamaConfig {
    baseUrl: string;
    model: string;
    temperature: number;
    timeout: number;
    maxTokens?: number;
}

export interface OllamaRequest {
    model: string;
    prompt: string;
    stream?: boolean;
    options?: {
        temperature?: number;
        top_p?: number;
        max_tokens?: number;
    };
}

export interface OllamaResponse {
    response: string;
    done: boolean;
    context?: number[];
    total_duration?: number;
    load_duration?: number;
    prompt_eval_count?: number;
    prompt_eval_duration?: number;
    eval_count?: number;
    eval_duration?: number;
}

export interface InsightRequest {
    context: LLMContext;
    focusArea?: 'strategic' | 'operational' | 'research' | 'financial' | 'governance';
    priority?: 'high' | 'medium' | 'low';
    templateType?: 'executive-summary' | 'technical-analysis' | 'action-plan' | 'risk-assessment';
}

export interface AnalysisTemplate {
    name: string;
    description: string;
    prompt: string;
    expectedOutputFormat: string;
    confidenceThreshold: number;
}

export interface BoardRecommendation {
    title: string;
    summary: string;
    category: string;
    priority: 'critical' | 'high' | 'medium' | 'low';
    confidence: number;
    reasoning: string[];
    actionItems: ActionableItem[];
    risks: string[];
    opportunities: string[];
    timeline: string;
    resources: string[];
    successMetrics: string[];
    generatedAt: Date;
}

/**
 * Ollama LLM Service for Board Governance Insights
 */
export class OllamaService {
    private config: OllamaConfig;
    private isServerRunning: boolean = false;
    private templates: Map<string, AnalysisTemplate> = new Map();

    constructor(config: Partial<OllamaConfig> = {}) {
        this.config = {
            baseUrl: 'http://localhost:11434',
            model: 'llama3.2',
            temperature: 0.7,
            timeout: 30000,
            ...config
        };
        
        this.initializeTemplates();
    }

    /**
     * Initialize analysis templates for different use cases
     */
    private initializeTemplates(): void {
        this.templates.set('executive-summary', {
            name: 'Executive Summary',
            description: 'High-level strategic overview for board members',
            prompt: this.getExecutiveSummaryTemplate(),
            expectedOutputFormat: 'structured-summary',
            confidenceThreshold: 0.8
        });

        this.templates.set('technical-analysis', {
            name: 'Technical Analysis',
            description: 'Detailed technical assessment and recommendations',
            prompt: this.getTechnicalAnalysisTemplate(),
            expectedOutputFormat: 'detailed-analysis',
            confidenceThreshold: 0.75
        });

        this.templates.set('action-plan', {
            name: 'Action Plan',
            description: 'Concrete action items with timelines and priorities',
            prompt: this.getActionPlanTemplate(),
            expectedOutputFormat: 'actionable-list',
            confidenceThreshold: 0.85
        });

        this.templates.set('risk-assessment', {
            name: 'Risk Assessment',
            description: 'Comprehensive risk analysis and mitigation strategies',
            prompt: this.getRiskAssessmentTemplate(),
            expectedOutputFormat: 'risk-matrix',
            confidenceThreshold: 0.9
        });

        this.templates.set('strategic-planning', {
            name: 'Strategic Planning',
            description: 'Long-term strategic insights and planning recommendations',
            prompt: this.getStrategicPlanningTemplate(),
            expectedOutputFormat: 'strategic-framework',
            confidenceThreshold: 0.8
        });
    }

    /**
     * Start Ollama server if not running
     */
    async startOllamaServer(): Promise<boolean> {
        try {
            // Check if server is already running
            if (await this.checkServerStatus()) {
                this.isServerRunning = true;
                console.log('Ollama server is already running');
                return true;
            }

            console.log('Starting Ollama server...');
            
            // For Windows, we'll use spawn to start ollama serve
            const { spawn } = require('child_process');
            const ollamaProcess = spawn('ollama', ['serve'], {
                detached: true,
                stdio: 'ignore'
            });

            ollamaProcess.unref();

            // Wait for server to start (up to 30 seconds)
            for (let i = 0; i < 30; i++) {
                await this.sleep(1000);
                if (await this.checkServerStatus()) {
                    this.isServerRunning = true;
                    console.log('Ollama server started successfully');
                    return true;
                }
            }

            console.error('Failed to start Ollama server within timeout');
            return false;

        } catch (error) {
            console.error('Error starting Ollama server:', error);
            return false;
        }
    }

    /**
     * Check if Ollama server is running
     */
    async checkServerStatus(): Promise<boolean> {
        try {
            const response = await axios.get(`${this.config.baseUrl}/api/tags`, {
                timeout: 5000
            });
            return response.status === 200;
        } catch (error) {
            return false;
        }
    }

    /**
     * Ensure required model is available
     */
    async ensureModel(): Promise<boolean> {
        try {
            const response = await axios.get(`${this.config.baseUrl}/api/tags`);
            const models = response.data.models || [];
            
            const modelExists = models.some((model: any) => 
                model.name.includes(this.config.model)
            );

            if (!modelExists) {
                console.log(`Pulling model: ${this.config.model}`);
                await this.pullModel(this.config.model);
            }

            return true;
        } catch (error) {
            console.error('Error checking/pulling model:', error);
            return false;
        }
    }

    /**
     * Pull a model from Ollama registry
     */
    private async pullModel(modelName: string): Promise<void> {
        try {
            await axios.post(`${this.config.baseUrl}/api/pull`, {
                name: modelName
            }, {
                timeout: 300000 // 5 minutes for model download
            });

            console.log(`Model ${modelName} pulled successfully`);
        } catch (error) {
            console.error(`Error pulling model ${modelName}:`, error);
            throw error;
        }
    }

    /**
     * Generate board recommendations using LLM analysis
     */
    async generateBoardRecommendations(request: InsightRequest): Promise<BoardRecommendation[]> {
        if (!await this.ensureSystemReady()) {
            throw new Error('Ollama system not ready');
        }

        const recommendations: BoardRecommendation[] = [];
        const templateType = request.templateType || 'executive-summary';
        const template = this.templates.get(templateType);

        if (!template) {
            throw new Error(`Template not found: ${templateType}`);
        }

        try {
            // Generate insights for different areas
            const areas = request.focusArea ? [request.focusArea] : 
                ['strategic', 'operational', 'research', 'financial', 'governance'];

            for (const area of areas) {
                const areaRecommendation = await this.generateAreaRecommendation(
                    request.context, 
                    area as any, 
                    template
                );
                
                if (areaRecommendation && areaRecommendation.confidence >= template.confidenceThreshold) {
                    recommendations.push(areaRecommendation);
                }
            }

            // Sort by priority and confidence
            recommendations.sort((a, b) => {
                const priorityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
                const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
                if (priorityDiff !== 0) return priorityDiff;
                return b.confidence - a.confidence;
            });

            return recommendations;

        } catch (error) {
            console.error('Error generating board recommendations:', error);
            throw error;
        }
    }

    /**
     * Generate recommendation for specific area
     */
    private async generateAreaRecommendation(
        context: LLMContext, 
        area: string, 
        template: AnalysisTemplate
    ): Promise<BoardRecommendation | null> {
        try {
            const prompt = this.buildContextualPrompt(context, area, template);
            const response = await this.queryOllama(prompt);
            
            return this.parseRecommendationResponse(response, area);
            
        } catch (error) {
            console.error(`Error generating recommendation for ${area}:`, error);
            return null;
        }
    }

    /**
     * Build contextual prompt with workspace data
     */
    private buildContextualPrompt(context: LLMContext, area: string, template: AnalysisTemplate): string {
        const contextSummary = this.summarizeContextForArea(context, area);
        
        return `${template.prompt}

WORKSPACE CONTEXT:
${contextSummary}

FOCUS AREA: ${area}

Please provide a comprehensive analysis and actionable recommendations based on this context. 
Format your response as a structured JSON object with the following fields:
- title: Brief descriptive title
- summary: Executive summary (2-3 sentences)
- category: The focus area category
- priority: critical/high/medium/low
- confidence: 0.0-1.0 confidence score
- reasoning: Array of key reasoning points
- actionItems: Array of specific action items
- risks: Array of identified risks
- opportunities: Array of identified opportunities
- timeline: Suggested implementation timeline
- resources: Required resources/dependencies
- successMetrics: How to measure success

Ensure all recommendations are practical, data-driven, and directly actionable.`;
    }

    /**
     * Summarize context for specific area
     */
    private summarizeContextForArea(context: LLMContext, area: string): string {
        let summary = '';
        
        summary += `METADATA: Generated at ${context.metadata.generatedAt}, ${context.metadata.totalDataPoints} data points\n\n`;
        
        switch (area) {
            case 'strategic':
                summary += `STRATEGIC CONTEXT:\n`;
                summary += `- Enterprise strategies: ${context.enterprise.strategies.length} active\n`;
                summary += `- Research trends: ${context.research.researchTrends.length} identified\n`;
                summary += `- DAO governance: ${context.dao.governance.proposals.active} active proposals\n`;
                break;
                
            case 'operational':
                summary += `OPERATIONAL CONTEXT:\n`;
                summary += `- System efficiency: ${context.enterprise.operations.efficiency}\n`;
                summary += `- Automation level: ${context.enterprise.operations.automation}\n`;
                summary += `- Database systems: ${context.databases.length} active\n`;
                break;
                
            case 'research':
                summary += `RESEARCH CONTEXT:\n`;
                summary += `- Research papers: ${context.research.papers.length}\n`;
                summary += `- Cognitive models: ${context.research.models.length}\n`;
                summary += `- Security level: ${context.research.securityLevel}\n`;
                break;
                
            case 'financial':
                summary += `FINANCIAL CONTEXT:\n`;
                summary += `- Treasury balance: ${context.dao.treasury.balance}\n`;
                summary += `- Budget allocations: ${context.dao.treasury.allocations.length}\n`;
                summary += `- KPI metrics: ${context.enterprise.kpis.length} tracked\n`;
                break;
                
            case 'governance':
                summary += `GOVERNANCE CONTEXT:\n`;
                summary += `- Compliance score: ${context.enterprise.governance.compliance.overall}\n`;
                summary += `- DAO participation: ${context.dao.governance.participation.averageParticipation}\n`;
                summary += `- Policies: ${context.enterprise.governance.policies.length} active\n`;
                break;
        }
        
        // Add current insights
        const areaInsights = context.insights.filter(insight => insight.category === area);
        if (areaInsights.length > 0) {
            summary += `\nCURRENT INSIGHTS:\n`;
            areaInsights.forEach(insight => {
                summary += `- ${insight.insight} (confidence: ${insight.confidence})\n`;
            });
        }
        
        // Add actionable items
        const areaActions = context.actionableItems.filter(item => item.category === area);
        if (areaActions.length > 0) {
            summary += `\nCURRENT ACTION ITEMS:\n`;
            areaActions.forEach(item => {
                summary += `- ${item.title} (${item.priority})\n`;
            });
        }
        
        return summary;
    }

    /**
     * Query Ollama with prompt
     */
    private async queryOllama(prompt: string): Promise<string> {
        try {
            const request: OllamaRequest = {
                model: this.config.model,
                prompt: prompt,
                stream: false,                options: {
                    temperature: this.config.temperature,
                    ...(this.config.maxTokens && { max_tokens: this.config.maxTokens })
                }
            };

            const response = await axios.post(`${this.config.baseUrl}/api/generate`, request, {
                timeout: this.config.timeout
            });

            return response.data.response;

        } catch (error) {
            console.error('Error querying Ollama:', error);
            throw error;
        }
    }

    /**
     * Parse LLM response into structured recommendation
     */
    private parseRecommendationResponse(response: string, area: string): BoardRecommendation | null {
        try {
            // Try to extract JSON from response
            const jsonMatch = response.match(/\{[\s\S]*\}/);
            if (!jsonMatch) {
                console.warn('No JSON found in response, creating fallback recommendation');
                return this.createFallbackRecommendation(response, area);
            }

            const parsed = JSON.parse(jsonMatch[0]);
            
            return {
                title: parsed.title || `${area} Analysis`,
                summary: parsed.summary || 'Analysis summary not provided',
                category: area,
                priority: parsed.priority || 'medium',
                confidence: parsed.confidence || 0.7,
                reasoning: Array.isArray(parsed.reasoning) ? parsed.reasoning : [parsed.reasoning || 'No reasoning provided'],
                actionItems: this.parseActionItems(parsed.actionItems),
                risks: Array.isArray(parsed.risks) ? parsed.risks : [parsed.risks || 'No risks identified'],
                opportunities: Array.isArray(parsed.opportunities) ? parsed.opportunities : [parsed.opportunities || 'No opportunities identified'],
                timeline: parsed.timeline || 'Timeline not specified',
                resources: Array.isArray(parsed.resources) ? parsed.resources : [parsed.resources || 'Resources not specified'],
                successMetrics: Array.isArray(parsed.successMetrics) ? parsed.successMetrics : [parsed.successMetrics || 'Metrics not specified'],
                generatedAt: new Date()
            };

        } catch (error) {
            console.warn('Error parsing LLM response, creating fallback:', error);
            return this.createFallbackRecommendation(response, area);
        }
    }

    /**
     * Parse action items from LLM response
     */
    private parseActionItems(actionItems: any): ActionableItem[] {
        if (!Array.isArray(actionItems)) {
            return [];
        }

        return actionItems.map((item, index) => ({
            id: `ai-llm-${Date.now()}-${index}`,
            title: typeof item === 'string' ? item : (item.title || `Action Item ${index + 1}`),
            description: typeof item === 'string' ? item : (item.description || item.title || 'No description provided'),
            category: typeof item === 'object' ? (item.category || 'general') : 'general',
            priority: typeof item === 'object' ? (item.priority || 'medium') : 'medium',
            estimatedEffort: typeof item === 'object' ? (item.estimatedEffort || 'Not specified') : 'Not specified',
            potentialImpact: typeof item === 'object' ? (item.potentialImpact || 'Not specified') : 'Not specified',
            dependencies: typeof item === 'object' && Array.isArray(item.dependencies) ? item.dependencies : [],
            status: 'pending' as const
        }));
    }

    /**
     * Create fallback recommendation when parsing fails
     */
    private createFallbackRecommendation(response: string, area: string): BoardRecommendation {
        return {
            title: `${area.charAt(0).toUpperCase() + area.slice(1)} Analysis`,
            summary: response.substring(0, 200) + (response.length > 200 ? '...' : ''),
            category: area,
            priority: 'medium',
            confidence: 0.6,
            reasoning: ['Generated from LLM analysis', 'Parsing failed, using raw response'],
            actionItems: [],
            risks: ['Unable to parse specific risks from response'],
            opportunities: ['Unable to parse specific opportunities from response'],
            timeline: 'Not specified in response',
            resources: ['Not specified in response'],
            successMetrics: ['Not specified in response'],
            generatedAt: new Date()
        };
    }

    /**
     * Ensure Ollama system is ready
     */
    private async ensureSystemReady(): Promise<boolean> {
        if (!this.isServerRunning) {
            if (!await this.startOllamaServer()) {
                return false;
            }
        }

        if (!await this.checkServerStatus()) {
            return false;
        }

        return await this.ensureModel();
    }

    /**
     * Utility sleep function
     */
    private sleep(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Template methods for different analysis types
    private getExecutiveSummaryTemplate(): string {
        return `You are an AI assistant specializing in executive-level analysis for board governance.
Analyze the provided workspace context and generate a concise executive summary with high-level strategic recommendations.
Focus on key insights that board members need to know for strategic decision-making.
Prioritize clarity, actionability, and business impact.`;
    }

    private getTechnicalAnalysisTemplate(): string {
        return `You are an AI assistant specializing in technical analysis for board governance systems.
Analyze the provided workspace context and generate detailed technical recommendations.
Focus on system architecture, data flows, integration points, and technical debt.
Provide specific technical action items with implementation guidance.`;
    }

    private getActionPlanTemplate(): string {
        return `You are an AI assistant specializing in action planning for board governance.
Analyze the provided workspace context and generate a concrete action plan.
Focus on specific, measurable, achievable, relevant, and time-bound (SMART) action items.
Prioritize actions by impact and urgency, provide clear timelines and resource requirements.`;
    }

    private getRiskAssessmentTemplate(): string {
        return `You are an AI assistant specializing in risk assessment for board governance.
Analyze the provided workspace context and identify potential risks and mitigation strategies.
Focus on operational, strategic, financial, and governance risks.
Provide risk likelihood, impact assessment, and specific mitigation recommendations.`;
    }

    private getStrategicPlanningTemplate(): string {
        return `You are an AI assistant specializing in strategic planning for board governance.
Analyze the provided workspace context and generate long-term strategic recommendations.
Focus on competitive positioning, market opportunities, innovation strategies, and growth initiatives.
Provide strategic frameworks and implementation roadmaps.`;
    }
}

/**
 * Factory function to create configured Ollama service
 */
export function createOllamaService(config?: Partial<OllamaConfig>): OllamaService {
    return new OllamaService(config);
}
