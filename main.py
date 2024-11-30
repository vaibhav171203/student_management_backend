# from fastapi import FastAPI, HTTPException, Query
# from pydantic import BaseModel
# from pymongo import MongoClient
# from bson.objectid import ObjectId
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # MongoDB connection
# MONGO_URI = os.getenv("MONGO_URI")
# client = MongoClient(MONGO_URI)
# db = client["studentManage"]

# # Fix ObjectId serialization
# from pydantic.json import ENCODERS_BY_TYPE
# ENCODERS_BY_TYPE[ObjectId] = str

# # Initialize FastAPI app
# app = FastAPI()

# # Models
# class AddressModel(BaseModel):
#     city: str
#     country: str

# class StudentModel(BaseModel):
#     name: str
#     age: int
#     address: AddressModel

# class UpdateStudentModel(BaseModel):
#     name: str | None = None
#     age: int | None = None
#     address: AddressModel | None = None

# # Routes

# ## Create a student
# @app.post("/students", status_code=201)
# async def create_student(student: StudentModel):
#     result = db.students.insert_one(student.dict())
#     return {"id": str(result.inserted_id)}

# ## List students
# @app.get("/students")
# async def list_students(
#     country: str = Query(None, description="Filter by country"),
#     age: int = Query(None, description="Filter by minimum age"),
#     offset: int = 0,
#     limit: int = 100
# ):
#     query = {}
#     if country:
#         query["address.country"] = country
#     if age:
#         query["age"] = {"$gte": age}
#     students_cursor = db.students.find(query).skip(offset).limit(limit)
#     students = [{"id": str(student["_id"]), **student} for student in students_cursor]
#     return {"data": students}

# ## Fetch a single student
# @app.get("/students/{id}")
# async def fetch_student(id: str):
#     student = db.students.find_one({"_id": ObjectId(id)})
#     if not student:
#         raise HTTPException(status_code=404, detail="Student not found")
#     student["id"] = str(student.pop("_id"))
#     return student

# ## Update a student
# @app.patch("/students/{id}", status_code=204)
# async def update_student(id: str, student: UpdateStudentModel):
#     update_data = {k: v for k, v in student.dict(exclude_unset=True).items()}
#     result = db.students.update_one({"_id": ObjectId(id)}, {"$set": update_data})
#     if result.matched_count == 0:
#         raise HTTPException(status_code=404, detail="Student not found")

# ## Delete a student
# @app.delete("/students/{id}")
# async def delete_student(id: str):
#     result = db.students.delete_one({"_id": ObjectId(id)})
#     if result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="Student not found")
#     return {"message": "Student deleted successfully"}

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
from typing import List

# Load environment variables
load_dotenv()
 
# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI environment variable not set.")
client = MongoClient(MONGO_URI)
db = client["studentManage"]

# Fix ObjectId serialization
from pydantic.json import ENCODERS_BY_TYPE
ENCODERS_BY_TYPE[ObjectId] = str

# Initialize FastAPI app
app = FastAPI()

# Models
class AddressModel(BaseModel):
    city: str = Field(..., example="New York")
    country: str = Field(..., example="USA")
 
class StudentModel(BaseModel):
    name: str = Field(..., example="John Doe")
    age: int = Field(..., ge=0, example=20)
    address: AddressModel

class UpdateStudentModel(BaseModel):
    name: str | None = Field(None, example="John Doe")
    age: int | None = Field(None, ge=0, example=25)
    address: AddressModel | None = None

class StudentResponseModel(StudentModel):
    id: str

# Routes

## Create a student
@app.post("/students", status_code=201, response_model=StudentResponseModel)
async def create_student(student: StudentModel):
    try:
        result = db.students.insert_one(student.dict())
        return {"id": str(result.inserted_id), **student.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create student")

## List students
@app.get("/students", response_model=List[StudentResponseModel])
async def list_students(
    country: str = Query(None, description="Filter by country"),
    age: int = Query(None, ge=0, description="Filter by minimum age"),
    offset: int = Query(0, ge=0, description="Offset must be non-negative"),
    limit: int = Query(100, ge=1, le=1000, description="Limit must be between 1 and 1000")
):
    query = {}
    if country:
        query["address.country"] = country
    if age:
        query["age"] = {"$gte": age}

    try:
        students_cursor = db.students.find(query).skip(offset).limit(limit)
        students = [{"id": str(student["_id"]), **student} for student in students_cursor]
        for student in students:
            student.pop("_id", None)  # Avoid duplicate ID field
        return students
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to list students")

## Fetch a single student
@app.get("/students/{id}", response_model=StudentResponseModel)
async def fetch_student(id: str):
    try:
        student = db.students.find_one({"_id": ObjectId(id)})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        student["id"] = str(student.pop("_id"))
        return student
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch student")

## Update a student
@app.patch("/students/{id}", status_code=204)
async def update_student(id: str, student: UpdateStudentModel):
    try:
        update_data = {k: v for k, v in student.dict(exclude_unset=True).items()}
        result = db.students.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Student not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update student")

## Delete a student
@app.delete("/students/{id}")
async def delete_student(id: str):
    try:
        result = db.students.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Student not found")
        return {"message": "Student deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete student")
