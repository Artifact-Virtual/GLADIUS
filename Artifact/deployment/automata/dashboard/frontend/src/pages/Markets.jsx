import React, { useEffect, useState } from 'react';
import { Layout, Row, Col, Card, Statistic, Table, Tag, Space, Button, Spin, Alert, Divider } from 'antd';
import { 
  DollarOutlined, 
  RiseOutlined, 
  FallOutlined, 
  ReloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  BankOutlined
} from '@ant-design/icons';
import { infraAPI } from '../utils/api';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const { Content } = Layout;

export default function Markets() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [markets, setMarkets] = useState([]);
  const [assets, setAssets] = useState([]);
  const [portfolios, setPortfolios] = useState([]);
  const [infraHealth, setInfraHealth] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Check Infra API health first
      const health = await infraAPI.health();
      setInfraHealth(health.status);
      
      if (health.status === 'down') {
        setError('Infra API is not available. Please ensure it is running on port 7000.');
        setLoading(false);
        return;
      }

      // Fetch all data in parallel
      const [marketsRes, assetsRes, portfoliosRes] = await Promise.allSettled([
        infraAPI.getMarkets(),
        infraAPI.getAssets(),
        infraAPI.getPortfolios(),
      ]);

      if (marketsRes.status === 'fulfilled') {
        setMarkets(marketsRes.value.data || []);
      }
      if (assetsRes.status === 'fulfilled') {
        setAssets(assetsRes.value.data || []);
      }
      if (portfoliosRes.status === 'fulfilled') {
        setPortfolios(portfoliosRes.value.data || []);
      }
    } catch (err) {
      setError('Failed to fetch market data: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Market columns for table
  const marketColumns = [
    {
      title: 'Symbol',
      dataIndex: 'symbol',
      key: 'symbol',
      render: (text) => <strong>{text}</strong>,
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Exchange',
      dataIndex: 'exchange',
      key: 'exchange',
      render: (text) => <Tag color="blue">{text}</Tag>,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'active' ? 'green' : 'default'}>
          {status || 'active'}
        </Tag>
      ),
    },
  ];

  // Asset columns for table
  const assetColumns = [
    {
      title: 'Ticker',
      dataIndex: 'ticker',
      key: 'ticker',
      render: (text) => <strong>{text}</strong>,
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Type',
      dataIndex: 'asset_type',
      key: 'asset_type',
      render: (type) => {
        const colors = {
          crypto: 'orange',
          commodity: 'gold',
          stock: 'blue',
          forex: 'purple',
        };
        return <Tag color={colors[type] || 'default'}>{type}</Tag>;
      },
    },
    {
      title: 'Last Price',
      dataIndex: 'last_price',
      key: 'last_price',
      render: (price) => price ? `$${parseFloat(price).toLocaleString()}` : 'N/A',
    },
  ];

  // Portfolio columns
  const portfolioColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Positions',
      dataIndex: 'positions',
      key: 'positions',
      render: (positions) => positions?.length || 0,
    },
    {
      title: 'Total Value',
      dataIndex: 'total_value',
      key: 'total_value',
      render: (value) => value ? `$${parseFloat(value).toLocaleString()}` : 'N/A',
    },
    {
      title: 'P&L',
      dataIndex: 'pnl',
      key: 'pnl',
      render: (pnl) => {
        if (pnl === undefined || pnl === null) return 'N/A';
        const isPositive = pnl >= 0;
        return (
          <span style={{ color: isPositive ? '#52c41a' : '#ff4d4f' }}>
            {isPositive ? <RiseOutlined /> : <FallOutlined />}
            {' '}
            ${Math.abs(pnl).toLocaleString()}
          </span>
        );
      },
    },
  ];

  // Sample price chart data (would come from real API)
  const priceChartData = [
    { time: '09:00', gold: 2650, btc: 42000 },
    { time: '10:00', gold: 2655, btc: 42100 },
    { time: '11:00', gold: 2648, btc: 41800 },
    { time: '12:00', gold: 2660, btc: 42300 },
    { time: '13:00', gold: 2658, btc: 42200 },
    { time: '14:00', gold: 2662, btc: 42500 },
  ];

  return (
    <Layout style={{ minHeight: '100vh', padding: 24 }}>
      <Content>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          {/* Header */}
          <Row justify="space-between" align="middle">
            <Col>
              <h2>
                <BankOutlined style={{ marginRight: 12 }} />
                Markets & Data
              </h2>
            </Col>
            <Col>
              <Space>
                <Tag color={infraHealth === 'ok' ? 'green' : 'red'}>
                  {infraHealth === 'ok' ? (
                    <><CheckCircleOutlined /> Infra API Online</>
                  ) : (
                    <><CloseCircleOutlined /> Infra API Offline</>
                  )}
                </Tag>
                <Button icon={<ReloadOutlined />} onClick={fetchData}>
                  Refresh
                </Button>
              </Space>
            </Col>
          </Row>

          {error && (
            <Alert 
              message="Connection Error" 
              description={error} 
              type="error" 
              showIcon 
              closable 
            />
          )}

          {loading ? (
            <div style={{ textAlign: 'center', padding: 60 }}>
              <Spin size="large" tip="Loading market data..." />
            </div>
          ) : (
            <>
              {/* Stats Row */}
              <Row gutter={16}>
                <Col xs={24} sm={12} md={6}>
                  <Card>
                    <Statistic
                      title="Markets"
                      value={markets.length}
                      prefix={<BankOutlined />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Card>
                    <Statistic
                      title="Assets"
                      value={assets.length}
                      prefix={<DollarOutlined />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Card>
                    <Statistic
                      title="Portfolios"
                      value={portfolios.length}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Card>
                    <Statistic
                      title="Data Source"
                      value="Infra API"
                      valueStyle={{ fontSize: 16 }}
                    />
                  </Card>
                </Col>
              </Row>

              <Divider />

              {/* Price Chart */}
              <Row gutter={16}>
                <Col span={24}>
                  <Card title="Price Overview (Sample Data)">
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={priceChartData}>
                        <XAxis dataKey="time" />
                        <YAxis yAxisId="gold" orientation="left" domain={['auto', 'auto']} />
                        <YAxis yAxisId="btc" orientation="right" domain={['auto', 'auto']} />
                        <Tooltip />
                        <Line 
                          yAxisId="gold" 
                          type="monotone" 
                          dataKey="gold" 
                          stroke="#d4af37" 
                          name="Gold (USD)" 
                          strokeWidth={2}
                        />
                        <Line 
                          yAxisId="btc" 
                          type="monotone" 
                          dataKey="btc" 
                          stroke="#f7931a" 
                          name="BTC (USD)" 
                          strokeWidth={2}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </Card>
                </Col>
              </Row>

              <Divider />

              {/* Markets Table */}
              <Row gutter={16}>
                <Col xs={24} lg={12}>
                  <Card title="Registered Markets">
                    <Table
                      dataSource={markets}
                      columns={marketColumns}
                      rowKey="id"
                      size="small"
                      pagination={{ pageSize: 5 }}
                      locale={{ emptyText: 'No markets registered. Seed data with: python scripts/seed_gold_bitcoin.py' }}
                    />
                  </Card>
                </Col>
                <Col xs={24} lg={12}>
                  <Card title="Registered Assets">
                    <Table
                      dataSource={assets}
                      columns={assetColumns}
                      rowKey="id"
                      size="small"
                      pagination={{ pageSize: 5 }}
                      locale={{ emptyText: 'No assets registered' }}
                    />
                  </Card>
                </Col>
              </Row>

              <Divider />

              {/* Portfolios Table */}
              <Row>
                <Col span={24}>
                  <Card title="Portfolios">
                    <Table
                      dataSource={portfolios}
                      columns={portfolioColumns}
                      rowKey="id"
                      size="small"
                      pagination={{ pageSize: 10 }}
                      locale={{ emptyText: 'No portfolios created' }}
                    />
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
