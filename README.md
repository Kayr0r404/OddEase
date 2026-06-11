# OddEase

A FastAPI-based backend application with dual-database support (PostgreSQL + MongoDB) and Spring Boot starter scaffolding.

## Architecture

```
OddEase/
├── backend/
│   ├── fastAPI/                   # Python FastAPI application
│   │   ├── main.py                # Entry point – creates FastAPI app, registers routers
│   │   ├── .env.example           # Environment variable template
│   │   ├── requirements.txt       # Python dependencies
│   │   ├── shared/                # Shared modules (engine, models, auth, repositories)
│   │   └── services/              # Domain services (auth, user)
│   └── springBoot/OddEase/        # Spring Boot starter (Java, placeholder)
└── README.md
```

## Backend: FastAPI (`backend/fastAPI/`)

### Entry Point — `main.py`

Creates a `FastAPI` app with a lifespan handler (`int_db_engine`) that initialises both databases on startup and tears down PostgreSQL on shutdown. Registers two routers under `/api/v1`:

| Router        | Prefix                |
|---------------|-----------------------|
| User service  | `/api/v1/users`       |
| Auth service  | `/api/v1/auth`        |

---

### `shared/` — Shared Layer

#### `shared/confiq.py`
Pydantic `Settings` loaded from `.env`. Provides:
- JWT secrets (`secret_key`, `refresh_key`) and token lifetimes
- PostgreSQL credentials and computed connection URL (`postgresql+asyncpg://…`)
- MongoDB credentials and computed connection URL (`mongodb://…`)
- `user_db_provider` switch (`"mongo"` / `"postgres"`) to select user repository backend

#### `shared/engine/db_engine.py`
FastAPI lifespan handler. Calls `init_postgres()` and `init_mongo()`, yields a session factory, and closes PostgreSQL on shutdown.

#### `shared/engine/postgres.py`
Initialises an async SQLAlchemy engine (`create_async_engine`) with `asyncpg`, creates all tables via `SQLModel.metadata.create_all`, and exposes an `async_sessionmaker`. Provides `get_session()` and `close_postgres()`.

#### `shared/engine/mongo.py`
Connects to MongoDB via `AsyncMongoClient` and initialises Beanie ODM with the `User` document model.

#### `shared/models/no_sql_models.py`
Beanie ODM documents stored in MongoDB:

| Document | Collection | Key fields |
|----------|------------|------------|
| `User`   | `users`    | username, email, hashed_password, first_name, last_name, avatar_url, sex, created_at |
| `Review` | `reviews`  | user (Link[User]), rating (1-5), content (max 2000 chars), created_at |

- `User` has unique indexes on `username` and `email`, and auto-normalises both to lowercase.
- `Review` indexes on `user.$id` for efficient lookups.

#### `shared/models/sql_models.py`
SQLModel ORM tables stored in PostgreSQL:

| Table     | Fields                                  |
|-----------|-----------------------------------------|
| `Image`   | id (UUID PK), image_url (unique), created_at |
| `Comment` | id, content, created_at                 |
| `Like`    | id, user_id (UUID), created_at          |

All share a `BaseModel` with auto-generated UUID primary key and UTC `created_at`.

#### `shared/models/token.py`
Pydantic model `Token` with `access_token: str` and `token_type: str`.

#### `shared/models/users.py`
Empty file (placeholder).

#### `shared/auth.py`
JWT authentication utilities:

| Function | Purpose |
|----------|---------|
| `hash_password` / `verify_password` | Argon2 password hashing via `pwdlib` |
| `create_access_token` | Short-lived JWT (default 10 min) with `exp`, `iat`, `jti`, `type="access"` |
| `verify_access_token` | Decodes and validates access JWT; returns `sub` (user ID) |
| `try_get_user_id_from_access_token` | Non-raising variant; returns `None` on failure |
| `create_refresh_token` | Long-lived JWT (default 7 days) with `type="refresh"` |
| `verify_refresh_token` | Decodes refresh JWT; validates `type` claim |
| `get_current_user` | FastAPI dependency – reads `access_token` + `csrf_token` cookies, verifies CSRF for mutating methods, fetches user from MongoDB via Beanie |

#### `shared/route_guard.py`
Route-level guard system combining authentication, rate-limiting, and CSRF protection.

| Component | Description |
|-----------|-------------|
| `InMemoryRateStore` | Async-safe in-memory sliding-window rate limiter |
| `GuardConfig` | Frozen dataclass holding auth mode, throttle config, CSRF flag, email verification flag |
| `public_route()` | Returns FastAPI deps for unauthenticated routes (rate-limited by IP) |
| `protected_route()` | Returns FastAPI deps for authenticated routes (rate-limited by user ID, CSRF on mutations, optional email verification) |

Default limits: 120 req/window for public, 60 req/window for protected routes.

#### `shared/repositories/factory.py`
Factory function `get_user_repository()` that returns either a `MongoUserRepository` or `PostgresUserRepository` based on `settings.user_db_provider`.

#### `shared/repositories/UserRepository/`

| File | Description |
|------|-------------|
| `schemas/user_repository.py` | `PrivateUserRecord` / `PublicUserRecord` Pydantic models + `UserRepository` Protocol |
| `mongo_user_repository.py` | MongoDB implementation via Beanie – `get_by_email`, `get_by_id`, `create_user`, stubs for `update_user`/`delete_user`/`get_users` |
| `postgres_user_repository.py` | PostgreSQL implementation – all methods are stubs (not yet implemented) |

---

### `services/auth/` — Authentication Service

#### `services/auth/schemas/schemas.py`
`LoginSchema` – `email: EmailStr`, `password: str`.

#### `services/auth/api/v1/endpoints/endpoints.py`

| Endpoint | Function | Description |
|----------|----------|-------------|
| `POST /token` | `login_for_access_token` | Validates credentials, issues access + refresh JWT + CSRF cookies (HttpOnly, Secure, SameSite) |
| `POST /refresh` | `refresh_token` | Placeholder |
| `DELETE /logout` | `logout` | Placeholder |

The login response sets three cookies:
- `access_token` (HttpOnly, 15 min)
- `refresh_token` (HttpOnly, 30 days)
- `csrf_token` (JS-accessible, 15 min)

#### `services/auth/api/v1/routes/routes.py`
Registers auth endpoints under `/auth`.

---

### `services/user/` — User Service

#### `services/user/schemas/user_schema.py`

| Model | Fields |
|-------|--------|
| `CreateUser` | email, password, first_name, last_name, username, optional avatar_url, optional sex |
| `PrivateUser` | id, email, password, names, username, avatar_url, sex |
| `PublicUser` | id, names, username, avatar_url, sex |

#### `services/user/api/v1/endpoints/endpoints.py`

| Endpoint | Function | Description |
|----------|----------|-------------|
| `POST /register-new-account` | `create_user` | Checks for duplicate email, creates user via repository |
| `PUT /update/{user_id}` | `update_user` | Authorises via `CurrentUser`, updates user fields |
| `DELETE /delete/{user_id}` | `delete_user` | Authorises via `CurrentUser`, deletes user |
| `GET /{user_id}` | `get_user_by_id` | Returns public user profile |
| `GET /` | `get_users` | Lists users (pagination via `skip`/`limit`) |

#### `services/user/api/v1/routes/routes.py`
Registers user endpoints under `/users`. All routes use `public_route()` guard.

---

## Backend: Spring Boot (`backend/springBoot/`)

Minimal Spring Boot 3 application with a single starter class (`OddEaseApplication`) and a context-loads test. Currently a placeholder for future Java microservices.

## Running the Application

### Prerequisites
- Python 3.11+
- MongoDB
- PostgreSQL

### Setup

```bash
cd backend/fastAPI
cp .env.example .env          # edit with your credentials
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | JWT signing key for access tokens |
| `REFRESH_KEY` | JWT signing key for refresh tokens |
| `POSTGRES_DB_*` | PostgreSQL connection parameters |
| `MONGO_DB_*` | MongoDB connection parameters |
| `USER_DB_PROVIDER` | `mongo` (default) or `postgres` |

## Key Dependencies

- **FastAPI** – web framework
- **Beanie** – MongoDB ODM (async)
- **SQLModel / SQLAlchemy** – PostgreSQL ORM (async)
- **PyJWT** – JWT encoding/decoding
- **pwdlib** – Argon2 password hashing
- **pydantic-settings** – environment config
- **uvicorn** – ASGI server
