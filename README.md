<div align="center">

# 💸 Personal Expense Tracker API

**A small REST API to register, log in, and track your own expenses by category.**

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-SQLAlchemy-4169E1?logo=postgresql&logoColor=white)
![uv](https://img.shields.io/badge/package%20manager-uv-DE5FE9)
![Status](https://img.shields.io/badge/status-in%20development-orange)

</div>

---

## ✨ Features

| | Feature | Description |
|---|---|---|
| 🔐 | Register & login | Sign up with email + password (hashed with bcrypt), log in to get a JWT |
| 🎫 | Token auth | Every expense/category/user route needs a `Bearer` token (60 min by default) |
| 💰 | Expenses CRUD | List, get, create, update, delete your expenses |
| 🏷️ | Categories CRUD | List, get, create, rename, delete your categories |
| 👤 | Profile | `GET /users/me` returns the logged-in user |
| 🧱 | Data isolation | You only see and change your own data |
| ✅ | Validation | Valid email, password ≥ 6 chars, amount > 0, category must be yours |
| 📖 | Auto docs | Swagger UI at `/docs` |

---

## 🗺️ How it works

### Big picture

```mermaid
flowchart LR
    U["🧑 Client / Swagger UI"] -->|HTTP + JWT| A["⚡ FastAPI app<br/>main.py"]
    A --> R["🛣️ Routers<br/>auth, users, expenses, categories"]
    R --> S["📐 Pydantic schemas<br/>validation"]
    R --> AU["🔑 auth_utils<br/>hash + JWT"]
    R --> M["🗃️ SQLAlchemy models"]
    M --> DB[("🐘 PostgreSQL")]

    classDef client fill:#fde68a,stroke:#b45309,color:#000
    classDef app fill:#bbf7d0,stroke:#15803d,color:#000
    classDef logic fill:#bfdbfe,stroke:#1d4ed8,color:#000
    classDef db fill:#fecaca,stroke:#b91c1c,color:#000
    class U client
    class A,R app
    class S,AU,M logic
    class DB db
```

### Request flow (protected route)

```mermaid
flowchart TD
    A["📥 Request with Bearer token"] --> B{"🔑 JWT valid<br/>and not expired?"}
    B -- No --> X["❌ 401 Unauthorized"]
    B -- Yes --> C{"👤 User exists in DB?"}
    C -- No --> X
    C -- Yes --> D{"📐 Body valid?"}
    D -- No --> Y["❌ 422 Validation error"]
    D -- Yes --> E{"🧱 Row belongs<br/>to this user?"}
    E -- No --> Z["❌ 404 Not found"]
    E -- Yes --> F["✅ Read / write DB<br/>and return JSON"]

    style X fill:#fecaca,stroke:#b91c1c
    style Y fill:#fecaca,stroke:#b91c1c
    style Z fill:#fecaca,stroke:#b91c1c
    style F fill:#bbf7d0,stroke:#15803d
```

### Example: log in and add an expense

```mermaid
sequenceDiagram
    actor User as 🧑 User
    participant API as ⚡ FastAPI
    participant Auth as 🔑 auth_utils
    participant DB as 🐘 PostgreSQL

    User->>API: POST /auth/login (email, password)
    API->>DB: find user by email
    DB-->>API: user row
    API->>Auth: verify_password()
    Auth-->>API: ok
    API-->>User: access_token (JWT)

    User->>API: POST /expenses/ (Bearer token + body)
    API->>Auth: get_current_user()
    Auth->>DB: find user by id from token
    API->>DB: find category (must be yours)
    API->>DB: INSERT expense
    DB-->>API: new row
    API-->>User: 201 Created
```

### Module map

```mermaid
flowchart TD
    main["🚀 main.py"] --> routers["🛣️ routers/*"]
    main --> models["🗃️ models.py"]
    main --> database["🐘 database.py"]
    routers --> schemas["📐 schemas/*"]
    routers --> auth_utils["🔑 auth_utils.py"]
    routers --> models
    routers --> database
    auth_utils --> models
    auth_utils --> database
    models --> database

    classDef entry fill:#fde68a,stroke:#b45309,color:#000
    classDef mod fill:#bfdbfe,stroke:#1d4ed8,color:#000
    classDef core fill:#fecaca,stroke:#b91c1c,color:#000
    class main entry
    class routers,schemas,auth_utils mod
    class models,database core
```

> [!TIP]
> **Key idea:** every query filters by `current_user.id`. The user id comes from the JWT, so one user can never read or edit another user's expenses or categories.

---

## 🛠️ Main components

| Component | Tool | What it does |
|---|---|---|
| 🌐 Web framework | FastAPI | Routes, validation, Swagger docs |
| 🗃️ ORM | SQLAlchemy 2 | Maps `User`, `Category`, `Expense` to tables |
| 🐘 Database driver | psycopg 3 | Connects to PostgreSQL |
| 📐 Schemas | Pydantic v2 | Request/response models (`EmailStr`, `Field`) |
| 🔒 Passwords | passlib + bcrypt | Hash and verify passwords |
| 🎫 Tokens | PyJWT (HS256) | Create and decode access tokens |
| ⚙️ Config | python-dotenv | Loads settings from `.env` |

### Endpoints

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/auth/register` | ❌ | Create account |
| POST | `/auth/login` | ❌ | Get JWT (form: `username` = email, `password`) |
| GET | `/users/me` | ✅ | Current user |
| GET / POST | `/expenses/` | ✅ | List / create |
| GET / PUT / DELETE | `/expenses/{id}` | ✅ | Get / update / delete |
| GET / POST | `/categories/` | ✅ | List / create |
| GET / PUT / DELETE | `/categories/{id}` | ✅ | Get / rename / delete |

---

## 🚀 Getting started

### Requirements

- 🐍 Python 3.13+
- 📦 [uv](https://docs.astral.sh/uv/)
- 🐘 A running PostgreSQL server with a database (e.g. `ExpenseTracker`)

### Setup

```bash
# 1. Install dependencies
uv sync

# 2. Create a .env file in the project root
```

```env
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/ExpenseTracker
SECRET_KEY=change-me-to-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Run

```bash
uv run fastapi dev main.py
```

Tables are created automatically on startup. Open http://127.0.0.1:8000/docs.

### Example session

```text
POST /auth/register   {"email": "me@example.com", "password": "secret123"}
-> 201 {"id": 1, "email": "me@example.com"}

POST /auth/login      username=me@example.com&password=secret123
-> 200 {"access_token": "eyJ...", "token_type": "bearer"}

POST /categories/     {"name": "Food"}                      (Bearer token)
-> 201 {"id": 1, "name": "Food"}

POST /expenses/       {"title": "Lunch", "amount": 5.5, "date": "2026-11-08", "category_id": 1}
-> 201 {"id": 1, "title": "Lunch", "amount": 5.5, "date": "2026-11-08", "category_id": 1}

DELETE /categories/1
-> 400 "Cannot delete category because it is referenced by existing expenses"
```

---

## 📂 Project structure

```text
Personal-Expense-Tracker-API/
├── 🚀 main.py            # App entry: creates tables, registers routers
├── 🐘 database.py        # Engine, session, get_db dependency
├── 🗃️ models.py          # SQLAlchemy tables: User, Category, Expense
├── 🔑 auth_utils.py      # Password hashing, JWT create/decode, get_current_user
├── 🛣️ routers/
│   ├── 🔐 auth.py        # /auth/register, /auth/login
│   ├── 👤 users.py       # /users/me
│   ├── 💰 expenses.py    # /expenses CRUD
│   └── 🏷️ categories.py  # /categories CRUD
├── 📐 schemas/
│   ├── user.py           # UserCreate, UserResponse
│   ├── category.py       # CategoryCreate, CategoryUpdate, CategoryResponse
│   ├── expense.py        # ExpenseCreate, ExpenseUpdate, ExpenseResponse
│   └── token.py          # Token
├── ⚙️ .env               # Local settings (git-ignored)
└── 📦 pyproject.toml     # Dependencies
```

---

## ⚠️ Safety notes & limitations

> [!WARNING]
> - `database.py` and `auth_utils.py` still contain **fallback defaults** (a DB password and a secret key) used when `.env` is missing. Remove them before sharing the code or deploying, and rotate any credential that was ever committed.
> - Always set a strong, unique `SECRET_KEY` in `.env`. Never commit `.env`.
> - Tables are made with `create_all`. There are no migrations, so changing a model won't alter existing tables.
> - No tests, rate limiting, or HTTPS setup are included.
> - Deleting a category is blocked while expenses use it. Deleting a user is not supported.

---

## 🧭 Roadmap

- [x] Register and login with JWT
- [x] Expenses CRUD (scoped per user)
- [x] Categories CRUD with duplicate-name check
- [x] `GET /users/me`
- [x] Input validation and env-based config
- [ ] Remove hardcoded fallback secrets
- [ ] Database migrations (Alembic)
- [ ] Automated tests
- [ ] Filter / sort / paginate expenses
- [ ] Spending summaries per category or month

