# PlanVenture API

PlanVenture API is a Flask REST API for user authentication and trip management. It uses SQLAlchemy for database access, bcrypt for password hashing, and JWTs for protected API routes.

## Features

- User registration and login
- bcrypt password hashing
- JWT authentication with 24-hour access tokens
- Authenticated trip CRUD operations
- Automatic default itineraries based on travel dates
- SQLite database support
- CORS support for React and Vite development servers

## Technology Stack

- Python 3.8+
- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-CORS
- bcrypt
- python-dotenv
- SQLite

## Project Structure

```text
planventure-api/
|-- app.py                 # Flask application and configuration
|-- auth.py                # Registration and login routes
|-- auth_middleware.py     # Authentication helpers and decorators
|-- extensions.py          # Shared SQLAlchemy instance
|-- init_db.py             # Database table creation script
|-- jwt_utils.py           # JWT generation and validation helpers
|-- models.py              # User and Trip SQLAlchemy models
|-- password_utils.py      # Password hashing and verification helpers
|-- trip_routes.py         # Trip CRUD routes
|-- requirements.txt       # Python dependencies
|-- .env                   # Local environment variables
|-- .sample.env            # Environment variable template
`-- README.md              # API documentation
```

## Setup

### 1. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 2. Configure environment variables

Copy the sample file:

```powershell
Copy-Item .sample.env .env
```

Update `.env` as needed:

```env
SECRET_KEY=replace-with-a-long-random-secret
JWT_SECRET_KEY=replace-with-another-long-random-secret
DATABASE_URL=sqlite:///planventure.db
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

Multiple CORS origins can be separated with commas.

### 3. Create database tables

```powershell
python init_db.py
```

The SQLite database is created in the Flask instance directory unless another `DATABASE_URL` is configured.

### 4. Start the API

```powershell
python app.py
```

The API defaults to:

```text
http://localhost:5000
```

## Authentication

JWT tokens are valid for 24 hours. Send an access token in protected requests:

```http
Authorization: Bearer <access-token>
```

### Register

```http
POST /auth/register
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:

```json
{
  "message": "User registered successfully",
  "access_token": "<jwt-token>",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

Registration returns `201 Created`. Invalid email addresses or passwords return `400 Bad Request`; a duplicate email returns `409 Conflict`.

### Login

```http
POST /auth/login
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Successful login returns `200 OK` with an access token and user details. Invalid credentials return `401 Unauthorized`.

## API Routes

### General Routes

#### Home

```http
GET /
```

Response:

```json
{
  "message": "Welcome to PlanVenture API"
}
```

#### Health Check

```http
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

### Trip Routes

All trip routes require a valid JWT.

#### Create a Trip

```http
POST /trips
Authorization: Bearer <access-token>
Content-Type: application/json
```

```json
{
  "destination": "Paris, France",
  "start_date": "2026-12-01",
  "end_date": "2026-12-05",
  "latitude": 48.8566,
  "longitude": 2.3522,
  "itinerary": [
    {
      "day": 1,
      "date": "2026-12-01",
      "activities": ["Visit the Eiffel Tower"]
    },
    {
      "day": 2,
      "date": "2026-12-02",
      "activities": ["Visit the Louvre"]
    }
  ]
}
```

If `itinerary` is omitted, PlanVenture generates an entry for every inclusive travel date:

```json
[
  {
    "day": 1,
    "date": "2026-12-01",
    "activities": []
  },
  {
    "day": 2,
    "date": "2026-12-02",
    "activities": []
  }
]
```

Date values must use ISO format: `YYYY-MM-DD`.

#### List Trips

```http
GET /trips
Authorization: Bearer <access-token>
```

Returns the trips belonging to the authenticated user.

#### Get a Trip

```http
GET /trips/<trip_id>
Authorization: Bearer <access-token>
```

Returns `404 Not Found` when the trip does not exist or belongs to another user.

#### Update a Trip

```http
PATCH /trips/<trip_id>
Authorization: Bearer <access-token>
Content-Type: application/json
```

```json
{
  "destination": "Rome, Italy",
  "end_date": "2026-12-06"
}
```

`PUT` and `PATCH` are both supported.

#### Delete a Trip

```http
DELETE /trips/<trip_id>
Authorization: Bearer <access-token>
```

Success response:

```json
{
  "message": "Trip deleted successfully"
}
```

## Data Models

### User

| Field | Type | Description |
| --- | --- | --- |
| `id` | Integer | Primary key |
| `email` | String | Unique, normalized email address |
| `password_hash` | String | bcrypt password hash |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

### Trip

| Field | Type | Description |
| --- | --- | --- |
| `id` | Integer | Primary key |
| `user_id` | Integer | Owning user ID |
| `destination` | String | Trip destination |
| `start_date` | Date | First travel day |
| `end_date` | Date | Final travel day |
| `latitude` | Float | Optional latitude |
| `longitude` | Float | Optional longitude |
| `itinerary` | JSON | Daily itinerary data |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

Each trip belongs to one user. Deleting a user removes their trips through the configured relationship cascade.

## Authentication Errors

Missing token:

```json
{
  "error": "Authentication token is required"
}
```

Status: `401 Unauthorized`

Invalid token:

```json
{
  "error": "Invalid authentication token"
}
```

Status: `401 Unauthorized`

Expired token:

```json
{
  "error": "Authentication token has expired"
}
```

Status: `401 Unauthorized`

## Development Notes

- Use a strong, unique JWT secret outside development.
- Passwords are never stored in plain text.
- Trip ownership is checked before trip access or modification.
- Coordinates are optional but, when supplied, must be numeric.
- End dates cannot precede start dates.
- An itinerary must be supplied as a JSON array when provided.
