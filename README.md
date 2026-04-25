# SmileSchedule Availability Service

`availability-service` is the slot management microservice for SmileSchedule. It provides availability-focused APIs and delegates persistence operations to `database-service`.

## Current scope

This implementation currently includes:

- FastAPI application bootstrap
- HTTP integration with `database-service`
- listing only free slots (not reserved)
- creating availability slots
- updating existing slots
- deleting slots
- container-ready local setup

## Environment

Copy `.env.example` to `.env` and adjust values if needed.

Important variable:

- `DATABASE_SERVICE_URL`: base URL of the existing `database-service`

## Run locally

```bash
docker compose up --build
```

Swagger UI will be available at `http://localhost:8200/docs`.

## Main endpoints

- `GET /health`
- `GET /availability/slots`
- `POST /availability/slots`
- `PATCH /availability/slots/{slot_id}`
- `DELETE /availability/slots/{slot_id}`

## Integration note

To use this service, the target `database-service` should expose:

- `GET /slots`
- `POST /slots`
- `PATCH /slots/{id}`
- `DELETE /slots/{id}`
