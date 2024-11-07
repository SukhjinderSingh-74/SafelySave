# tests/test_integration.py

import pytest
import firebase_admin
from firebase_admin import credentials, auth, storage
import io

@pytest.fixture(scope='session')
def firebase_app():
    """Initialize Firebase app for testing"""
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate('firebase-credentials.json')
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'safe-upload-3e2d8.firebasestorage.app'
        })
    return firebase_admin.get_app()

@pytest.fixture(scope='session')
def test_user(firebase_app):
    """Create a test user for integration testing"""
    try:
        user = auth.create_user(
            email='integration_test@test.com',
            password='TestPass123!'
        )
        yield user
        # Cleanup test user
        auth.delete_user(user.uid)
    except Exception as e:
        print(f"Error creating test user: {e}")
        raise

@pytest.fixture
def test_client():
    """Create a test client"""
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestAuthenticationFlow:
    def test_full_auth_flow(self, test_client, test_user):
        """Test complete authentication flow"""
        # Test login
        login_response = test_client.post('/login', data={
            'email': 'integration_test@test.com',
            'password': 'TestPass123!'
        })
        assert login_response.status_code == 302  # Redirect to home

        # Test accessing home page
        home_response = test_client.get('/')
        assert home_response.status_code == 200

        # Test logout
        logout_response = test_client.get('/logout')
        assert logout_response.status_code == 302  # Redirect to login

class TestFileOperationsFlow:
    def test_file_upload_download_delete(self, test_client, test_user):
        """Test complete file operations flow"""
        # Login first
        test_client.post('/login', data={
            'email': 'integration_test@test.com',
            'password': 'TestPass123!'
        })

        # Test file upload
        file_content = b'Integration test file content'
        data = {
            'file': (io.BytesIO(file_content), 'integration_test.txt')
        }
        upload_response = test_client.post('/upload', data=data)
        assert upload_response.status_code == 302

        # Verify file in storage
        bucket = storage.bucket()
        blob = bucket.blob('integration_test.txt')
        assert blob.exists()

        # Test home page shows uploaded file
        home_response = test_client.get('/')
        assert b'integration_test.txt' in home_response.data

        # Test file deletion
        delete_response = test_client.post('/delete/integration_test.txt')
        assert delete_response.status_code == 302

        # Verify file is deleted
        assert not blob.exists()

    def test_unauthorized_access(self, test_client):
        """Test unauthorized access to protected routes"""
        # Try to access home without login
        home_response = test_client.get('/')
        assert home_response.status_code == 302
        assert b'/login' in home_response.data

        # Try to upload without login
        file_data = {
            'file': (io.BytesIO(b'test'), 'test.txt')
        }
        upload_response = test_client.post('/upload', data=file_data)
        assert upload_response.status_code == 302
        assert b'/login' in upload_response.data

        # Try to delete without login
        delete_response = test_client.post('/delete/test.txt')
        assert delete_response.status_code == 302
        assert b'/login' in delete_response.data