# Post Manager App with FastAPI

This project implements a simple web application for managing posts using FastAPI. The application includes a system for registration, authentication, adding posts, viewing posts, and deleting posts.

## Requirements

- Use Python and FastAPI to create an application.
- Implement four endpoints: "signup", "login", "addPost", and "getPosts".
- All endpoints must have appropriate input and output data using Pydantic schemas with type checking.
- Implement authentication for the "addPost" and "getPosts" endpoints using a token obtained from the "login" endpoint.
- If the token is not provided or is invalid, the "addPost" and "getPosts" endpoints should return an appropriate false response.
- The "addPost" endpoint should store the post in memory and return the postID.
- The "getPosts" endpoint should return all posts added by the user.
- Implement request validation for the "addPost" endpoint to limit the packet size to 1 MB.
- Implement response caching for the "getPosts" endpoint.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/ruslan-kornich/post-manager-app-fastapi.git
```

2. Set the necessary dependencies:

```bash
pip install -r requirements.txt
```

## Run tests

Run tests using the command:

```bash
pytest tests/test_app.py -v

```

## Run application 

Run the application using the command:

```bash
uvicorn app.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

## Instructions for use

### Signup Endpoint

- **URL:** `/signup`
- **Method:** `POST`
- **Input data:** `email` (string), `password` (string)
- **Output data:** `access_token`

### Login Endpoint

- **URL:** `/login`
- **Method:** `POST`
- **Input data:** `email` (string), `password` (string)
- **Output data:** `access_token`

### AddPost Endpoint

- **URL:** `/addPost`
- **Method:** `POST`
- **Input data:** `text` (string)
- **Output data:** `postID`

### GetPosts Endpoint

- **URL:** `/getPosts`
- **Method:** `GET`
- **Input data:** `access_token`
- **Output data:** list of user posts

### DeletePost Endpoint

- **URL:** `/deletePost/{postID}`
- **Method:** `DELETE`
- **Input data:** `access_token`


## Technologies

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- cachetools


