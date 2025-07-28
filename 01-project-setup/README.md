# 01 - Project Setup

## Overview
Set up the foundational project structure, development environment, and basic configuration files.

## Tasks to Complete
- [ ] Create GitHub repository structure
- [ ] Set up Docker Compose for local development
- [ ] Create initial requirements.txt and package.json
- [ ] Configure environment variables

## Folder Structure to Create
```
ScrapIt/
├── backend/
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Key Files to Create
1. **docker-compose.yml** - PostgreSQL, Redis, backend, frontend services
2. **backend/requirements.txt** - FastAPI, SQLAlchemy, Celery, etc.
3. **frontend/package.json** - React, TypeScript, Material-UI
4. **.env.example** - Template for environment variables

## Tips
- Use official Docker images for PostgreSQL and Redis
- Set up volume mounts for database persistence
- Configure hot reloading for development
- Include health checks in Docker services