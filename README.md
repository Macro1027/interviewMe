# AI Interview Simulation Platform

A comprehensive platform for conducting AI-powered interview simulations to help candidates improve their interviewing skills.

## Project Structure

```
├── cloud_infra/        # Cloud infrastructure configuration 
├── config/             # Configuration files
├── data/               # Data files for training and testing
├── docs/               # Documentation files
├── frontend/           # React frontend application
├── logs/               # Application logs
├── models/             # ML model files
├── notebooks/          # Jupyter notebooks for experimentation
├── reports/            # Generated reports
└── src/                # Source code
    ├── ai/             # AI components
    ├── app/            # Application code
    ├── services/       # Service integrations
    ├── tests/          # Test suite
    └── utils/          # Utility functions
```

## Environment Configuration

### Environment Files

The application uses the following environment files:

- `.env.example`: Template with all available configuration options
- `.env`: Local development environment (not committed to Git)
- `.env.test`: Testing environment
- `.env.production`: Production environment

### Setting Up Environment

1. Copy the template file to create your local environment:

```bash
cp .env.example .env
```

2. Edit the `.env` file to add your configurations, especially:
   - Database credentials
   - API keys for external services
   - Secret keys for JWT and application

### Environment Variables

Key environment variables include:

- `APP_ENV`: Current environment (development, test, production)
- `DEBUG`: Enable debug mode
- `SECRET_KEY`: Secret key for application security
- `JWT_SECRET`: Secret for JWT token generation
- `POSTGRES_URI`: PostgreSQL connection string
- `MONGODB_URI`: MongoDB connection string
- `OPENAI_API_KEY`: OpenAI API key for AI services

See the `.env.example` file for a complete list of configuration options.

## Dependencies

### Backend (Python)

The backend uses Python with the following key dependencies:

- FastAPI: Web framework
- SQLAlchemy: ORM for PostgreSQL
- PyMongo/Motor: MongoDB driver
- TensorFlow/PyTorch: Machine learning
- Spacy/NLTK: Natural language processing

Install dependencies with:

```bash
pip install -r requirements.txt
```

### Frontend (React)

The frontend uses React with TypeScript and the following key dependencies:

- Material UI: Component library
- Redux Toolkit: State management
- React Router: Navigation
- Axios: HTTP client
- Socket.IO: WebSocket client

Install dependencies with:

```bash
cd frontend
npm install
```

## Development

### Starting the Backend

```bash
uvicorn src.app.api.main:app --reload
```

### Starting the Frontend

```bash
cd frontend
npm start
```

### Testing

```bash
# Backend tests
pytest src/tests

# Frontend tests
cd frontend
npm test
```

## CI/CD

The project uses GitHub Actions for continuous integration and deployment. See [CICD.md](CICD.md) for details.

## License

See [LICENSE](LICENSE) file for details.
