# SweetHand Backend

Backend for the SweetHand storefront, built with Django and Django REST Framework.

## Features

- email/password registration and login
- token authentication
- profile endpoint
- product catalog and categories
- favorites
- order creation and order history
- feedback/contact form endpoint
- admin panel
- demo catalog seed command

## Quick start

Use any Python environment with Django and DRF installed, then:

```powershell
python manage.py migrate
python manage.py bootstrap_demo
python manage.py runserver
```

For local development, the project uses SQLite by default. Set `DATABASE_URL` to switch
to PostgreSQL without changing the code.

Default demo admin credentials after `bootstrap_demo`:

- email: `admin@gmail.com`
- password: `admin123`

## Render deployment

Recommended Render setup:

- `Build Command`: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py bootstrap_project_data`
- `Start Command`: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

Environment variables:

- `SECRET_KEY=<your-secret>`
- `DEBUG=false`
- `CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app`
- `CSRF_TRUSTED_ORIGINS=https://your-frontend.vercel.app`
- `DATABASE_URL=<Neon PostgreSQL URL or Render Internal Database URL>`

`bootstrap_project_data` loads `fixtures/project_data.json` only when the database is empty, so free Render deployments do not need Shell access to import the initial catalog and users.

## API

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `GET/PATCH /api/auth/me/`
- `GET /api/catalog/categories/`
- `GET /api/catalog/products/`
- `GET /api/catalog/products/<id>/`
- `GET /api/catalog/favorites/`
- `POST /api/catalog/favorites/`
- `DELETE /api/catalog/favorites/<product_id>/`
- `GET /api/orders/`
- `POST /api/orders/`
- `GET /api/orders/<id>/`
- `POST /api/feedback/`
