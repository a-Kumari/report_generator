This project is a secure report generation system built with FastAPI that provides JWT authentication, role-based access control, and background report generation with email notifications.

# Features
🔒 JWT Authentication with OAuth2 password flow

👥 User roles (Admin and Regular User)

💾 PostgreSQL database with SQLAlchemy ORM

📊 Background report generation (CSV files)

✉️ Email notifications with download links

📄 Paginated report listings

🌦️ OpenWeatherMap API integration

📁 Secure file download system

### Prerequisites
- Python 3.8+
- OpenWeatherMap API key
- SMTP email credentials 

1. Clone the repository:
   ```bash
   git clone https://github.com/a-Kumari/report_generator.git
   cd report_generator

2. Create a virtual environment:
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate    # Windows

3. Install dependencies:
    pip install -r requirements.txt

4. Create .env file:
    OPENWEATHER_API_KEY=your_openweather_key
    EMAIL_FROM=your@gmail.com
    EMAIL_PASSWORD=your_app_password
    SMTP_SERVER=smtp.gmail.com
    SMTP_PORT=465 # for TLS 
    SECRET_KEY=your_jwt_secret
    ALGORITHM = JWT algorithm HS256
    POSTGRES_USER = your_postgres_username
    POSTGRES_PASSWORD = your_postgres_password
    POSTGRES_DB = your_database_name
    POSTGRES_HOST = hostname 
    POSTGRES_PORT = port     
    ADMIN_SECRET_KEY = your_key  #it can be anything

* Run database migrations (if using Alembic or similar):
    ```bash
    #example with alembic
    alembic revision --autogenerate -m "inital migration"
    alembic upgrade head

### Running the Server
uvicorn main:app --reload

### Documentation
Interactive docs: http://localhost:8000/docs
Redoc: http://localhost:8000/redoc

## API Endpoints

| Endpoint             | Method | Description                               | Access                |
|----------------------|--------|-------------------------------------------|-----------------------|
| `/auth/login`         | POST   | Get JWT token (login)                     | Public                |
| `/users/me`          | GET    | Get current user details                  | Authenticated         |
| `/users/`             | POST   | Create new user                           | Admin only            |
| `/reports/?city={city}`| POST   | Generate weather report for a given city | Authenticated         |
| `/reports/`            | GET    | List user's reports                       | Authenticated         |

