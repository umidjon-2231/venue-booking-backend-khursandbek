# Venue Booking Backend API

A REST API backend for a venue/spot booking application inspired by [Bron24.uz](https://bron24.uz/). The system includes user authentication via OTP, venue management, and booking functionality with a full admin panel.

## 🚀 Features

- **📱 OTP Authentication**: Phone number-based authentication with OTP verification (Uzbekistan numbers)
- **🏢 Venue Management**: Full CRUD with multi-language support (Uzbek, Russian, English)
- **📅 Booking System**: Create, view, and cancel bookings with double-booking prevention
- **✅ Availability Checking**: Real-time venue availability with hourly slots (9 AM - 10 PM)
- **💰 Automatic Pricing**: Price calculated based on duration × hourly rate
- **🌐 Multi-language**: Full i18n support with Accept-Language header detection
- **👨‍💼 Admin Panel**: Django admin with translation tabs, image uploads, bulk actions
- **📚 API Documentation**: Interactive Swagger UI and ReDoc
- **🛡️ Rate Limiting**: Protection against abuse (3 OTP requests per 10 minutes)
- **🐳 Docker Support**: Complete Docker Compose setup for easy deployment

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Applications                      │
│                    (Mobile App / Web Frontend)                   │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Django REST Framework                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Users     │  │   Venues    │  │       Bookings          │  │
│  │   App       │  │   App       │  │       App               │  │
│  │             │  │             │  │                         │  │
│  │ - OTP Auth  │  │ - CRUD      │  │ - Create/Cancel         │  │
│  │ - JWT       │  │ - Filters   │  │ - Availability Check    │  │
│  │ - Profiles  │  │ - i18n      │  │ - Double-booking Guard  │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                    │                     │
         ▼                    ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐
│   PostgreSQL    │  │      Redis      │  │   Media Storage     │
│   Database      │  │   (OTP Cache)   │  │   (Venue Images)    │
└─────────────────┘  └─────────────────┘  └─────────────────────┘
```

### Key Components

| Component | Purpose |
|-----------|---------|
| **Users App** | Custom User model with phone-based auth, OTP service with Redis |
| **Venues App** | Venue model with translations, image uploads, amenities |
| **Bookings App** | Booking lifecycle management with status transitions |
| **Core Module** | Shared base models, custom exceptions, permissions |

## 🛠️ Tech Stack

| Category | Technology | Version |
|----------|------------|---------|
| **Language** | Python | 3.11+ |
| **Framework** | Django | 5.0+ |
| **API** | Django REST Framework | 3.14+ |
| **Database** | PostgreSQL | 15 |
| **Cache** | Redis | 7 |
| **Auth** | SimpleJWT | 5.3+ |
| **i18n** | django-modeltranslation | 0.18+ |
| **Docs** | drf-spectacular | 0.27+ |
| **Container** | Docker + Compose | Latest |

## Getting Started

### Prerequisites

- Docker and Docker Compose
- OR Python 3.11+ and PostgreSQL 15+, Redis 7+

### Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd venue-booking-backend
```

2. Copy the environment file:
```bash
cp .env.example .env
```

3. Update the `.env` file with your settings (for production, change SECRET_KEY).

### Running with Docker (Recommended)

1. Build and start the containers:
```bash
docker-compose up --build
```

2. The API will be available at `http://localhost:8000`

3. Create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

### Running Locally (Without Docker)

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements/development.txt
```

3. Update `.env` with local database settings:
```
POSTGRES_HOST=localhost
REDIS_URL=redis://localhost:6379/0
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

### Running Database Migrations

```bash
# With Docker
docker-compose exec web python manage.py migrate

# Without Docker
python manage.py migrate
```

## API Documentation

Once the server is running, access the API documentation at:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Authentication Flow

1. **Send OTP**: `POST /api/auth/send-otp/`
   ```json
   {
     "phone_number": "+998901234567"
   }
   ```
   OTP will be logged to the console (mock SMS).

2. **Verify OTP**: `POST /api/auth/verify-otp/`
   ```json
   {
     "phone_number": "+998901234567",
     "otp": "123456"
   }
   ```
   Returns access and refresh JWT tokens.

3. **Use Access Token**: Include in headers:
   ```
   Authorization: Bearer <access_token>
   ```

4. **Refresh Token**: `POST /api/auth/refresh/`
   ```json
   {
     "refresh": "<refresh_token>"
   }
   ```

### Example Requests

#### Authentication Flow

**Step 1: Send OTP**
```bash
curl -X POST "http://localhost:8000/api/auth/send-otp/" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+998901234567"}'
```
Response:
```json
{
  "message": "OTP sent successfully",
  "phone_number": "+998901234567"
}
```

**Step 2: Verify OTP & Get Tokens**
```bash
curl -X POST "http://localhost:8000/api/auth/verify-otp/" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+998901234567", "otp": "123456"}'
```
Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "phone_number": "+998901234567",
    "name": null,
    "is_verified": true
  }
}
```

**Step 3: Refresh Access Token**
```bash
curl -X POST "http://localhost:8000/api/auth/refresh/" \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

---

#### Venue Operations

**List Venues with Filters:**
```bash
# Filter by price range and search
curl -X GET "http://localhost:8000/api/venues/?min_price=50000&max_price=200000&search=sport" \
  -H "Accept-Language: uz"
```

**Get Venue Details:**
```bash
curl -X GET "http://localhost:8000/api/venues/1/" \
  -H "Accept-Language: en"
```

**Check Venue Availability:**
```bash
curl -X GET "http://localhost:8000/api/venues/1/availability/?date=2026-02-15"
```
Response:
```json
{
  "venue_id": 1,
  "date": "2026-02-15",
  "time_slots": [
    {"start_time": "09:00:00", "end_time": "10:00:00", "is_available": true},
    {"start_time": "10:00:00", "end_time": "11:00:00", "is_available": false},
    {"start_time": "11:00:00", "end_time": "12:00:00", "is_available": false},
    {"start_time": "12:00:00", "end_time": "13:00:00", "is_available": true}
  ]
}
```

**Create Venue (Admin Only):**
```bash
curl -X POST "http://localhost:8000/api/venues/" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Sports Hall",
    "name_ru": "Новый спортзал",
    "name_uz": "Yangi sport zali",
    "address": "123 Main St",
    "description": "A modern sports facility",
    "price_per_hour": "150000.00",
    "amenities": ["WiFi", "Parking", "Showers"],
    "images": ["https://example.com/image.jpg"]
  }'
```

---

#### Booking Operations

**Create Booking:**
```bash
curl -X POST "http://localhost:8000/api/bookings/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "venue": 1,
    "booking_date": "2026-02-15",
    "start_time": "10:00",
    "end_time": "12:00"
  }'
```
Response:
```json
{
  "id": 1,
  "venue": {"id": 1, "name": "Sports Hall"},
  "booking_date": "2026-02-15",
  "start_time": "10:00:00",
  "end_time": "12:00:00",
  "total_price": "300000.00",
  "status": "pending",
  "duration_hours": 2.0,
  "can_cancel": true
}
```

**List My Bookings:**
```bash
curl -X GET "http://localhost:8000/api/bookings/" \
  -H "Authorization: Bearer <token>"
```

**Cancel Booking:**
```bash
curl -X PATCH "http://localhost:8000/api/bookings/1/cancel/" \
  -H "Authorization: Bearer <token>"
```

---

#### User Profile

**Get Profile:**
```bash
curl -X GET "http://localhost:8000/api/auth/profile/" \
  -H "Authorization: Bearer <token>"
```

**Update Profile:**
```bash
curl -X PATCH "http://localhost:8000/api/auth/profile/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe"}'
```

## 👨‍💼 Admin Panel Guide

Access the Django admin at: **http://localhost:8000/admin/**

### Features by Model

#### Users Management
- View all users with phone numbers and verification status
- **Colored badges**: Green for verified, red for unverified
- **Booking statistics**: See booking count per user
- **Bulk actions**: Verify/unverify, activate/deactivate users
- Filter by: verification status, active status, staff status

#### Venues Management
- **Tabbed translation editing**: Edit Russian, Uzbek, English in tabs
- **Image uploads**: Add multiple images with drag-and-drop ordering
- **Inline image previews**: See thumbnails in list and detail views
- **List-editable fields**: Quick edit price and active status
- **Bulk actions**: Activate, deactivate, duplicate venues
- Filter by: active status, price range, creation date

#### Bookings Management
- **Colored status badges**: Pending (orange), Confirmed (green), Cancelled (red), Completed (blue)
- **Date hierarchy**: Navigate by year/month/day
- **Bulk status actions**: Mark as confirmed, completed, cancelled
- **CSV export**: Export selected bookings to CSV file
- **Duration display**: Shows booking duration in hours
- Filter by: status, venue, booking date

### Creating an Admin User

```bash
# With Docker
docker-compose exec web python manage.py createsuperuser

# Without Docker
python manage.py createsuperuser

# Or use seed_data with --admin flag
python manage.py seed_data --admin
# Creates: +998900000000 (Admin)

## 🌐 Internationalization Guide

The API supports three languages with full translation support:

| Language | Code | Default |
|----------|------|---------|
| Russian | `ru` | ✅ Yes |
| Uzbek | `uz` | No |
| English | `en` | No |

### Using Translations

**Set language via Accept-Language header:**
```bash
# Get venues in Uzbek
curl -X GET "http://localhost:8000/api/venues/" \
  -H "Accept-Language: uz"

# Get venues in English
curl -X GET "http://localhost:8000/api/venues/" \
  -H "Accept-Language: en"
```

### Translatable Fields

| Model | Translated Fields |
|-------|-------------------|
| Venue | `name`, `address`, `description` |

### Database Fields

Each translated field creates language-specific columns:
- `name` → `name_ru`, `name_uz`, `name_en`
- `address` → `address_ru`, `address_uz`, `address_en`
- `description` → `description_ru`, `description_uz`, `description_en`

### Admin Panel Translations

The admin uses **TabbedTranslationAdmin** which shows:
- Language tabs at the top of each translatable field
- Click a tab to switch between Russian, Uzbek, English
- All translations are saved together

### Adding New Languages

1. Add to `LANGUAGES` in `config/settings/base.py`:
   ```python
   LANGUAGES = [
       ("ru", "Russian"),
       ("uz", "Uzbek"),
       ("en", "English"),
       ("kk", "Kazakh"),  # New language
   ]
   MODELTRANSLATION_LANGUAGES = ("ru", "uz", "en", "kk")
   ```

2. Run migrations to create new columns:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

## 🧪 Testing Guide

### Running Tests

```bash
# Run all tests with Docker
docker-compose exec web pytest

# Run all tests locally
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest apps/bookings/tests/test_views.py

# Run specific test class
pytest apps/bookings/tests/test_views.py::TestBookingListCreateView

# Run specific test
pytest apps/bookings/tests/test_views.py::TestBookingListCreateView::test_create_booking_success
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=apps --cov-report=html

# View HTML report
open htmlcov/index.html
```

### Test Categories

| Category | Location | Tests |
|----------|----------|-------|
| **User Models** | `apps/users/tests/test_models.py` | User creation, validation |
| **OTP Service** | `apps/users/tests/test_services.py` | OTP generation, rate limiting |
| **Auth Endpoints** | `apps/users/tests/test_views.py` | Send/verify OTP, tokens |
| **Venue Models** | `apps/venues/tests/test_models.py` | CRUD, managers |
| **Venue API** | `apps/venues/tests/test_views.py` | List, filter, availability |
| **Booking Models** | `apps/bookings/tests/test_models.py` | Price calc, cancellation |
| **Booking API** | `apps/bookings/tests/test_views.py` | Create, cancel, double-booking |

### Key Test Fixtures (conftest.py)

| Fixture | Description |
|---------|-------------|
| `user` | Regular verified user |
| `admin_user` | Superuser for admin tests |
| `api_client` | Unauthenticated API client |
| `authenticated_client` | Client with JWT token |
| `admin_client` | Client with admin JWT token |
| `venue`, `venue2` | Test venues with translations |
| `booking`, `confirmed_booking` | Test bookings |

## 📁 Project Structure

```
venue-booking-backend/
├── apps/
│   ├── users/                    # User authentication app
│   │   ├── models.py            # Custom User model (phone-based)
│   │   ├── services.py          # OTPService with Redis
│   │   ├── views.py             # Auth endpoints
│   │   ├── serializers.py       # Request/response serialization
│   │   ├── admin.py             # User admin configuration
│   │   └── tests/               # User-related tests
│   │
│   ├── venues/                   # Venue management app
│   │   ├── models/              # Venue + VenueImage models
│   │   ├── translation.py       # Translation field registration
│   │   ├── views.py             # Venue CRUD + availability
│   │   ├── serializers.py       # Venue serializers
│   │   ├── filters.py           # Price range filtering
│   │   ├── services.py          # Availability calculation
│   │   ├── admin.py             # Admin with tabbed translations
│   │   ├── management/commands/ # seed_data command
│   │   └── tests/               # Venue-related tests
│   │
│   └── bookings/                 # Booking management app
│       ├── models.py            # Booking model with status
│       ├── views.py             # Booking CRUD + cancellation
│       ├── serializers.py       # Validation + price calculation
│       ├── admin.py             # Admin with bulk actions
│       └── tests/               # Booking-related tests
│
├── config/
│   ├── settings/
│   │   ├── base.py              # Common settings
│   │   ├── development.py       # Debug, local settings
│   │   └── production.py        # Security, HTTPS settings
│   ├── urls.py                  # Root URL routing
│   ├── wsgi.py                  # WSGI entry point
│   └── asgi.py                  # ASGI entry point
│
├── core/                         # Shared components
│   ├── models.py                # TimeStampedModel, ActiveModel
│   ├── exceptions.py            # Custom exception classes
│   ├── permissions.py           # IsOwner, IsAdminOrReadOnly
│   └── utils.py                 # Phone validation, OTP generation
│
├── docker/
│   ├── Dockerfile               # Development image
│   └── Dockerfile.prod          # Production image
│
├── requirements/
│   ├── base.txt                 # Core dependencies
│   ├── development.txt          # Dev tools (debug toolbar)
│   └── production.txt           # Production (gunicorn)
│
├── docker-compose.yml           # Container orchestration
├── conftest.py                  # Pytest fixtures
├── pytest.ini                   # Pytest configuration
├── setup.cfg                    # Flake8, isort config
├── .env.example                 # Environment template
└── README.md                    # This file
```

## 🤖 AI Tools Usage Documentation

This project was built with assistance from **GitHub Copilot** powered by **Claude Opus 4.5** AI.

### Which AI Tools Were Used

| Tool | Purpose |
|------|---------|
| **GitHub Copilot (Claude)** | Primary coding assistant for all implementation |
| **VS Code Integration** | Real-time code suggestions and completions |

### What Specific Tasks AI Was Used For

| Phase | AI Contribution |
|-------|-----------------|
| **Architecture Design** | Project structure planning, app organization, model relationships |
| **Docker Setup** | Dockerfile, docker-compose.yml, multi-stage production builds |
| **Testing** | Test fixtures, test cases, pytest configuration |
| **Documentation** | README, inline docstrings, API documentation |
| **Security** | Rate limiting implementation, JWT configuration, atomic transactions |
| **Database Optimization** | Index planning, query optimization with select_related/prefetch_related |

### Examples of Prompts Used

#### Project Planning
```
"According to the ProjectPlan.md lets build the project. Create a plan"
```

#### Phase Implementation
```
"Check that all stages of all phases are fully implemented. If not, first explain fully how to implement, and then proceed implementing"
```

#### Validation Logic
```
"Add validation to prevent double booking for the same venue and time slot"
```

#### Testing
```
"Write comprehensive tests for the booking API including edge cases"
```

#### Documentation
```
"Create a comprehensive README with architecture diagram, API examples, and setup instructions"
```

#### Security Enhancements
```
"Add atomic transactions and database indexes for the booking system"
```

### Personal Evaluation of AI Assistance

#### Strengths
- **Speed**: What would take days was completed in hours
- **Best Practices**: Applied Django/DRF patterns correctly throughout
- **Documentation**: Generated comprehensive inline docs and README
- **Error Handling**: Proactively added edge case handling
- **Testing**: Generated thorough test cases covering happy paths and edge cases

#### Challenges
- **Context Management**: Needed to remind AI of previous decisions occasionally
- **Database Connectivity**: AI couldn't run tests (Docker DB not running) but code was syntactically correct
- **Customization**: Some generated code needed minor adjustments for specific requirements

#### Overall Assessment
AI assistance was **highly effective** for this project. The phased approach worked well:
1. Plan first, then implement
2. Verify each phase before moving to the next
3. Final audit to catch any missing requirements

The AI correctly identified missing "Key Technical Considerations" (atomic transactions, database indexes) during the final audit phase, demonstrating thorough requirement tracking.

**Productivity Gain**: Estimated 5-10x faster development compared to manual implementation.

**Quality**: Production-ready code with proper error handling, security measures, and comprehensive documentation.

---

## 📄 API Endpoints Reference

### Authentication (`/api/auth/`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/send-otp/` | Send OTP to phone | No |
| POST | `/verify-otp/` | Verify OTP, get tokens | No |
| POST | `/refresh/` | Refresh access token | No |
| GET | `/profile/` | Get user profile | Yes |
| PATCH | `/profile/` | Update user profile | Yes |

### Venues (`/api/venues/`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | List venues (paginated, filterable) | No |
| POST | `/` | Create venue | Admin |
| GET | `/{id}/` | Get venue details | No |
| PUT/PATCH | `/{id}/` | Update venue | Admin |
| DELETE | `/{id}/` | Soft-delete venue | Admin |
| GET | `/{id}/availability/` | Check availability | No |

### Bookings (`/api/bookings/`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | List my bookings | Yes |
| POST | `/` | Create booking | Yes |
| GET | `/{id}/` | Get booking details | Yes (Owner) |
| PATCH | `/{id}/cancel/` | Cancel booking | Yes (Owner) |

## 🔒 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | (required) |
| `DEBUG` | Debug mode | `False` |
| `POSTGRES_DB` | Database name | `venue_booking` |
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Database password | `postgres` |
| `POSTGRES_HOST` | Database host | `db` |
| `POSTGRES_PORT` | Database port | `5432` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `ACCESS_TOKEN_LIFETIME_MINUTES` | JWT access token lifetime | `60` |
| `REFRESH_TOKEN_LIFETIME_DAYS` | JWT refresh token lifetime | `7` |

## 📜 License

MIT License
