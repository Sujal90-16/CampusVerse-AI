from fastapi.testclient import TestClient
from app.main import app

def test_auth_academic_access_and_role_guards():
    with TestClient(app) as client:
        assert client.get('/api/health').status_code == 200
        response = client.post('/api/auth/register', json={
            'name':'Test Student', 'email':'test.student@example.com',
            'password':'LongSecurePass123!', 'department':'CSE', 'semester':7
        })
        assert response.status_code == 201
        token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        assert client.get('/api/auth/me', headers=headers).status_code == 200
        assert client.get('/api/academics/courses', headers=headers).status_code == 200
        assert client.post('/api/shaan/chat', headers=headers, json={'message':'When is my next exam?'}).status_code == 200
        assert client.get('/api/admin/users', headers=headers).status_code == 403
