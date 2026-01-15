/**
 * Governance Metrics and Performance Measurement
 * Comprehensive metrics for board oversight and system governance
 */

import { DirectorRole } from './core-types';

/**
 * Metric Value Interface
 * Standard structure for all metric values
 */
export interface MetricValue {
    readonly value: number;
    readonly trend: number;
    readonly lastUpdated: Date;
    readonly confidence?: number;
    readonly current?: number;
    readonly target?: number;
    readonly previous?: number;
    readonly variance?: number;
    readonly threshold?: number;
    readonly status?: 'NORMAL' | 'WARNING' | 'CRITICAL';
}

/**
 * Confidence Interval Interface
 */
export interface ConfidenceInterval {
    readonly lower: number;
    readonly upper: number;
    readonly confidenceLevel: number;
}

/**
 * Performance Metrics Vector g: S → R^k
 * Multi-dimensional performance measurement system
 */
export interface PerformanceMetrics {
    /** Overall performance score [0,1] */
    readonly overallScore: number;
    
    /** Financial performance indicators */
    readonly financial: FinancialMetrics;
    
    /** Operational efficiency metrics */
    readonly operational: OperationalMetrics;
    
    /** Strategic alignment metrics */
    readonly strategic: StrategicMetrics;
    
    /** Research and innovation metrics */
    readonly research: ResearchMetrics;
    
    /** Security and compliance metrics */
    readonly security: SecurityMetrics;
    
    /** Governance effectiveness metrics */
    readonly governance: GovernanceMetrics;
    
    /** Timestamp of metric calculation */
    readonly timestamp: Date;
    
    /** Metric confidence interval */
    readonly confidence: ConfidenceInterval;
}

/**
 * Risk Assessment Framework
 * Comprehensive risk evaluation and management
 */
export interface RiskAssessment {
    /** Overall risk score [0,1] */
    readonly overallRisk: number;
    
    /** Risk categories and scores */
    readonly risks: Map<RiskCategory, RiskMetric>;
    
    /** Risk trends and projections */
    readonly trends: RiskTrend[];
    
    /** Mitigation strategies */
    readonly mitigations: RiskMitigation[];
    
    /** Risk tolerance thresholds */
    readonly thresholds: RiskThreshold[];
    
    /** Assessment timestamp */
    readonly timestamp: Date;
    
    /** Next assessment due date */
    readonly nextAssessment: Date;
}

/**
 * Compliance Status Framework
 * Multi-layered compliance monitoring and verification
 */
export interface ComplianceStatus {
    /** Overall compliance score [0,1] */
    readonly overallCompliance: number;
    
    /** Compliance by regulatory domain */
    readonly regulatory: Map<RegulatoryDomain, ComplianceMetric>;
    
    /** Internal policy compliance */
    readonly internal: Map<PolicyDomain, ComplianceMetric>;
    
    /** Constitutional compliance (blockchain governance) */
    readonly constitutional: ConstitutionalCompliance;
    
    /** Audit trail and documentation */
    readonly auditTrail: AuditRecord[];
    
    /** Compliance issues and remediation */
    readonly issues: ComplianceIssue[];
    
    /** Status timestamp */
    readonly timestamp: Date;
}

// Financial Metrics

export interface FinancialMetrics {
    readonly revenue: MetricValue;
    readonly profitMargin: MetricValue;
    readonly cashFlow: MetricValue;
    readonly returnOnInvestment: MetricValue;
    readonly costEfficiency: MetricValue;
    readonly financialStability: MetricValue;
    readonly liquidityRatio: MetricValue;
    readonly debtServiceCoverage: MetricValue;
}

// Operational Metrics

export interface OperationalMetrics {
    readonly systemUptime: MetricValue;
    readonly responseTime: MetricValue;
    readonly throughput: MetricValue;
    readonly errorRate: MetricValue;
    readonly customerSatisfaction: MetricValue;
    readonly processEfficiency: MetricValue;
    readonly resourceUtilization: MetricValue;
    readonly serviceQuality: MetricValue;
}

// Strategic Metrics

export interface StrategicMetrics {
    readonly marketPosition: MetricValue;
    readonly competitiveAdvantage: MetricValue;
    readonly innovationIndex: MetricValue;
    readonly brandValue: MetricValue;
    readonly strategicAlignment: MetricValue;
    readonly futureReadiness: MetricValue;
    readonly partnershipValue: MetricValue;
    readonly scalabilityIndex: MetricValue;
}

// Research Metrics

export interface ResearchMetrics {
    readonly researchProductivity: MetricValue;
    readonly innovationPipeline: MetricValue;
    readonly intellectualProperty: MetricValue;
    readonly collaborationIndex: MetricValue;
    readonly breakthroughPotential: MetricValue;
    readonly researchQuality: MetricValue;
    readonly technologyTransfer: MetricValue;
    readonly scientificImpact: MetricValue;
}

// Security Metrics

export interface SecurityMetrics {
    readonly securityPosture: MetricValue;
    readonly threatDetection: MetricValue;
    readonly incidentResponse: MetricValue;
    readonly vulnerabilityManagement: MetricValue;
    readonly accessControl: MetricValue;
    readonly dataProtection: MetricValue;
    readonly businessContinuity: MetricValue;
    readonly securityTraining: MetricValue;
}

// Governance Metrics

export interface GovernanceMetrics {
    readonly boardEffectiveness: MetricValue;
    readonly decisionQuality: MetricValue;
    readonly stakeholderEngagement: MetricValue;
    readonly transparencyIndex: MetricValue;
    readonly accountabilityScore: MetricValue;
    readonly ethicsCompliance: MetricValue;
    readonly diversityIndex: MetricValue;
    readonly governanceMaturity: MetricValue;
}

// Risk Assessment Types

export enum RiskCategory {
    FINANCIAL = 'FINANCIAL',
    OPERATIONAL = 'OPERATIONAL',
    STRATEGIC = 'STRATEGIC',
    REGULATORY = 'REGULATORY',
    TECHNOLOGY = 'TECHNOLOGY',
    SECURITY = 'SECURITY',
    REPUTATIONAL = 'REPUTATIONAL',
    ENVIRONMENTAL = 'ENVIRONMENTAL',
    MARKET = 'MARKET',
    LIQUIDITY = 'LIQUIDITY'
}

export interface RiskMetric {
    readonly category: RiskCategory;
    readonly score: number;
    readonly impact: number;
    readonly probability: number;
    readonly velocity: number;
    readonly trend: number;
    readonly description: string;
}

export interface RiskTrend {
    readonly category: RiskCategory;
    readonly direction: 'INCREASING' | 'DECREASING' | 'STABLE';
    readonly rate: number;
    readonly projection: number[];
    readonly timeframe: number;
}

export interface RiskMitigation {
    readonly riskCategory: RiskCategory;
    readonly strategy: string;
    readonly effectiveness: number;
    readonly cost: number;
    readonly timeline: number;
    readonly responsible: DirectorRole;
}

export interface RiskThreshold {
    readonly category: RiskCategory;
    readonly level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    readonly threshold: number;
    readonly action: string;
    readonly escalation: DirectorRole[];
}

// Compliance Types

export enum RegulatoryDomain {
    FINANCIAL_SERVICES = 'FINANCIAL_SERVICES',
    DATA_PROTECTION = 'DATA_PROTECTION',
    SECURITIES = 'SECURITIES',
    EMPLOYMENT = 'EMPLOYMENT',
    ENVIRONMENTAL = 'ENVIRONMENTAL',
    INTERNATIONAL_TRADE = 'INTERNATIONAL_TRADE',
    INTELLECTUAL_PROPERTY = 'INTELLECTUAL_PROPERTY',
    HEALTHCARE = 'HEALTHCARE',
    CYBERSECURITY = 'CYBERSECURITY'
}

export enum PolicyDomain {
    CODE_OF_CONDUCT = 'CODE_OF_CONDUCT',
    INFORMATION_SECURITY = 'INFORMATION_SECURITY',
    HUMAN_RESOURCES = 'HUMAN_RESOURCES',
    FINANCIAL_MANAGEMENT = 'FINANCIAL_MANAGEMENT',
    RESEARCH_ETHICS = 'RESEARCH_ETHICS',
    VENDOR_MANAGEMENT = 'VENDOR_MANAGEMENT',
    BUSINESS_CONTINUITY = 'BUSINESS_CONTINUITY',
    QUALITY_ASSURANCE = 'QUALITY_ASSURANCE'
}

export interface ComplianceMetric {
    readonly domain: RegulatoryDomain | PolicyDomain;
    readonly score: number;
    readonly requirements: ComplianceRequirement[];
    readonly gaps: ComplianceGap[];
    readonly lastAudit: Date;
    readonly nextAudit: Date;
}

export interface ConstitutionalCompliance {
    readonly governanceScore: number;
    readonly votingCompliance: number;
    readonly consensusHealth: number;
    readonly constitutionalAdherence: number;
    readonly blockchainIntegrity: number;
}

export interface ComplianceRequirement {
    readonly requirementId: string;
    readonly description: string;
    readonly status: 'COMPLIANT' | 'NON_COMPLIANT' | 'PARTIAL' | 'PENDING';
    readonly evidence: string[];
    readonly responsible: DirectorRole;
}

export interface ComplianceGap {
    readonly gapId: string;
    readonly description: string;
    readonly severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    readonly remediation: string;
    readonly timeline: number;
    readonly responsible: DirectorRole;
}

export interface AuditRecord {
    readonly auditId: string;
    readonly type: 'INTERNAL' | 'EXTERNAL' | 'REGULATORY';
    readonly scope: string[];
    readonly findings: AuditFinding[];
    readonly recommendations: string[];
    readonly auditor: string;
    readonly date: Date;
}

export interface AuditFinding {
    readonly findingId: string;
    readonly severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    readonly description: string;
    readonly recommendation: string;
    readonly status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED';
}

export interface ComplianceIssue {
    readonly issueId: string;
    readonly domain: RegulatoryDomain | PolicyDomain;
    readonly severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    readonly description: string;
    readonly impact: string;
    readonly remediation: RemediationPlan;
    readonly status: 'IDENTIFIED' | 'IN_PROGRESS' | 'RESOLVED';
}

export interface RemediationPlan {
    readonly actions: RemediationAction[];
    readonly timeline: number;
    readonly cost: number;
    readonly responsible: DirectorRole;
    readonly success: SuccessCriteria[];
}

export interface RemediationAction {
    readonly actionId: string;
    readonly description: string;
    readonly priority: number;
    readonly timeline: number;
    readonly dependencies: string[];
}

export interface SuccessCriteria {
    readonly criterion: string;
    readonly metric: string;
    readonly target: number;
    readonly measurement: string;
}

// Supporting Metric Types

// Advanced Governance Metrics

/**
 * Board Effectiveness Metrics
 * Specialized metrics for board performance assessment
 */
export interface BoardEffectivenessMetrics {
    readonly decisionSpeed: MetricValue;
    readonly decisionQuality: MetricValue;
    readonly stakeholderAlignment: MetricValue;
    readonly riskOversight: MetricValue;
    readonly strategicGuidance: MetricValue;
    readonly complianceOversight: MetricValue;
    readonly crisisResponse: MetricValue;
    readonly innovationSupport: MetricValue;
}

/**
 * Director Performance Metrics
 * Individual director contribution assessment
 */
export interface DirectorPerformanceMetrics {
    readonly director: DirectorRole;
    readonly attendance: MetricValue;
    readonly contribution: MetricValue;
    readonly expertise: MetricValue;
    readonly independence: MetricValue;
    readonly preparation: MetricValue;
    readonly stakeholderValue: MetricValue;
    readonly ethicalStandards: MetricValue;
    readonly continuousLearning: MetricValue;
}

/**
 * Stakeholder Value Metrics
 * Multi-stakeholder value creation measurement
 */
export interface StakeholderValueMetrics {
    readonly shareholders: MetricValue;
    readonly employees: MetricValue;
    readonly customers: MetricValue;
    readonly partners: MetricValue;
    readonly community: MetricValue;
    readonly environment: MetricValue;
    readonly regulators: MetricValue;
    readonly overall: MetricValue;
}

/**
 * Innovation Metrics
 * Research and development effectiveness
 */
export interface InnovationMetrics {
    readonly researchInvestment: MetricValue;
    readonly patentPortfolio: MetricValue;
    readonly timeToMarket: MetricValue;
    readonly innovationRevenue: MetricValue;
    readonly collaborationIndex: MetricValue;
    readonly technologyReadiness: MetricValue;
    readonly disruptivePotential: MetricValue;
    readonly knowledgeTransfer: MetricValue;
}

/**
 * Digital Transformation Metrics
 * Technology adoption and modernization
 */
export interface DigitalTransformationMetrics {
    readonly digitalizationIndex: MetricValue;
    readonly automationLevel: MetricValue;
    readonly dataMaturity: MetricValue;
    readonly aiIntegration: MetricValue;
    readonly cybersecurityPosture: MetricValue;
    readonly digitalSkills: MetricValue;
    readonly customerDigitalExperience: MetricValue;
    readonly operationalAgility: MetricValue;
}

/**
 * Sustainability Metrics
 * Environmental, social, and governance (ESG) performance
 */
export interface SustainabilityMetrics {
    readonly environmental: EnvironmentalMetrics;
    readonly social: SocialMetrics;
    readonly governance: ESGGovernanceMetrics;
    readonly overall: MetricValue;
}

export interface EnvironmentalMetrics {
    readonly carbonFootprint: MetricValue;
    readonly energyEfficiency: MetricValue;
    readonly wasteReduction: MetricValue;
    readonly resourceConservation: MetricValue;
    readonly renewableEnergy: MetricValue;
}

export interface SocialMetrics {
    readonly employeeWellbeing: MetricValue;
    readonly diversityInclusion: MetricValue;
    readonly communityImpact: MetricValue;
    readonly ethicalSupplyChain: MetricValue;
    readonly socialInnovation: MetricValue;
}

export interface ESGGovernanceMetrics {
    readonly boardDiversity: MetricValue;
    readonly executiveCompensation: MetricValue;
    readonly transparencyIndex: MetricValue;
    readonly stakeholderEngagement: MetricValue;
    readonly ethicsTraining: MetricValue;
}

/**
 * Crisis Management Metrics
 * Emergency response and business continuity
 */
export interface CrisisManagementMetrics {
    readonly preparedness: MetricValue;
    readonly responseTime: MetricValue;
    readonly coordinationEffectiveness: MetricValue;
    readonly stakeholderCommunication: MetricValue;
    readonly businessContinuity: MetricValue;
    readonly recoveryTime: MetricValue;
    readonly lessonsLearned: MetricValue;
    readonly resilienceImprovement: MetricValue;
}

// Risk Management Supporting Types

export interface RiskManagementResult {
    readonly status: 'SUCCESS' | 'WARNING' | 'FAILURE';
    readonly risksAssessed: number;
    readonly risksIdentified: number;
    readonly risksMitigated: number;
    readonly overallRiskScore: number;
    readonly recommendations: string[];
}

export interface ComplianceVerificationResult {
    readonly status: 'COMPLIANT' | 'NON_COMPLIANT' | 'PARTIAL';
    readonly score: number;
    readonly verifiedRequirements: number;
    readonly totalRequirements: number;
    readonly issues: ComplianceIssue[];
    readonly recommendations: string[];
}

export interface DecisionSupport {
    readonly analysisResult: string;
    readonly recommendations: string[];
    readonly risks: string[];
    readonly opportunities: string[];
    readonly confidence: number;
    readonly alternatives: DecisionAlternative[];
}

export interface DecisionAlternative {
    readonly option: string;
    readonly pros: string[];
    readonly cons: string[];
    readonly riskLevel: number;
    readonly expectedValue: number;
}

export interface ResponseCoordination {
    readonly coordinationLevel: 'LOW' | 'MEDIUM' | 'HIGH';
    readonly responseTime: number;
    readonly resourceAllocation: ResourceAllocation[];
    readonly communicationPlan: CommunicationPlan;
    readonly escalationPath: EscalationPath[];
}

export interface ResourceAllocation {
    readonly resource: string;
    readonly allocated: number;
    readonly available: number;
    readonly priority: number;
}

export interface CommunicationPlan {
    readonly stakeholders: string[];
    readonly channels: string[];
    readonly frequency: string;
    readonly messaging: string[];
}

export interface EscalationPath {
    readonly level: number;
    readonly trigger: string;
    readonly authority: DirectorRole;
    readonly timeline: number;
}

export interface ProtocolImplementation {
    readonly protocolId: string;
    readonly implementationStatus: 'SUCCESS' | 'PARTIAL' | 'FAILURE';
    readonly changesApplied: number;
    readonly effectiveness: number;
    readonly feedback: string[];
    readonly nextReview: Date;
}

export interface AdaptationContext {
    readonly trigger: string;
    readonly magnitude: number;
    readonly affectedSystems: string[];
    readonly requiredChanges: string[];
    readonly timeframe: number;
}

export interface EmergencyContext {
    readonly emergencyType: string;
    readonly severity: number;
    readonly scope: string[];
    readonly timeline: number;
    readonly resources: string[];
}

export interface DecisionContext {
    readonly decision: string;
    readonly urgency: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    readonly stakeholders: string[];
    readonly constraints: string[];
    readonly alternatives: string[];
    readonly timeframe: number;
}
