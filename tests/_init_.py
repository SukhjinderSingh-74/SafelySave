# tests/__init__.py

import pytest
import os
import sys

# Add the parent directory to PYTHONPATH so tests can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Shared test configuration
pytest_plugins = []

# Common test constants
TEST_CONFIG = {
    'TESTING': True,
    'SECRET_KEY': 'test_secret_key',
    'FIREBASE_BUCKET': 'safe-upload-3e2d8.firebasestorage.app'
}

# Shared fixtures that can be used across all test files
@pytest.fixture(scope='session')
def app_config():
    """Provides base configuration for test app"""
    return TEST_CONFIG

@pytest.fixture(scope='session')
def test_file_content():
    """Provides standard test file content for file operation tests"""
    return b"Test file content for unit and integration tests"

# Helper functions that might be useful across test files
def create_test_file(filename, content=None):
    """Helper function to create test files"""
    if content is None:
        content = b"Default test content"
    return {
        'filename': filename,
        'content': content
    }

def get_firebase_test_config():
    """Helper function to get Firebase test configuration"""
    return {
        'storageBucket': TEST_CONFIG['FIREBASE_BUCKET']
    }