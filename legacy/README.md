# 📍 Back2Me — Campus Lost & Found Platform

> Production-grade Full-Stack Web Application  
> **Stack:** HTML · CSS · JavaScript · Python (Flask) · MongoDB

---

## 🏗 Architecture

```
back2me_v2/
├── frontend/
│   ├── index.html               ← Smart redirect entry point
│   ├── css/
│   │   └── style.css            ← Complete dark-theme design system
│   ├── js/
│   │   ├── app.js               ← API client, auth guards, post renderer
│   │   └── shell.js             ← Shared topbar + sidebar injector
│   └── pages/
│       ├── login.html
│       ├── register.html
│       ├── forgot-password.html
│       ├── home.html            ← Live feed (all posts)
│       ├── lost.html            ← Filtered lost posts
│       ├── found.html           ← Filtered found posts
│       ├── create-post.html     ← Create new report
│       ├── search.html          ← Full-text + regex search
│       └── messages.html        ← Real-time-style DM threads
│
└── backend/
    ├── app.py                   ← Flask app factory + SPA serving
    ├── config/
    │   └── database.py          ← MongoDB connection + index setup
    └── routes/
        ├── auth.py              ← /register /login /logout /me /forgot-password
        ├── posts.py             ← CRUD + /lost /found /search
        └── messages.py          ← Send, conversations, thread view
```

---

## ⚡ Quick Start

### 1 — Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.10+ |
| MongoDB | 6.x (local or Atlas) |
| pip | latest |

### 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### 3 — Configure MongoDB (optional)

By default the app connects to `mongodb://localhost:27017/back2me`.  
Override with environment variables:

```bash
export MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net/"
export DB_NAME="back2me"
export JWT_SECRET="change_me_in_production"
```

Or use a `.env` file and `python-dotenv`.

### 4 — Run the server

```bash
cd backend
python app.py
```

Server starts at **http://localhost:5000**  
Open your browser → you'll be redirected to login.

---

## 🔌 API Reference

All routes are prefixed with `/api`.

### Auth

| Method | Path | Body | Auth |
|--------|------|------|------|
| POST | `/register` | `{username, email, password}` | No |
| POST | `/login` | `{email, password}` | No |
| POST | `/logout` | — | No |
| GET | `/me` | — | Cookie |
| POST | `/forgot-password` | `{email}` | No |

### Posts

| Method | Path | Params | Auth |
|--------|------|--------|------|
| GET | `/posts` | `page` | No |
| POST | `/posts` | JSON body | Cookie |
| GET | `/posts/lost` | `page` | No |
| GET | `/posts/found` | `page` | No |
| GET | `/posts/search` | `q, post_type, page` | No |
| DELETE | `/posts/<id>` | — | Cookie (owner) |

**Create Post Body:**
```json
{
  "post_type": "lost",
  "item_name": "Blue Nike Backpack",
  "place":     "Library 2nd Floor",
  "location":  "Main Campus",
  "time":      "Today, 3:00 PM",
  "description": "Has my laptop inside",
  "image_url": "https://…"
}
```

### Messages

| Method | Path | Body | Auth |
|--------|------|------|------|
| POST | `/messages` | `{receiver_id, message_text}` | Cookie |
| GET | `/messages/conversations` | — | Cookie |
| GET | `/messages/<user_id>` | — | Cookie |

---

## 🗄 MongoDB Collections

### `users`
```json
{
  "_id": ObjectId,
  "username": "johndoe",
  "email": "john@campus.edu",
  "hashed_password": "sha256_hash",
  "profile_image": "https://…",
  "created_at": ISODate
}
```

### `posts`
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "username": "johndoe",
  "profile_image": "https://…",
  "post_type": "lost",
  "item_name": "Blue Nike Backpack",
  "place": "Library 2nd Floor",
  "time": "Today, 3 PM",
  "location": "Main Campus",
  "description": "Has my laptop inside",
  "image_url": "https://…",
  "created_at": ISODate
}
```

### `messages`
```json
{
  "_id": ObjectId,
  "sender_id": ObjectId,
  "receiver_id": ObjectId,
  "message_text": "Is it still available?",
  "timestamp": ISODate
}
```

---

## 🔒 Security Notes

- Passwords hashed with **SHA-256** (swap for `bcrypt` in production)
- **JWT** stored in `HttpOnly` cookies — not accessible from JS
- Protected routes return **401** without a valid, unexpired token
- Input sanitised server-side (length limits, type validation)
- HTML escaped client-side via `esc()` to prevent XSS

---

## 🔍 MongoDB Indexes

Created automatically on first run:

```python
# users
db.users.create_index("email",    unique=True)
db.users.create_index("username", unique=True)

# posts
db.posts.create_index([("item_name", TEXT), ("place", TEXT),
                        ("location", TEXT), ("description", TEXT)])
db.posts.create_index("post_type")
db.posts.create_index("created_at")

# messages
db.messages.create_index([("sender_id", ASC), ("receiver_id", ASC)])
db.messages.create_index("timestamp")
```

---

## 🌐 Deployment

### With Atlas (Free Tier)

1. Create cluster at https://cloud.mongodb.com
2. Get connection string
3. `export MONGO_URI="mongodb+srv://…"`
4. `export FLASK_DEBUG=0`
5. Use **gunicorn** for production:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### With Docker (optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend/app:app"]
```

---

## ✅ Feature Checklist

- [x] Secure registration with duplicate check
- [x] Login with JWT cookie auth
- [x] Forgot password endpoint
- [x] Protected routes (server-side + client-side guard)
- [x] Create lost/found posts stored in MongoDB
- [x] Home feed — real data only, paginated
- [x] Lost section — filtered by `post_type = "lost"`
- [x] Found section — filtered by `post_type = "found"`
- [x] Search — case-insensitive regex across all fields
- [x] Delete own posts
- [x] Messaging — send, conversations list, thread view
- [x] Professional dark-theme UI (no Bootstrap)
- [x] Consistent navigation across all pages
- [x] No hardcoded / pseudo data anywhere
- [x] MongoDB indexes for performance
- [x] Input validation (frontend + backend)
- [x] XSS prevention via HTML escaping
- [x] Paginated post results
- [x] Responsive (mobile + desktop)
