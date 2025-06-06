# LEIA beheeromgeving Web App - Svelte + FastAPI + PostgreSQL

Gebruikt om de JSON configuratie files van LEIA digital twins te beheren.

## Clone
```sh
git clone https://github.com/ElwinMan/LEIA_beheeromgeving.git
cd LEIA_beheeromgeving
```
## Build

### With docker

```sh
docker compose up --build
```

Svelte frontend: http://localhost:8080/

FastAPI backend: http://localhost:8000/
API docs: http://localhost:8000/docs

PostgreSQL: http://localhost:5432/