# ScrapIt - AI-Powered Email Cleaner

An intelligent web-based email management system that uses AI to automatically clean, categorize, and organize Gmail inboxes.

## 🚀 Features

- **AI-Powered Classification**: Uses OpenAI/Claude APIs to intelligently categorize emails
- **Smart Spam Detection**: Advanced spam detection with sender reputation tracking
- **Bulk Operations**: Safe bulk delete, archive, and organize operations
- **Email Clustering**: K-means clustering for automatic email organization
- **Analytics Dashboard**: Comprehensive insights and email pattern analysis
- **Real-time Processing**: Background task processing with progress tracking

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Primary database
- **Redis** - Caching and task queue
- **Celery** - Background task processing
- **SQLAlchemy** - Database ORM
- **OpenAI/Claude APIs** - AI classification
- **Gmail API** - Email integration

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Material-UI** - Component library
- **Chart.js** - Data visualization
- **Redux Toolkit** - State management

### Infrastructure
- **Docker** - Containerization
- **AWS ECS** - Container orchestration
- **AWS RDS** - Managed database
- **AWS ElastiCache** - Managed Redis

## 📁 Project Structure

```
ScrapIt/
├── 01-project-setup/           # Development environment setup
├── 02-authentication/          # Google OAuth & JWT authentication
├── 03-gmail-integration/       # Gmail API client and email sync
├── 04-ai-classification/       # LLM-powered email classification
├── 05-spam-detection/          # Spam detection and sender management
├── 06-bulk-operations/         # Bulk email management operations
├── 07-analytics-dashboard/     # Data visualization and insights
├── 08-react-frontend/          # React TypeScript frontend
├── 09-background-processing/   # Celery task management
├── 10-testing-suite/          # Comprehensive testing framework
├── 11-deployment-infrastructure/ # Docker and AWS deployment
└── 12-final-integration/      # End-to-end testing and launch prep
```

## 🚦 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker & Docker Compose
- PostgreSQL
- Redis

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/zeeshxnb/ScrapIt.git
   cd ScrapIt
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

### Development Workflow

Each numbered folder represents a development phase:

1. **Start with `01-project-setup/`** - Set up your development environment
2. **Follow the README in each folder** for detailed implementation guidance
3. **Use the skeleton files** as templates for your code implementation
4. **Test incrementally** as you complete each phase

## 🔧 Configuration

### Required API Keys
- **Google OAuth**: Client ID and Secret from Google Cloud Console
- **OpenAI API**: API key for email classification
- **Gmail API**: Enabled in Google Cloud Console

### Database Setup
```bash
# Create database
createdb scrapit

# Run migrations
alembic upgrade head
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# End-to-end tests
npm run test:e2e
```

## 🚀 Deployment

### Docker Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### AWS Deployment
See `11-deployment-infrastructure/` for detailed AWS setup instructions.

## 📊 Data Science Features

- **Email Classification**: Multi-category classification using LLMs
- **Clustering Analysis**: K-means clustering for email organization
- **Sender Reputation**: Machine learning-based sender scoring
- **Pattern Recognition**: Time series analysis of email patterns
- **Spam Detection**: Advanced spam detection algorithms

## 🤝 Contributing

This is a collaborative project between team members. Each folder contains detailed implementation guides and TODO comments to help with development.

### Development Guidelines
- Follow the numbered folder sequence for implementation
- Use the provided class structures and method signatures
- Implement comprehensive error handling and logging
- Write tests for all new functionality

## 📝 License

This project is for educational and portfolio purposes.

## 🔗 Links

- [Project Specification](.kiro/specs/ai-email-cleaner/)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)

---

**Built with ❤️ for efficient email management**
