# IDENTIFY TARGETS - Backend

This is the MVP Django REST API for managing Targets, Sources, Indicators, and Associations.

## Quickstart

- Install dependencies:
  - Python 3.11+
  - pip install -r backend/requirements.txt
- Run migrations:
  - cd backend
  - python manage.py makemigrations
  - python manage.py migrate
- Run server:
  - python manage.py runserver 0.0.0.0:3001

## API Endpoints

Base path: /api/

- Health
  - GET /api/health/

- Targets
  - GET /api/targets/
  - POST /api/targets/
  - GET /api/targets/{id}/
  - PATCH /api/targets/{id}/
  - DELETE /api/targets/{id}/
  - GET /api/targets/{id}/score/
  - POST /api/targets/{id}/promote/  body: {"status": "new|under_review|confirmed|rejected"}

- Sources
  - CRUD on /api/sources/

- Indicators
  - CRUD on /api/indicators/

- Associations
  - CRUD on /api/associations/

## Filtering, Search, Ordering

- Targets:
  - search: ?search=<term> on name, description, tags
  - filters: status=<value>, priority_min/max, confidence_min/max, created_at_after/before via created_at param (DateTimeFromToRange)
  - ordering: ?ordering=priority,-confidence,updated_at

- Indicators:
  - filters: type=<value>, source=<id>, score_min/max
  - ordering: ?ordering=-score,created_at

- Associations:
  - filters: target=<id>, indicator=<id>, weight_min/max

## Pagination

- Default PageNumberPagination with page_size=20
- ?page=<n>&page_size=<m> (max 200)

## Docs

- Swagger UI: /docs
- ReDoc: /redoc
- Raw schema: /swagger.json

## Example curl

- Create target:
  curl -X POST http://localhost:3001/api/targets/ -H "Content-Type: application/json" -d '{"name":"Alpha","status":"new","priority":5,"tags":"alpha,beta","confidence":0.7}'

- Compute score:
  curl http://localhost:3001/api/targets/1/score/

- Promote:
  curl -X POST http://localhost:3001/api/targets/1/promote/ -H "Content-Type: application/json" -d '{"status":"confirmed"}'

## Testing

- cd backend
- python manage.py test
