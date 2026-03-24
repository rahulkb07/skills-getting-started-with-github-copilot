"""
Tests for DELETE /activities/{activity_name}/unregister endpoint.

Following AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and client
- Act: Execute the API call
- Assert: Verify the results
"""

import pytest


class TestUnregisterActivity:
    """Test suite for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_successful_unregister_with_valid_activity_and_email(self, app_with_fresh_activities):
        """
        Test successful unregister with valid activity and registered email.
        
        Arrange: TestClient with registered participant
        Act: DELETE /activities/{activity}/unregister with registered email
        Assert: Verify response status 200 and success message
        """
        # Arrange
        client = app_with_fresh_activities
        activity_name = "Chess Club"
        registered_email = "michael@mergington.edu"  # Already registered in Chess Club
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": registered_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert registered_email in data["message"]
        assert activity_name in data["message"]

    def test_error_on_nonexistent_activity_unregister(self, app_with_fresh_activities):
        """
        Test error when activity doesn't exist during unregister (404).
        
        Arrange: TestClient with fake activity name
        Act: DELETE /activities/FakeActivity/unregister with email
        Assert: Verify response status 404
        """
        # Arrange
        client = app_with_fresh_activities
        fake_activity = "NonexistentActivity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{fake_activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_error_when_student_not_registered(self, app_with_fresh_activities):
        """
        Test error when trying to unregister a student who is not registered (400).
        
        Arrange: TestClient, select activity with unregistered email
        Act: DELETE /activities/{activity}/unregister with unregistered email
        Assert: Verify response status 400
        """
        # Arrange
        client = app_with_fresh_activities
        activity_name = "Basketball Team"
        unregistered_email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": unregistered_email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"] or "not" in data["detail"]

    def test_participants_list_updated_after_unregister(self, app_with_fresh_activities):
        """
        Test that participants list is updated after successful unregister.
        
        Arrange: TestClient, select registered participant
        Act: DELETE unregister, then GET /activities
        Assert: Verify email is removed from participants list
        """
        # Arrange
        client = app_with_fresh_activities
        activity_name = "Tennis Club"
        email_to_remove = "james@mergington.edu"  # Already registered in Tennis Club
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_participants = initial_data[activity_name]["participants"].copy()
        
        # Verify email is initially registered
        assert email_to_remove in initial_participants, "Email should be in initial participants"
        
        # Act
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )
        
        # Get updated state
        updated_response = client.get("/activities")
        updated_data = updated_response.json()
        updated_participants = updated_data[activity_name]["participants"]
        
        # Assert
        assert unregister_response.status_code == 200
        assert email_to_remove not in updated_participants, "Email should be removed from participants"
        assert len(updated_participants) == len(initial_participants) - 1

    def test_unregister_multiple_participants_from_same_activity(self, app_with_fresh_activities):
        """
        Test that unregistering one student doesn't affect others in same activity.
        
        Arrange: TestClient, select activity with multiple registered participants
        Act: DELETE unregister for first email
        Assert: Verify other participants remain, only target email is removed
        """
        # Arrange
        client = app_with_fresh_activities
        activity_name = "Programming Class"
        # Both are registered in Programming Class
        email_to_remove = "emma@mergington.edu"
        email_to_keep = "sophia@mergington.edu"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_participants = initial_data[activity_name]["participants"].copy()
        
        # Verify both are in initial participants
        assert email_to_remove in initial_participants
        assert email_to_keep in initial_participants
        
        # Act
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )
        
        # Get updated state
        updated_response = client.get("/activities")
        updated_data = updated_response.json()
        updated_participants = updated_data[activity_name]["participants"]
        
        # Assert
        assert unregister_response.status_code == 200
        assert email_to_remove not in updated_participants, "Target email should be removed"
        assert email_to_keep in updated_participants, "Other participants should remain"
        assert len(updated_participants) == len(initial_participants) - 1

    def test_cannot_unregister_same_student_twice(self, app_with_fresh_activities):
        """
        Test that trying to unregister a student twice results in error on second attempt.
        
        Arrange: TestClient, select registered participant
        Act: DELETE unregister first time (success), then DELETE unregister second time (error)
        Assert: First returns 200, second returns 400
        """
        # Arrange
        client = app_with_fresh_activities
        activity_name = "Gym Class"
        email = "john@mergington.edu"  # Already registered in Gym Class
        
        # Act - First unregister
        response1 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Act - Second unregister attempt
        response2 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response1.status_code == 200, "First unregister should succeed"
        assert response2.status_code == 400, "Second unregister should fail (student not registered)"
        assert "not registered" in response2.json()["detail"]
