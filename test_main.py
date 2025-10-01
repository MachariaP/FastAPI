"""
Comprehensive test suite for main.py FastAPI application.

This test suite covers all endpoints, edge cases, and error scenarios
to ensure 100% code coverage and robust functionality.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
import jwt
from main import (
    app,
    users_db,
    items_db,
    user_counter,
    item_counter,
    SECRET_KEY,
    ALGORITHM,
    create_access_token,
)


@pytest.fixture(autouse=True)
def reset_databases():
    """Reset databases before each test."""
    global user_counter, item_counter
    users_db.clear()
    items_db.clear()

    # Re-add the default admin user
    from main import user_counter as uc

    users_db.append(
        {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "full_name": "Administrator",
            "password_hash": "hashed_password",
            "created_at": datetime.now(timezone.utc),
            "is_active": True,
        }
    )
    yield
    # Cleanup after test
    users_db.clear()
    items_db.clear()


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def admin_token():
    """Generate an admin token for authenticated requests."""
    return create_access_token(data={"sub": "admin"})


@pytest.fixture
def test_user_token(client):
    """Create a test user and return their token."""
    # Register a test user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201

    # Login and get token
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpassword123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


class TestHealthEndpoints:
    """Test health check and configuration endpoints."""

    def test_root_health_check(self, client):
        """Test the root health check endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "FastAPI is running!"
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"

    def test_detailed_health_check(self, client):
        """Test the detailed health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "database" in data
        assert data["version"] == "1.0.0"

    def test_config_endpoint(self, client):
        """Test the configuration endpoint."""
        response = client.get("/config")
        assert response.status_code == 200
        data = response.json()
        assert "app_name" in data
        assert "app_version" in data
        assert "environment" in data
        assert "debug" in data


class TestAuthenticationHelp:
    """Test authentication help and info endpoints."""

    def test_auth_help(self, client):
        """Test the authentication help endpoint."""
        response = client.get("/auth/help")
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "steps" in data
        assert "examples" in data
        assert "protected_endpoints" in data
        assert "public_endpoints" in data

    def test_api_info(self, client):
        """Test the API information endpoint."""
        response = client.get("/api/info")
        assert response.status_code == 200
        data = response.json()
        assert data["api_name"] == "Comprehensive FastAPI Example"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
        assert "authentication_flow" in data
        assert "features" in data


class TestUserRegistration:
    """Test user registration endpoint."""

    def test_register_info(self, client):
        """Test GET request to register endpoint for information."""
        response = client.get("/auth/register")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "required_fields" in data
        assert "example" in data

    def test_successful_registration(self, client):
        """Test successful user registration."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword123",
            "full_name": "New User",
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "password" not in data
        assert "id" in data
        assert data["is_active"] is True

    def test_registration_duplicate_username(self, client):
        """Test registration with duplicate username."""
        user_data = {
            "username": "admin",
            "email": "newemail@example.com",
            "password": "password123",
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]

    def test_registration_duplicate_email(self, client):
        """Test registration with duplicate email."""
        user_data = {
            "username": "newuser",
            "email": "admin@example.com",
            "password": "password123",
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_registration_invalid_email(self, client):
        """Test registration with invalid email format."""
        user_data = {
            "username": "newuser",
            "email": "invalid-email",
            "password": "password123",
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 422

    def test_registration_short_password(self, client):
        """Test registration with password less than 8 characters."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "short",
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 422

    def test_registration_short_username(self, client):
        """Test registration with username less than 3 characters."""
        user_data = {
            "username": "ab",
            "email": "newuser@example.com",
            "password": "password123",
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 422


class TestUserLogin:
    """Test user login endpoint."""

    def test_login_info(self, client):
        """Test GET request to login endpoint for information."""
        response = client.get("/auth/login")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "required_parameters" in data
        assert "default_user" in data

    def test_successful_login(self, client):
        """Test successful login with admin credentials."""
        response = client.post(
            "/auth/login",
            data={"username": "admin", "password": "password"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_username(self, client):
        """Test login with non-existent username."""
        response = client.post(
            "/auth/login",
            data={"username": "nonexistent", "password": "password"},
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_wrong_password(self, client):
        """Test login with incorrect password."""
        response = client.post(
            "/auth/login",
            data={"username": "admin", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_missing_credentials(self, client):
        """Test login with missing credentials."""
        response = client.post("/auth/login", data={})
        assert response.status_code == 422


class TestAuthenticatedUser:
    """Test authenticated user endpoints."""

    def test_get_current_user(self, client, admin_token):
        """Test getting current authenticated user."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["email"] == "admin@example.com"

    def test_get_current_user_no_token(self, client):
        """Test getting current user without token."""
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401

    def test_get_current_user_expired_token(self, client):
        """Test getting current user with expired token."""
        expired_token = create_access_token(
            data={"sub": "admin"}, expires_delta=timedelta(seconds=-1)
        )
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()


class TestUserManagement:
    """Test user management endpoints."""

    def test_get_all_users(self, client, admin_token):
        """Test getting all users."""
        response = client.get(
            "/users",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_all_users_no_auth(self, client):
        """Test getting all users without authentication."""
        response = client.get("/users")
        assert response.status_code == 401

    def test_get_all_users_with_pagination(self, client, admin_token):
        """Test getting users with pagination."""
        response = client.get(
            "/users?skip=0&limit=10",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_user_by_id(self, client, admin_token):
        """Test getting user by ID."""
        response = client.get(
            "/users/1",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["username"] == "admin"

    def test_get_user_by_id_not_found(self, client, admin_token):
        """Test getting non-existent user."""
        response = client.get(
            "/users/999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404


class TestItemManagement:
    """Test item CRUD operations."""

    def test_get_items_empty(self, client):
        """Test getting items when database is empty."""
        response = client.get("/items")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0

    def test_create_item(self, client, admin_token):
        """Test creating a new item."""
        item_data = {
            "name": "Test Item",
            "description": "A test item",
            "price": 99.99,
            "category": "Electronics",
        }
        response = client.post(
            "/items",
            json=item_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Item"
        assert data["price"] == 99.99
        assert "id" in data
        assert "owner_id" in data

    def test_create_item_no_auth(self, client):
        """Test creating item without authentication."""
        item_data = {
            "name": "Test Item",
            "price": 99.99,
            "category": "Electronics",
        }
        response = client.post("/items", json=item_data)
        assert response.status_code == 401

    def test_create_item_invalid_price(self, client, admin_token):
        """Test creating item with invalid price."""
        item_data = {
            "name": "Test Item",
            "price": -10.00,
            "category": "Electronics",
        }
        response = client.post(
            "/items",
            json=item_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 422

    def test_get_item_by_id(self, client, admin_token):
        """Test getting item by ID."""
        # Create an item first
        item_data = {
            "name": "Test Item",
            "description": "A test item",
            "price": 99.99,
            "category": "Electronics",
        }
        create_response = client.post(
            "/items",
            json=item_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        item_id = create_response.json()["id"]

        # Get the item
        response = client.get(f"/items/{item_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
        assert data["name"] == "Test Item"

    def test_get_item_by_id_not_found(self, client):
        """Test getting non-existent item."""
        response = client.get("/items/999")
        assert response.status_code == 404

    def test_update_item(self, client, admin_token):
        """Test updating an item."""
        # Create an item first
        item_data = {
            "name": "Test Item",
            "price": 99.99,
            "category": "Electronics",
        }
        create_response = client.post(
            "/items",
            json=item_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        item_id = create_response.json()["id"]

        # Update the item
        update_data = {"name": "Updated Item", "price": 149.99}
        response = client.put(
            f"/items/{item_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Item"
        assert data["price"] == 149.99

    def test_update_item_not_found(self, client, admin_token):
        """Test updating non-existent item."""
        update_data = {"name": "Updated Item"}
        response = client.put(
            "/items/999",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404

    def test_update_item_not_owner(self, client, test_user_token, admin_token):
        """Test updating item by non-owner (should fail unless admin)."""
        # Admin creates an item
        item_data = {
            "name": "Admin Item",
            "price": 99.99,
            "category": "Electronics",
        }
        create_response = client.post(
            "/items",
            json=item_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        item_id = create_response.json()["id"]

        # Test user tries to update admin's item
        update_data = {"name": "Stolen Item"}
        response = client.put(
            f"/items/{item_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {test_user_token}"},
        )
        assert response.status_code == 403

    def test_delete_item(self, client, admin_token):
        """Test deleting an item."""
        # Create an item first
        item_data = {
            "name": "Test Item",
            "price": 99.99,
            "category": "Electronics",
        }
        create_response = client.post(
            "/items",
            json=item_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        item_id = create_response.json()["id"]

        # Delete the item
        response = client.delete(
            f"/items/{item_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 204

        # Verify item is deleted
        get_response = client.get(f"/items/{item_id}")
        assert get_response.status_code == 404

    def test_delete_item_not_found(self, client, admin_token):
        """Test deleting non-existent item."""
        response = client.delete(
            "/items/999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404

    def test_delete_item_not_owner(self, client, test_user_token, admin_token):
        """Test deleting item by non-owner (should fail unless admin)."""
        # Admin creates an item
        item_data = {
            "name": "Admin Item",
            "price": 99.99,
            "category": "Electronics",
        }
        create_response = client.post(
            "/items",
            json=item_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        item_id = create_response.json()["id"]

        # Test user tries to delete admin's item
        response = client.delete(
            f"/items/{item_id}",
            headers={"Authorization": f"Bearer {test_user_token}"},
        )
        assert response.status_code == 403


class TestItemFiltering:
    """Test item filtering and search functionality."""

    def test_get_items_with_pagination(self, client, admin_token):
        """Test getting items with pagination."""
        # Create multiple items
        for i in range(5):
            item_data = {
                "name": f"Item {i}",
                "price": 10.0 + i,
                "category": "Electronics",
            }
            client.post(
                "/items",
                json=item_data,
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        response = client.get("/items?skip=0&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 5

    def test_get_items_filter_by_category(self, client, admin_token):
        """Test filtering items by category."""
        # Create items in different categories
        categories = ["Electronics", "Books", "Electronics"]
        for i, category in enumerate(categories):
            item_data = {
                "name": f"Item {i}",
                "price": 10.0 + i,
                "category": category,
            }
            client.post(
                "/items",
                json=item_data,
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        response = client.get("/items?category=Electronics")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    def test_get_items_search(self, client, admin_token):
        """Test searching items by name/description."""
        # Create items with different names
        items = [
            {"name": "Laptop Computer", "price": 999.99, "category": "Electronics"},
            {"name": "Python Book", "price": 29.99, "category": "Books"},
            {"name": "Gaming Laptop", "price": 1499.99, "category": "Electronics"},
        ]
        for item_data in items:
            client.post(
                "/items",
                json=item_data,
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        response = client.get("/items?search=laptop")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    def test_get_items_price_range(self, client, admin_token):
        """Test filtering items by price range."""
        # Create items with different prices
        for i in range(3):
            item_data = {
                "name": f"Item {i}",
                "price": 100.0 * (i + 1),
                "category": "Electronics",
            }
            client.post(
                "/items",
                json=item_data,
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        response = client.get("/items?min_price=150&max_price=250")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1


class TestAdvancedItemSearch:
    """Test advanced item search endpoint."""

    def test_advanced_search_basic(self, client, admin_token):
        """Test basic advanced search."""
        # Create test items
        item_data = {
            "name": "Test Laptop",
            "description": "A great laptop",
            "price": 999.99,
            "category": "Electronics",
        }
        client.post(
            "/items",
            json=item_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        response = client.get("/items/search?q=laptop")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["name"] == "Test Laptop"

    def test_advanced_search_with_category(self, client, admin_token):
        """Test advanced search with category filter."""
        # Create items in different categories
        items = [
            {"name": "Item 1", "price": 99.99, "category": "Electronics"},
            {"name": "Item 2", "price": 29.99, "category": "Books"},
        ]
        for item_data in items:
            client.post(
                "/items",
                json=item_data,
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        response = client.get("/items/search?category=Electronics")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "Electronics"

    def test_advanced_search_price_range(self, client, admin_token):
        """Test advanced search with price range."""
        items = [
            {"name": "Cheap Item", "price": 10.0, "category": "Books"},
            {"name": "Expensive Item", "price": 1000.0, "category": "Electronics"},
        ]
        for item_data in items:
            client.post(
                "/items",
                json=item_data,
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        response = client.get("/items/search?min_price=100&max_price=2000")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Expensive Item"

    def test_advanced_search_sorting(self, client, admin_token):
        """Test advanced search with sorting."""
        items = [
            {"name": "B Item", "price": 50.0, "category": "Electronics"},
            {"name": "A Item", "price": 100.0, "category": "Electronics"},
        ]
        for item_data in items:
            client.post(
                "/items",
                json=item_data,
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        # Sort by name ascending
        response = client.get("/items/search?sort_by=name&sort_order=asc")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "A Item"

        # Sort by price descending
        response = client.get("/items/search?sort_by=price&sort_order=desc")
        assert response.status_code == 200
        data = response.json()
        assert data[0]["price"] == 100.0


class TestItemCategories:
    """Test item categories endpoint."""

    def test_get_categories_empty(self, client):
        """Test getting categories when no items exist."""
        response = client.get("/items/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_categories_with_items(self, client, admin_token):
        """Test getting categories with items."""
        # Create items in different categories
        items = [
            {"name": "Item 1", "price": 100.0, "category": "Electronics"},
            {"name": "Item 2", "price": 50.0, "category": "Electronics"},
            {"name": "Item 3", "price": 20.0, "category": "Books"},
        ]
        for item_data in items:
            client.post(
                "/items",
                json=item_data,
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        response = client.get("/items/categories")
        assert response.status_code == 200
        data = response.json()
        assert "Electronics" in data
        assert "Books" in data
        assert data["Electronics"]["count"] == 2
        assert data["Books"]["count"] == 1
        assert data["Electronics"]["avg_price"] == 75.0


class TestUserItems:
    """Test getting user's items."""

    def test_get_user_items(self, client, admin_token):
        """Test getting items for a specific user."""
        # Create items
        item_data = {
            "name": "Admin Item",
            "price": 99.99,
            "category": "Electronics",
        }
        client.post(
            "/items",
            json=item_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        response = client.get(
            "/users/1/items",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_user_items_not_authorized(self, client, test_user_token):
        """Test getting another user's items without permission."""
        response = client.get(
            "/users/1/items",
            headers={"Authorization": f"Bearer {test_user_token}"},
        )
        assert response.status_code == 403


class TestStatistics:
    """Test statistics endpoint."""

    def test_get_statistics(self, client, admin_token):
        """Test getting application statistics."""
        # Create some items first
        for i in range(3):
            item_data = {
                "name": f"Item {i}",
                "price": 100.0 + i * 10,
                "category": "Electronics",
            }
            client.post(
                "/items",
                json=item_data,
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        response = client.get(
            "/stats",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_items" in data
        assert "your_items" in data
        assert "categories" in data
        assert "average_price" in data
        assert data["total_items"] == 3

    def test_get_statistics_no_auth(self, client):
        """Test getting statistics without authentication."""
        response = client.get("/stats")
        assert response.status_code == 401


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_validation_error_handling(self, client):
        """Test that validation errors are properly handled."""
        # Missing required fields
        response = client.post("/auth/register", json={})
        assert response.status_code == 422

    def test_404_not_found(self, client):
        """Test 404 error for non-existent routes."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_token_with_nonexistent_user(self, client):
        """Test token for user that doesn't exist in database."""
        # Create token for non-existent user
        fake_token = create_access_token(data={"sub": "nonexistentuser"})
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {fake_token}"},
        )
        assert response.status_code == 401

    def test_malformed_token(self, client):
        """Test request with malformed token."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer not.a.real.token"},
        )
        assert response.status_code == 401


class TestMiddleware:
    """Test middleware functionality."""

    def test_request_logging(self, client):
        """Test that requests are logged (basic check)."""
        # Make a request and check it completes successfully
        response = client.get("/")
        assert response.status_code == 200


class TestModels:
    """Test Pydantic models and validation."""

    def test_item_model_validation(self, client, admin_token):
        """Test item model validation."""
        # Test with missing required fields
        response = client.post(
            "/items",
            json={"name": "Test"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 422

    def test_user_model_validation(self, client):
        """Test user model validation."""
        # Test with invalid data types
        response = client.post(
            "/auth/register",
            json={"username": 123, "email": "test@test.com", "password": "password123"},
        )
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=main", "--cov-report=html", "--cov-report=term"])
