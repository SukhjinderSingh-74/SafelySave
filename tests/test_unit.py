# tests/test_unit.py

import pytest
from unittest.mock import Mock, patch
from app import app
import io


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_firebase():
    with patch('firebase_admin.credentials.Certificate') as mock_cred, \
            patch('firebase_admin.initialize_app') as mock_init, \
            patch('firebase_admin.firestore.client') as mock_db, \
            patch('firebase_admin.storage.bucket') as mock_bucket:
        mock_bucket_instance = Mock()
        mock_bucket.return_value = mock_bucket_instance

        yield {
            'bucket': mock_bucket_instance,
            'cred': mock_cred,
            'init': mock_init
        }


class TestLogin:
    def test_login_get(self, client):
        """Test GET request to login page"""
        response = client.get('/login')
        assert response.status_code == 200

    def test_login_success(self, client):
        """Test successful login"""
        with patch('firebase_admin.auth.get_user_by_email') as mock_auth:
            mock_user = Mock()
            mock_user.uid = 'test123'
            mock_auth.return_value = mock_user

            response = client.post('/login', data={
                'email': 'test@test.com',
                'password': 'password123'
            }, follow_redirects=True)

            assert response.status_code == 200

    def test_login_failure(self, client):
        """Test failed login"""
        with patch('firebase_admin.auth.get_user_by_email') as mock_auth:
            mock_auth.side_effect = Exception('Invalid credentials')

            response = client.post('/login', data={
                'email': 'wrong@test.com',
                'password': 'wrongpass'
            })

            assert b'Invalid credentials or user not found' in response.data


class TestHome:
    def test_home_authenticated(self, client, mock_firebase):
        """Test home page access when authenticated"""
        with client.session_transaction() as session:
            session['user'] = 'test123'

        # Mock storage bucket list_blobs
        mock_blob = Mock()
        mock_blob.name = 'test.txt'
        mock_blob.public_url = 'http://test.com/test.txt'
        mock_firebase['bucket'].list_blobs.return_value = [mock_blob]

        response = client.get('/')
        assert response.status_code == 200
        assert b'test.txt' in response.data

    def test_home_unauthenticated(self, client):
        """Test home page access when not authenticated"""
        response = client.get('/')
        assert response.status_code == 302  # Redirect to login


class TestFileOperations:
    def test_upload_file_authenticated(self, client, mock_firebase):
        """Test file upload when authenticated"""
        with client.session_transaction() as session:
            session['user'] = 'test123'

        # Create mock file
        file_content = b'Test file content'
        data = {
            'file': (io.BytesIO(file_content), 'test.txt')
        }

        mock_blob = Mock()
        mock_firebase['bucket'].blob.return_value = mock_blob

        response = client.post('/upload', data=data)
        assert response.status_code == 302
        mock_firebase['bucket'].blob.assert_called_once_with('test.txt')

    def test_delete_file_authenticated(self, client, mock_firebase):
        """Test file deletion when authenticated"""
        with client.session_transaction() as session:
            session['user'] = 'test123'

        mock_blob = Mock()
        mock_firebase['bucket'].blob.return_value = mock_blob

        response = client.post('/delete/test.txt')
        assert response.status_code == 302
        mock_firebase['bucket'].blob.assert_called_once_with('test.txt')
        mock_blob.delete.assert_called_once()


class TestLogout:
    def test_logout(self, client):
        """Test logout functionality"""
        with client.session_transaction() as session:
            session['user'] = 'test123'

        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

        with client.session_transaction() as session:
            assert 'user' not in session