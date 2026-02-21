# Vehicle Database API

An API built to manage vehicle records. This application allows users to create, read, update, and delete (CRUD) vehicle information stored in a SQLite database.

## Prerequisites
* Python 3.10+
* Unix-based terminal (Linux/macOS) or WSL for Windows

## Setup and Installation

1. Clone the repository and navigate to the project directory:
    cd path/to/your/project

2. Create and activate a virtual environment:
    python3 -m venv venv
    source venv/bin/activate

3. Install the dependencies:
    pip install -r requirements.txt

4. Run the application:
    uvicorn main:app --reload

5. Access the API Documentation:
    Once the server is running, open your browser and navigate to:
    * Swagger UI (Interactive Docs): http://127.0.0.1:8000/docs
    * ReDoc: http://127.0.0.1:8000/redoc

---

## General Informatin

### 1. File Structure
The codebase is divided into 4 files.
* `database.py`: This manages the SQLAlchemy engine and database connection.
* `models.py`: Contains the SQLAlchemy ORM models, defining how data is stored in the database tables.
* `schemas.py`: Contains the Pydantic models, defining how data flows in and out of the API and handling data validation.
* `main.py`: Coordinates the application, containing the FastAPI instance, API routes, and logic.

### 2. Technology 
* FastAPI: I chose FastAPI over Flask or Django 
* Pydantic: I used Pydantic for strict data validation and parsing. It guarantees that the data entering the API strictly matches the required types before it reaches the main logic.
* SQLAlchemy 2.0: This is an Object-Relational Mapper (ORM) that allows database interactions using Python objects rather than raw SQL strings. It makes it easy for database engine changes.