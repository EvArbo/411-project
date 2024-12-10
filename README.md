Google Doc of Formatted README file: https://docs.google.com/document/d/1cbagQ2LKVb2h2vnXpsTZcGNkiww9Xb0cG5U-d1LhGYM/edit?usp=sharing

# 411-project    -    Meal-Tracker
Meal Tracker by
Harrison hche@bu.edu, 
Evan evanda@bu.edu,
Beren bydonmez@bu.edu

Notes for Grading: The berensnewbranch2 and meal-max copy was worked on initially. Then we met and decided to make a meal-tracker during our daily meetings instead of the workout model you are seeing if you look at the different branches. 

  Our app is a meal-tracking and nutrition management system in order to help people track their dietary intakes. It provides an easy and comprehensive way of doing this. Meal tracker makes use of the Wger API to fetch detailed nutritional information about different food ingredients, which lets users build a personalized database. Moreover, users can create accounts,  authenticate themselves, and then interact with our food management system where they can add, update, retrieve, and delete ingredients from their  food inventory. We aimed to make our app follow a modular approach so there are distinct components handling user authentication, food ingredient management, and database interactions. We implemented password hashing and storage in the user model, ensuring user credentials are protected. The food model on the other hand is a flexible interface for retrieving nutritional data, with functions that we implemented to  allow our users to fetch ingredient details by ID, store those ingredients locally, and perform  CRUD (Create, Read, Update, Delete) operations on their food list. A bash-based smoke test script further validates the application's functionality by systematically testing various API endpoints, including health checks, user account creation, login processes, and food ingredient management operations. Here is a screenshot of our smoketest working:

![smoketest image](smoketestscreenshotmealtracker.PNG)

How to run the Meal Tracker Application:
1. In terminal, run: docker build -t meal-tracker-app .
2. Then run: docker run -p 5000:5000 meal-tracker-app
3. In a new terminal (like Git Bash), run: ./smoketest.sh


Route: /
Request Type: GET
Purpose: Returns a welcome message for the application.
Request Format:
No GET parameters
Request Example:
GET /
Response Example:
String: “Welcome to the Meal Tracker App!”

Route: /health
Request Type: GET
Purpose: Verifies that the app is running.
Request Format: JSON
No GET parameters
Request Example:
GET /health
Response Example:
Code: 200
Content:
{ “status: “healthy” }

Route: /food/add/<int:ingredient_id>
Request Type: POST
Purpose: Adds a new ingredient to stored_ingredients dictionary based on the ingredient ID.
Request Format: JSON
No POST Body
ingredient_id (Integer): Ingredient ID of the ingredient that should be added.
Request Example:
cURL: /food/add/1
Response Example:
 Code: 201
 Content: 
{
"status": "success",
“message”: “Ingredient added.”,
“ingredient”: 
	{
		“id": 1,
"name": "Tomato",
"energy": 50,
"protein": 2.5,
"carbohydrates": 10,
"fat": 1,
"fiber": 3
}
			}

Route: /food/update/<int:ingredient_id>
Request Type: PUT
Purpose: Updates the ingredient by ID in stored_ingredients dictionary.
Request Format: JSON
PUT Body:
{
“name”: “Tomato”
	“energy”: 50,
	“protein”: 2.5
			}
ingredient_id (Integer): Ingredient ID of the ingredient that should be added.
Request Example:
cURL: PUT /food/update/1
Body:
{
"name": "Tomato",
"energy": 50,
“protein”: 2.5
}
Response Example:
 Code: 200
 Content: 
{
"status": "success",
“message”: “Ingredient added.”,
“ingredient”: 
	{
		“id": 1,
"name": "Tomato",
"energy": 50,
"protein": 2.5,
"carbohydrates": 10,
"fat": 1,
"fiber": 3
}
			}

Route: /food/delete/<int:ingredient_id>
Request Type: DELETE
Purpose: Deletes the ingredient by ID in stored_ingredients dictionary.
Request Format: JSON
No DELETE Body
ingredient_id (Integer): Ingredient ID of the ingredient that should be added.
Request Example:
cURL: PUT /food/delete/1
Response Example:
 Code: 200
 Content: 
{
"status": "success",
“message”: “Ingredient deleted.”,
“ingredient”: 
	{
		“id": 1,
"name": "Tomato",
"energy": 50,
"protein": 2.5,
"carbohydrates": 10,
"fat": 1,
"fiber": 3
}
			}

Route: /food/<int:ingredient_id>
Request Type: GET
Purpose: Returns information about an ingredient by ID from stored_ingredients dictionary.
Request Format: JSON
ingredient_id (Integer): Ingredient ID of the ingredient that should be added.
Request Example:
cURL: GET /food/1
Response Example:
 Code: 200
 Content: 
{
"status": "success",
“ingredient”: 
	{
		“id": 1,
"name": "Tomato",
"energy": 50,
"protein": 2.5,
"carbohydrates": 10,
"fat": 1,
"fiber": 3
}
			}

Route: /food/list
Request Type: GET
Purpose: Returns information on all ingredients in stored_ingredients dictionary.
Request Format: JSON
stored_ingredients (Array of Objects): list of all ingredients.
Request Example:
cURL: GET /food/1
Response Example:
 Code: 200
 Content: 
{
"stored_ingredients":
[
{
"id": 1,
"name": "Tomato",
"energy": 50,
"protein": 2.5,
"carbohydrates": 10,
"fat": 1,
"fiber": 3
},
{
"id": 2,
"name": "Onion",
"energy": 40,
"protein": 1.1,
"carbohydrates": 9.3,
"fat": 0.1,
"fiber": 1.7
}
]
}


