import pytest
import json
from app import app, WEAPONS

@pytest.fixture
def client():
    """
    Create a test client for our Flask app.
    
    This fixture configures the app for testing and provides a test client
    that can be used to send requests to the application endpoints.
    """
    app.config['TESTING'] = True  # Enable testing mode
    app.config['SECRET_KEY'] = 'test-key'  # Set a testing secret key for sessions
    with app.test_client() as client:
        yield client  # Return the test client for the tests to use


# This is the simplest test to check for the status code:-
def test_index_route(client):
    """Test that the index route returns 200 status code."""
    # Send a GET request to the root URL
    response = client.get('/')
    # Verify that the response status code is 200 (OK)
    assert response.status_code == 200


# TASK 1
def test_weapons_api_status_code(client):
    """Test that the weapons API returns a 200 status code."""
    # Send a GET request to the weapons API endpoint
    response = client.get('/api/weapons')
    # Verify that the response status code is 200 (OK)
    assert response.status_code == 200



def test_weapons_api(client):
    """Test that the weapons API returns all weapons with correct data."""
    # Send a GET request to the weapons API endpoint
    response = client.get('/api/weapons')
    
    # Parse the JSON response data
    data = json.loads(response.data)
    # Check that the response contains all weapons from our catalog
    assert len(data) == len(WEAPONS)
    # Verify that each weapon has an image URL
    assert all("image" in weapon for weapon in data)
    # Verify specific weapon details are correct
    assert data[0]["name"] == "Assault Rifle"
    assert data[0]["rarity"] == "Rare"


# TASK 2
def test_empty_cart(client):
    """Test that a new session has an empty cart."""
    # Send a GET request to the cart API endpoint
    response = client.get('/api/cart')

    # Verify the response status code is 200 (OK)
    assert response.status_code == 200

    # Parse the JSON response data
    data = json.loads(response.data)

    # Verify the response is a list (Tip Google search how to use assert with isinstance())
    assert isinstance(data, list)

    # Verify the cart is empty (new session)
    assert len(data) == 0


def test_add_to_cart(client):
    """Test adding an item to the cart."""
    # Add weapon with ID 1 to cart using POST request
    response = client.post('/api/cart', 
                          json={"id": 1},  # Send JSON data with weapon ID
                          content_type='application/json')  # Set content type
    # Verify the response status code is 201 (Created)
    assert response.status_code == 201
    
    # Check if cart contains the added weapon by getting cart contents
    response = client.get('/api/cart')
    data = json.loads(response.data)
    # Verify cart has exactly one item
    assert len(data) == 1
    # Verify the weapon ID matches what we added
    assert data[0]["id"] == 1
    # Verify the weapon name is correct
    assert data[0]["name"] == "Assault Rifle"


# TASK 3
def test_add_invalid_weapon(client):
    """Test adding a non-existent weapon ID."""
    # Try to add a weapon with an invalid ID
    response = client.post('/api/cart',
                          json={"id": 9999},
                          content_type='application/json')

    # Verify the response status code is 404 (Not Found)
    assert response.status_code == 404

# TASK 4
# TIP - similar to test_add_to_cart
def test_clear_cart(client):
    """Test clearing the cart."""
    # Add an item to the cart first using /api/cart API
    client.post('/api/cart', json={"id": 1}, content_type='application/json')

    # Clear the cart using the clear endpoint /api/cart/clear
    response = client.post('/api/cart/clear')

    # Verify the response status code is 200 (OK)
    assert response.status_code == 200

    # Verify cart is empty after clearing by using GET /api/cart
    response = client.get('/api/cart')

    # verify that the response status code is 200
    assert response.status_code == 200

    # get response data
    data = json.loads(response.data)

    # verify the length of response data is 0
    assert len(data) == 0


def test_remove_from_cart(client):
    """Test removing an item from the cart."""
    # Add two items to the cart
    client.post('/api/cart', json={"id": 1}, content_type='application/json')
    client.post('/api/cart', json={"id": 2}, content_type='application/json')
    
    # Remove one item using the remove endpoint
    response = client.post('/api/cart/remove/1')
    # Verify the response status code is 200 (OK)
    assert response.status_code == 200
    
    # Verify only one item remains and it's the correct one
    response = client.get('/api/cart')
    data = json.loads(response.data)
    # Check cart has exactly one item left
    assert len(data) == 1
    # Verify the remaining item is the one that wasn't removed
    assert data[0]["id"] == 2

# TASK 5
def test_remove_nonexistent_item(client):
    """Test removing an item that isn't in the cart."""
    # Try to remove an item that doesn't exist in the cart
    response = client.post('/api/cart/remove/9999')

    # Verify the response status code is 404 (Not Found)
    assert response.status_code == 404