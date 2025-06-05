# TechMart

A full-stack inventory, sales, and analytics dashboard built with Django (backend) and React (frontend).

---

## Quick Setup Guide

Follow these steps to get TechMart running on your local machine.

---

### 1. Clone the Repository

```sh
git clone "https://github.com/OsamaFahim/TechMart.git"
cd TechMart
```

---

### 2. Backend Setup

#### a. Create and Activate a Virtual Environment

Navigate to the backend directory and create a virtual environment to keep dependencies isolated:

```sh
cd backend
python -m venv venv
```

Activate the virtual environment:

- **On Windows:**
  ```sh
  venv\Scripts\activate
  ```
- **On macOS/Linux:**
  ```sh
  source venv/bin/activate
  ```

#### b. Install Python Dependencies

```sh
pip install -r requirements.txt
```

---

### 3. Redis Server Setup (Required for Django Caching)

Django’s cache framework needs a real Redis server running in the background.

- Download Redis for Windows from:  
  [https://github.com/microsoftarchive/redis/releases](https://github.com/microsoftarchive/redis/releases)
- Download the latest version (e.g., `Redis-x64-3.0.504.zip`).
- Unzip it to a folder, e.g., `C:\Redis`.

Start the Redis server:

```sh
cd C:\Redis
# In PowerShell:
.\redis-server.exe
```

You should see:
```
Server started, Redis version 3.0.504
The server is now ready to accept connections on port 6379
```

**Leave this window open while using the app.**

---

### 4. Database Setup

- Make sure you have MySQL running and a database created.
- Update your database credentials in `backend/Techmart/Techmart/settings.py` or set the appropriate environment variables.
- It is Recommended to use .env (.env.example) is given as well, instead of hardcoding the variables in settings.py and never share your credentials with anyone keep them safe
- Run migrations:

```sh
cd backend/Techmart
python manage.py migrate
```

- (Optional) Create a superuser for Django admin:

```sh
python manage.py createsuperuser
```

---

### 5. Start the Django Backend Server

In the `backend/Techmart` directory:

```sh
python manage.py runserver
```

---

### 6. Frontend Setup

Open a new terminal window/tab:

```sh
cd frontend
npm install
npm run dev
```

This will start the React development server (usually on [http://localhost:5173](http://localhost:5173)).

---

## Summary of Commands

```sh
# 1. Clone repo
git clone "https://github.com/OsamaFahim/TechMart.git"
cd TechMart

# 2. Backend setup
cd backend
python -m venv venv
venv\Scripts\activate      # (or source venv/bin/activate on macOS/Linux)
pip install -r requirements.txt

# 3. Start Redis (in a new terminal)
cd C:\Redis
.\redis-server.exe

# 4. Database migrations
cd backend/Techmart
python manage.py migrate
python manage.py createsuperuser  # (optional)

# 5. Start Django server
python manage.py runserver

# 6. Frontend setup (in a new terminal)
cd frontend
npm install
npm run dev
```

---

## Notes

- **Redis must be running** for Django caching to work.
- **Virtual environment** keeps your Python dependencies isolated.
- **Database credentials** must be set correctly in your settings.
- **Frontend and backend** run on different ports; make sure CORS is enabled in Django for local development.
- For any issues, check the terminal output for errors and ensure all services (MySQL, Redis, Django, React) are running.

---

Enjoy using TechMart! 
