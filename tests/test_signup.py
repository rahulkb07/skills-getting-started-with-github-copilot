"""
Tests for POST /activities/{activity_name}/signup endpoint.

Following AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and client
- Act: Execute the API call
- Assert: Verify the results
"""

import pytest


class TestSignupActivity:
    """Test suite for the POST /activities/{activity_name}/signup endpoint."""

    def test_successful_signup_with_valid_activity_and_email(self, app_with_fresh_activities):
        """
        Test successful signup with valid activity and email.
        
        Arrange: TestClient, select existing activity and new email
        Act: POST /activities/{activity}/signup with email
        Assert: Verify response status 200 and success message
        """
        # Arrange
        client = app_with_fresh_activities
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert new_email in data["message"]
        assert activity_name in data["message"]

    def test_error_on_nonexistent_activity(self, app_with_fresh_activities):
        """
        Test error when activity doesn't exist (404).
        
        Arrange: TestClient with fake activity name
        Act: POST /activities/FakeActivity/signup with email
        Assert: Verify response status 404 with "Activity not found"
        """
        # Arrange
        client = app_with_fresh_activities
        fake_activity = "NonexistentActivity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_error_on_duplicate_signup(self, app_with_fresh_activities):
        """
        Test error when student tries to sign up for same activity twice (400).
        
        Arrange: TestClient, select activity with existing participant
        Act: POST /activities/{activity}/signup with already-registered email
        Assert: Verify response status 400 with duplicate message
        """
        # Arrange
        client = app_with_fresh_activities
        activity_name = "Chess Club"
        # Use an email that already exists in Chess Club participants
        existing_email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already registered" in data["detail"] or "already" in data["detail"]

    def test_participants_list_updated_after_signup(self, app_with_fresh_activities):
        """
        Test that participants list is updated after successful signup.
        
        Arrange: TestClient, note initial state
        Act: POST signup, then GET /activities
        Assert: Verify new email appears in activity's participants list
        """
        # Arrange
        client = app_with_fresh_activities
        activity_name = "Tennis Club"
        new_email = "newtennis@mergington.edu"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_participants = initial_data[activity_name]["participants"].copy()
        
        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Get updated state
        updated_response = client.get("/activities")
        updated_data = updated_response.json()
        updated_participants = updated_data[activity_name]["participants"]
        
        # Assert
        assert signup_response.status_code == 200
        assert new_email not in initial_participants, "Email should not be in initial participants"
        assert new_email in updated_participants, "Email should be in updated participants"
        assert len(updated_participants) == len(initial_participants) + 1

    def test_signup_with_multiple_different_emails(self, app_with_fresh_activities):
        """
        Test that multiple different students can sign up for the same activity.
        
        Arrange: TestClient, select activity and two unique emails
        Act: POST signup for first email, then POST signup for second email
        Assert: Verify both emails are in participants list
        """
        # Arrange
        client = app_with_fresh_activities
        activity_name = "Drama Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        
        # Get final state
        final_response = client.get("/activities")
        final_data = final_response.json()
        final_participants = final_data[activity_name]["participants"]
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email1 in final_participants
        assert email2 in final_participants
