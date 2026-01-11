import React, { useEffect, useState } from 'react';
import { Layout, Row, Col, Card, Tag, Space, Button, Spin, Alert, Divider, List, Typography, Badge } from 'antd';
import { 
  ReloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
  ApiOutlined,
  DatabaseOutlined,
  CloudServerOutlined,
  RobotOutlined,
} from '@ant-design/icons';
import { healthAPI } from '../utils/api';

const { Content } = Layout;
const { Text, Title } = Typography;

export default function Health() {
  const [loading, setLoading] = useState(true);
  const [healthData, setHealthData] = useState(null);
  const [lastCheck, setLastCheck] = useState(null);

  const checkHealth = async () => {
    setLoading(true);
    try {
      const results = await healthAPI.checkAll();
      setHealthData(results);
      setLastCheck(new Date().toLocaleTimeString());
    } catch (err) {
      console.error('Health check failed:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
    // Auto-refresh every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusBadge = (status) => {
    if (status === 'up') {
      return <Badge status="success" text="Healthy" />;
    } else if (status === 'down') {
      return <Badge status="error" text="Down" />;
    }
    return <Badge status="warning" text="Unknown" />;
  };

  const getStatusIcon = (status) => {
    if (status === 'up') {
      return <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 24 }} />;
    } else if (status === 'down') {
      return <CloseCircleOutlined style={{ color: '#ff4d4f', fontSize: 24 }} />;
    }
    return <WarningOutlined style={{ color: '#faad14', fontSize: 24 }} />;
  };

  const services = [
    {
      key: 'infra',
      name: 'Infra API',
      description: 'Market data, assets, portfolios',
      port: 7000,
      icon: <DatabaseOutlined />,
      docsUrl: 'http://localhost:7000/docs',
    },
    {
      key: 'dashboard',
      name: 'Dashboard Backend',
      description: 'Automata control, content management',
      port: 5000,
      icon: <ApiOutlined />,
      docsUrl: null,
    },
    {
      key: 'syndicate',
      name: 'Syndicate Daemon',
      description: 'Market intelligence pipeline',
      port: null,
      icon: <RobotOutlined />,
      docsUrl: null,
      manualCheck: true,
    },
    {
      key: 'frontend',
      name: 'Dashboard Frontend',
      description: 'React UI (this page)',
      port: 3000,
      icon: <CloudServerOutlined />,
      docsUrl: null,
      selfCheck: true,
    },
  ];

  const overallHealth = healthData 
    ? (healthData.infra?.status === 'up' && healthData.dashboard?.status === 'up' ? 'healthy' : 'degraded')
    : 'unknown';

  return (
    <Layout style={{ minHeight: '100vh', padding: 24 }}>
      <Content>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          {/* Header */}
          <Row justify="space-between" align="middle">
            <Col>
              <h2>
                <ApiOutlined style={{ marginRight: 12 }} />
                System Health
              </h2>
            </Col>
            <Col>
              <Space>
                {lastCheck && (
                  <Text type="secondary">Last check: {lastCheck}</Text>
                )}
                <Button icon={<ReloadOutlined />} onClick={checkHealth} loading={loading}>
                  Check Now
                </Button>
              </Space>
            </Col>
          </Row>

          {/* Overall Status Banner */}
          <Alert
            message={
              overallHealth === 'healthy' 
                ? '🎉 All systems operational' 
                : overallHealth === 'degraded'
                ? '⚠️ System degraded - some services unavailable'
                : '❓ Checking system status...'
            }
            type={overallHealth === 'healthy' ? 'success' : overallHealth === 'degraded' ? 'warning' : 'info'}
            showIcon
          />

          {loading && !healthData ? (
            <div style={{ textAlign: 'center', padding: 60 }}>
              <Spin size="large" tip="Checking system health..." />
            </div>
          ) : (
            <>
              {/* Service Cards */}
              <Row gutter={[16, 16]}>
                {services.map((service) => {
                  const status = service.selfCheck 
                    ? 'up' 
                    : service.manualCheck 
                    ? 'unknown'
                    : healthData?.[service.key]?.status || 'unknown';

                  return (
                    <Col xs={24} sm={12} lg={6} key={service.key}>
                      <Card
                        hoverable
                        style={{ 
                          borderColor: status === 'up' ? '#52c41a' : status === 'down' ? '#ff4d4f' : '#d9d9d9',
                          borderWidth: 2,
                        }}
                      >
                        <Space direction="vertical" style={{ width: '100%' }}>
                          <Row justify="space-between" align="middle">
                            <Col>
                              <Space>
                                {service.icon}
                                <Text strong>{service.name}</Text>
                              </Space>
                            </Col>
                            <Col>
                              {getStatusIcon(status)}
                            </Col>
                          </Row>
                          <Text type="secondary">{service.description}</Text>
                          <Divider style={{ margin: '8px 0' }} />
                          <Row justify="space-between">
                            <Col>
                              {service.port && (
                                <Tag>Port: {service.port}</Tag>
                              )}
                              {service.manualCheck && (
                                <Tag color="orange">Manual check required</Tag>
                              )}
                            </Col>
                            <Col>
                              {getStatusBadge(status)}
                            </Col>
                          </Row>
                          {service.docsUrl && status === 'up' && (
                            <Button 
                              type="link" 
                              size="small" 
                              href={service.docsUrl} 
                              target="_blank"
                            >
                              Open API Docs →
                            </Button>
                          )}
                        </Space>
                      </Card>
                    </Col>
                  );
                })}
              </Row>

              <Divider />

              {/* Quick Actions */}
              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Card title="Quick Commands">
                    <List
                      size="small"
                      dataSource={[
                        { cmd: './scripts/start_gladius.sh', desc: 'Start all services' },
                        { cmd: './scripts/stop_gladius.sh', desc: 'Stop all services' },
                        { cmd: './scripts/health_check.sh', desc: 'CLI health check' },
                        { cmd: 'tail -f logs/*.log', desc: 'View live logs' },
                      ]}
                      renderItem={(item) => (
                        <List.Item>
                          <code style={{ 
                            background: '#f5f5f5', 
                            padding: '2px 8px', 
                            borderRadius: 4,
                            fontFamily: 'monospace',
                          }}>
                            {item.cmd}
                          </code>
                          <Text type="secondary" style={{ marginLeft: 12 }}>{item.desc}</Text>
                        </List.Item>
                      )}
                    />
                  </Card>
                </Col>
                <Col xs={24} md={12}>
                  <Card title="Service URLs">
                    <List
                      size="small"
                      dataSource={[
                        { name: 'Dashboard', url: 'http://localhost:3000', status: 'up' },
                        { name: 'Infra API Docs', url: 'http://localhost:7000/docs', status: healthData?.infra?.status },
                        { name: 'Dashboard API', url: 'http://localhost:5000/health', status: healthData?.dashboard?.status },
                        { name: 'Grafana', url: 'http://localhost:3000', status: 'unknown' },
                      ]}
                      renderItem={(item) => (
                        <List.Item>
                          <Space>
                            {item.status === 'up' ? (
                              <CheckCircleOutlined style={{ color: '#52c41a' }} />
                            ) : item.status === 'down' ? (
                              <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
                            ) : (
                              <WarningOutlined style={{ color: '#faad14' }} />
                            )}
                            <Text strong>{item.name}</Text>
                          </Space>
                          <Button 
                            type="link" 
                            href={item.url} 
                            target="_blank"
                            disabled={item.status === 'down'}
                          >
                            {item.url}
                          </Button>
                        </List.Item>
                      )}
                    />
                  </Card>
                </Col>
              </Row>

              <Divider />

              {/* Grafana Embed Placeholder */}
              <Row>
                <Col span={24}>
                  <Card 
                    title="Metrics Dashboard (Grafana)"
                    extra={
                      <Button type="link" href="http://localhost:3000" target="_blank">
                        Open Full Grafana →
                      </Button>
                    }
                  >
                    <div 
                      style={{ 
                        background: '#f5f5f5', 
                        padding: 40, 
                        textAlign: 'center',
                        borderRadius: 8,
                        minHeight: 300,
                      }}
                    >
                      <Title level={4} type="secondary">
                        Grafana Integration
                      </Title>
                      <Text type="secondary">
                        Start Grafana with: <code>cd Artifact/syndicate/docker && docker-compose up -d grafana</code>
                      </Text>
                      <br /><br />
                      <Text type="secondary">
                        Once running, embed panels here or access full dashboard at{' '}
                        <a href="http://localhost:3000" target="_blank" rel="noopener noreferrer">
                          http://localhost:3000
                        </a>
                      </Text>
                      {/* 
                        Future: Add iframe embed
                        <iframe 
                          src="http://localhost:3000/d-solo/syndicate/overview?orgId=1&panelId=1"
                          width="100%" 
                          height="400"
                          frameBorder="0"
                        />
                      */}
                    </div>
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
