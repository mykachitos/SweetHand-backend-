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

Default demo admin credentials after `bootstrap_demo`:

- email: `admin@gmail.com`
- password: `admin123`

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
