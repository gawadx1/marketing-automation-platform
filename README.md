# Marketing Automation & Reporting Platform

A production-grade Marketing Technology (MarTech) platform built with Python, FastAPI, PostgreSQL, Redis, Celery, and Docker. This system simulates a real enterprise marketing platform that collects data from multiple ad platforms, manages contacts, automates campaigns, generates reports, and triggers workflows.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│              (Swagger UI, API Clients, cURL)                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      API GATEWAY (FastAPI)                    │
│  ┌───────┐ ┌───────┐ ┌──────────┐ ┌──────┐ ┌───────────┐  │
│  │ Auth  │ │Campaign│ │Dashboard │ │News  │ │Automation │  │
│  │Routes │ │Routes  │ │ Routes   │ │Routes│ │  Routes   │  │
│  └───┬───┘ └───┬───┘ └────┬─────┘ └──┬───┘ └─────┬─────┘  │
└──────┼─────────┼──────────┼───────────┼────────────┼───────┘
       │         │          │           │            │
┌──────▼─────────▼──────────▼───────────▼────────────▼───────┐
│                    SERVICE LAYER                              │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐  │
│  │ Integrations │  │   Analytics   │  │   Reporting      │  │
│  │  (Google,    │  │   & Metrics   │  │   (CSV, JSON)    │  │
│  │   Meta,      │  │               │  │                  │  │
│  │   HubSpot,   │  │               │  │                  │  │
│  │   Mailchimp) │  │               │  │                  │  │
│  └──────┬───────┘  └───────┬───────┘  └────────┬─────────┘  │
└─────────┼──────────────────┼───────────────────┼────────────┘
          │                  │                   │
┌─────────▼──────────────────▼───────────────────▼────────────┐
│                    REPOSITORY LAYER (SQLAlchemy)              │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      DATABASE (PostgreSQL)                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    BACKGROUND WORKERS                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Celery Worker│  │ Celery Beat  │  │   APScheduler    │  │
│  │ (Task Exec)  │  │ (Scheduler)  │  │   (Fallback)     │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
└─────────┼─────────────────┼───────────────────┼────────────┘
          │                 │                   │
┌─────────▼─────────────────▼───────────────────▼────────────┐
│                   REDIS (Queue & Cache)                      │
└─────────────────────────────────────────────────────────────┘
```

## Folder Structure

```
marketing-automation-platform/
├── app/                          # Application package
│   ├── main.py                   # FastAPI entry point
│   ├── api/                      # API layer
│   │   ├── deps.py               # Dependency injection
│   │   └── routes/               # Route handlers
│   │       ├── auth.py           # Authentication endpoints
│   │       ├── campaigns.py      # Campaign CRUD
│   │       ├── contacts.py       # Contact management
│   │       ├── dashboard.py      # Dashboard & reports
│   │       ├── newsletter.py     # Newsletter campaigns
│   │       ├── automation.py     # Job monitoring
│   │       └── health.py         # Health & metrics
│   ├── core/                     # Core infrastructure
│   │   ├── config.py             # Settings (Pydantic)
│   │   ├── database.py           # Async SQLAlchemy engine
│   │   ├── security.py           # JWT auth & password hashing
│   │   ├── cache.py              # Redis caching layer
│   │   ├── celery_app.py         # Celery configuration
│   │   └── logging.py            # Loguru configuration
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── campaign.py           # Campaigns table
│   │   ├── campaign_metric.py    # Daily campaign metrics
│   │   ├── contact.py            # Contacts/leads
│   │   ├── newsletter_campaign.py # Newsletter campaigns
│   │   ├── email_event.py        # Email tracking events
│   │   ├── lead_event.py         # Lead tracking
│   │   ├── api_log.py            # API request logs
│   │   ├── automation_job.py     # Background job tracking
│   │   ├── user.py               # User accounts
│   │   └── activity_log.py       # Activity audit log
│   ├── schemas/                  # Pydantic schemas
│   │   ├── auth.py               # Auth request/response
│   │   ├── campaign.py           # Campaign DTOs
│   │   ├── contact.py            # Contact DTOs
│   │   ├── dashboard.py          # Dashboard/report DTOs
│   │   ├── newsletter.py         # Newsletter DTOs
│   │   └── automation.py         # Job DTOs
│   ├── services/                 # Business logic
│   │   └── integrations/         # External API integrations
│   │       ├── google_ads.py     # Google Ads simulation
│   │       ├── meta_ads.py       # Meta Ads simulation
│   │       ├── hubspot.py        # HubSpot CRM simulation
│   │       ├── mailchimp.py      # Mailchimp email simulation
│   │       └── google_analytics.py # GA4 simulation
│   ├── repositories/             # Data access layer
│   │   ├── base.py               # Generic CRUD repository
│   │   ├── campaign.py           # Campaign-specific queries
│   │   ├── contact.py            # Contact-specific queries
│   │   ├── automation_job.py     # Job monitoring queries
│   │   └── user.py               # User auth queries
│   ├── workers/                  # Celery background tasks
│   │   └── tasks.py              # All task definitions
│   ├── scheduler/                # APScheduler
│   │   └── scheduler.py          # Scheduler configuration
│   ├── integrations/             # Webhook handlers
│   │   └── webhooks.py           # Facebook/Mailchimp webhooks
│   └── analytics/                # Analytics & reporting
│       ├── reporting.py          # Daily report generation
│       └── metrics.py            # Dashboard metrics
├── alembic/                      # Database migrations
│   ├── env.py                    # Alembic environment
│   └── script.py.mako            # Migration template
├── docker/                       # Docker configuration
│   ├── Dockerfile                # Python 3.12 container
│   └── .dockerignore
├── tests/                        # Test suite
│   ├── conftest.py               # Test fixtures
│   ├── test_api.py               # API integration tests
│   └── test_services.py          # Service unit tests
├── docker-compose.yml            # Multi-service orchestration
├── requirements.txt              # Python dependencies
├── pyproject.toml                # Project configuration
├── .env.example                  # Environment template
└── README.md                     # This file
```

## ER Diagram

```
┌─────────────────┐       ┌─────────────────────┐
│     users       │       │     campaigns        │
├─────────────────┤       ├─────────────────────┤
│ id (PK)         │       │ id (PK)              │
│ email           │       │ name                 │
│ username        │       │ platform             │
│ hashed_password │       │ status               │
│ full_name       │       │ budget               │
│ is_active       │       │ spent                │
│ created_at      │       │ start_date           │
│ updated_at      │       │ end_date             │
└─────────────────┘       │ created_at           │
                           │ updated_at           │
                           └────────┬────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
     ┌─────────────────────────┐   ┌────────────────────────────┐
     │    campaign_metrics     │   │     contacts                │
     ├─────────────────────────┤   ├────────────────────────────┤
     │ id (PK)                 │   │ id (PK)                    │
     │ campaign_id (FK)        │   │ email (unique)             │
     │ date                    │   │ first_name                 │
     │ impressions             │   │ last_name                  │
     │ clicks                  │   │ phone                      │
     │ conversions             │   │ company                    │
     │ spend                   │   │ source                     │
     │ revenue                 │   │ status                     │
     │ leads                   │   │ campaign_id (FK)           │
     │ ctr / cpc / cpa / roas  │   │ score                      │
     └─────────────────────────┘   │ created_at                 │
                                    │ updated_at                 │
                                    └────────┬───────────────────┘
                                             │
                           ┌─────────────────┼──────────────────┐
                           │                 │                  │
        ┌──────────────────────────┐  ┌──────────────┐  ┌───────────────┐
        │     lead_events          │  │  email_events │  │newsletter    │
        ├──────────────────────────┤  ├──────────────┤  │_campaigns    │
        │ id (PK)                  │  │ id (PK)      │  ├───────────────┤
        │ contact_id (FK)          │  │ contact_id   │  │ id (PK)       │
        │ campaign_id (FK)         │  │ campaign_id  │  │ name          │
        │ source                   │  │ event_type   │  │ subject       │
        │ status                   │  │ occurred_at  │  │ content       │
        │ score                    │  │ ip_address   │  │ status        │
        │ assigned_to              │  │ user_agent   │  │ sent_count    │
        │ created_at               │  └──────────────┘  │ open_rate     │
        └──────────────────────────┘                    │ click_rate    │
                                                        └───────────────┘
```

## Features

### Core Features
- **Campaign Management**: CRUD operations for multi-platform campaigns
- **Contact Management**: Store, search, and segment contacts
- **Dashboard**: Real-time aggregated marketing metrics
- **Daily Reports**: Auto-generated reports with CSV export
- **Newsletter Automation**: Welcome emails and campaign sending
- **Lead Management**: Facebook Lead Ads webhook integration
- **Background Jobs**: Celery workers with automatic retries
- **Scheduled Tasks**: APScheduler for periodic data fetching

### Technical Features
- **Async FastAPI**: Fully asynchronous request handling
- **SQLAlchemy 2.0**: Modern async ORM with repository pattern
- **JWT Authentication**: Secure token-based auth
- **Redis Caching**: In-memory cache for frequent queries
- **Rate Limiting**: SlowAPI-based request throttling
- **Prometheus Metrics**: Monitoring endpoint
- **Health Checks**: Database, Redis, and Celery status
- **Comprehensive Logging**: Loguru with rotation
- **Pagination & Filtering**: All list endpoints support filtering
- **CSV Export**: Downloadable daily reports
- **Swagger/OpenAPI**: Auto-generated API documentation

### Simulated Integrations
- **Google Ads API**: Campaigns, stats, performance metrics
- **Meta Ads API**: Campaigns, insights, lead forms
- **HubSpot CRM**: Contacts, deals, pipelines
- **Mailchimp**: Lists, members, campaigns, reports
- **Google Analytics 4**: Realtime, analytics, acquisition channels

All integrations return realistic JSON matching real API responses. Replace with real API keys for production use.

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | Login & get JWT token |
| POST | `/api/v1/auth/register` | Register new user |

### Campaigns
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/campaigns` | List campaigns (paginated, filterable) |
| GET | `/api/v1/campaigns/{id}` | Get campaign with metrics |
| POST | `/api/v1/campaigns` | Create campaign |
| PUT | `/api/v1/campaigns/{id}` | Update campaign |
| DELETE | `/api/v1/campaigns/{id}` | Delete campaign |

### Contacts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/contacts` | List contacts (search, filter) |
| GET | `/api/v1/contacts/{id}` | Get contact |
| POST | `/api/v1/contacts` | Create contact |
| PUT | `/api/v1/contacts/{id}` | Update contact |
| DELETE | `/api/v1/contacts/{id}` | Delete contact |
| POST | `/api/v1/contacts/webhook/facebook-lead` | Facebook Lead Ads webhook |

### Dashboard & Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/dashboard` | Aggregated dashboard data |
| GET | `/api/v1/dashboard/metrics` | Raw metrics with date range |
| GET | `/api/v1/dashboard/report` | Daily report (JSON) |
| GET | `/api/v1/dashboard/report/csv` | Daily report (CSV download) |

### Newsletter
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/newsletter/send` | Send newsletter campaign |
| POST | `/api/v1/newsletter/campaigns` | Create newsletter campaign |
| GET | `/api/v1/newsletter/campaigns` | List newsletter campaigns |
| GET | `/api/v1/newsletter/campaigns/{id}` | Get newsletter campaign |

### Automation
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/automation/jobs` | List background jobs |
| GET | `/api/v1/automation/jobs/stats` | Job statistics |

### Health & Monitoring
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | System health check |
| GET | `/api/v1/metrics` | Prometheus metrics |

## API Examples

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### List Campaigns
```bash
curl http://localhost:8000/api/v1/campaigns?skip=0&limit=10
```

### Get Dashboard
```bash
curl http://localhost:8000/api/v1/dashboard
```

### Get Daily Report (CSV)
```bash
curl http://localhost:8000/api/v1/dashboard/report/csv -o report.csv
```

### Create Contact
```bash
curl -X POST http://localhost:8000/api/v1/contacts \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "first_name": "John", "last_name": "Doe"}'
```

### Facebook Lead Webhook
```bash
curl -X POST http://localhost:8000/api/v1/contacts/webhook/facebook-lead \
  -H "Content-Type: application/json" \
  -d '{"email": "lead@example.com", "first_name": "Jane", "last_name": "Doe", "phone": "+15551234567"}'
```

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

## Deployment Guide

### Prerequisites
- Docker & Docker Compose (recommended)
- Python 3.12+ (for local development)
- PostgreSQL 16+ (for local development)

### Quick Start with Docker
```bash
# Clone the repository
git clone <repo-url>
cd marketing-automation-platform

# Start all services
docker compose up --build

# Access the API
open http://localhost:8000/docs

# Default credentials
# Username: admin
# Password: admin123
```

### Local Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up PostgreSQL and Redis
# Update .env with your local connection strings

# Run migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --port 8000

# Start Celery worker (in separate terminal)
celery -A app.core.celery_app.celery_app worker --loglevel=info

# Start Celery beat (in separate terminal)
celery -A app.core.celery_app.celery_app beat --loglevel=info
```

## Docker Services

| Service | Container Name | Port | Purpose |
|---------|---------------|------|---------|
| FastAPI | `marketing_api` | 8000 | REST API server |
| PostgreSQL | `marketing_postgres` | 5432 | Primary database |
| Redis | `marketing_redis` | 6379 | Queue & cache |
| Celery Worker | `marketing_celery_worker` | - | Background task execution |
| Celery Beat | `marketing_celery_beat` | - | Scheduled task trigger |
| APScheduler | `marketing_scheduler` | - | Fallback scheduler |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `marketing_user` | Database user |
| `POSTGRES_PASSWORD` | `marketing_pass` | Database password |
| `POSTGRES_HOST` | `postgres` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |
| `POSTGRES_DB` | `marketing_platform` | Database name |
| `REDIS_HOST` | `redis` | Redis host |
| `REDIS_PORT` | `6379` | Redis port |
| `JWT_SECRET_KEY` | *(change in production)* | JWT signing key |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token expiry |
| `LOG_LEVEL` | `DEBUG` | Logging level |
| `RATE_LIMIT_PER_MINUTE` | `60` | API rate limit |
| `CACHE_TTL_SECONDS` | `300` | Cache TTL |

## Automation Schedule

| Task | Interval | Description |
|------|----------|-------------|
| `fetch_all_campaign_metrics` | Every 60s | Fetch metrics from Google & Meta |
| `fetch_all_contacts` | Every 60s | Sync contacts from HubSpot |
| `generate_daily_report` | Every 60min | Generate daily performance report |
| `cleanup_old_logs` | Every 24h | Remove logs older than 90 days |
| `test_task` | Every 30s | Health verification task |

## Newsletter Automation Flow

```
User Registration
       │
       ▼
Save to PostgreSQL ──────► Create contact record
       │
       ▼
Add to Mailchimp ────────► Subscribe to mailing list
       │
       ▼
Send Welcome Email ──────► Queue email via Celery
       │
       ▼
Log Event ───────────────► Record email_event in database
       │
       ▼
Notify Sales Team ───────► Trigger sales notification
```

## Lead Automation Flow (Facebook Lead Ads)

```
Facebook Lead Form Submission
       │
       ▼
Webhook Received ──────────► POST /api/v1/contacts/webhook/facebook-lead
       │
       ▼
Validate Payload ──────────► Pydantic validation
       │
       ▼
Check Existing Contact ────► Lookup by email
       │
       ├── Found: Update contact
       └── New: Create contact record
       │
       ▼
Create Lead Event ─────────► Store in lead_events table
       │
       ▼
Assign Campaign ───────────► Link to marketing campaign
       │
       ▼
Notify Sales Team ─────────► Celery task (notify_sales_team.delay)
```

## Future Improvements

- [ ] **Real API Integrations**: Replace simulated services with actual API calls
- [ ] **Web UI**: React/Next.js frontend dashboard
- [ ] **Multi-tenancy**: Organizations with separate data isolation
- [ ] **Advanced Segmentation**: RFM analysis, predictive scoring
- [ ] **A/B Testing**: Campaign split testing with statistical analysis
- [ ] **Email Templates**: Drag-and-drop email builder
- [ ] **SMS Marketing**: Twilio integration for SMS campaigns
- [ ] **Data Warehouse**: Export to BigQuery/Snowflake
- [ ] **ML Predictions**: Churn prediction, LTV estimation, lookalike audiences
- [ ] **Real-time Sync**: WebSocket for live dashboard updates
- [ ] **SSO**: OAuth2/OIDC for enterprise authentication
- [ ] **Audit Trail**: Immutable event log for compliance
- [ ] **API Versioning**: Proper versioned API lifecycle
- [ ] **Load Testing**: k6/Gatling performance benchmarks
- [ ] **Kubernetes**: Helm charts for production orchestration
- [ ] **CI/CD**: GitHub Actions for testing and deployment
- [ ] **Monitoring**: Grafana dashboards, AlertManager
- [ ] **GDPR Compliance**: Data anonymization and export tools
