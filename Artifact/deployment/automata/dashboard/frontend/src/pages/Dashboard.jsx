import React, { useEffect, useState } from 'react';
import { Layout, Row, Col, Card, Statistic, Button, Space, Divider, List, Spin, Tag } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { statusAPI, analyticsAPI, configAPI } from '../utils/api';
import api from '../utils/api';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const { Content } = Layout;

export default function Dashboard({ darkMode, setDarkMode }) {
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [drafts, setDrafts] = useState([]);
  const [contextStats, setContextStats] = useState(null);

  const fetchAll = async () => {
    setLoading(true);
    try {
      // Prefer a single overview endpoint when available
      try {
        const ov = await api.get('/overview');
        if (ov?.data?.success && ov.data.overview) {
          const o = ov.data.overview;
          setStatus(o.status);
          setAnalytics(o.analytics);
          setDrafts(o.content?.drafts || []);
          setContextStats(o.context_stats || null);
          setLoading(false);
          return;
        }
      } catch (e) {
        // fallback to individual calls
      }

      const [sRes, aRes, dRes, cRes] = await Promise.allSettled([
        statusAPI.getStatus(),
        analyticsAPI.getAnalytics(),
        api.get('/content/drafts'),
        api.get('/context/stats')
      ]);

      if (sRes.status === 'fulfilled') setStatus(sRes.value.data);
      if (aRes.status === 'fulfilled') setAnalytics(aRes.value.data.analytics);
      if (dRes.status === 'fulfilled') setDrafts(dRes.value.data.items || []);
      if (cRes.status === 'fulfilled') setContextStats(cRes.value.data.stats || null);
    } catch (e) {
      // ignore, individual promises handled above
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const smallChartData = (
    analytics && analytics.content && analytics.content.timeline
  ) || [{ name: 't1', value: 0 }, { name: 't2', value: 0 }, { name: 't3', value: 0 }];

  return (
    <Layout style={{ height: '100vh', padding: 24 }}>
      <Content>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Row justify="space-between" align="middle">
            <Col>
              <h2>Automata Dashboard — Unified Overview</h2>
            </Col>
            <Col>
              <Space>
                <Button icon={<ReloadOutlined />} onClick={fetchAll} />
                <Button onClick={() => setDarkMode(!darkMode)}>{darkMode ? 'Light' : 'Dark'}</Button>
              </Space>
            </Col>
          </Row>

          {loading ? (
            <Spin tip="Loading…" />
          ) : (
            <>
              <Row gutter={16}>
                <Col xs={24} sm={12} md={6}>
                  <Card>
                    <Statistic
                      title="System Running"
                      value={status ? (status.running ? 'Yes' : 'No') : 'Unknown'}
                    />
                  </Card>
                </Col>

                <Col xs={24} sm={12} md={6}>
                  <Card>
                    <Statistic
                      title="Queued Drafts"
                      value={drafts.length}
                    />
                  </Card>
                </Col>

                <Col xs={24} sm={12} md={6}>
                  <Card>
                    <Statistic
                      title="Context Size"
                      value={contextStats ? contextStats.size || 0 : 'N/A'}
                    />
                  </Card>
                </Col>

                <Col xs={24} sm={12} md={6}>
                  <Card>
                    <Statistic
                      title="ERP / Social Platforms"
                      value={status ? (status.erp_systems ? Object.keys(status.erp_systems).length : 0) : 'N/A'}
                    />
                  </Card>
                </Col>
              </Row>

              <Divider />

              <Row gutter={16} style={{ minHeight: 240 }}>
                <Col xs={24} md={12}>
                  <Card title="Content / Reports Timeline" style={{ height: 300 }}>
                    <ResponsiveContainer width="100%" height={220}>
                      <AreaChart data={smallChartData}>
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Area type="monotone" dataKey="value" stroke="#8884d8" fill="#8884d8" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </Card>
                </Col>

                <Col xs={24} md={12}>
                  <Card title="Latest Drafts">
                    <List
                      dataSource={drafts.slice(0, 8)}
                      renderItem={item => (
                        <List.Item>
                          <List.Item.Meta
                            title={<div>{item.title || item.id} <Tag style={{ marginLeft: 8 }}>{item.status}</Tag></div>}
                            description={item.platform ? `${item.platform} • ${item.topic || ''}` : (item.topic || '')}
                          />
                        </List.Item>
                      )}
                    />
                  </Card>
                </Col>
              </Row>

              <Divider />

              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Card title="Social Platforms / ERP" style={{ minHeight: 180 }}>
                    <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(status ? { erp: status.erp_systems, social: status.social_media } : {}, null, 2)}</pre>
                  </Card>
                </Col>

                <Col xs={24} md={12}>
                  <Card title="Quick Actions" style={{ minHeight: 180 }}>
                    <Space direction="vertical">
                      <Button onClick={async () => { await statusAPI.start(); fetchAll(); }}>Start System</Button>
                      <Button onClick={async () => { await statusAPI.stop(); fetchAll(); }}>Stop System</Button>
                      <Button onClick={async () => { const r = await api.post('/context/reflect'); console.log(r.data); }}>Run Reflection</Button>
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
