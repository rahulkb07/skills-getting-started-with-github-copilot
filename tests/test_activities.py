"""
Tests for GET /activities endpoint.

Following AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and client
- Act: Execute the API call
- Assert: Verify the results
"""

import pytest


class TestGetActivities:
    """Test suite for the GET /activities endpoint."""

    def test_returns_all_activities_with_correct_structure(self, app_with_fresh_activities):
        """
        Test that GET /activities returns all activities with correct structure.
        
        Arrange: Initialize TestClient
        Act: Call GET /activities
        Assert: Verify response status 200 and contains all 9 activities with required fields
        """
        # Arrange
        client = app_with_fresh_activities
        expected_activity_count = 9
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == expected_activity_count
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Basketball Team" in data
        assert "Tennis Club" in data
        assert "Drama Club" in data
        assert "Art Studio" in data
        assert "Debate Team" in data
        assert "Science Club" in data

    def test_validates_activity_properties_exist(self, app_with_fresh_activities):
        """
        Test that each activity has all required properties.
        
        Arrange: Initialize TestClient
        Act: Call GET /activities
        Assert: Verify each activity has description, schedule, max_participants, participants keys
        """
        # Arrange
        client = app_with_fresh_activities
        required_properties = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data, dict), f"{activity_name} should be a dict"
            assert required_properties.issubset(
                activity_data.keys()
            ), f"{activity_name} missing required properties"
            
            # Also validate property types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)

    def test_confirms_activities_dict_not_empty(self, app_with_fresh_activities):
        """
        Test that activities dictionary is not empty.
        
        Arrange: Initialize TestClient
        Act: Call GET /activities
        Assert: Verify response contains activities and length > 0
        """
        # Arrange
        client = app_with_fresh_activities
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert len(data) > 0, "Activities should not be empty"
        assert data, "Activities response should be truthy"
