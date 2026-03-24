"""
Shared pytest fixtures for FastAPI application tests.

This module provides:
- FastAPI TestClient fixture for making test requests
- Sample activities data fixture for test setup
"""

import pytest
from fastapi.testclient import TestClient
from copy import deepcopy
import sys
from pathlib import Path
from unittest.mock import patch

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import app as app_module
from app import app, activities


@pytest.fixture
def client():
    """
    Fixture: FastAPI TestClient
    
    Provides a test client for making HTTP requests to the application.
    """
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """
    Fixture: Sample activities data
    
    Provides a fresh deep copy of the activities dictionary for each test.
    This ensures test isolation - modifications in one test don't affect others.
    
    Returns:
        dict: A copy of the activities dictionary with all sample data
    """
    return deepcopy(activities)


@pytest.fixture
def app_with_fresh_activities(client, sample_activities):
    """
    Fixture: Application with fresh activities data
    
    Resets the app module's activities dictionary to a fresh copy before each test.
    This ensures each test starts with the original state.
    
    Yields:
        TestClient: The test client with fresh activities data
    """
    # Store original activities reference
    original_activities = deepcopy(app_module.activities)
    
    # Replace with fresh copy by clearing and updating the dict
    app_module.activities.clear()
    app_module.activities.update(deepcopy(sample_activities))
    
    yield client
    
    # Restore original after test
    app_module.activities.clear()
    app_module.activities.update(original_activities)
