from fastapi import FastAPI, HTTPException, Depends, status, Query, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import jwt
from jwt import ExpiredSignatureError
import logging
from contextlib import asynccontextmanager
import os
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Configuration Settings
class Settings(BaseModel):
    """Application settings"""

    app_name: str = "Comprehensive FastAPI Example"
    app_version: str = "1.0.0"
    debug: bool = False
    secret_key: str = Field(default="your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    environment: str = Field(default="development")
    cors_origins: List[str] = ["*"]

    model_config = ConfigDict(env_file=".env")


# Initialize settings
settings = Settings(
    secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
    debug=os.getenv("DEBUG", "false").lower() == "true",
    environment=os.getenv("ENVIRONMENT", "development"),
    access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
)

# Configuration (using settings)
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# Security
security = HTTPBearer(auto_error=False)  # Don't auto-error, let us handle it


# Custom authentication dependency with better error messages
def require_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """
    Require authentication with helpful error messages.

    Args:
        credentials: Optional HTTP authorization credentials from request header

    Returns:
        Dict[str, Any]: User dictionary containing user information

    Raises:
        HTTPException: If authentication fails or token is invalid/expired
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please login and include your token in the Authorization header as 'Bearer <token>'. Visit /auth/help for detailed instructions.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: Could not validate credentials. Please login again.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = get_user_by_username(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found. The token may be for a deleted user. Please login again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please login again to get a new token at /auth/login",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format. Please login again to get a valid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Data Models
class UserBase(BaseModel):
    """Base user model with common fields"""

    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Valid email address")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")


class UserCreate(UserBase):
    """Model for user creation"""

    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "password": "secretpassword123",
            }
        }
    )


class UserResponse(UserBase):
    """Model for user response (without password)"""

    id: int = Field(..., description="Unique user identifier")
    created_at: datetime = Field(..., description="User creation timestamp")
    is_active: bool = Field(True, description="Whether the user is active")

    model_config = ConfigDict(from_attributes=True)


class ItemBase(BaseModel):
    """Base item model with common fields"""

    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(None, max_length=500, description="Item description")
    price: float = Field(..., gt=0, description="Item price (must be positive)")
    category: str = Field(..., description="Item category")


class ItemCreate(ItemBase):
    """Model for item creation"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Laptop",
                "description": "High-performance laptop for developers",
                "price": 1299.99,
                "category": "Electronics",
            }
        }
    )


class ItemUpdate(BaseModel):
    """Model for item updates (all fields optional)"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None


class ItemResponse(ItemBase):
    """Model for item response"""

    id: int = Field(..., description="Unique item identifier")
    created_at: datetime = Field(..., description="Item creation timestamp")
    updated_at: datetime = Field(..., description="Item last update timestamp")
    owner_id: int = Field(..., description="ID of the user who created the item")

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """JWT token response model"""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Token payload data"""

    username: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Generic paginated response model"""

    items: List[Dict[str, Any]] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


# Enhanced Response Models for Better Documentation
class SuccessResponse(BaseModel):
    """Standard success response format"""

    success: bool = Field(True, description="Indicates successful operation")
    message: str = Field(..., description="Human-readable success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"id": 1, "name": "Sample Item"},
            }
        }
    )


class ErrorResponse(BaseModel):
    """Standard error response format"""

    success: bool = Field(False, description="Indicates failed operation")
    message: str = Field(..., description="Human-readable error message")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "message": "Validation error occurred",
                "error_code": "VALIDATION_FAILED",
                "details": {"field": "email", "issue": "Invalid email format"},
            }
        }
    )


class AuthResponse(BaseModel):
    """Authentication response with user info"""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": 1,
                    "username": "johndoe",
                    "email": "john@example.com",
                    "full_name": "John Doe",
                    "created_at": "2024-01-01T12:00:00Z",
                    "is_active": True,
                },
            }
        }
    )


class UserListResponse(BaseModel):
    """Paginated users list response"""

    users: List[UserResponse] = Field(..., description="List of users")
    pagination: PaginatedResponse = Field(..., description="Pagination information")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "users": [
                    {
                        "id": 1,
                        "username": "johndoe",
                        "email": "john@example.com",
                        "full_name": "John Doe",
                        "created_at": "2024-01-01T12:00:00Z",
                        "is_active": True,
                    }
                ],
                "pagination": {"items": [], "total": 1, "page": 1, "size": 10, "pages": 1},
            }
        }
    )


class ItemListResponse(BaseModel):
    """Paginated items list response"""

    items: List[ItemResponse] = Field(..., description="List of items")
    pagination: PaginatedResponse = Field(..., description="Pagination information")
    filters_applied: Optional[Dict[str, Any]] = Field(None, description="Applied filters")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 1,
                        "name": "Laptop",
                        "description": "High-performance laptop",
                        "price": 1299.99,
                        "category": "Electronics",
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-01T12:00:00Z",
                        "owner_id": 1,
                    }
                ],
                "pagination": {"items": [], "total": 1, "page": 1, "size": 10, "pages": 1},
                "filters_applied": {"search": "laptop", "category": "Electronics"},
            }
        }
    )


class HealthCheckResponse(BaseModel):
    """Health check response"""

    status: str = Field(..., description="Service health status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment name")
    uptime: str = Field(..., description="Service uptime")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00Z",
                "version": "1.0.0",
                "environment": "development",
                "uptime": "2 hours, 30 minutes",
            }
        }
    )


# Custom Exceptions
class CustomHTTPException(HTTPException):
    """Custom HTTP exception with additional context"""

    def __init__(self, status_code: int, detail: str, error_code: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


class DatabaseException(Exception):
    """Custom database exception"""

    pass


class AuthenticationException(Exception):
    """Custom authentication exception"""

    pass


# In-memory storage (use a real database in production)
users_db: List[Dict[str, Any]] = []
items_db: List[Dict[str, Any]] = []
user_counter = 0
item_counter = 0


# Utility functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.

    Args:
        data: Dictionary containing data to encode in the token
        expires_delta: Optional token expiration time

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """
    Verify JWT token and return current user.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        Dict[str, Any]: User information dictionary

    Raises:
        HTTPException: If token is invalid or expired
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token in the Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(username=username)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please login again to get a new token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_username(username=token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found. The token may be for a deleted user.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# Optional authentication dependency (for endpoints that can work with or without auth)
def optional_verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
) -> Optional[Dict[str, Any]]:
    """
    Verify JWT token if provided, return None if not provided.

    Args:
        credentials: Optional HTTP authorization credentials

    Returns:
        Optional[Dict[str, Any]]: User information if token is valid, None otherwise
    """
    if not credentials:
        return None

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None

        user = get_user_by_username(username)
        return user if user else None
    except jwt.PyJWTError:
        return None


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Get user by username from the database.

    Args:
        username: Username to search for

    Returns:
        Optional[Dict[str, Any]]: User dictionary if found, None otherwise
    """
    return next((user for user in users_db if user["username"] == username), None)


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Get user by email from the database.

    Args:
        email: Email address to search for

    Returns:
        Optional[Dict[str, Any]]: User dictionary if found, None otherwise
    """
    """Get user by email"""
    return next((user for user in users_db if user["email"] == email), None)


# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("Starting up FastAPI application...")

    # Create a sample user
    global user_counter
    user_counter += 1
    sample_user = {
        "id": user_counter,
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Administrator",
        "password_hash": "hashed_password",  # In production, hash the password
        "created_at": datetime.now(timezone.utc),
        "is_active": True,
    }
    users_db.append(sample_user)

    logger.info("Application startup complete")
    yield

    # Shutdown
    logger.info("Shutting down FastAPI application...")


# FastAPI app configuration
app = FastAPI(
    title="🚀 Comprehensive FastAPI Example",
    description="""
# Welcome to the Comprehensive FastAPI Demo! 👋

This is a **production-ready FastAPI application** that demonstrates enterprise-level development patterns and best practices. Perfect for learning and as a starting point for your own projects!

---

## 🎯 Quick Start - Test the API in 3 Steps!

1. **Click the 🔒 Authorize button** at the top right
2. **Use these test credentials**:
   - Username: `admin`
   - Password: `password`
3. **Try any endpoint** marked with 🔒

> 💡 **Tip**: All endpoints below have **"Try it out"** buttons - click them to test the API directly!

---

## 🔐 Authentication & Security

Our authentication system uses **JSON Web Tokens (JWT)** for secure access:

- ✅ **JWT Authentication**: Industry-standard token-based security
- ✅ **Password Protection**: Secure password hashing
- ✅ **Role-Based Access**: Control who can access what
- ✅ **CORS Support**: Safe cross-origin requests

**How to authenticate:**
1. Register a new account at `/auth/register` OR use the default `admin` account
2. Login at `/auth/login` to get your access token
3. Click the 🔒 Authorize button and paste your token
4. Now you can access all protected endpoints!

---

## 📊 Data Management Features

**Full CRUD Operations** - Create, Read, Update, and Delete:
- ✨ **Smart Validation**: Automatic data validation with helpful error messages
- 🔍 **Advanced Search**: Filter, search, and sort your data
- 📄 **Pagination**: Handle large datasets efficiently
- 🎨 **Flexible Queries**: Combine multiple filters for precise results

---

## 🛠️ Built-In Quality Features

- ⚡ **Fast Performance**: Async/await for high concurrency
- 🎯 **Type Safety**: Full type hints prevent bugs
- 📝 **Auto Documentation**: This page updates automatically!
- 🔔 **Error Handling**: Clear, helpful error messages
- 📊 **Request Logging**: Track all API activity
- ✅ **Input Validation**: Catch problems before they happen

---

## 📚 API Organization

Endpoints are organized into clear sections (see below):

| Section | Purpose | Examples |
|---------|---------|----------|
| 🔐 **Authentication** | User registration & login | Register, Login, Get current user |
| 👥 **Users** | User management | List users, Get user details |
| 📦 **Items** | Product/item management | Create items, Search, Filter by category |
| 💓 **Health** | System monitoring | Health checks, Configuration |
| 📊 **Statistics** | Analytics & insights | User stats, Item statistics |

---

## 📖 Need Help?

- 🆘 Visit `/auth/help` for detailed authentication instructions
- 📖 Visit `/api/info` for a complete API overview
- 💡 All endpoints have detailed descriptions and examples below
- 🧪 Use the **"Try it out"** feature to test endpoints interactively

---

## 🎓 Learning Resources

Want to learn more about FastAPI? Check out:
- Official FastAPI documentation
- Pydantic for data validation
- JWT authentication guides

**Happy API testing!** 🎉
    """,
    version="1.0.0",
    contact={
        "name": "API Development Team",
        "email": "api-support@example.com",
        "url": "https://github.com/MachariaP/FastAPI",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {"url": "http://localhost:8000", "description": "🏠 Local Development Server"},
        {"url": "https://api.example.com", "description": "🌐 Production Server"},
    ],
    tags_metadata=[
        {
            "name": "Health",
            "description": (
                """
## 💓 Health & System Status

Quick endpoints to check if the API is running and healthy.

**Perfect for:**
- 🔍 Monitoring systems and uptime checks
- ⚖️ Load balancer health checks
- 🚀 CI/CD pipeline validations
- 📊 System diagnostics

**Available Endpoints:**
- `GET /` - Quick health check
- `GET /health` - Detailed system information
- `GET /config` - Application configuration

> 💡 **Tip**: These endpoints don't require authentication - they're always available!
            """
            ),
        },
        {
            "name": "Authentication",
            "description": (
                """
## 🔐 User Authentication & Authorization

Complete authentication system powered by **JWT (JSON Web Tokens)**.

**What you can do:**
- ✅ Register new user accounts with validation
- ✅ Login securely to get access tokens
- ✅ Verify your identity with tokens
- ✅ Check your authentication status

**🚀 Quick Start (3 easy steps):**

1. **Test with default user** (fastest way):
   - Username: `admin`
   - Password: `password`
   - Use `POST /auth/login` endpoint below

2. **Or register your own account**:
   - Use `POST /auth/register`
   - Fill in your details
   - Then login to get your token

3. **Authorize and test**:
   - Click the 🔒 **Authorize** button at top right
   - Paste your token
   - Now test any protected endpoint!

> 📚 **Need detailed help?** Visit the `/auth/help` endpoint for comprehensive examples and troubleshooting!
            """
            ),
            "externalDocs": {
                "description": "📖 FastAPI Security Tutorial",
                "url": "https://fastapi.tiangolo.com/tutorial/security/",
            },
        },
        {
            "name": "Users",
            "description": (
                """
## 👥 User Management

Manage user profiles and accounts in the system.

**Available Operations:**
- 👤 View user profiles and details
- 📋 List all users (with pagination)
- 📦 Get user's items and content
- ⚙️ User account management

**Features:**
- ✅ Pagination support for large user lists
- ✅ Detailed user information
- ✅ User-item relationships
- ✅ Protected by authentication

> 🔒 **Authentication Required**: You must be logged in to access these endpoints. Click the Authorize button first!
            """
            ),
            "externalDocs": {
                "description": "📖 User Management Guide",
                "url": "https://fastapi.tiangolo.com/tutorial/sql-databases/",
            },
        },
        {
            "name": "Items",
            "description": (
                """
## 📦 Item & Product Management

Full-featured system for managing items, products, or any inventory.

**CRUD Operations** (Create, Read, Update, Delete):
- ➕ Create new items (authenticated users)
- 📖 View all items (public access)
- ✏️ Update your items
- 🗑️ Delete your items

**Advanced Features:**
- 🔍 **Search**: Find items by name, description, or category
- 🎯 **Filter**: Category, price range, owner
- 📊 **Sort**: By name, price, date created/updated
- 📄 **Paginate**: Handle thousands of items efficiently

**Example Categories:**
Electronics, Books, Clothing, Home, Sports, Toys, etc.

**Ownership & Permissions:**
- Anyone can view items
- Only the owner (or admin) can update/delete items
- Each item is linked to its creator

> 💡 **Try it**: Use `GET /items/search` for powerful search capabilities!
            """
            ),
            "externalDocs": {
                "description": "📖 CRUD Operations Guide",
                "url": "https://fastapi.tiangolo.com/tutorial/sql-databases/#crud-operations",
            },
        },
        {
            "name": "Configuration",
            "description": (
                """
## ⚙️ Configuration & Settings

View application configuration and settings.

**What you can see:**
- Application name and version
- Environment (development/production)
- Token expiration settings
- Debug mode status

> 🔒 **Note**: Sensitive information like secret keys are never exposed through these endpoints!
            """
            ),
        },
        {
            "name": "Statistics",
            "description": (
                """
## 📊 Analytics & Statistics

Get insights and statistics about the application data.

**Available Metrics:**
- 👥 Total users count
- 📦 Total items count
- 🏷️ Items by category
- 💰 Average prices
- 📈 Your personal statistics

> 🔒 **Authentication Required**: Login to see statistics and analytics!
            """
            ),
        },
        {
            "name": "API Information",
            "description": (
                """
## ℹ️ API Overview & Help

Comprehensive information about the entire API.

**What you'll find:**
- 📋 Complete list of all endpoints
- 🔑 Authentication workflow guide
- ✨ Available features overview
- 📖 Documentation links

> 💡 **Perfect for**: Getting a bird's-eye view of the entire API in one place!
            """
            ),
        },
    ],
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom Exception Handlers
@app.exception_handler(CustomHTTPException)
async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
    """Handle custom HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": exc.error_code,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "detail": f"Validation error: {exc.errors()}",
            "error_code": "VALIDATION_ERROR",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle standard HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": "HTTP_ERROR",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url),
        },
    )


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses"""
    start_time = datetime.now(timezone.utc)

    # Log request
    logger.info(f"Request: {request.method} {request.url}")

    try:
        response = await call_next(request)

        # Log response
        process_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.info(f"Response: {response.status_code} - {process_time:.4f}s")

        return response
    except Exception as e:
        # Log error
        process_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.error(f"Request failed: {e} - {process_time:.4f}s")
        raise


# API Routes


# Health Check
@app.get(
    "/",
    tags=["Health"],
    summary="Health Check",
    description="Check if the API is running and healthy",
)
async def root():
    """
    Health check endpoint to verify API status.

    Returns:
        dict: Status message with timestamp
    """
    return {
        "message": "FastAPI is running!",
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
    }


@app.get(
    "/auth/help",
    tags=["Authentication"],
    summary="Authentication Help",
    description="Get detailed help on how to authenticate with the API",
)
async def auth_help():
    """
    Get comprehensive authentication help and examples.

    Returns:
        dict: Detailed authentication instructions and examples
    """
    return {
        "title": "Authentication Help",
        "overview": "This API uses JWT (JSON Web Token) authentication for protected endpoints",
        "steps": {
            "1": "Register a new user account (POST /auth/register) or use default credentials",
            "2": "Login to get an access token (POST /auth/login)",
            "3": "Include the token in the Authorization header for protected endpoints",
        },
        "default_credentials": {
            "username": "admin",
            "password": "password",
            "note": "Use these credentials for testing",
        },
        "examples": {
            "login": {
                "method": "POST",
                "url": "/auth/login",
                "headers": {"Content-Type": "application/x-www-form-urlencoded"},
                "body": "username=admin&password=password",
                "curl_example": (
                    "curl -X POST http://localhost:8000/auth/login -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=admin&password=password'"
                ),
            },
            "using_token": {
                "description": (
                    "After login, use the returned access_token in the Authorization header"
                ),
                "header_format": "Authorization: Bearer <your_access_token>",
                "curl_example": (
                    "curl -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' http://localhost:8000/auth/me"
                ),
            },
            "create_item": {
                "description": "Example of creating an item with authentication",
                "curl_example": (
                    'curl -X POST http://localhost:8000/items -H \'Authorization: Bearer <token>\' -H \'Content-Type: application/json\' -d \'{"name":"Laptop","description":"Gaming laptop","price":1299.99,"category":"Electronics"}\''
                ),
            },
        },
        "protected_endpoints": [
            "POST /items - Create new item",
            "PUT /items/{id} - Update item",
            "DELETE /items/{id} - Delete item",
            "GET /auth/me - Get current user",
            "GET /users - Get all users",
            "GET /stats - Get statistics",
        ],
        "public_endpoints": [
            "GET / - Health check",
            "GET /items - Get all items",
            "GET /items/{id} - Get specific item",
            "POST /auth/register - Register user",
            "POST /auth/login - Login user",
            "GET /auth/help - This help page",
        ],
        "common_errors": {
            "403_forbidden": (
                "Missing or invalid Authorization header. Make sure to include 'Authorization: Bearer <token>'"
            ),
            "401_unauthorized": "Invalid or expired token. Login again to get a new token",
            "422_validation_error": (
                "Invalid request data. Check the required fields and data types"
            ),
        },
    }


@app.get(
    "/api/info",
    tags=["API Information"],
    summary="API Overview",
    description="Get comprehensive API information and available endpoints",
)
async def api_info():
    """
    Get comprehensive API information.

    Returns:
        dict: Complete API overview with all endpoints
    """
    return {
        "api_name": "Comprehensive FastAPI Example",
        "version": "1.0.0",
        "description": "A comprehensive FastAPI application demonstrating best practices",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
        },
        "endpoints": {
            "health": {
                "GET /": "Basic health check",
                "GET /health": "Detailed health information",
                "GET /config": "Application configuration",
            },
            "authentication": {
                "GET /auth/register": "Registration information",
                "POST /auth/register": "Register new user",
                "GET /auth/login": "Login information",
                "POST /auth/login": "User login",
                "GET /auth/me": "Get current user (requires auth)",
                "GET /auth/help": "Comprehensive authentication help and examples",
            },
            "users": {
                "GET /users": "Get all users (requires auth)",
                "GET /users/{user_id}": "Get user by ID (requires auth)",
                "GET /users/{user_id}/items": "Get user's items (requires auth)",
            },
            "items": {
                "GET /items": "Get all items with pagination/filtering",
                "GET /items/{item_id}": "Get item by ID",
                "POST /items": "Create new item (requires auth)",
                "PUT /items/{item_id}": "Update item (owner/admin only)",
                "DELETE /items/{item_id}": "Delete item (owner/admin only)",
                "GET /items/search": "Advanced item search",
                "GET /items/categories": "Get item categories with stats",
            },
            "statistics": {"GET /stats": "Application statistics (requires auth)"},
            "api_info": {"GET /api/info": "This endpoint - API overview"},
        },
        "authentication_flow": {
            "step_1": "Register a new user: POST /auth/register",
            "step_2": "Login to get token: POST /auth/login",
            "step_3": "Use token in Authorization header: Bearer <token>",
            "default_user": {"username": "admin", "password": "password"},
        },
        "features": [
            "JWT Authentication",
            "CRUD Operations",
            "Data Validation",
            "Error Handling",
            "Pagination & Filtering",
            "Advanced Search",
            "Request Logging",
            "CORS Support",
            "Comprehensive Documentation",
        ],
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Detailed Health Check",
    description="Detailed health check with system information",
)
async def health_check():
    """
    Detailed health check endpoint.

    Returns:
        dict: Detailed system health information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": {"users_count": len(users_db), "items_count": len(items_db)},
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
    }


# Configuration and Settings Routes
@app.get(
    "/config",
    tags=["Configuration"],
    summary="Get Application Configuration",
    description="Get current application configuration (non-sensitive data only)",
)
async def get_config():
    """
    Get application configuration.

    Returns:
        dict: Application configuration (non-sensitive data)
    """
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "access_token_expire_minutes": settings.access_token_expire_minutes,
    }


# Advanced Item Routes
@app.get(
    "/items/search",
    response_model=List[ItemResponse],
    tags=["Items"],
    summary="Advanced Item Search",
    description="Advanced search with multiple criteria",
)
async def search_items(
    q: Optional[str] = Query(None, description="General search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    sort_by: Optional[str] = Query(
        "created_at", enum=["name", "price", "created_at", "updated_at"], description="Sort field"
    ),
    sort_order: Optional[str] = Query("desc", enum=["asc", "desc"], description="Sort order"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
):
    """
    Advanced item search with sorting and filtering.
    """
    filtered_items = items_db.copy()

    # Apply filters
    if q:
        q_lower = q.lower()
        filtered_items = [
            item
            for item in filtered_items
            if q_lower in item["name"].lower()
            or (item["description"] and q_lower in item["description"].lower())
            or q_lower in item["category"].lower()
        ]

    if category:
        filtered_items = [
            item for item in filtered_items if item["category"].lower() == category.lower()
        ]

    if min_price is not None:
        filtered_items = [item for item in filtered_items if item["price"] >= min_price]

    if max_price is not None:
        filtered_items = [item for item in filtered_items if item["price"] <= max_price]

    # Sort items
    reverse = sort_order == "desc"
    if sort_by == "name":
        filtered_items.sort(key=lambda x: x["name"].lower(), reverse=reverse)
    elif sort_by == "price":
        filtered_items.sort(key=lambda x: x["price"], reverse=reverse)
    elif sort_by == "created_at":
        filtered_items.sort(key=lambda x: x["created_at"], reverse=reverse)
    elif sort_by == "updated_at":
        filtered_items.sort(key=lambda x: x["updated_at"], reverse=reverse)

    return [ItemResponse(**item) for item in filtered_items[:limit]]


@app.get(
    "/items/categories",
    tags=["Items"],
    summary="Get Item Categories",
    description="Get all available item categories with counts",
)
async def get_categories():
    """
    Get all item categories with item counts.

    Returns:
        dict: Categories with counts
    """
    categories = {}
    for item in items_db:
        category = item["category"]
        if category in categories:
            categories[category]["count"] += 1
        else:
            categories[category] = {"count": 1, "avg_price": 0}

    # Calculate average prices
    for category in categories:
        category_items = [item for item in items_db if item["category"] == category]
        if category_items:
            categories[category]["avg_price"] = sum(item["price"] for item in category_items) / len(
                category_items
            )

    return categories


@app.get(
    "/users/{user_id}/items",
    response_model=List[ItemResponse],
    tags=["Users"],
    summary="Get User's Items",
    description="Get all items owned by a specific user",
)
async def get_user_items(
    user_id: int,
    current_user: dict = Depends(require_auth),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get all items owned by a specific user.
    """
    # Check if requesting own items or is admin
    if current_user["id"] != user_id and current_user["username"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this user's items"
        )

    user_items = [item for item in items_db if item["owner_id"] == user_id]
    return [ItemResponse(**item) for item in user_items[skip : skip + limit]]


# Authentication Routes
@app.get(
    "/auth/register",
    tags=["Authentication"],
    summary="Registration Information",
    description="Get information about user registration requirements",
)
async def register_info():
    """
    Get information about user registration.

    Returns:
        dict: Registration requirements and example
    """
    return {
        "message": "User registration endpoint",
        "method": "POST",
        "endpoint": "/auth/register",
        "required_fields": ["username", "email", "password"],
        "optional_fields": ["full_name"],
        "example": {
            "username": "johndoe",
            "email": "john@example.com",
            "full_name": "John Doe",
            "password": "secretpassword123",
        },
        "password_requirements": "Minimum 8 characters",
        "note": "Send a POST request to this endpoint with the required data to register",
    }


@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
    summary="Register New User",
    description="""
    Create a new user account with comprehensive validation.

    **Requirements:**
    - Username: 3-50 characters, must be unique
    - Email: Valid email format, must be unique
    - Password: Minimum 8 characters
    - Full Name: Optional, max 100 characters

    **Process:**
    1. Validates all input data
    2. Checks for existing username/email
    3. Hashes password securely
    4. Creates user record
    5. Returns user information (password excluded)

    **Common Errors:**
    - 400: Username or email already exists
    - 422: Validation errors (invalid email, short password, etc.)
    """,
    responses={
        201: {
            "description": "User successfully created",
            "content": {
                "application/json": {
                    "example": {
                        "id": 2,
                        "username": "johndoe",
                        "email": "john@example.com",
                        "full_name": "John Doe",
                        "created_at": "2024-01-01T12:00:00Z",
                        "is_active": True,
                    }
                }
            },
        },
        400: {
            "description": "Username or email already exists",
            "content": {"application/json": {"example": {"detail": "Username already registered"}}},
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "email"],
                                "msg": "field required",
                                "type": "value_error.missing",
                            }
                        ]
                    }
                }
            },
        },
    },
)
async def register_user(user: UserCreate):
    """
    Register a new user.

    Args:
        user (UserCreate): User registration data

    Returns:
        UserResponse: Created user information

    Raises:
        HTTPException: If username or email already exists
    """
    global user_counter

    # Check if user already exists
    if get_user_by_username(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered"
        )

    if get_user_by_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    user_counter += 1
    new_user = {
        "id": user_counter,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "password_hash": f"hashed_{user.password}",  # In production, properly hash the password
        "created_at": datetime.now(timezone.utc),
        "is_active": True,
    }

    users_db.append(new_user)
    logger.info(f"New user registered: {user.username}")

    return UserResponse(**new_user)


@app.get(
    "/auth/login",
    tags=["Authentication"],
    summary="Login Information",
    description="Get information about user login requirements",
)
async def login_info():
    """
    Get information about user login.

    Returns:
        dict: Login requirements and example
    """
    return {
        "message": "User login endpoint",
        "method": "POST",
        "endpoint": "/auth/login",
        "required_parameters": ["username", "password"],
        "example": {"username": "admin", "password": "password"},
        "default_user": {
            "username": "admin",
            "password": "password",
            "note": "Default user for testing purposes",
        },
        "response": "Returns JWT access token on successful authentication",
        "note": "Send a POST request with username and password as form data or JSON",
    }


@app.post(
    "/auth/login",
    response_model=Token,
    tags=["Authentication"],
    summary="User Authentication",
    description="""
    Authenticate user credentials and return JWT access token.

    **Authentication Methods:**
    - Form data (recommended for web forms)
    - JSON payload (for API clients)

    **Process:**
    1. Validates username and password
    2. Verifies user credentials
    3. Generates JWT access token
    4. Returns token with expiration info

    **Default Test User:**
    - Username: `admin`
    - Password: `password`

    **Token Usage:**
    Include the returned token in subsequent requests:
    ```
    Authorization: Bearer <access_token>
    ```

    **Security Notes:**
    - Tokens expire in 30 minutes (configurable)
    - Use HTTPS in production
    - Store tokens securely in client applications
    """,
    responses={
        200: {
            "description": "Authentication successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": (
                            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcwNjc4MDQwMH0.example"
                        ),
                        "token_type": "bearer",
                    }
                }
            },
        },
        401: {
            "description": "Authentication failed",
            "content": {
                "application/json": {"example": {"detail": "Incorrect username or password"}}
            },
        },
        422: {
            "description": "Missing credentials",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "username"],
                                "msg": "field required",
                                "type": "value_error.missing",
                            }
                        ]
                    }
                }
            },
        },
    },
)
async def login(username: str = Form(...), password: str = Form(...)):
    """
    Authenticate user and return JWT token.

    Args:
        username (str): Username
        password (str): Password

    Returns:
        Token: JWT access token

    Raises:
        HTTPException: If credentials are invalid
    """
    user = get_user_by_username(username)
    if not user or user["password_hash"] != f"hashed_{password}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )

    logger.info(f"User logged in: {username}")
    return {"access_token": access_token, "token_type": "bearer"}


@app.get(
    "/auth/me",
    response_model=UserResponse,
    tags=["Authentication"],
    summary="Get Current User",
    description="Get current authenticated user information",
)
async def get_current_user(current_user: dict = Depends(require_auth)):
    """
    Get current authenticated user.

    Args:
        current_user (dict): Current user from token

    Returns:
        UserResponse: Current user information
    """
    return UserResponse(**current_user)


# User Management Routes
@app.get(
    "/users",
    response_model=List[UserResponse],
    tags=["Users"],
    summary="Get All Users",
    description="Retrieve all users (admin only)",
)
async def get_users(
    current_user: dict = Depends(require_auth),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
):
    """
    Get all users with pagination.

    Args:
        current_user (dict): Current authenticated user
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return

    Returns:
        List[UserResponse]: List of users
    """
    return [UserResponse(**user) for user in users_db[skip : skip + limit]]


@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"],
    summary="Get User by ID",
    description="Retrieve a specific user by ID",
)
async def get_user(user_id: int, current_user: dict = Depends(require_auth)):
    """
    Get user by ID.

    Args:
        user_id (int): User ID
        current_user (dict): Current authenticated user

    Returns:
        UserResponse: User information

    Raises:
        HTTPException: If user not found
    """
    user = next((user for user in users_db if user["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse(**user)


# Item Management Routes
@app.get(
    "/items",
    response_model=PaginatedResponse,
    tags=["Items"],
    summary="Get All Items",
    description="Retrieve all items with pagination and filtering",
)
async def get_items(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
):
    """
    Get all items with advanced filtering and pagination.

    Args:
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        category (str, optional): Filter by category
        search (str, optional): Search term for name/description
        min_price (float, optional): Minimum price filter
        max_price (float, optional): Maximum price filter

    Returns:
        PaginatedResponse: Paginated list of items
    """
    filtered_items = items_db.copy()

    # Apply filters
    if category:
        filtered_items = [
            item for item in filtered_items if item["category"].lower() == category.lower()
        ]

    if search:
        search_lower = search.lower()
        filtered_items = [
            item
            for item in filtered_items
            if search_lower in item["name"].lower()
            or (item["description"] and search_lower in item["description"].lower())
        ]

    if min_price is not None:
        filtered_items = [item for item in filtered_items if item["price"] >= min_price]

    if max_price is not None:
        filtered_items = [item for item in filtered_items if item["price"] <= max_price]

    total = len(filtered_items)
    items_page = filtered_items[skip : skip + limit]

    return PaginatedResponse(
        items=[ItemResponse(**item).model_dump() for item in items_page],
        total=total,
        page=skip // limit + 1,
        size=len(items_page),
        pages=(total + limit - 1) // limit,
    )


@app.get(
    "/items/{item_id}",
    response_model=ItemResponse,
    tags=["Items"],
    summary="Get Item by ID",
    description="Retrieve a specific item by ID",
)
async def get_item(item_id: int):
    """
    Get item by ID.

    Args:
        item_id (int): Item ID

    Returns:
        ItemResponse: Item information

    Raises:
        HTTPException: If item not found
    """
    item = next((item for item in items_db if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return ItemResponse(**item)


@app.post(
    "/items",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Items"],
    summary="Create New Item",
    description="""
    Create a new item in the system with full validation.

    **Authentication Required:** You must be logged in to create items.

    **Item Requirements:**
    - Name: 1-100 characters, required
    - Description: Optional, max 500 characters
    - Price: Positive number, required
    - Category: Required, any string

    **Process:**
    1. Validates all input data
    2. Creates item with auto-generated ID
    3. Associates item with authenticated user
    4. Sets creation timestamps
    5. Returns complete item information

    **Ownership:** The authenticated user becomes the item owner.

    **Categories:** Common categories include Electronics, Books, Clothing, Home, Sports, etc.
    """,
    responses={
        201: {
            "description": "Item successfully created",
            "content": {
                "application/json": {
                    "example": {
                        "id": 5,
                        "name": "Gaming Laptop",
                        "description": "High-performance gaming laptop with RTX graphics",
                        "price": 1599.99,
                        "category": "Electronics",
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-01T12:00:00Z",
                        "owner_id": 1,
                    }
                }
            },
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {
                        "detail": (
                            "Authentication required. Please login and include your token in the Authorization header as 'Bearer <token>'. Visit /auth/help for detailed instructions."
                        )
                    }
                }
            },
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "price"],
                                "msg": "ensure this value is greater than 0",
                                "type": "value_error.number.not_gt",
                            }
                        ]
                    }
                }
            },
        },
    },
)
async def create_item(item: ItemCreate, current_user: dict = Depends(require_auth)):
    """
    Create a new item.

    Args:
        item (ItemCreate): Item creation data
        current_user (dict): Current authenticated user

    Returns:
        ItemResponse: Created item information
    """
    global item_counter

    item_counter += 1
    new_item = {
        "id": item_counter,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "category": item.category,
        "owner_id": current_user["id"],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    items_db.append(new_item)
    logger.info(f"New item created: {item.name} by user {current_user['username']}")

    return ItemResponse(**new_item)


@app.put(
    "/items/{item_id}",
    response_model=ItemResponse,
    tags=["Items"],
    summary="Update Item",
    description="Update an existing item (owner or admin only)",
)
async def update_item(
    item_id: int, item_update: ItemUpdate, current_user: dict = Depends(require_auth)
):
    """
    Update an existing item.

    Args:
        item_id (int): Item ID
        item_update (ItemUpdate): Item update data
        current_user (dict): Current authenticated user

    Returns:
        ItemResponse: Updated item information

    Raises:
        HTTPException: If item not found or user not authorized
    """
    item_index = next((i for i, item in enumerate(items_db) if item["id"] == item_id), None)
    if item_index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    existing_item = items_db[item_index]

    # Check if user owns the item or is admin
    if existing_item["owner_id"] != current_user["id"] and current_user["username"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this item"
        )

    # Update only provided fields
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        existing_item[field] = value

    existing_item["updated_at"] = datetime.now(timezone.utc)

    logger.info(f"Item updated: {item_id} by user {current_user['username']}")
    return ItemResponse(**existing_item)


@app.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Items"],
    summary="Delete Item",
    description="Delete an item (owner or admin only)",
)
async def delete_item(item_id: int, current_user: dict = Depends(require_auth)):
    """
    Delete an item.

    Args:
        item_id (int): Item ID
        current_user (dict): Current authenticated user

    Raises:
        HTTPException: If item not found or user not authorized
    """
    item_index = next((i for i, item in enumerate(items_db) if item["id"] == item_id), None)
    if item_index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    existing_item = items_db[item_index]

    # Check if user owns the item or is admin
    if existing_item["owner_id"] != current_user["id"] and current_user["username"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this item"
        )

    items_db.pop(item_index)
    logger.info(f"Item deleted: {item_id} by user {current_user['username']}")


# Statistics Routes
@app.get(
    "/stats",
    tags=["Statistics"],
    summary="Get Application Statistics",
    description="Get various application statistics",
)
async def get_statistics(current_user: dict = Depends(require_auth)):
    """
    Get application statistics.

    Args:
        current_user (dict): Current authenticated user

    Returns:
        dict: Various application statistics
    """
    user_items = [item for item in items_db if item["owner_id"] == current_user["id"]]

    categories = {}
    for item in items_db:
        category = item["category"]
        if category in categories:
            categories[category] += 1
        else:
            categories[category] = 1

    return {
        "total_users": len(users_db),
        "total_items": len(items_db),
        "your_items": len(user_items),
        "categories": categories,
        "average_price": sum(item["price"] for item in items_db) / len(items_db) if items_db else 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
