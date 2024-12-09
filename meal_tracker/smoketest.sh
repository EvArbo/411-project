#!/bin/bash

# Base URL for the Flask API
BASE_URL="http://127.0.0.1:5000"

############################################
# Helper Functions
############################################

check_health() {
  echo "Checking health status..."
  response=$(curl -s "$BASE_URL/health")
  echo "$response" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed: $response"
    exit 1
  fi
}

create_user() {
  echo "Creating a test user account..."
  response=$(curl -s -X POST -H "Content-Type: application/json" -d '{"username": "testuser7", "password": "password123"}' "$BASE_URL/create-account")
  echo "$response" | grep -q '"message": "Account created successfully."'
  if [ $? -eq 0 ]; then
    echo "User account creation passed!"
  else
    echo "User account creation failed: $response"
    exit 1
  fi
}

login_user() {
  echo "Testing user login..."
  response=$(curl -s -X POST -H "Content-Type: application/json" -d '{"username": "testuser7", "password": "password123"}' "$BASE_URL/login")
  echo "$response" | grep -q '"message": "Login successful."'
  if [ $? -eq 0 ]; then
    echo "User login passed!"
  else
    echo "User login failed: $response"
    exit 1
  fi
}

add_food() {
  food_id=$1
  echo "Adding food ID $food_id..."
  response=$(curl -s -X POST "$BASE_URL/food/add/$food_id")
  echo "$response" | grep -q '"message": "Ingredient added."'
  if [ $? -eq 0 ]; then
    echo "Add food passed!"
  else
    echo "Add food failed: $response"
    exit 1
  fi
}

get_food_list() {
  echo "Retrieving user's food list..."
  response=$(curl -s -X GET "$BASE_URL/food/list")
  echo "$response" | grep -q '"stored_ingredients"'
  if [ $? -eq 0 ]; then
    echo "Get food list passed!"
  else
    echo "Get food list failed: $response"
    exit 1
  fi
}

update_food() {
  food_id=$1
  echo "Updating food ID $food_id..."
  response=$(curl -s -X PUT -H "Content-Type: application/json" -d '{"new_name": "Updated Food"}' "$BASE_URL/food/update/$food_id")
  
  echo "$response" | grep -q '"message": "Ingredient updated."'
  if [ $? -eq 0 ]; then
    echo "Update food passed!"
  else
    echo "Update food failed: $response"
    exit 1
  fi
}

delete_food() {
  food_id=$1
  echo "Deleting food ID $food_id..."
  response=$(curl -s -X DELETE "$BASE_URL/food/delete/$food_id")
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
############################################

# Step 1: Check service health
check_health

# Step 2: Test user login functionality
# create_user
# login_user

# Step 3: Test food ingredient functionality
add_food 524878    # Add "Biscuit Tablette Chocolat au Lait bio"
add_food 129981    # Add "Beef Madras"
get_food_list
update_food 524878  # Update "Biscuit Tablette Chocolat au Lait bio"
delete_food 129981  # Delete "Beef Madras"
get_food_list

echo "All smoke tests passed successfully!"