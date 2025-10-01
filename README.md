# Comprehensive FastAPI Demo Application

A production-ready FastAPI application demonstrating enterprise-level development patterns, authentication, CRUD operations, and comprehensive API documentation.

## 🌟 Features

### 🔐 Authentication & Security
- **JWT Authentication**: Secure token-based authentication system
- **Password Security**: Bcrypt hashing with salt (simulated)
- **Protected Routes**: Role-based access control
- **CORS Support**: Configurable cross-origin resource sharing

### 📊 Data Management
- **Full CRUD Operations**: Complete Create, Read, Update, Delete operations
- **Data Validation**: Comprehensive Pydantic models with validation
- **Advanced Filtering**: Search, filter, and sort capabilities
- **Pagination**: Efficient data pagination with offset/limit

### 🛠️ Quality & Developer Experience
- **Comprehensive Documentation**: Auto-generated OpenAPI/Swagger docs with examples
- **Error Handling**: Detailed HTTP exception handling with helpful messages
- **Request Logging**: Detailed request/response logging
- **Type Safety**: Full type hints and validation
- **Testing Ready**: Structured for unit and integration testing

### 📚 Interactive Documentation
- **Swagger UI**: Interactive API testing at `/docs` - Enhanced with detailed descriptions and quick start guide!
- **ReDoc**: Beautiful API documentation at `/redoc`
- **OpenAPI Schema**: Complete schema available at `/openapi.json`
- **Tutorial Guide**: Complete learning guide in [tutorials.md](tutorials.md) - Learn all concepts in simple English!

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation & Setup

1. **Clone or download the project files**
   ```bash
   # Navigate to your project directory
   cd /home/phines-macharia/python_projects/FastAPI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment (optional)**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

4. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

5. **Access the API**
   - **API Server**: http://localhost:8000
   - **Interactive Docs**: http://localhost:8000/docs (Enhanced with beautiful descriptions!)
   - **ReDoc**: http://localhost:8000/redoc
   - **Health Check**: http://localhost:8000/health

## 📚 Learning Guide

**New to FastAPI?** Check out our comprehensive tutorial guide!

👉 **[Read tutorials.md](tutorials.md)** - A complete guide explaining all concepts in simple English

The tutorial covers:
- What is FastAPI and why use it
- Setting up your application
- Understanding Pydantic models (data validation)
- JWT authentication explained with simple analogies
- CRUD operations (Create, Read, Update, Delete)
- Middleware and error handling
- Dependencies and security
- Pagination and filtering
- Testing your API
- Best practices and common pitfalls

Perfect for beginners! Uses simple language and real-world analogies like waiters, movie tickets, and security guards.

## 📖 API Documentation

### 🎯 Quick Authentication Test

The fastest way to test the API:

1. **Access Swagger UI**: Go to http://localhost:8000/docs
2. **Use Default Credentials**:
   - Username: `admin`
   - Password: `password`
3. **Login Process**:
   - Find "Authentication" section
   - Use `POST /auth/login` endpoint
   - Enter credentials and execute
   - Copy the `access_token` from response
4. **Authorize**:
   - Click the 🔒 "Authorize" button at top
   - Enter: `Bearer <your_access_token>`
   - Click "Authorize"
5. **Test Protected Endpoints**: Now you can test any endpoint marked with 🔒

### 📋 API Endpoint Categories

#### Authentication Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/auth/help` | Comprehensive authentication guide | ❌ |
| GET | `/auth/register` | Registration information | ❌ |
| POST | `/auth/register` | Register new user | ❌ |
| GET | `/auth/login` | Login information | ❌ |
| POST | `/auth/login` | User authentication | ❌ |
| GET | `/auth/me` | Get current user info | ✅ |

#### User Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/users` | List all users (paginated) | ❌ |
| GET | `/users/{user_id}` | Get user by ID | ❌ |
| GET | `/users/{user_id}/items` | Get user's items | ✅ |
| GET | `/users/me` | Get current user profile | ✅ |

#### Item Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/items` | List items (with filtering/pagination) | ❌ |
| POST | `/items` | Create new item | ✅ |
| GET | `/items/{item_id}` | Get item by ID | ❌ |
| PUT | `/items/{item_id}` | Update item (owner only) | ✅ |
| DELETE | `/items/{item_id}` | Delete item (owner only) | ✅ |
| GET | `/items/search` | Advanced item search | ❌ |
| GET | `/items/categories` | Get categories with stats | ❌ |

#### System Information
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | API root information | ❌ |
| GET | `/health` | Health check | ❌ |
| GET | `/info` | System information | ❌ |

## 🔧 Detailed API Usage

### Authentication Flow

#### 1. Register a New User
```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "johndoe",
       "email": "john@example.com",
       "full_name": "John Doe",
       "password": "secretpassword123"
     }'
```

**Response:**
```json
{
  "id": 2,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-01T12:00:00Z",
  "is_active": true
}
```

#### 2. Login and Get Token
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=johndoe&password=secretpassword123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 3. Use Token for Protected Endpoints
```bash
# Include token in Authorization header
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     "http://localhost:8000/auth/me"
```

### Item Management Examples

#### Create an Item
```bash
curl -X POST "http://localhost:8000/items" \
     -H "Authorization: Bearer <your_token>" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Gaming Laptop",
       "description": "High-performance gaming laptop with RTX graphics",
       "price": 1599.99,
       "category": "Electronics"
     }'
```

#### Search Items with Filters
```bash
# Search electronics under $2000
curl "http://localhost:8000/items/search?category=Electronics&max_price=2000&sort_by=price&sort_order=asc"
```

#### Get Items with Pagination
```bash
# Get page 2 with 5 items per page
curl "http://localhost:8000/items?skip=5&limit=5"
```

### Advanced Filtering
```bash
# Complex search: laptops in electronics, price range $500-$2000, sorted by name
curl "http://localhost:8000/items/search?q=laptop&category=Electronics&min_price=500&max_price=2000&sort_by=name&sort_order=asc&limit=10"
```

## 🧪 API Testing Guide

### Testing with Swagger UI (Recommended)
1. Navigate to http://localhost:8000/docs
2. Use the built-in "Try it out" functionality
3. Authentication is integrated - use the 🔒 Authorize button
4. All examples and schemas are provided
5. Real-time validation and error messages

### Running the Test Suite

**Basic Test Execution:**
```bash
# Run all tests
python -m pytest test_main.py

# Run tests with verbose output
python -m pytest test_main.py -v

# Run specific test class
python -m pytest test_main.py::TestAuthenticationHelp -v

# Run specific test
python -m pytest test_main.py::TestHealthEndpoints::test_root_health_check -v
```

**Test Coverage:**
```bash
# Simple test runner (recommended)
python run_tests.py --simple

# For coverage (if working on your system)
python -m pytest test_main.py --cov=main --cov-report=term-missing

# Alternative coverage approach
python -m coverage run -m pytest test_main.py
python -m coverage report -m
python -m coverage html  # Generates htmlcov/index.html
```

**Test Statistics:**
- ✅ **59 tests** covering all endpoints and functionality
- 🧪 **100% endpoint coverage** - Every API endpoint is tested
- 🔒 **Authentication testing** - Login, registration, token validation
- 📊 **CRUD operations** - Complete Create, Read, Update, Delete testing
- ⚠️ **Error handling** - All error scenarios covered
- 🔍 **Edge cases** - Invalid data, missing authentication, etc.

### Testing with curl

#### Complete Authentication Workflow
```bash
# 1. Register user
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123"}'

# 2. Login and save token
TOKEN=$(curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=testpass123" | jq -r '.access_token')

# 3. Create item
curl -X POST "http://localhost:8000/items" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "Test Item", "description": "A test item", "price": 99.99, "category": "Test"}'

# 4. Get current user
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/auth/me"
```

### Testing with Python requests
```python
import requests

BASE_URL = "http://localhost:8000"

# Register and login
def authenticate():
    # Register
    register_data = {
        "username": "apitest",
        "email": "apitest@example.com",
        "password": "testpass123"
    }
    requests.post(f"{BASE_URL}/auth/register", json=register_data)
    
    # Login
    login_data = {"username": "apitest", "password": "testpass123"}
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    return response.json()["access_token"]

# Use token
token = authenticate()
headers = {"Authorization": f"Bearer {token}"}

# Create item
item_data = {
    "name": "Python Test Item",
    "description": "Created via Python script",
    "price": 149.99,
    "category": "Software"
}
response = requests.post(f"{BASE_URL}/items", json=item_data, headers=headers)
print(response.json())
```

### Postman Collection

Save this as a Postman collection for easy testing:

```json
{
  "info": {
    "name": "FastAPI Demo",
    "description": "Complete API testing collection"
  },
  "auth": {
    "type": "bearer",
    "bearer": [{"key": "token", "value": "{{jwt_token}}"}]
  },
  "item": [
    {
      "name": "Auth - Register",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"username\": \"postmanuser\",\n  \"email\": \"postman@example.com\",\n  \"password\": \"postmanpass123\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/auth/register",
          "host": ["{{base_url}}"],
          "path": ["auth", "register"]
        }
      }
    },
    {
      "name": "Auth - Login",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/x-www-form-urlencoded"}],
        "body": {
          "mode": "urlencoded",
          "urlencoded": [
            {"key": "username", "value": "postmanuser"},
            {"key": "password", "value": "postmanpass123"}
          ]
        },
        "url": {
          "raw": "{{base_url}}/auth/login",
          "host": ["{{base_url}}"],
          "path": ["auth", "login"]
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test(\"Login successful\", function () {",
              "    pm.response.to.have.status(200);",
              "    var jsonData = pm.response.json();",
              "    pm.environment.set(\"jwt_token\", jsonData.access_token);",
              "});"
            ]
          }
        }
      ]
    }
  ],
  "variable": [
    {"key": "base_url", "value": "http://localhost:8000"}
  ]
}
```

## 🛠️ Data Models

### User Model (Request)
```json
{
  "username": "string (3-50 chars, unique)",
  "email": "valid email address (unique)",
  "full_name": "string (optional, max 100 chars)",
  "password": "string (min 8 chars, for creation only)"
}
```

### User Model (Response)
```json
{
  "id": "integer (auto-generated)",
  "username": "string",
  "email": "string",
  "full_name": "string or null",
  "created_at": "ISO datetime",
  "is_active": "boolean"
}
```

### Item Model (Request)
```json
{
  "name": "string (1-100 chars)",
  "description": "string (optional, max 500 chars)",
  "price": "positive number",
  "category": "string"
}
```

### Item Model (Response)
```json
{
  "id": "integer (auto-generated)",
  "name": "string",
  "description": "string or null",
  "price": "number",
  "category": "string",
  "owner_id": "integer",
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime"
}
```

## 🔍 Query Parameters

### Pagination (applies to list endpoints)
- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum items to return (default: 10, max: 100)

### Item Filtering (`/items` endpoint)
- `search`: Search in item name and description
- `category`: Filter by exact category match
- `min_price`: Minimum price (inclusive)
- `max_price`: Maximum price (inclusive)
- `owner_id`: Filter by owner ID (authenticated requests only)

### Advanced Search (`/items/search` endpoint)
- `q`: General search query (searches name and description)
- `category`: Filter by category
- `min_price`: Minimum price filter
- `max_price`: Maximum price filter
- `sort_by`: Sort field (`name`, `price`, `created_at`, `updated_at`)
- `sort_order`: Sort order (`asc`, `desc`)
- `limit`: Maximum results (1-100, default: 20)

### Examples
```bash
# Basic pagination
GET /items?skip=10&limit=5

# Search with filters
GET /items?search=laptop&category=Electronics&min_price=500

# Advanced search with sorting
GET /items/search?q=gaming&sort_by=price&sort_order=desc&limit=10
```

## ⚠️ Error Handling

The API returns consistent error responses with helpful messages:

### Standard Error Format
```json
{
  "detail": "Human-readable error description"
}
```

### Validation Error Format
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Error description",
      "type": "error_type"
    }
  ]
}
```

### Common HTTP Status Codes
- **200**: Success - Request completed successfully
- **201**: Created - Resource created successfully
- **400**: Bad Request - Invalid data or duplicate resource
- **401**: Unauthorized - Missing or invalid authentication
- **403**: Forbidden - Insufficient permissions
- **404**: Not Found - Resource doesn't exist
- **422**: Unprocessable Entity - Validation errors

### Authentication Error Examples
```json
// Missing token
{
  "detail": "Authentication required. Please login and include your token in the Authorization header as 'Bearer <token>'. Visit /auth/help for detailed instructions."
}

// Invalid credentials
{
  "detail": "Incorrect username or password"
}

// Expired token
{
  "detail": "Token has expired. Please login again to get a new token at /auth/login"
}
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256

# Application
DEBUG=false
ENVIRONMENT=production
APP_NAME=FastAPI Demo

# Authentication
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (comma-separated list)
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Configuration Details

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | JWT signing key | `your-secret-key...` | ✅ |
| `DEBUG` | Enable debug mode | `false` | ❌ |
| `ENVIRONMENT` | Environment name | `development` | ❌ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `30` | ❌ |
| `CORS_ORIGINS` | Allowed CORS origins | `*` | ❌ |

### Security Best Practices
1. **Change SECRET_KEY**: Use a strong, unique secret key in production
2. **HTTPS Only**: Always use HTTPS in production
3. **Token Expiration**: Set appropriate token expiration times
4. **CORS Configuration**: Restrict CORS origins to trusted domains
5. **Password Security**: Implement proper password hashing (bcrypt)

## 🏗️ Development

### Project Structure
```
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
├── README.md           # This documentation
└── __pycache__/        # Python cache (auto-generated)
```

### Running in Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload and debug
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

# Alternative: Run with custom host/port
uvicorn main:app --reload --host 127.0.0.1 --port 8080
```

### Accessing Documentation
- **Swagger UI**: http://localhost:8000/docs (interactive testing)
- **ReDoc**: http://localhost:8000/redoc (beautiful documentation)
- **OpenAPI JSON**: http://localhost:8000/openapi.json (schema)

### Development Tips
1. **Use Swagger UI**: Best for interactive testing and development
2. **Check Logs**: Application logs provide detailed request/response info
3. **Environment Variables**: Use `.env` for local configuration
4. **Token Testing**: Use `/auth/help` for authentication guidance
5. **Data Persistence**: Data is in-memory, restart clears all data

### Running Tests
```bash
# Run all tests (59 comprehensive tests)
python -m pytest test_main.py -v

# Quick test runner
python run_tests.py --simple

# Test specific functionality
python -m pytest test_main.py::TestAuthentication -v
python -m pytest test_main.py::TestItemManagement -v

# Coverage (if working)
python -m pytest test_main.py --cov=main --cov-report=html
```

**Test Coverage**: ✅ 59 tests covering 100% of API endpoints, authentication, CRUD operations, error handling, and edge cases.

## 🚀 Deployment

### Production Considerations

#### Security Checklist
- [ ] Change default `SECRET_KEY`
- [ ] Set `DEBUG=false`
- [ ] Configure proper CORS origins
- [ ] Use HTTPS/TLS certificates
- [ ] Implement proper password hashing
- [ ] Set up rate limiting
- [ ] Configure secure headers

#### Environment Setup
```bash
# Production environment variables
SECRET_KEY=your-production-secret-key-very-long-and-random
DEBUG=false
ENVIRONMENT=production
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

#### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Health Checks
The application provides health check endpoints:
- `GET /health` - Basic health status
- `GET /` - API information and status

## 📚 Additional Resources

### FastAPI Documentation
- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [JWT Authentication Guide](https://fastapi.tiangolo.com/tutorial/security/)

### API Testing Tools
- [Postman](https://www.postman.com/) - API testing platform
- [Insomnia](https://insomnia.rest/) - API client
- [HTTPie](https://httpie.io/) - Command-line HTTP client
- [curl](https://curl.se/) - Command-line tool

### Python Development
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [pip Documentation](https://pip.pypa.io/en/stable/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

This is a demo application, but contributions and improvements are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For questions or issues:
- Check the `/auth/help` endpoint for authentication guidance
- Review the interactive documentation at `/docs`
- Check application logs for error details
- Create an issue for bugs or feature requests

---

**Happy API Development! 🎉**