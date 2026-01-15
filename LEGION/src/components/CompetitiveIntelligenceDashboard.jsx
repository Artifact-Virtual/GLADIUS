import React, { useState, useEffect } from 'react';

const CompetitiveIntelligenceDashboard = ({ onComponentUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeView, setActiveView] = useState('overview');
  const [selectedCompetitor, setSelectedCompetitor] = useState(null);
  const [timeRange, setTimeRange] = useState('6months');
  const [refreshInterval, setRefreshInterval] = useState(300000); // 5 minutes
  const [data, setData] = useState({
    overview: {},
    competitors: [],
    marketPositioning: {},
    pricingIntelligence: [],
    productComparison: [],
    socialSentiment: {},
    competitiveAlerts: [],
    swotAnalysis: {}
  });

  useEffect(() => {
    const loadCompetitiveData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Simulate API calls to competitive intelligence services
        const [
          overviewResponse,
          competitorsResponse,
          positioningResponse,
          pricingResponse,
          productResponse,
          sentimentResponse,
          alertsResponse,
          swotResponse
        ] = await Promise.allSettled([
          fetch('/api/enterprise/competitive-overview'),
          fetch('/api/enterprise/competitor-profiles'),
          fetch('/api/enterprise/market-positioning'),
          fetch('/api/enterprise/pricing-intelligence'),
          fetch('/api/enterprise/product-comparison'),
          fetch('/api/enterprise/social-sentiment'),
          fetch('/api/enterprise/competitive-alerts'),
          fetch('/api/enterprise/swot-analysis')
        ]);

        // Process responses or use mock data
        const mockData = {
          overview: {
            totalCompetitors: 47,
            directCompetitors: 12,
            indirectCompetitors: 35,
            marketLeaders: 5,
            emergingThreat: 8,
            marketShare: 0.8, // Our market share
            competitiveStrength: 7.2, // Out of 10
            threatLevel: 4.5, // Out of 10
            opportunityScore: 8.1, // Out of 10
            lastUpdated: new Date().toISOString(),
            competitiveAdvantages: [
              'Specialized AI expertise',
              'Agile delivery methodology',
              'Competitive pricing structure',
              'Strong customer satisfaction',
              'Rapid innovation cycles'
            ],
            keyWeaknesses: [
              'Limited brand recognition',
              'Smaller team size',
              'Limited geographic presence',
              'Fewer enterprise references'
            ]
          },
          competitors: [
            {
              id: 'comp_accenture',
              name: 'Accenture AI',
              type: 'direct',
              tier: 'leader',
              marketShare: 12.5,
              revenue: 2800000000, // USD
              employees: 15000,
              founded: '2017',
              headquarters: 'Dublin, Ireland',
              globalPresence: 45,
              competitiveStrength: 9.2,
              threatLevel: 8.7,
              recentGrowth: 18.5, // Percent
              logoUrl: '/assets/competitors/accenture.png',
              description: 'Global professional services company with comprehensive AI and technology consulting capabilities.',
              keyStrengths: [
                'Massive global scale and reach',
                'Established enterprise relationships',
                'Comprehensive service portfolio',
                'Strong brand recognition and trust',
                'Deep industry expertise across verticals'
              ],
              keyWeaknesses: [
                'High pricing and overhead costs',
                'Slow decision-making processes',
                'Complex engagement structures',
                'Limited innovation agility',
                'Generic solutions approach'
              ],
              serviceOfferings: [
                'AI Strategy and Consulting',
                'Machine Learning Implementation',
                'Process Automation',
                'Data Analytics and Insights',
                'AI Governance and Ethics'
              ],
              targetMarkets: [
                'Large Enterprise (Fortune 500)',
                'Government and Public Sector',
                'Financial Services',
                'Healthcare and Life Sciences',
                'Manufacturing and Industrial'
              ],
              pricingStrategy: 'Premium pricing with value-based models',
              recentNews: [
                {
                  date: '2024-10-10',
                  title: 'Acquires AI startup for $180M to enhance NLP capabilities',
                  impact: 'high',
                  category: 'acquisition'
                },
                {
                  date: '2024-10-05',
                  title: 'Announces 200+ new AI consultants across European markets',
                  impact: 'medium',
                  category: 'expansion'
                },
                {
                  date: '2024-09-28',
                  title: 'Partners with Microsoft for Azure AI implementation services',
                  impact: 'high',
                  category: 'partnership'
                }
              ],
              socialMetrics: {
                linkedinFollowers: 2400000,
                twitterFollowers: 890000,
                sentimentScore: 0.72, // -1 to 1
                brandMentions: 15600,
                thoughtLeadershipScore: 8.9
              },
              financialMetrics: {
                quarterlyGrowth: 18.5,
                profitMargin: 15.2,
                rdInvestment: 4.8, // Percent of revenue
                marketCapitalization: 180000000000
              }
            },
            {
              id: 'comp_ibm',
              name: 'IBM Consulting',
              type: 'direct',
              tier: 'challenger',
              marketShare: 8.3,
              revenue: 1200000000,
              employees: 8500,
              founded: '2021', // Watson consulting division
              headquarters: 'Armonk, NY, USA',
              globalPresence: 38,
              competitiveStrength: 7.8,
              threatLevel: 6.2,
              recentGrowth: 12.3,
              logoUrl: '/assets/competitors/ibm.png',
              description: 'Technology consulting division focused on AI and hybrid cloud solutions with Watson platform integration.',
              keyStrengths: [
                'Watson AI platform integration',
                'Strong R&D capabilities',
                'Industry-specific solutions',
                'Hybrid cloud expertise',
                'Established technology partnerships'
              ],
              keyWeaknesses: [
                'Legacy technology constraints',
                'Market perception challenges',
                'Slower innovation cycles',
                'Higher overhead costs',
                'Complex product portfolio'
              ],
              serviceOfferings: [
                'Watson AI Integration',
                'Hybrid Cloud AI Solutions',
                'Industry-Specific AI Applications',
                'AI Governance and Risk Management',
                'Cognitive Process Automation'
              ],
              targetMarkets: [
                'Large Enterprise',
                'Financial Services',
                'Healthcare',
                'Manufacturing',
                'Government'
              ],
              pricingStrategy: 'Competitive pricing with platform bundling',
              recentNews: [
                {
                  date: '2024-10-12',
                  title: 'Invests $1B in AI research and development initiatives',
                  impact: 'high',
                  category: 'investment'
                },
                {
                  date: '2024-10-01',
                  title: 'Launches watsonx enterprise AI platform for consulting',
                  impact: 'high',
                  category: 'product_launch'
                },
                {
                  date: '2024-09-20',
                  title: 'Announces 40,000 job cuts to focus on AI and cloud',
                  impact: 'medium',
                  category: 'restructuring'
                }
              ],
              socialMetrics: {
                linkedinFollowers: 1800000,
                twitterFollowers: 645000,
                sentimentScore: 0.58,
                brandMentions: 12300,
                thoughtLeadershipScore: 7.6
              },
              financialMetrics: {
                quarterlyGrowth: 12.3,
                profitMargin: 12.8,
                rdInvestment: 6.2,
                marketCapitalization: 120000000000
              }
            },
            {
              id: 'comp_deloitte',
              name: 'Deloitte AI Institute',
              type: 'direct',
              tier: 'challenger',
              marketShare: 6.7,
              revenue: 950000000,
              employees: 5200,
              founded: '2018',
              headquarters: 'London, UK',
              globalPresence: 42,
              competitiveStrength: 8.1,
              threatLevel: 7.3,
              recentGrowth: 22.8,
              logoUrl: '/assets/competitors/deloitte.png',
              description: 'Professional services firm with dedicated AI practice focusing on ethics, governance, and enterprise transformation.',
              keyStrengths: [
                'Strong AI ethics and governance expertise',
                'Comprehensive consulting methodology',
                'Industry thought leadership',
                'Global delivery capabilities',
                'Strong C-suite relationships'
              ],
              keyWeaknesses: [
                'High pricing structure',
                'Complex engagement processes',
                'Limited technical depth in some areas',
                'Slower execution compared to boutiques',
                'Generic solution approaches'
              ],
              serviceOfferings: [
                'AI Ethics and Governance',
                'Enterprise AI Transformation',
                'AI Risk Management',
                'Responsible AI Implementation',
                'AI Strategy and Roadmapping'
              ],
              targetMarkets: [
                'Fortune 500 Enterprise',
                'Financial Services',
                'Government and Public Sector',
                'Healthcare',
                'Energy and Resources'
              ],
              pricingStrategy: 'Premium consulting rates with outcome-based options',
              recentNews: [
                {
                  date: '2024-10-08',
                  title: 'Launches AI Ethics Center of Excellence',
                  impact: 'medium',
                  category: 'service_expansion'
                },
                {
                  date: '2024-09-25',
                  title: 'Partners with leading universities for AI research',
                  impact: 'low',
                  category: 'partnership'
                },
                {
                  date: '2024-09-15',
                  title: 'Acquires boutique AI consulting firm in Asia Pacific',
                  impact: 'medium',
                  category: 'acquisition'
                }
              ],
              socialMetrics: {
                linkedinFollowers: 1200000,
                twitterFollowers: 423000,
                sentimentScore: 0.69,
                brandMentions: 9800,
                thoughtLeadershipScore: 8.4
              },
              financialMetrics: {
                quarterlyGrowth: 22.8,
                profitMargin: 18.5,
                rdInvestment: 3.2,
                marketCapitalization: 45000000000
              }
            },
            {
              id: 'comp_boutiques',
              name: 'Emerging AI Boutiques',
              type: 'indirect',
              tier: 'emerging',
              marketShare: 15.2, // Collective
              revenue: 2100000000, // Collective
              employees: 12500, // Collective
              founded: '2020-2024',
              headquarters: 'Various Global',
              globalPresence: 25,
              competitiveStrength: 6.8,
              threatLevel: 7.9,
              recentGrowth: 45.2,
              logoUrl: '/assets/competitors/boutiques.png',
              description: 'Collective of specialized AI consulting boutiques showing rapid growth and market disruption.',
              keyStrengths: [
                'Specialized deep expertise',
                'Agile delivery methodologies',
                'Competitive pricing strategies',
                'Innovation and cutting-edge approaches',
                'Focused market positioning'
              ],
              keyWeaknesses: [
                'Limited scale capabilities',
                'Resource and capacity constraints',
                'Brand recognition challenges',
                'Inconsistent service quality',
                'Financial stability concerns'
              ],
              serviceOfferings: [
                'Niche AI Specializations',
                'Rapid Prototyping and MVP Development',
                'Technical AI Implementation',
                'Industry-Specific Solutions',
                'AI Training and Upskilling'
              ],
              targetMarkets: [
                'Mid-Market Companies',
                'Startups and Scale-ups',
                'Technology Companies',
                'Digital-Native Businesses',
                'Emerging Market Enterprises'
              ],
              pricingStrategy: 'Competitive pricing with flexible engagement models',
              recentNews: [
                {
                  date: '2024-10-14',
                  title: 'Collective funding reaches $2.3B in Q3 2024',
                  impact: 'high',
                  category: 'funding'
                },
                {
                  date: '2024-10-07',
                  title: 'Market share gains accelerate in mid-market segment',
                  impact: 'high',
                  category: 'market_growth'
                },
                {
                  date: '2024-09-30',
                  title: 'Increased consolidation activity observed',
                  impact: 'medium',
                  category: 'consolidation'
                }
              ],
              socialMetrics: {
                linkedinFollowers: 450000, // Average
                twitterFollowers: 180000, // Average
                sentimentScore: 0.75,
                brandMentions: 8900,
                thoughtLeadershipScore: 7.1
              },
              financialMetrics: {
                quarterlyGrowth: 45.2,
                profitMargin: 22.3, // Higher due to lower overhead
                rdInvestment: 8.5,
                marketCapitalization: 8500000000 // Collective estimated
              }
            }
          ],
          marketPositioning: {
            competitiveMatrix: {
              axes: {
                x: 'Market Reach',
                y: 'Innovation Capability'
              },
              positions: [
                { competitor: 'Accenture AI', x: 9.5, y: 6.8, size: 12.5 },
                { competitor: 'IBM Consulting', x: 8.2, y: 7.1, size: 8.3 },
                { competitor: 'Deloitte AI', x: 8.8, y: 7.9, size: 6.7 },
                { competitor: 'Our Company', x: 4.2, y: 8.9, size: 0.8 },
                { competitor: 'Boutique Average', x: 3.8, y: 8.5, size: 2.1 }
              ]
            },
            marketQuadrants: {
              leaders: ['Accenture AI', 'Deloitte AI'],
              challengers: ['IBM Consulting'],
              visionaries: ['Our Company', 'Top Boutiques'],
              niche_players: ['Emerging Boutiques']
            },
            competitiveGaps: [
              {
                area: 'Global Scale',
                gap: 'Large',
                impact: 'High',
                timeToClose: '24-36 months',
                strategy: 'Strategic partnerships and selective acquisitions'
              },
              {
                area: 'Brand Recognition',
                gap: 'Medium',
                impact: 'Medium',
                timeToClose: '12-18 months',
                strategy: 'Thought leadership and case study development'
              },
              {
                area: 'Enterprise References',
                gap: 'Medium',
                impact: 'High',
                timeToClose: '6-12 months',
                strategy: 'Focus on marquee client acquisitions'
              }
            ]
          },
          pricingIntelligence: [
            {
              competitor: 'Accenture AI',
              pricingModel: 'Time and Materials + Value-based',
              hourlyRates: {
                senior_consultant: 350,
                principal: 500,
                partner: 750
              },
              projectRates: {
                small_project: 75000, // <3 months
                medium_project: 250000, // 3-6 months
                large_project: 750000, // 6+ months
              },
              discountStrategy: 'Volume discounts for multi-year engagements',
              recentChanges: [
                {
                  date: '2024-09-15',
                  change: 'Increased rates by 8% across all levels',
                  reason: 'Market demand and inflation adjustment'
                }
              ]
            },
            {
              competitor: 'IBM Consulting',
              pricingModel: 'Platform bundling + Professional services',
              hourlyRates: {
                senior_consultant: 275,
                principal: 425,
                partner: 650
              },
              projectRates: {
                small_project: 65000,
                medium_project: 200000,
                large_project: 600000
              },
              discountStrategy: 'Watson platform licensing discounts',
              recentChanges: [
                {
                  date: '2024-10-01',
                  change: 'Introduced watsonx bundling discounts',
                  reason: 'Platform adoption incentive'
                }
              ]
            },
            {
              competitor: 'Our Company',
              pricingModel: 'Competitive value-based pricing',
              hourlyRates: {
                senior_consultant: 225,
                principal: 325,
                partner: 475
              },
              projectRates: {
                small_project: 45000,
                medium_project: 135000,
                large_project: 385000
              },
              discountStrategy: 'Performance-based pricing with success fees',
              competitiveAdvantage: '25-35% cost advantage with faster delivery'
            }
          ],
          productComparison: {
            categories: [
              {
                category: 'AI Strategy Consulting',
                ourRating: 8.5,
                competitors: [
                  { name: 'Accenture AI', rating: 9.2, marketLeader: true },
                  { name: 'Deloitte AI', rating: 8.8 },
                  { name: 'IBM Consulting', rating: 7.9 }
                ],
                differentiators: [
                  'Rapid strategy development (2-3 weeks vs 6-8 weeks)',
                  'Industry-specific AI use case library',
                  'ROI modeling and business case development'
                ]
              },
              {
                category: 'AI Implementation Services',
                ourRating: 9.1,
                competitors: [
                  { name: 'Accenture AI', rating: 8.7 },
                  { name: 'IBM Consulting', rating: 8.9, marketLeader: true },
                  { name: 'Boutique Average', rating: 8.3 }
                ],
                differentiators: [
                  'Faster time-to-value (4-6 weeks typical)',
                  'Agile development methodology',
                  'Comprehensive post-implementation support'
                ]
              },
              {
                category: 'AI Governance & Compliance',
                ourRating: 7.8,
                competitors: [
                  { name: 'Deloitte AI', rating: 9.5, marketLeader: true },
                  { name: 'Accenture AI', rating: 8.9 },
                  { name: 'IBM Consulting', rating: 8.2 }
                ],
                differentiators: [
                  'Pragmatic compliance approach',
                  'Automated governance tools',
                  'Industry-specific compliance templates'
                ]
              }
            ]
          },
          socialSentiment: {
            overallSentiment: 0.73, // Our sentiment
            competitorComparison: [
              { competitor: 'Accenture AI', sentiment: 0.72, trend: 'stable' },
              { competitor: 'Deloitte AI', sentiment: 0.69, trend: 'improving' },
              { competitor: 'IBM Consulting', sentiment: 0.58, trend: 'declining' },
              { competitor: 'Boutique Average', sentiment: 0.75, trend: 'improving' }
            ],
            keyMentions: {
              positive: [
                'Exceptional technical expertise and implementation speed',
                'Great value for money compared to big consulting firms',
                'Responsive team and excellent customer service'
              ],
              negative: [
                'Limited brand recognition in enterprise space',
                'Smaller team size concerns for large projects',
                'Need more case studies and references'
              ]
            },
            brandHealth: {
              awareness: 23, // Percent
              consideration: 67, // Among aware prospects
              preference: 78, // Among those who consider
              loyalty: 89 // Existing client retention
            }
          },
          competitiveAlerts: [
            {
              id: 'alert_001',
              priority: 'high',
              type: 'pricing_change',
              competitor: 'IBM Consulting',
              title: 'IBM reduces watsonx bundling prices by 25%',
              description: 'IBM announced significant price reductions for watsonx platform bundled with consulting services to accelerate market adoption.',
              impact: 'May pressure our pricing in platform-adjacent services',
              recommendedAction: 'Review our platform partnership strategies and consider competitive pricing adjustments',
              detectedAt: '2024-10-15T09:30:00Z',
              source: 'Press release monitoring',
              confidence: 94
            },
            {
              id: 'alert_002',
              priority: 'medium',
              type: 'market_entry',
              competitor: 'Google Cloud',
              title: 'Google announces AI consulting practice expansion',
              description: 'Google Cloud is expanding its professional services team with 300+ AI consultants across North America and Europe.',
              impact: 'New competitor entry in our primary markets',
              recommendedAction: 'Monitor their service offerings and pricing strategy, consider differentiation opportunities',
              detectedAt: '2024-10-14T14:20:00Z',
              source: 'Industry news monitoring',
              confidence: 87
            },
            {
              id: 'alert_003',
              priority: 'high',
              type: 'acquisition',
              competitor: 'Accenture AI',
              title: 'Accenture acquires specialized healthcare AI consultancy',
              description: 'Accenture acquired a 120-person healthcare AI consultancy to strengthen their vertical expertise.',
              impact: 'Increased competitive threat in healthcare vertical',
              recommendedAction: 'Accelerate our healthcare AI capabilities development and market positioning',
              detectedAt: '2024-10-13T11:45:00Z',
              source: 'M&A monitoring',
              confidence: 96
            }
          ],
          swotAnalysis: {
            strengths: [
              {
                factor: 'Technical Expertise',
                rating: 9.2,
                description: 'Deep AI/ML technical capabilities with proven implementation success',
                evidence: ['95% project success rate', '4.8/5 technical satisfaction scores', '67% faster implementation']
              },
              {
                factor: 'Agile Delivery',
                rating: 8.9,
                description: 'Rapid, iterative delivery methodology with faster time-to-value',
                evidence: ['6-week average delivery vs 12-week industry', 'Agile methodology adoption', 'Continuous client feedback loops']
              },
              {
                factor: 'Cost Competitiveness',
                rating: 8.7,
                description: '25-35% cost advantage over large consulting firms',
                evidence: ['Hourly rate comparison analysis', 'Total project cost benchmarking', 'Value-for-money client feedback']
              },
              {
                factor: 'Customer Satisfaction',
                rating: 8.8,
                description: 'High client satisfaction and retention rates',
                evidence: ['89% client retention', '4.7/5 satisfaction scores', '78% referral rate']
              }
            ],
            weaknesses: [
              {
                factor: 'Brand Recognition',
                rating: 3.2,
                description: 'Limited brand awareness in enterprise market',
                impact: 'Difficulty in initial client acquisition and premium pricing',
                mitigation: 'Thought leadership, case studies, strategic partnerships'
              },
              {
                factor: 'Scale Limitations',
                rating: 4.1,
                description: 'Limited team size for large enterprise engagements',
                impact: 'Cannot compete for largest deals, capacity constraints',
                mitigation: 'Strategic hiring, partner network development'
              },
              {
                factor: 'Geographic Presence',
                rating: 3.8,
                description: 'Limited global presence compared to major competitors',
                impact: 'Cannot serve multinational clients effectively',
                mitigation: 'Remote delivery capabilities, regional partnerships'
              }
            ],
            opportunities: [
              {
                factor: 'Market Growth',
                potential: 9.1,
                description: 'AI consulting market growing at 31% CAGR',
                timeframe: 'Immediate',
                strategy: 'Aggressive market expansion and service portfolio growth'
              },
              {
                factor: 'Boutique Preference',
                potential: 8.4,
                description: 'Increasing preference for specialized boutique providers',
                timeframe: '6-12 months',
                strategy: 'Capitalize on agility and specialization advantages'
              },
              {
                factor: 'Compliance Focus',
                potential: 8.7,
                description: 'Growing demand for AI governance and compliance',
                timeframe: '3-6 months',
                strategy: 'Develop compliance-focused service offerings'
              }
            ],
            threats: [
              {
                factor: 'Big Tech Entry',
                severity: 7.8,
                description: 'Major tech companies expanding consulting services',
                timeframe: '12-18 months',
                mitigation: 'Focus on differentiated expertise and mid-market positioning'
              },
              {
                factor: 'Price Competition',
                severity: 6.9,
                description: 'Increasing price pressure from emerging competitors',
                timeframe: '6-12 months',
                mitigation: 'Value-based pricing, outcome guarantees, premium positioning'
              },
              {
                factor: 'Talent War',
                severity: 7.5,
                description: 'Intense competition for AI talent driving up costs',
                timeframe: 'Immediate',
                mitigation: 'Employee retention programs, remote work flexibility, equity incentives'
              }
            ]
          }
        };

        setData(mockData);
      } catch (err) {
        console.error('Error loading competitive data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadCompetitiveData();
    const interval = setInterval(loadCompetitiveData, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  const handleComponentUpdate = (component, updateData) => {
    if (onComponentUpdate) {
      onComponentUpdate(component, updateData);
    }
  };

  const formatCurrency = (amount) => {
    if (amount >= 1000000000) {
      return `$${(amount / 1000000000).toFixed(1)}B`;
    } else if (amount >= 1000000) {
      return `$${(amount / 1000000).toFixed(0)}M`;
    } else if (amount >= 1000) {
      return `$${(amount / 1000).toFixed(0)}K`;
    }
    return `$${amount}`;
  };

  const formatPercentage = (value) => {
    return `${value.toFixed(1)}%`;
  };

  const getTierColor = (tier) => {
    switch (tier) {
      case 'leader': return '#10b981';
      case 'challenger': return '#f59e0b';
      case 'visionary': return '#3b82f6';
      case 'emerging': return '#8b5cf6';
      default: return '#6b7280';
    }
  };

  const getThreatColor = (level) => {
    if (level >= 8) return '#ef4444';
    if (level >= 6) return '#f59e0b';
    if (level >= 4) return '#3b82f6';
    return '#10b981';
  };

  const getSentimentColor = (sentiment) => {
    if (sentiment >= 0.7) return '#10b981';
    if (sentiment >= 0.5) return '#f59e0b';
    return '#ef4444';
  };

  if (loading) {
    return (
      <div className="competitive-intelligence loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading competitive intelligence...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="competitive-intelligence error">
        <div className="error-message">
          <h3>Error Loading Competitive Intelligence</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="competitive-intelligence-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-content">
          <h1>Competitive Intelligence Dashboard</h1>
          <p>Real-time competitive monitoring, analysis, and strategic insights</p>
        </div>
        <div className="header-controls">
          <select 
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-range-selector"
          >
            <option value="3months">3 Months</option>
            <option value="6months">6 Months</option>
            <option value="12months">12 Months</option>
            <option value="24months">24 Months</option>
          </select>
          <button className="refresh-button" onClick={() => window.location.reload()}>
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Navigation */}
      <div className="intelligence-nav">
        {[
          { id: 'overview', label: 'Overview', icon: '📊' },
          { id: 'competitors', label: 'Competitor Profiles', icon: '🏢' },
          { id: 'positioning', label: 'Market Positioning', icon: '📈' },
          { id: 'pricing', label: 'Pricing Intelligence', icon: '💰' },
          { id: 'products', label: 'Product Comparison', icon: '⚖️' },
          { id: 'sentiment', label: 'Social Sentiment', icon: '📱' },
          { id: 'alerts', label: 'Competitive Alerts', icon: '🚨' },
          { id: 'swot', label: 'SWOT Analysis', icon: '🎯' }
        ].map(section => (
          <button
            key={section.id}
            className={`nav-button ${activeView === section.id ? 'active' : ''}`}
            onClick={() => setActiveView(section.id)}
          >
            <span className="nav-icon">{section.icon}</span>
            <span className="nav-label">{section.label}</span>
          </button>
        ))}
      </div>

      {/* Overview Section */}
      {activeView === 'overview' && (
        <div className="overview-section">
          <div className="overview-metrics">
            <div className="metric-card">
              <div className="metric-icon">🏢</div>
              <div className="metric-content">
                <div className="metric-value">{data.overview.totalCompetitors}</div>
                <div className="metric-label">Total Competitors</div>
                <div className="metric-breakdown">
                  <span>{data.overview.directCompetitors} direct</span>
                  <span>•</span>
                  <span>{data.overview.indirectCompetitors} indirect</span>
                </div>
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-icon">📊</div>
              <div className="metric-content">
                <div className="metric-value">{formatPercentage(data.overview.marketShare)}</div>
                <div className="metric-label">Market Share</div>
                <div className="metric-trend positive">+0.2% this quarter</div>
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-icon">💪</div>
              <div className="metric-content">
                <div className="metric-value">{data.overview.competitiveStrength}/10</div>
                <div className="metric-label">Competitive Strength</div>
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-icon">⚠️</div>
              <div className="metric-content">
                <div className="metric-value">{data.overview.threatLevel}/10</div>
                <div className="metric-label">Threat Level</div>
                <div className="metric-trend">{data.overview.emergingThreat} emerging threats</div>
              </div>
            </div>
          </div>

          <div className="overview-grid">
            <div className="competitive-advantages">
              <h3>Our Competitive Advantages</h3>
              <div className="advantages-list">
                {data.overview.competitiveAdvantages.map((advantage, index) => (
                  <div key={index} className="advantage-item">
                    <span className="advantage-icon">✅</span>
                    <span className="advantage-text">{advantage}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="key-weaknesses">
              <h3>Areas for Improvement</h3>
              <div className="weaknesses-list">
                {data.overview.keyWeaknesses.map((weakness, index) => (
                  <div key={index} className="weakness-item">
                    <span className="weakness-icon">⚠️</span>
                    <span className="weakness-text">{weakness}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="competitive-landscape">
              <h3>Competitive Landscape</h3>
              <div className="landscape-tiers">
                <div className="tier-item leaders">
                  <span className="tier-label">Market Leaders</span>
                  <span className="tier-count">{data.overview.marketLeaders}</span>
                </div>
                <div className="tier-item challengers">
                  <span className="tier-label">Challengers</span>
                  <span className="tier-count">
                    {data.overview.totalCompetitors - data.overview.marketLeaders - data.overview.emergingThreat}
                  </span>
                </div>
                <div className="tier-item emerging">
                  <span className="tier-label">Emerging Threats</span>
                  <span className="tier-count">{data.overview.emergingThreat}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Competitor Profiles */}
      {activeView === 'competitors' && (
        <div className="competitors-section">
          <div className="section-header">
            <h2>Competitor Profiles</h2>
            <div className="competitor-filters">
              <button className="filter-btn active">All</button>
              <button className="filter-btn">Direct</button>
              <button className="filter-btn">Indirect</button>
              <button className="filter-btn">Leaders</button>
              <button className="filter-btn">Emerging</button>
            </div>
          </div>

          <div className="competitors-grid">
            {data.competitors.map(competitor => (
              <div key={competitor.id} className="competitor-card">
                <div className="competitor-header">
                  <div className="competitor-info">
                    <div className="competitor-name">{competitor.name}</div>
                    <div className="competitor-meta">
                      <span className={`tier-badge ${competitor.tier}`}>
                        {competitor.tier}
                      </span>
                      <span className="market-share">
                        {formatPercentage(competitor.marketShare)} market share
                      </span>
                    </div>
                  </div>
                  <div className="threat-indicator">
                    <div 
                      className="threat-meter"
                      style={{ 
                        '--threat-level': `${competitor.threatLevel * 10}%`,
                        '--threat-color': getThreatColor(competitor.threatLevel)
                      }}
                    >
                      <span className="threat-value">{competitor.threatLevel}/10</span>
                    </div>
                  </div>
                </div>

                <div className="competitor-stats">
                  <div className="stat-item">
                    <span className="stat-label">Revenue:</span>
                    <span className="stat-value">{formatCurrency(competitor.revenue)}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Employees:</span>
                    <span className="stat-value">{competitor.employees.toLocaleString()}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Growth:</span>
                    <span className="stat-value positive">+{formatPercentage(competitor.recentGrowth)}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Countries:</span>
                    <span className="stat-value">{competitor.globalPresence}</span>
                  </div>
                </div>

                <div className="competitor-description">
                  {competitor.description}
                </div>

                <div className="strengths-weaknesses">
                  <div className="strengths">
                    <h4>Key Strengths</h4>
                    <ul>
                      {competitor.keyStrengths.slice(0, 3).map((strength, index) => (
                        <li key={index}>{strength}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="weaknesses">
                    <h4>Key Weaknesses</h4>
                    <ul>
                      {competitor.keyWeaknesses.slice(0, 3).map((weakness, index) => (
                        <li key={index}>{weakness}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="recent-news">
                  <h4>Recent Activity</h4>
                  <div className="news-list">
                    {competitor.recentNews.slice(0, 2).map((news, index) => (
                      <div key={index} className={`news-item ${news.impact}`}>
                        <div className="news-title">{news.title}</div>
                        <div className="news-meta">
                          <span className="news-date">{news.date}</span>
                          <span className={`news-impact ${news.impact}`}>
                            {news.impact} impact
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="competitor-actions">
                  <button 
                    className="action-btn primary"
                    onClick={() => setSelectedCompetitor(competitor)}
                  >
                    📊 View Details
                  </button>
                  <button className="action-btn secondary">📈 Track Changes</button>
                  <button className="action-btn secondary">🔄 Compare</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Continue with other sections... */}
      
    </div>
  );
};

export default CompetitiveIntelligenceDashboard;
