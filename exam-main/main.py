from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import csv
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # This allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # This allows all headers
)

# Define the path to the users CSV file
USERS_FILE = "users.csv"
TASKS_FILE = "tasks.csv"

class User(BaseModel):
    username: str
    password: str 

class Task(BaseModel):
    task: str
    deadline: str 
    user: str
 
# Define the path to the users CSV file
USERS_FILE = "users.csv"
TASKS_FILE = "tasks.csv"  # Updated path to tasks.csv

def initialize_files():
    """
    Ensures that the required CSV files (users.csv and tasks.csv) exist.
    If the files do not exist, they will be created with appropriate headers.
    """
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([user.username, user.password])


    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["task", "deadline", "user"])
# Ensure CSV files exist when the application starts
initialize_files()


@app.post("/login/")
async def user_login(User: User):
    """
    Handles the user login process. The function checks if the user exists in the users CSV file.
    If the username and password match, the user is logged in successfully.
    """
    try:
        with open(USERS_FILE, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["username"] == User.username and row["password"] == User.password:
                    return {"status": "Logged in"}
        return {"status": "Invalid username or password"}
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Users file not found.")

@app.post("/create_user/")
async def create_user(User: User):
    """
    Creates a new user by adding their username and password to the users CSV file.
    """
    try:
        # Check if the user already exists
        with open(USERS_FILE, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["username"] == User.username:
                    return {"status": "User already exists"}

        # Add the new user to the CSV file
        with open(USERS_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([User.username, User.password])

        return {"status": "User Created"}
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Users file not found.")

@app.post("/create_task/")
async def create_task(Task: Task):
    """
    Creates a new task by adding the task description, deadline, and user to tasks.csv.
    Validates if the user exists before creating the task.
    """
    try:
        # Check if the user exists in the users.csv file
        with open(USERS_FILE, mode="r") as file:
            reader = csv.DictReader(file)
            if not any(row["username"] == Task.user for row in reader):
                return {"status": "User does not exist"}

        # Add the new task to the tasks.csv file
        with open(TASKS_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([Task.task, Task.deadline, Task.user])

        return {"status": "Task Created"}
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Tasks file not found. Please ensure the system is set up correctly.")
    
@app.get("/get_tasks/")
async def get_tasks(name: str):
    """
    Retrieves all tasks associated with a specific user from tasks.csv.
    """
    # Read tasks.csv and filter tasks for the given user
    user_tasks = []
    with open(TASKS_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["user"] == name:
                user_tasks.append([row["task"], row["deadline"], row["user"]])
    
    return {"tasks": user_tasks}