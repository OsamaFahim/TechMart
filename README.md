# TechMart

A full-stack inventory, sales, and analytics dashboard built with Django (backend) and React (frontend).

**Note: All documents for this branch are located in the Documents folder. Since they are tracked using Git LFS, please use “View Raw” or “Download” to access them properly.**

---

## Quick Start Guide

Get TechMart running on your machine in minutes. Choose **Docker** for the easiest, most reliable setup, or follow the **manual setup** for local development.

---

## 1. Dockerized Setup (Recommended)

The Dockerized setup is the fastest and most reliable way to get started. All dependencies (MySQL, Redis, Django, React) are managed automatically.

### a. Switch to the Docker Branch

First, clone the repository and switch to the Docker deployment branch:

```sh
git clone "https://github.com/OsamaFahim/TechMart.git"
cd TechMart
git checkout Post-submission/deploy
```

### b. Build Docker Images

Build all services (backend, frontend, database, cache):

```sh
docker-compose build
```
For a completely fresh build (ignore cache):
```sh
docker-compose build --no-cache
```

### c. Start All Services

Run all containers in detached mode:

```sh
docker-compose up -d
```

> **Note:**  
> On first run, MySQL may take up to a minute to initialize and connect. Please wait for the backend to finish loading data.

### d. Access the Application

- **Backend (Django):** [http://localhost:8000](http://localhost:8000)
- **Frontend (React):** [http://localhost:5173](http://localhost:5173)

### e. Managing Docker Containers

- **Stop all containers:**
  ```sh
  docker-compose stop
  ```
- **Remove containers and networks:**
  ```sh
  docker-compose down
  ```
- **Remove unused images:**
  ```sh
  docker image prune -a
  ```
- You can also use **Docker Desktop** to manage containers and images visually.

---

## 2. Manual Local Development Setup

If you prefer to run everything manually (for development or debugging), use the `dev` branch:

### a. Clone the Dev Branch

```sh
git clone -b dev "https://github.com/OsamaFahim/TechMart.git"
cd TechMart
```

### b. Backend Setup

1. **Create and activate a virtual environment:**
    ```sh
    cd backend
    python -m venv venv
    ```
    - **On Windows:**  
      `venv\Scripts\activate`
    - **On macOS/Linux:**  
      `source venv/bin/activate`

2. **Install Python dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

    > If you face issues, try using the `requirements.txt` from the `Post-submission/deploy` branch.

3. **Start Redis (required for Django caching):**
    - Download Redis for Windows:  
      [https://github.com/microsoftarchive/redis/releases](https://github.com/microsoftarchive/redis/releases)
    - Unzip and run:
      ```sh
      cd C:\Redis
      .\redis-server.exe
      ```
    - Leave this window open.

4. **Database Setup:**
    - Ensure MySQL is running and a database is created.
    - Update credentials in `backend/Techmart/Techmart/settings.py` or use a `.env` file (`.env.example` provided).
    - Run migrations:
      ```sh
      cd backend/Techmart
      python manage.py migrate
      ```
    - (Optional) Create a superuser:
      ```sh
      python manage.py createsuperuser
      ```

5. **Start the Django backend:**
    ```sh
    python manage.py runserver
    ```

### c. Frontend Setup

Open a new terminal:

```sh
cd frontend
npm install
npm run dev
```

- The React app will be available at [http://localhost:5173](http://localhost:5173).

---

## 3. Summary of Commands

```sh
# Dockerized setup (recommended)
git clone "https://github.com/OsamaFahim/TechMart.git"
cd TechMart
git checkout Post-submission/deploy
docker-compose build
# or for a fresh build:
docker-compose build --no-cache
docker-compose up -d

# Manual setup (dev branch)
git clone -b dev "https://github.com/OsamaFahim/TechMart.git"
cd TechMart
cd backend
python -m venv venv
venv\Scripts\activate      # or source venv/bin/activate
pip install -r requirements.txt
# Start Redis (see above)
cd backend/Techmart
python manage.py migrate
python manage.py createsuperuser  # optional
python manage.py runserver
# Frontend (in new terminal)
cd frontend
npm install
npm run dev
```

---

## 4. Important: Disk Space Requirements

**Ensure you have several GB of free space on the drive where Docker stores its data (usually C: on Windows).**

- Docker Desktop and its containers/images/volumes are stored on the system drive by default.
- If your C: drive is nearly full, Docker containers may become unresponsive, and commands may stop working.
- If you encounter issues with containers hanging or not responding, check your disk space and free up space as needed.
- You can move Docker's storage location to another drive (e.g., D:) via Docker Desktop settings:  
  **Settings → Resources → Advanced → Disk image location**

---

## 5. Notes & Troubleshooting

- **Docker** is the easiest way to avoid dependency issues.
- **Redis** must be running for Django caching.
- **Database credentials** should be set in `.env` or `settings.py`.
- **CORS**: Frontend and backend run on different ports; ensure CORS is enabled in Django for local development.
- **First-time Docker startup**: Wait up to a minute for MySQL and backend to initialize.
- **Stopping Docker**: Use `docker-compose stop` or Docker Desktop.
- **Removing images**: Use `docker image prune -a` or Docker Desktop.
- **If `pip install -r requirements.txt` fails**: Try the `requirements.txt` from the `Post-submission/deploy` branch.

---

Enjoy using **TechMart**! If you have any issues, check the terminal output for errors and ensure all services (MySQL, Redis, Django, React) are running.
