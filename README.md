# Aptitude Build

A Django + MySQL web app to let users practice aptitude MCQs.

This repository will contain a Django project (aptitudebuild) with:

- Django (latest)
- MySQL (database)
- Docker & Docker Compose for easy local development
- A management command to import questions from an Excel file (questions.xlsx)
- Authentication (signup/login), admin interface for questions and results
- A Tailwind-based responsive frontend (Django templates + Tailwind) for a clean UI

## Where this file is

This README.md is at the repository root.

## Quick decisions made for this scaffold

- MySQL credentials (development):
  - DB name: `aptitudebuild`
  - DB user: `root`
  - DB password: `mysql1234`
  - Host (Docker Compose): `db`
  - Port: `3306`
- Django: latest stable release (use `pip install "django>=4.2"` or the provided `requirements.txt`)
- Excel dataset: `questions.xlsx` (you provided a URL). The importer supports either a local path or a direct URL.
- Docker: included by default (docker-compose) but you can run without it.

## What I will add next (scaffold plan)

If you want me to continue, I will scaffold and commit the following files/folders:

- `Dockerfile`, `docker-compose.yml` to run Django + MySQL + optional Adminer/pgAdmin
- `requirements.txt` with Python deps (Django, mysqlclient, pandas, openpyxl, django-tailwind or Tailwind via npm)
- Django project: `aptitudebuild/` (settings, urls, wsgi/asgi)
- Django app: `quiz/` (models, views, templates, static, management command to import Excel)
- Management command: `python manage.py import_questions --file <path-or-url>` to import questions
- Admin registration for models (Question, UserProfile/Result)
- Minimal Tailwind integration and starter templates (base.html, index/home, quiz flow)
- README updated with usage and import instructions (this file)

Tell me: should I scaffold now? Reply "Yes scaffold" and I will create the files and commit them.

## Local development (recommended)

Follow these steps to run the project locally on your machine (no Docker required).

### 1) Install system requirements

- Python 3.11+ (or 3.10+)
- MySQL server (8.0+)
- `pip` (bundled with Python)

On macOS you can use Homebrew; on Ubuntu use apt-get.

### 2) Create MySQL database and user

Run these SQL commands (adjust if you prefer a different user):

```sql
CREATE DATABASE aptitudebuild CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'root'@'localhost' IDENTIFIED BY 'mysql1234';
GRANT ALL PRIVILEGES ON aptitudebuild.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

### 3) Create Python virtual environment and install dependencies

From the repo root:

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
# .\.venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r web/requirements.txt
```

### 4) Configure environment variables

Create a `.env` file inside the `web/` folder with the following content (do not commit secrets):

```
DB_NAME=aptitudebuild
DB_USER=root
DB_PASSWORD=mysql1234
DB_HOST=127.0.0.1
DB_PORT=3306
DJANGO_SECRET_KEY=replace-this-with-a-secure-key
DEBUG=1
```

### 5) Run migrations and create superuser

```bash
cd web
python manage.py migrate
python manage.py createsuperuser
```

### 6) Import questions.xlsx (local or remote URL)

- Download the `questions.xlsx` you provided into the repo root or any local path.

Examples:

```bash
# Import from a local file (if placed in repo root):
python manage.py import_questions --file ../questions.xlsx

# Import directly from the remote URL:
python manage.py import_questions --file "https://cdn.builder.io/o/assets%2F3ee889915f1e45489b723eb1c8e31275%2Fe4c19c0f43fa4b40b97a935d6f1b37bc?alt=media&token=8c63ee91-2206-485e-adc3-72bc7dd7cfbd&apiKey=3ee889915f1e45489b723eb1c8e31275"
```

### 7) Run the development server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ for the site and http://127.0.0.1:8000/admin/ for the admin.

### Helper script

A helper script `web/setup_local.sh` is included to automate steps 3-6 (Linux/macOS). Run it with `bash web/setup_local.sh`.

### Notes

- The Django project is under `web/`.
- If your MySQL server binds to `localhost` sockets (instead of TCP), ensure Django connects via 127.0.0.1 and the user is allowed for that host.
- For a production deployment you should set `DEBUG=0` and provide a strong `DJANGO_SECRET_KEY`.

If you want, I can remove Docker files entirely; say "Remove Docker" and I'll delete docker-compose.yml and web/Dockerfile.

## Management command: import_questions

A management command `import_questions` will be added that supports:

- Excel files (.xlsx) with columns: Question, Option_A, Option_B, Option_C, Option_D, Answer
- Local file path or remote URL
- Will create Question model instances and skip duplicates (based on exact question text)

Usage example:

```
python manage.py import_questions --file path_or_url
```

## Data model (summary)

- Question
  - question_text (TextField)
  - option_a, option_b, option_c, option_d (CharField / TextField)
  - answer (CharField) - expects one of "A", "B", "C", "D" or the exact text matching
  - category (CharField) - e.g., "logical reasoning"

- Result / Attempt
  - user (ForeignKey to User)
  - question (ForeignKey to Question)
  - selected_option
  - is_correct (Boolean)
  - timestamp

- UserProfile (optional) to show overall score / progress

Admin models will be registered so admin can view users, questions and results.

## Frontend and UX

- Base template `templates/base.html` with responsive header and footer
- Tailwind CSS for modern responsive UI. We will use a minimal Tailwind setup (npm) or `django-tailwind`.
- Pages to include:
  - Home / Dashboard: shows categories (Logical Reasoning) and user progress
  - Quiz view: shows one question at a time with four options; immediate feedback on submit and progression
  - Results page: final score and per-question review

## Security notes

- Do NOT commit `.env` or secret keys.
- For production, replace `DEBUG=1` with `DEBUG=0` and set a secure `DJANGO_SECRET_KEY`.
- Use managed DB credentials and restrict network permissions in production.

## Next steps

Reply with: `Yes scaffold` to let me create the Django scaffold, Docker files, management command, models, admin and starter templates and commit them into the repository. I will then:

1. Add project files and commit
2. Start with the import command and sample templates
3. Provide short demo instructions and verify import of the provided XLSX

If you prefer I can only add the README and Docker files first — tell me which.
