[English](README_EN.md) | [中文](README.md)

# The Light on the Way Back - 归途的光

A poetic emotional expression platform featuring two core experiences: Time Capsule Letter and Façade Gallery.

## Project Overview

"The Light on the Way Back" is an emotional expression platform built with FastAPI and modern web technologies. It provides a safe, private, and poetic space for users to express their inner voice.

### Core Features

#### 🕰️ Time Capsule Letter
- Description: Users can create a "Time Capsule Letter" — a monologue, a wish, a secret, or even an unspeakable lie
- Encrypted Sealing: Letters are encrypted and sealed until a specified open date; nobody can read them before the time
- Send to the Void: Optionally "send to the void," meaning the letter is immediately destroyed after creation as pure emotional catharsis
- Scheduled Opening: When the specified time arrives, the letter becomes openable automatically

#### 🎭 Façade Gallery
- Description: An anonymous public space where users can create temporary, fully anonymous "façade" identities
- 24-Hour Lifespan: Façade identities exist only for 24 hours, echoing the theme "When daylight breaks, we put on our masks again"
- Anonymous Interaction: Users can post text content, and others can interact with anonymous "applause"
- No-Tracking Design: No follow feature, no long-term tracking — only brief, genuine expression

## Tech Stack

- Backend Framework: FastAPI
- Package Manager: uv
- Template Engine: Jinja2
- Database: SQLite (SQLAlchemy ORM)
- Cryptography: cryptography
- Scheduler: APScheduler
- Frontend: HTML + CSS + JavaScript (vanilla)

## Project Structure

```
The Light on the Way Back/
├── the_light_on_the_way_back/          # Main application package
│   ├── __init__.py
│   ├── app.py                          # FastAPI application entry
│   ├── config.py                       # Configuration
│   ├── database.py                     # Database connection and session
│   ├── models.py                       # ORM models
│   ├── encryption.py                   # Encryption service
│   ├── scheduler.py                    # Task scheduler
│   ├── routers/                        # Routers
│   │   ├── __init__.py
│   │   ├── main.py                     # Home routes
│   │   ├── time_capsule.py             # Time Capsule routes
│   │   └── facade_gallery.py           # Façade Gallery routes
│   └── services/                       # Business logic services
│       ├── __init__.py
│       ├── time_capsule.py             # Time Capsule services
│       └── facade_gallery.py           # Façade Gallery services
├── templates/                          # Jinja2 templates
│   ├── base.html                       # Base template
│   ├── index.html                      # Home
│   ├── time_capsule.html               # Time Capsule page
│   └── facade_gallery.html             # Façade Gallery page
├── data/                               # Data directory
│   └── app.db                          # SQLite database file
├── main.py                             # Application entry
├── start_server.py                     # Server start script
├── test_app.py                         # Test script
├── pyproject.toml                      # Project configuration
└── README.md                           # Project README (Chinese)
```

## Installation and Run

### Requirements
- Python 3.12+
- uv package manager

### Steps

1. Clone the repository
```bash
git clone https://github.com/zym9863/the-light-on-the-way-back.git
cd "The Light on the Way Back"
```

2. Install dependencies
```bash
uv sync
```

3. Run tests
```bash
uv run python test_app.py
```

4. Start the server
```bash
uv run python start_server.py
```

5. Access the app
Open your browser at `http://localhost:8000`

## Features

### Security
- Time Capsule Letters use time-based encryption to ensure decryption is impossible before the specified time
- IP addresses are hashed to protect privacy while preventing abuse
- Anonymous identity system with no way to trace real identities

### Poetic Design
- Interface design emphasizes poetic aesthetics with gradients and soft visuals
- Feature names are poetic: "Time Capsule Letter", "Façade Gallery", "Send to the Void"
- Interaction design focuses on emotional expression, using "applause" rather than "likes"

### Scheduled Tasks
- Automatically cleans up expired façade identities
- Automatically destroys letters "sent to the void"
- Periodically checks for letters that are ready to open

## API Endpoints

### Main Routes
- GET `/` - Home
- GET `/time-capsule` - Time Capsule page
- POST `/time-capsule/create` - Create a Time Capsule Letter
- POST `/time-capsule/open/{letter_id}` - Open a Time Capsule Letter
- GET `/facade-gallery` - Façade Gallery page
- POST `/facade-gallery/create-identity` - Create a façade identity
- POST `/facade-gallery/create-content` - Create gallery content
- POST `/facade-gallery/applaud/{content_id}` - Applaud content
- GET `/health` - Health check

## Configuration

Primary configurations are in `the_light_on_the_way_back/config.py`:

- `DATABASE_URL`: Database connection URL
- `SECRET_KEY`: Application secret
- `ENCRYPTION_KEY`: Encryption key
- `MAX_LETTER_LENGTH`: Max letter length
- `FACADE_LIFETIME_HOURS`: Façade identity lifespan (hours)

## Development

### Adding New Features
1. Define data models in `models.py`
2. Implement business logic in `services/`
3. Add API routes in `routers/`
4. Create frontend templates in `templates/`

### Testing
Run `test_app.py` for basic tests, including:
- Encryption/Decryption tests
- Time Capsule creation and opening
- Façade Gallery flow

## License

This project is licensed under the MIT License.

## Acknowledgements

Thanks to everyone who contributed ideas and code to this project. May everyone find their share of serenity and truth in "The Light on the Way Back".

---

*"A sheet of paper, a blot of ink, hides my fearless self."*  
*"When daylight breaks, we put on our masks again."*