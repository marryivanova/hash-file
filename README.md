# 📁 File Storage HTTP API Documentation

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-blue)
![Docker](https://img.shields.io/badge/Docker-supported-blue)
![Swagger](https://img.shields.io/badge/docs-Swagger-green)
![Auth](https://img.shields.io/badge/auth-Basic-yellowgreen)
![Poetry](https://img.shields.io/badge/deps-Poetry-orange)

## 🌟 Overview
A robust file storage service providing HTTP API for secure file operations with authentication.

## 🔗 API Documentation
Interactive Swagger UI available at:  
`http://localhost:8000/swagger/`

## 🔐 Authentication
| Aspect              | Details                                  |
|---------------------|------------------------------------------|
| Type                | Basic Authentication                    |
| Required For        | All endpoints except download           |
| User Management     | Pre-configured users (no registration)  |
| Credentials Format  | `username:password`                     |
| Security            | Recommended for HTTPS only              |

## ⚙️ Requirements
- **Python**: 3.9+
- **Database**: PostgreSQL 13+
- **Containerization**: Docker
- **Dependency Management**: Poetry

## 🚀 API Endpoints
| Method | Endpoint       | Description                | Auth Required |
|--------|----------------|----------------------------|---------------|
| POST   | `/upload/`     | Upload new files           | Yes           |
| GET    | `/download/`   | Download existing files    | No            |
| DELETE | `/files/{id}/` | Delete specific file       | Yes           |

## 🛠️ Installation

```bash
# Clone the repository
git https://github.com/marryivanova/hash-file.git

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
cd hash-file
pip install poetry
poetry install

# Start database
cd docker
docker-compose up --build
```
or 

```bash
# Clone the repository
git https://github.com/marryivanova/hash-file.git

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
cd hash-file
pip install poetry
poetry install

# Start database
cd docker
docker-compose -f docker-compose.yml up -d db

# Run migrations
alembic upgrade head  # Make sure to check database URL in alembic.ini

# Start the server
python main.py
```

**Example of work**:

<figure>
  <img src="src/docs_content/swagger.png">
  <figcaption>swagger api docs</figcaption>
</figure>

<figure>
  <img src="src/docs_content/login.png">
  <figcaption>login</figcaption>
</figure>

<figure>
  <img src="src/docs_content/validate_token.png">
  <figcaption>validate token</figcaption>
</figure>

<figure>
  <img src="src/docs_content/upload_file.png">
  <figcaption>upload file</figcaption>
</figure>

<figure>
  <img src="src/docs_content/chek_db_file.png">
  <figcaption>chek db file.png</figcaption>
</figure>

<figure>
  <img src="src/docs_content/show_file_dir.png">
  <figcaption>show file after create</figcaption>
</figure>

<figure>
  <img src="src/docs_content/delete.png">
  <figcaption>delete file</figcaption>
</figure>


<figure>
  <img src="src/docs_content/after_delete.png">
  <figcaption>after delete</figcaption>
</figure>

<figure>
  <img src="src/docs_content/download.png">
  <figcaption>download file</figcaption>
</figure>