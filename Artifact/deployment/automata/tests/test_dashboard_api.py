import json
import os
import sys
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Skip this test module if Flask (or Flask extensions) are not available in the environment
pytest.importorskip('flask_cors')
pytest.importorskip('flask_socketio')
from automata.dashboard.backend import app


def get_token(client):
    res = client.post('/api/auth/login', json={'username': 'admin', 'password': 'admin123'})
    assert res.status_code == 200
    data = res.get_json()
    assert data.get('access_token')
    return data.get('access_token')


def test_overview_endpoint_requires_auth_and_returns_overview():
    client = app.test_client()
    # unauthenticated should be 401
    r = client.get('/api/overview')
    assert r.status_code == 401

    token = get_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    r2 = client.get('/api/overview', headers=headers)
    assert r2.status_code == 200
    data = r2.get_json()
    assert data.get('success') is True
    assert 'overview' in data
    # overview should contain status and analytics keys
    assert 'status' in data['overview']
    assert 'analytics' in data['overview']
