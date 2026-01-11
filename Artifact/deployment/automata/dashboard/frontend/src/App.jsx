import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import { ConfigProvider, theme, Layout, Menu } from 'antd';
import {
  DashboardOutlined,
  BankOutlined,
  HeartOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Markets from './pages/Markets';
import Health from './pages/Health';
import { AuthProvider, useAuth } from './contexts/AuthContext';

const { Sider, Content } = Layout;

function PrivateRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" />;
}

function AppLayout({ darkMode, setDarkMode, children }) {
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: <Link to="/">Overview</Link>,
    },
    {
      key: '/markets',
      icon: <BankOutlined />,
      label: <Link to="/markets">Markets</Link>,
    },
    {
      key: '/health',
      icon: <HeartOutlined />,
      label: <Link to="/health">System Health</Link>,
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider 
        collapsible 
        collapsed={collapsed} 
        onCollapse={setCollapsed}
        theme={darkMode ? 'dark' : 'light'}
      >
        <div style={{ 
          height: 64, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          borderBottom: '1px solid rgba(0,0,0,0.1)',
        }}>
          <span style={{ 
            fontSize: collapsed ? 16 : 20, 
            fontWeight: 'bold',
            color: darkMode ? '#fff' : '#1890ff',
          }}>
            {collapsed ? '⚔️' : '⚔️ Gladius'}
          </span>
        </div>
        <Menu
          theme={darkMode ? 'dark' : 'light'}
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          style={{ marginTop: 8 }}
        />
      </Sider>
      <Layout>
        <Content style={{ margin: 0, overflow: 'auto' }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
}

function App() {
  const [darkMode, setDarkMode] = useState(false);

  return (
    <ConfigProvider
      theme={{
        algorithm: darkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route 
              path="/" 
              element={
                <PrivateRoute>
                  <AppLayout darkMode={darkMode} setDarkMode={setDarkMode}>
                    <Dashboard darkMode={darkMode} setDarkMode={setDarkMode} />
                  </AppLayout>
                </PrivateRoute>
              } 
            />
            <Route 
              path="/markets" 
              element={
                <PrivateRoute>
                  <AppLayout darkMode={darkMode} setDarkMode={setDarkMode}>
                    <Markets />
                  </AppLayout>
                </PrivateRoute>
              } 
            />
            <Route 
              path="/health" 
              element={
                <PrivateRoute>
                  <AppLayout darkMode={darkMode} setDarkMode={setDarkMode}>
                    <Health />
                  </AppLayout>
                </PrivateRoute>
              } 
            />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ConfigProvider>
  );
}

export default App;
