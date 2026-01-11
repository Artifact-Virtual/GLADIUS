import React, { useEffect, useState } from 'react';
import { Layout, Row, Col, Card, Statistic, Button, Space, Divider, List, Spin, Tag, Alert, Badge, Typography } from 'antd';
import { 
  ReloadOutlined, 
  CheckCircleOutlined, 
  CloseCircleOutlined,
  RocketOutlined,
  StopOutlined,
  ThunderboltOutlined,
  FileTextOutlined,
  RobotOutlined,
} from '@ant-design/icons';
import { statusAPI, analyticsAPI, configAPI, healthAPI, infraAPI } from '../utils/api';
import api from '../utils/api';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const { Content } = Layout;
const { Text, Title } = Typography;

export default function Dashboard({ darkMode, setDarkMode }) {
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [drafts, setDrafts] = useState([]);
  const [contextStats, setContextStats] = useState(null);
  const [reflectionsCount, setReflectionsCount] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);
  const [infraData, setInfraData] = useState({ markets: 0, assets: 0, portfolios: 0 });

  const fetchAll = async () => {
    setLoading(true);
    try {
      // Fetch health status
      const health = await healthAPI.checkAll();
      setHealthStatus(health);

      // Fetch infra data if available
      try {
        const [markets, assets, portfolios] = await Promise.all([
          infraAPI.getMarkets(),
          infraAPI.getAssets(),
          infraAPI.getPortfolios(),
        ]);
        setInfraData({
          markets: markets.data?.length || 0,
          assets: assets.data?.length || 0,
          portfolios: portfolios.data?.length || 0,
        });
      } catch {
        // Infra API may not be running
      }

      // Prefer a single overview endpoint when available
      try {
        const ov = await api.get('/overview');
        if (ov?.data?.success && ov.data.overview) {
          const o = ov.data.overview;
          setStatus(o.status);
          setAnalytics(o.analytics);
          setDrafts(o.content?.drafts || []);
          setContextStats(o.context_stats || null);
          setReflectionsCount(o.reflections_count || null);
          setLoading(false);
          return;
        }
      } catch (e) {
        // fallback to individual calls
      }

      const [sRes, aRes, dRes, cRes, rRes] = await Promise.allSettled([
        statusAPI.getStatus(),
        analyticsAPI.getAnalytics(),
        api.get('/content/drafts'),
        api.get('/context/stats'),
        api.get('/reflections/recent'),
      ]);

      if (sRes.status === 'fulfilled') setStatus(sRes.value.data);
      if (aRes.status === 'fulfilled') setAnalytics(aRes.value.data.analytics);
      if (dRes.status === 'fulfilled') setDrafts(dRes.value.data.items || []);
      if (cRes.status === 'fulfilled') setContextStats(cRes.value.data.stats || null);
      if (rRes.status === 'fulfilled') setReflectionsCount(rRes.value.data?.length || 0);
    } catch (e) {
      // ignore, individual promises handled above
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
    // Auto-refresh every 60 seconds
    const interval = setInterval(fetchAll, 60000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const smallChartData = (
    analytics && analytics.content && analytics.content.timeline
  ) || [{ name: 'Day 1', value: 0 }, { name: 'Day 2', value: 0 }, { name: 'Day 3', value: 0 }];

  // Status colors for pie chart
  const COLORS = ['#52c41a', '#ff4d4f', '#faad14'];
  const serviceStatusData = [
    { name: 'Healthy', value: (healthStatus?.infra?.status === 'up' ? 1 : 0) + (healthStatus?.dashboard?.status === 'up' ? 1 : 0) },
    { name: 'Down', value: (healthStatus?.infra?.status === 'down' ? 1 : 0) + (healthStatus?.dashboard?.status === 'down' ? 1 : 0) },
  ].filter(d => d.value > 0);

  const isSystemHealthy = healthStatus?.infra?.status === 'up' && healthStatus?.dashboard?.status === 'up';

  return (
    <Layout style={{ minHeight: '100vh', padding: 24, background: 'transparent' }}>
      <Content>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          {/* Header */}
          <Row justify="space-between" align="middle">
            <Col>
              <Title level={2} style={{ margin: 0 }}>
                <RobotOutlined style={{ marginRight: 12 }} />
                Gladius Control Center
              </Title>
              <Text type="secondary">Unified system overview and management</Text>
            </Col>
            <Col>
              <Space>
                <Badge 
                  status={isSystemHealthy ? 'success' : 'warning'} 
                  text={isSystemHealthy ? 'All Systems Operational' : 'Degraded'} 
                />
                <Button icon={<ReloadOutlined />} onClick={fetchAll} loading={loading}>
                  Refresh
                </Button>
                <Button onClick={() => setDarkMode(!darkMode)}>
                  {darkMode ? '☀️' : '🌙'}
                </Button>
              </Space>
            </Col>
          </Row>

          {/* System Alert */}
          {!isSystemHealthy && !loading && (
            <Alert
              message="System Status Warning"
              description="Some services are not responding. Check System Health page for details."
              type="warning"
              showIcon
              closable
            />
          )}

          {loading ? (
            <div style={{ textAlign: 'center', padding: 60 }}>
              <Spin size="large" tip="Loading dashboard..." />
            </div>
          ) : (
            <>
              {/* Primary Stats Row */}
              <Row gutter={[16, 16]}>
                <Col xs={24} sm={12} md={6}>
                  <Card hoverable>
                    <Statistic
                      title="Automata Status"
                      value={status?.running ? 'Running' : 'Stopped'}
                      valueStyle={{ color: status?.running ? '#52c41a' : '#ff4d4f' }}
                      prefix={status?.running ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Card hoverable>
                    <Statistic
                      title="Content Drafts"
                      value={drafts.length}
                      prefix={<FileTextOutlined />}
                      suffix={drafts.filter(d => d.status === 'final').length > 0 ? 
                        <Tag color="green" style={{ marginLeft: 8 }}>
                          {drafts.filter(d => d.status === 'final').length} ready
                        </Tag> : null
                      }
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Card hoverable>
                    <Statistic
                      title="Context Entries"
                      value={contextStats?.size || contextStats?.total || 0}
                      prefix={<ThunderboltOutlined />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Card hoverable>
                    <Statistic
                      title="AI Reflections"
                      value={reflectionsCount !== null ? reflectionsCount : 'N/A'}
                      prefix={<RobotOutlined />}
                    />
                  </Card>
                </Col>
              </Row>

              {/* Infra Stats Row */}
              <Row gutter={[16, 16]}>
                <Col xs={24} sm={8}>
                  <Card size="small">
                    <Statistic
                      title="Markets"
                      value={infraData.markets}
                      valueStyle={{ fontSize: 20 }}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={8}>
                  <Card size="small">
                    <Statistic
                      title="Assets"
                      value={infraData.assets}
                      valueStyle={{ fontSize: 20 }}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={8}>
                  <Card size="small">
                    <Statistic
                      title="Portfolios"
                      value={infraData.portfolios}
                      valueStyle={{ fontSize: 20 }}
                    />
                  </Card>
                </Col>
              </Row>

              <Divider />

              {/* Charts and Activity */}
              <Row gutter={[16, 16]}>
                <Col xs={24} lg={14}>
                  <Card title="Activity Timeline" style={{ height: 340 }}>
                    <ResponsiveContainer width="100%" height={260}>
                      <AreaChart data={smallChartData}>
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Area 
                          type="monotone" 
                          dataKey="value" 
                          stroke="#1890ff" 
                          fill="#1890ff" 
                          fillOpacity={0.3}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </Card>
                </Col>
                <Col xs={24} lg={10}>
                  <Card title="Service Status" style={{ height: 340 }}>
                    <Row gutter={16}>
                      <Col span={12}>
                        <ResponsiveContainer width="100%" height={180}>
                          <PieChart>
                            <Pie
                              data={serviceStatusData}
                              cx="50%"
                              cy="50%"
                              innerRadius={40}
                              outerRadius={60}
                              paddingAngle={5}
                              dataKey="value"
                            >
                              {serviceStatusData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                              ))}
                            </Pie>
                            <Tooltip />
                          </PieChart>
                        </ResponsiveContainer>
                      </Col>
                      <Col span={12}>
                        <Space direction="vertical" style={{ paddingTop: 20 }}>
                          <div>
                            <Badge status={healthStatus?.infra?.status === 'up' ? 'success' : 'error'} />
                            <Text style={{ marginLeft: 8 }}>Infra API (7000)</Text>
                          </div>
                          <div>
                            <Badge status={healthStatus?.dashboard?.status === 'up' ? 'success' : 'error'} />
                            <Text style={{ marginLeft: 8 }}>Dashboard (5000)</Text>
                          </div>
                          <div>
                            <Badge status="processing" />
                            <Text style={{ marginLeft: 8 }}>Frontend (3000)</Text>
                          </div>
                        </Space>
                      </Col>
                    </Row>
                  </Card>
                </Col>
              </Row>

              <Divider />

              {/* Drafts and Quick Actions */}
              <Row gutter={[16, 16]}>
                <Col xs={24} lg={14}>
                  <Card 
                    title="Recent Drafts" 
                    extra={<Button type="link" size="small">View All →</Button>}
                  >
                    <List
                      dataSource={drafts.slice(0, 6)}
                      renderItem={item => (
                        <List.Item>
                          <List.Item.Meta
                            title={
                              <Space>
                                {item.title || item.id}
                                <Tag color={
                                  item.status === 'final' ? 'green' : 
                                  item.status === 'published' ? 'blue' : 
                                  'default'
                                }>
                                  {item.status}
                                </Tag>
                              </Space>
                            }
                            description={
                              item.platform ? `${item.platform} • ${item.topic || 'No topic'}` : (item.topic || 'No topic')
                            }
                          />
                        </List.Item>
                      )}
                      locale={{ emptyText: 'No drafts yet. Generate content to see drafts here.' }}
                    />
                  </Card>
                </Col>
                <Col xs={24} lg={10}>
                  <Card title="Quick Actions">
                    <Space direction="vertical" style={{ width: '100%' }} size="middle">
                      <Button 
                        type="primary" 
                        icon={<RocketOutlined />}
                        onClick={async () => { await statusAPI.start(); fetchAll(); }}
                        block
                        disabled={status?.running}
                      >
                        Start Automata System
                      </Button>
                      <Button 
                        danger
                        icon={<StopOutlined />}
                        onClick={async () => { await statusAPI.stop(); fetchAll(); }}
                        block
                        disabled={!status?.running}
                      >
                        Stop Automata System
                      </Button>
                      <Divider style={{ margin: '8px 0' }} />
                      <Button 
                        icon={<RobotOutlined />}
                        onClick={async () => { 
                          const r = await api.post('/context/reflect'); 
                          console.log('Reflection result:', r.data);
                          fetchAll();
                        }}
                        block
                      >
                        Trigger AI Reflection
                      </Button>
                      <Button 
                        icon={<FileTextOutlined />}
                        onClick={async () => { 
                          const r = await api.post('/content/generate', {
                            platform: 'LinkedIn',
                            topic: 'AI and Trading',
                            content_type: 'article'
                          }); 
                          console.log('Generated:', r.data);
                          fetchAll();
                        }}
                        block
                      >
                        Generate Content
                      </Button>
                    </Space>
                  </Card>
                </Col>
              </Row>
            </>
          )}
        </Space>
      </Content>
    </Layout>
  );
}
