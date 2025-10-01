# Quick Start Guide 🚀

Welcome to the FastAPI Demo Application! This guide will get you up and running in minutes.

## ⚡ Super Quick Start (30 seconds)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
uvicorn main:app --reload

# 3. Open your browser
# Visit: http://localhost:8000/docs
```

**That's it!** You now have a fully functional API running!

---

## 🔐 Test Authentication (1 minute)

### Using the Interactive Docs

1. **Open Swagger UI**: http://localhost:8000/docs

2. **Find the Login endpoint**:
   - Scroll to "Authentication" section
   - Click on `POST /auth/login`

3. **Try it out**:
   - Click "Try it out" button
   - Enter credentials:
     - Username: `admin`
     - Password: `password`
   - Click "Execute"

4. **Copy your token**:
   - Find `access_token` in the response
   - Copy it (without quotes)

5. **Authorize**:
   - Click the green 🔒 "Authorize" button at top
   - Paste token in the "Value" field
   - Click "Authorize"
   - Click "Close"

6. **Test protected endpoints**:
   - Now try `GET /auth/me` to see your user info!

---

## 💻 Using Command Line (curl)

```bash
# Login and get token
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=password" | jq -r '.access_token')

# Use the token
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/auth/me"

# Create an item
curl -X POST "http://localhost:8000/items" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "My First Item",
       "description": "This is a test item",
       "price": 99.99,
       "category": "Test"
     }'

# List all items
curl "http://localhost:8000/items"
```

---

## 📚 What to Explore Next

### Documentation
- **Swagger UI**: http://localhost:8000/docs - Interactive testing
- **ReDoc**: http://localhost:8000/redoc - Beautiful documentation
- **Tutorial**: Read [tutorials.md](tutorials.md) - Learn everything in simple English

### Key Endpoints to Try

#### Public Endpoints (No auth needed)
- `GET /` - Health check
- `GET /health` - Detailed health info
- `GET /items` - List all items
- `GET /items/{id}` - Get specific item
- `GET /auth/help` - Complete authentication guide
- `GET /api/info` - API overview

#### Protected Endpoints (Auth required)
- `GET /auth/me` - Get current user
- `POST /items` - Create new item
- `PUT /items/{id}` - Update item
- `DELETE /items/{id}` - Delete item
- `GET /users` - List all users
- `GET /stats` - Get statistics

### Advanced Features
- **Search**: Try `GET /items/search?q=laptop&min_price=100`
- **Filter**: Try `GET /items?category=Electronics&limit=5`
- **Pagination**: Try `GET /items?skip=0&limit=10`

---

## 🎓 Learning Path

1. **Start Here**: Use Swagger UI at `/docs` to explore
2. **Read Tutorial**: Open [tutorials.md](tutorials.md) for detailed explanations
3. **Test Endpoints**: Try creating, reading, updating, and deleting items
4. **Understand Auth**: Read the authentication section in tutorials.md
5. **Build Something**: Use this as a template for your own API!

---

## ❓ Common Questions

### How do I register a new user?
```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "newuser",
       "email": "user@example.com",
       "password": "securepassword123",
       "full_name": "New User"
     }'
```

### How long do tokens last?
Tokens expire after 30 minutes. Just login again to get a new one!

### Can I change the default credentials?
Yes! The default "admin" user is created at startup in `main.py`. You can modify it or create new users via registration.

### Where is the data stored?
Currently in memory (lists in Python). When you restart the server, data is reset. For production, you'd connect to a real database like PostgreSQL.

### How do I add HTTPS?
In production, use a reverse proxy like Nginx or deploy to a platform that handles HTTPS (like Heroku, AWS, etc.).

---

## 🔧 Troubleshooting

### Server won't start
- Check if port 8000 is already in use
- Make sure all dependencies are installed: `pip install -r requirements.txt`

### Can't login
- Use the default credentials: `admin` / `password`
- Check the server logs for error messages

### Token expired
- Login again to get a fresh token
- Tokens expire after 30 minutes

### Permission denied errors
- Make sure you're logged in and authorized
- Check that you own the resource you're trying to modify

---

## 🎉 You're Ready!

You now have a fully functional API with:
- ✅ JWT authentication
- ✅ User management
- ✅ CRUD operations
- ✅ Search and filtering
- ✅ Interactive documentation

**Next Steps:**
- Read [tutorials.md](tutorials.md) to understand how it all works
- Check [DOCUMENTATION_IMPROVEMENTS.md](DOCUMENTATION_IMPROVEMENTS.md) to see what's new
- Start building your own endpoints!

**Happy coding!** 💻✨
