# Inventory Management System

A Django web application for electronics repair businesses to track inventory items, categories, and sales.

## Features

- **User Authentication**: Secure login/logout with custom user model
- **Category Management**: Hierarchical categories for organizing inventory
- **Inventory Tracking**: Track electronics with flexible JSON characteristics
- **Sales Management**: Record sales and calculate profit margins
- **User Data Isolation**: Each user only sees their own data
- **Docker Deployment**: Containerized deployment with MariaDB

## Tech Stack

- **Backend**: Django 4.x
- **Database**: SQLite (development), MariaDB (production)
- **Frontend**: Django Templates with Bootstrap 5
- **Deployment**: Docker with docker-compose

## Quick Start

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd inventory-management
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Docker Setup

1. **Build and run with docker-compose**
   ```bash
   docker-compose up --build
   ```

2. **Create superuser in Docker**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## Project Structure

```
inventory_management/
├── inventory_management/     # Django project settings
├── authentication/           # User authentication app
├── categories/              # Category management app
├── inventory/               # Inventory management app
├── sales/                   # Sales tracking app
├── templates/               # Django templates
├── static/                  # Static files (CSS, JS, images)
├── media/                   # User uploaded files
└── tests/                   # Test files
```

## Database Schema

- **User**: Custom user model extending Django's AbstractUser
- **Category**: Hierarchical categories with parent-child relationships
- **InventoryItem**: Electronics items with JSON characteristics field
- **Sale**: Sales transactions with profit calculation

## JSON Characteristics Field

The inventory items include a JSON field for storing flexible product specifications:

```json
{
  "brand": "Samsung",
  "model": "Galaxy S21",
  "storage_gb": 128,
  "ram_gb": 8,
  "color": "Phantom Black",
  "condition": "Good"
}
```

## Deployment

### Production with Docker

1. Set up production environment variables
2. Build Docker images: `docker-compose -f docker-compose.prod.yml build`
3. Run migrations: `docker-compose -f docker-compose.prod.yml run web python manage.py migrate`
4. Start services: `docker-compose -f docker-compose.prod.yml up -d`

### Environment Variables

See `.env.example` for all required environment variables.

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
- Follow PEP 8 guidelines
- Use Black for code formatting
- Use isort for import sorting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details