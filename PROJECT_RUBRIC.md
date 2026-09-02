Use this project rubric to understand and assess the project criteria.

Code Quality & Documentation
Criteria	Submission Requirements
Write clear, concise and well documented code

The code adheres to the PEP 8 style guide(opens in a new tab) and follows common best practices, including:

Variable and function names are clear(opens in a new tab).
Endpoints are logically named.
Code is commented appropriately(opens in a new tab).
The README file includes detailed instructions for scripts to install any project dependencies and to run the development server.
Secrets are stored as environment variables.
Write an informative README File

README includes:

Instructions for how to install project dependencies and start the project server.
Detailed documentation of API endpoints and expected behavior, using the format taught in the course:
METHOD Url
Request parameters
Response body
Leverage environment controls

Local files and virtual environment are included in .gitignore file

Handling HTTP Requests
Criteria	Submission Requirements
Follow RESTful principles

RESTful principles are followed throughout the project, including appropriate naming of endpoints, use of HTTP methods GET, POST, and DELETE.

Routes perform CRUD operations on the psql database

Utilize multiple HTTP request methods

Complete all TODO flags in backend/app.py:








Handle common errors

Project handles common errors using the @app.errorhandler decorator function to format an API friendly JSON error response

Passes all provided tests related to error handling

API Testing & Documentation
Criteria	Submission Requirements
Use unittest to test flask application for expected behavior

Import and utilize unittest library to test each endpoint for expected success and error behavior. Each endpoint should have at one test for the expected behavior and tests for error handling if applicable.

Demonstrate validity of API responses

Project includes tests to ensure CRUD operations are successful and persist accurately in the database for GET, POST, PUT and DELETE HTTP requests.

Suggestions to Make Your Project Stand Out
Add an additional question field such as rating and make all corresponding updates (db, api endpoints, add question form, etc.)

INTENSE: Add users to the DB and track their game scores

Add capability to create new categories.

