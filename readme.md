# FastAPI MongoDB  Student Management API

This is a FastAPI-based API for Student Management using MongoDB

## Setup
- Clone the repository
- Install the required packages by running pip install -r requirements.txt
- Start the API server by running uvicorn main:app --host 0.0.0.0 --port 8000
- The API will be available at https://student-management-backend-hqn0.onrender.com/

## Documentation
- The API documentation is available at https://student-management-backend-hqn0.onrender.com/docs.

## Endpoints
- GET /students - Get all students
- POST /students - Create a new student
- GET /student/{student_id} - Get a student by id
- PATCH /student/{student_id} - Update a student by id
- DELETE /student/{student_id} - Remove a student from the DB
