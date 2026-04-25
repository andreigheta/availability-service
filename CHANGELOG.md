# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog,
and this project adheres to Semantic Versioning.

## [Unreleased]

## [0.1.0]

### Added

- Initial `availability-service` skeleton in a separate folder.
- FastAPI availability layer connected to the existing `database-service`.
- Availability slot listing endpoint that returns only free (not reserved) slots.
- Availability slot create, update and delete flows delegated to `database-service`.
- Dockerfile, Compose stack and `.env.example` support for local execution.
