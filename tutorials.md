# FastAPI Tutorial - Understanding Our Application 📚

Welcome! This tutorial explains all the concepts and features we've used in our FastAPI application. Everything is explained in simple, easy-to-understand English.

---

## Table of Contents

1. [What is FastAPI?](#what-is-fastapi)
2. [Setting Up the Application](#setting-up-the-application)
3. [Understanding Pydantic Models](#understanding-pydantic-models)
4. [Authentication with JWT](#authentication-with-jwt)
5. [CRUD Operations](#crud-operations)
6. [Middleware and Error Handling](#middleware-and-error-handling)
7. [Dependencies and Security](#dependencies-and-security)
8. [Pagination and Filtering](#pagination-and-filtering)
9. [Testing Your API](#testing-your-api)

---

## What is FastAPI? 🚀

FastAPI is a modern Python framework for building APIs (Application Programming Interfaces). Think of an API as a waiter in a restaurant:
- You (the client) ask for something
- The waiter (API) takes your request to the kitchen (server)
- The kitchen prepares your order
- The waiter brings it back to you

**Why FastAPI is special:**
- **Fast**: It's one of the fastest Python frameworks available
- **Easy**: Write less code, get more done
- **Smart**: Automatically checks if data is correct
- **Documented**: Creates beautiful documentation automatically (like the `/docs` page!)

---

## Setting Up the Application 🛠️

### 1. Imports and Dependencies

At the top of `main.py`, we import all the tools we need:

```python
from fastapi import FastAPI, HTTPException, Depends, status, Query, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
```

**What each import does:**
- `FastAPI`: The main framework - like the foundation of a house
- `HTTPException`: Used to tell users when something goes wrong
- `Depends`: Helps us check things before running our code (like checking if someone is logged in)
- `Pydantic`: Checks if data is in the right format
- `CORSMiddleware`: Allows websites from other domains to use our API safely

### 2. Configuration Settings

```python
class Settings(BaseModel):
    app_name: str = "Comprehensive FastAPI Example"
    app_version: str = "1.0.0"
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
```

**Think of this as the settings panel for your app:**
- `app_name`: What your application is called
- `secret_key`: A secret password used to create secure tokens (like a master key)
- `access_token_expire_minutes`: How long someone can stay logged in (30 minutes in our case)

> 💡 **Important**: In a real app, never put real secrets in the code! Use environment variables instead (that's what the `.env` file is for).

### 3. Creating the FastAPI App

```python
app = FastAPI(
    title="🚀 Comprehensive FastAPI Example",
    description="A detailed description...",
    version="1.0.0"
)
```

This creates your application. The `title` and `description` appear on the `/docs` page.

### 4. CORS Middleware

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**What is CORS?**
Imagine your API is a house. CORS (Cross-Origin Resource Sharing) decides which other websites can knock on your door.

- `allow_origins=["*"]`: Allow any website to use our API (in production, you'd list specific websites)
- `allow_methods=["*"]`: Allow all types of requests (GET, POST, PUT, DELETE)
- `allow_headers=["*"]`: Allow all types of information in requests

---

## Understanding Pydantic Models 📋

Pydantic models are like forms with rules. They check if the data people send is correct.

### Example: User Model

```python
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
```

**Breaking it down:**
- `username: str`: Username must be text
- `Field(..., min_length=3, max_length=50)`: Username must be 3-50 characters long
- `EmailStr`: Email must be in proper email format (e.g., user@example.com)
- `password: str = Field(..., min_length=8)`: Password must be at least 8 characters
- `Optional[str] = None`: Full name is optional - you don't have to provide it

**Why is this useful?**
If someone tries to create a user with a 2-character username or an invalid email, FastAPI automatically rejects it and tells them what's wrong!

### Example: Item Model

```python
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    category: str
```

**Key points:**
- `price: float = Field(..., gt=0)`: Price must be greater than 0 (gt = greater than)
- `Optional[str]`: Description is optional
- Items have an owner (the user who created them)

---

## Authentication with JWT 🔐

JWT (JSON Web Tokens) is like a special ticket you get after logging in.

### How it Works

**1. User Logs In:**
```python
@app.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    # Check if username and password are correct
    user = get_user_by_username(username)
    if not user or user["password_hash"] != f"hashed_{password}":
        raise HTTPException(status_code=401, detail="Wrong username or password")
    
    # Create a token
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}
```

**What happens:**
1. User sends username and password
2. We check if they're correct
3. If yes, we create a JWT token (like a concert ticket)
4. We give them the token
5. They use this token to access protected pages

**2. Creating the Token:**
```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt
```

**Think of it like a movie ticket:**
- It has your seat information (`data`)
- It has an expiration time (`expire`)
- It's signed by the theater (`SECRET_KEY`) so it can't be faked

**3. Checking the Token:**
```python
def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Please login!")
    
    # Decode and verify token
    payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
    username = payload.get("sub")
    
    # Get the user
    user = get_user_by_username(username)
    return user
```

**The process:**
1. Check if a token was provided
2. Verify the token is real and not expired
3. Extract the username from the token
4. Get the user's information
5. Return the user (so we know who is making the request)

---

## CRUD Operations 📝

CRUD stands for: **C**reate, **R**ead, **U**pdate, **D**elete - the four basic operations you can do with data.

### Create - Adding New Data

```python
@app.post("/items", status_code=201)
async def create_item(item: ItemCreate, current_user: dict = Depends(require_auth)):
    global item_counter
    item_counter += 1
    
    new_item = {
        "id": item_counter,
        "name": item.name,
        "price": item.price,
        "owner_id": current_user["id"],
        "created_at": datetime.utcnow()
    }
    
    items_db.append(new_item)
    return new_item
```

**What happens:**
1. User must be logged in (`Depends(require_auth)`)
2. We create a unique ID for the item
3. We save who created it (`owner_id`)
4. We add it to our database
5. We return the created item

### Read - Getting Data

```python
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    item = next((item for item in items_db if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

**What happens:**
1. Look for the item with the matching ID
2. If found, return it
3. If not found, return a 404 error ("not found")

### Update - Changing Data

```python
@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item_update: ItemUpdate,
    current_user: dict = Depends(require_auth)
):
    # Find the item
    item_index = next((i for i, item in enumerate(items_db) if item["id"] == item_id), None)
    
    if item_index is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    existing_item = items_db[item_index]
    
    # Check if user owns the item
    if existing_item["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not your item!")
    
    # Update the item
    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        existing_item[field] = value
    
    return existing_item
```

**What happens:**
1. Find the item
2. Check if it exists
3. Check if the current user owns it
4. Update only the fields that were provided
5. Return the updated item

### Delete - Removing Data

```python
@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int, current_user: dict = Depends(require_auth)):
    item_index = next((i for i, item in enumerate(items_db) if item["id"] == item_id), None)
    
    if item_index is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    existing_item = items_db[item_index]
    
    # Check ownership
    if existing_item["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    items_db.pop(item_index)
```

**What happens:**
1. Find the item
2. Check if it exists
3. Check if the current user owns it
4. Delete it from the database
5. Return nothing (status code 204 means "success, no content")

---

## Middleware and Error Handling 🛡️

### What is Middleware?

Middleware is code that runs **before** and **after** every request. Think of it like a security checkpoint at an airport.

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.utcnow()
    
    # Log the request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Process the request
    response = await call_next(request)
    
    # Log how long it took
    process_time = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
    
    return response
```

**What it does:**
1. Note when the request started
2. Log what was requested
3. Process the request
4. Log how long it took
5. Return the response

### Error Handling

We handle errors to give users helpful messages instead of confusing technical errors.

```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": "HTTP_ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )
```

**Common HTTP Status Codes:**
- `200`: Success! Everything worked
- `201`: Created! New item was created successfully
- `204`: Success with no content (like after deleting)
- `400`: Bad Request - You sent invalid data
- `401`: Unauthorized - You need to log in
- `403`: Forbidden - You're logged in, but you can't do this
- `404`: Not Found - The item doesn't exist
- `422`: Validation Error - The data format is wrong
- `500`: Server Error - Something broke on our end

---

## Dependencies and Security 🔒

### What are Dependencies?

Dependencies are functions that run **before** your main function. They're like security guards checking your ID before letting you in.

```python
def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Please login!")
    
    # Verify the token
    payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
    username = payload.get("sub")
    user = get_user_by_username(username)
    
    return user
```

**Using the dependency:**
```python
@app.get("/protected-route")
async def protected_route(current_user: dict = Depends(require_auth)):
    return {"message": f"Hello {current_user['username']}!"}
```

**What happens:**
1. Before the function runs, `require_auth` is called
2. It checks if the user has a valid token
3. If yes, it returns the user
4. The user is passed to `current_user`
5. Now your function knows who is making the request

### Optional Dependencies

Sometimes you want to know who's logged in, but you don't require it:

```python
def optional_verify_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))):
    if not credentials:
        return None  # No one is logged in, that's okay
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        return get_user_by_username(username)
    except:
        return None  # Invalid token, that's okay
```

---

## Pagination and Filtering 🔍

### Pagination

Imagine you have 10,000 items. Showing all of them at once would be slow and overwhelming. Pagination lets you show them in chunks.

```python
@app.get("/items")
async def get_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return")
):
    # Skip the first 'skip' items, then take 'limit' items
    items_page = items_db[skip:skip + limit]
    
    total = len(items_db)
    
    return {
        "items": items_page,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }
```

**Example:**
- If `skip=0` and `limit=10`: Show items 1-10 (page 1)
- If `skip=10` and `limit=10`: Show items 11-20 (page 2)
- If `skip=20` and `limit=10`: Show items 21-30 (page 3)

### Filtering and Search

Let users find exactly what they want:

```python
@app.get("/items/search")
async def search_items(
    q: Optional[str] = Query(None, description="Search term"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price")
):
    filtered_items = items_db.copy()
    
    # Search in name and description
    if q:
        q_lower = q.lower()
        filtered_items = [
            item for item in filtered_items 
            if q_lower in item["name"].lower() or 
               (item.get("description") and q_lower in item["description"].lower())
        ]
    
    # Filter by category
    if category:
        filtered_items = [item for item in filtered_items if item["category"] == category]
    
    # Filter by price range
    if min_price is not None:
        filtered_items = [item for item in filtered_items if item["price"] >= min_price]
    
    if max_price is not None:
        filtered_items = [item for item in filtered_items if item["price"] <= max_price]
    
    return filtered_items
```

**Example searches:**
- `q=laptop`: Find all items with "laptop" in name or description
- `category=Electronics`: Show only Electronics items
- `min_price=100&max_price=500`: Show items between $100 and $500
- `q=laptop&category=Electronics&min_price=1000`: Combine all filters!

---

## Testing Your API 🧪

### Using the Interactive Docs

1. **Open your browser** and go to `http://localhost:8000/docs`
2. **Try the health check:**
   - Click on `GET /` 
   - Click "Try it out"
   - Click "Execute"
   - See the response!

3. **Test authentication:**
   - Scroll to `POST /auth/login`
   - Click "Try it out"
   - Enter username: `admin`, password: `password`
   - Click "Execute"
   - Copy the `access_token` from the response

4. **Authorize:**
   - Click the green 🔒 "Authorize" button at the top
   - Paste your token in the "Value" field
   - Click "Authorize"
   - Click "Close"

5. **Test protected endpoints:**
   - Now you can try any endpoint with a 🔒 icon
   - Try `GET /auth/me` to see your user information

### Using curl (Command Line)

```bash
# Health check
curl http://localhost:8000/

# Login
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=password"

# Use the token (replace YOUR_TOKEN with actual token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/auth/me"

# Create an item
curl -X POST "http://localhost:8000/items" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Laptop",
       "description": "Gaming laptop",
       "price": 1299.99,
       "category": "Electronics"
     }'
```

---

## Key Concepts Summary 📚

### 1. **Routes/Endpoints**
URLs where your API can receive requests. Defined with `@app.get()`, `@app.post()`, etc.

### 2. **Request Methods**
- `GET`: Retrieve data (like viewing a page)
- `POST`: Create new data (like submitting a form)
- `PUT`: Update existing data (like editing a profile)
- `DELETE`: Remove data (like deleting a photo)

### 3. **Path Parameters**
Variables in the URL: `/items/{item_id}` where `{item_id}` is the parameter

### 4. **Query Parameters**
Variables after the `?` in URL: `/items?skip=0&limit=10`

### 5. **Request Body**
Data sent with POST/PUT requests, usually in JSON format

### 6. **Response Models**
Pydantic models that define what data the API returns

### 7. **Status Codes**
Numbers that tell you if the request succeeded or failed (200, 404, etc.)

### 8. **Async/Await**
Python keywords that allow handling multiple requests at the same time (concurrent processing)

---

## Best Practices 💡

### Security
1. **Never hardcode secrets** - Use environment variables
2. **Always validate input** - Use Pydantic models
3. **Use HTTPS in production** - Encrypt data in transit
4. **Hash passwords** - Never store plain text passwords
5. **Expire tokens** - Don't let tokens work forever

### Code Organization
1. **One function, one purpose** - Keep functions small and focused
2. **Use descriptive names** - `get_user_by_id()` is better than `get_u()`
3. **Add docstrings** - Explain what each function does
4. **Handle errors gracefully** - Give helpful error messages

### Performance
1. **Use pagination** - Don't return 10,000 items at once
2. **Use async/await** - Handle multiple requests efficiently
3. **Add database indexes** - Make searches faster (in real databases)
4. **Cache common results** - Don't recalculate the same thing repeatedly

---

## Common Pitfalls and How to Avoid Them ⚠️

### 1. Forgetting to Handle Errors
**Bad:**
```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return users_db[user_id]  # What if user doesn't exist?
```

**Good:**
```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### 2. Not Validating Input
**Bad:**
```python
@app.post("/items")
def create_item(name: str, price: str):  # Price is a string?!
    # Anyone can send anything...
```

**Good:**
```python
@app.post("/items")
def create_item(item: ItemCreate):  # Pydantic validates everything!
    # Only correct data gets here
```

### 3. Exposing Sensitive Data
**Bad:**
```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return user  # Includes password_hash!
```

**Good:**
```python
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    return user  # UserResponse excludes password_hash
```

---

## Next Steps 🚀

Now that you understand the concepts, here's what you can do:

1. **Experiment**: Change things and see what happens
2. **Add features**: Try adding comments, likes, or ratings
3. **Connect a real database**: Replace the in-memory lists with PostgreSQL or MongoDB
4. **Add tests**: Write tests to make sure everything works
5. **Deploy**: Put your API online so others can use it

### Learning Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **JWT.io**: https://jwt.io/ - Learn about JSON Web Tokens
- **HTTP Status Codes**: https://httpstatuses.com/

---

## Conclusion 🎉

Congratulations! You now understand:
- What FastAPI is and why it's useful
- How to set up and configure a FastAPI application
- How Pydantic models validate data
- How JWT authentication works
- How to perform CRUD operations
- How middleware and error handling work
- How to use dependencies for security
- How to implement pagination and filtering

Remember: **Learning by doing** is the best way to learn. Try modifying the code, break things, fix them, and see what happens. That's how you truly understand!

Happy coding! 💻✨
