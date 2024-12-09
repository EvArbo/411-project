#!/bin/bash

# Set the base URL for the Flask API to be tested
BASE_URL="http://127.0.0.1:5000"

############################################
# Helper Functions
# These functions test different API endpoints and validate responses
############################################

# Checks if the API service is running and responsive
check_health() {
  echo "Checking health status..."
  # Send a health check request to the API
  response=$(curl -s "$BASE_URL/health")
  # Verify if the response indicates a healthy status
  echo "$response" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed: $response"
    exit 1
  fi
}

# Creates a new user account via the API
create_user() {
  echo "Creating a test user account..."
  # Send a POST request to create a user with predefined credentials
  response=$(curl -s -X POST -H "Content-Type: application/json" -d '{"username": "testuser7", "password": "password123"}' "$BASE_URL/create-account")
  # Check if the account creation was successful
  echo "$response" | grep -q '"message": "Account created successfully."'
  if [ $? -eq 0 ]; then
    echo "User account creation passed!"
  else
    echo "User account creation failed: $response"
    exit 1
  fi
}

# Attempts to log in with the created user credentials
login_user() {
  echo "Testing user login..."
  # Send a POST request to log in with user credentials
  response=$(curl -s -X POST -H "Content-Type: application/json" -d '{"username": "testuser7", "password": "password123"}' "$BASE_URL/login")
  # Verify if login was successful
  echo "$response" | grep -q '"message": "Login successful."'
  if [ $? -eq 0 ]; then
    echo "User login passed!"
  else
    echo "User login failed: $response"
    exit 1
  fi
}

# Adds a food/ingredient to the user's list by its ID
add_food() {
  food_id=$1
  echo "Adding food ID $food_id..."
  # Send a POST request to add a specific food item
  response=$(curl -s -X POST "$BASE_URL/food/add/$food_id")
  # Check if the food was added successfully
  echo "$response" | grep -q '"message": "Ingredient added."'
  if [ $? -eq 0 ]; then
    echo "Add food passed!"
  else
    echo "Add food failed: $response"
    exit 1
  fi
}

# Retrieves the list of food items for the current user
get_food_list() {
  echo "Retrieving user's food list..."
  # Send a GET request to fetch the food list
  response=$(curl -s -X GET "$BASE_URL/food/list")
  # Verify that the response contains a list of ingredients
  echo "$response" | grep -q '"stored_ingredients"'
  if [ $? -eq 0 ]; then
    echo "Get food list passed!"
  else
    echo "Get food list failed: $response"
    exit 1
  fi
}

# Updates the details of a specific food item
update_food() {
  food_id=$1
  echo "Updating food ID $food_id..."
  # Send a PUT request to update a food item's details
  response=$(curl -s -X PUT -H "Content-Type: application/json" -d '{"new_name": "Updated Food"}' "$BASE_URL/food/update/$food_id")
  
  # Check if the food update was successful
  echo "$response" | grep -q '"message": "Ingredient updated."'
  if [ $? -eq 0 ]; then
    echo "Update food passed!"
  else
    echo "Update food failed: $response"
    exit 1
  fi
}

# Deletes a specific food item from the user's list
delete_food() {
  food_id=$1
  echo "Deleting food ID $food_id..."
  # Send a DELETE request to remove a food item
  response=$(curl -s -X DELETE "$BASE_URL/food/delete/$food_id")
  # Verify if the deletion was successful
  echo "$response" | grep -q '"message": "Ingredient deleted."'
  if [ $? -eq 0 ]; then
    echo "Delete food passed!"
  else
    echo "Delete food failed: $response"
    exit 1
  fi
}

############################################
# Smoke Test Execution
# Runs a series of tests to verify API functionality
############################################

# Step 1: Verify the service is up and running
check_health

# Step 2: Test user login functionality (currently commented out)
# create_user
# login_user

# Step 3: Test food ingredient functionality
# Add two specific food items by their IDs
add_food 524878    # Add "Biscuit Tablette Chocolat au Lait bio"
add_food 129981    # Add "Beef Madras"

# Retrieve and verify the food list
get_food_list

# Update and delete food items to test CRUD operations
update_food 524878  # Update "Biscuit Tablette Chocolat au Lait bio"
delete_food 129981  # Delete "Beef Madras"

# Verify the food list after modifications
get_food_list

# Final confirmation that all tests passed
echo "All smoke tests passed successfully!"
