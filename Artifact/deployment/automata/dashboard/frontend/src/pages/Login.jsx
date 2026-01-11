import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Form, Input, Button, message } from 'antd';
import { authAPI } from '../utils/api';
import { useAuth } from '../contexts/AuthContext';

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const onFinish = async (values) => {
    try {
      const result = await login(values.username, values.password);
      if (result && result.success) {
        message.success('Logged in');
        navigate('/');
      } else {
        message.error(result.error || 'Login failed');
      }
    } catch (e) {
      message.error('Login failed');
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center' }}>
      <Card title="Automata Login" style={{ width: 360 }}>
        <Form name="login" initialValues={{ username: 'admin' }} onFinish={onFinish}>
          <Form.Item name="username" rules={[{ required: true, message: 'Please enter username' }]}>
            <Input placeholder="Username" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: 'Please enter password' }]}>
            <Input.Password placeholder="Password" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>Login</Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
