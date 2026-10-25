# Backend agent guide

This directory contains the Python FastAPI backend for the project management application. It is responsible for serving the built frontend, exposing board APIs, and later integrating with OpenRouter for AI-assisted Kanban workflows.

## Current state

The backend is intentionally minimal at this stage. It includes:
- a FastAPI application instance
- a health endpoint at /api/health
- a hello endpoint at /api/hello
- support for serving a built frontend from the repository's frontend/out directory when available
- startup hooks that make local development simple in Docker and via a local Python environment

## Responsibilities

The backend should eventually provide:
- SQLite database initialization and schema creation
- per-user board persistence
- API endpoints for reading and updating card data, columns, and board state
- authentication/session checks for the dummy MVP login
- AI connectivity using OpenRouter and structured board-aware prompts

## Implementation notes

- Keep the API simple and explicit.
- Keep the codebase lightweight and focused on the MVP.
- Use FastAPI dependency injection patterns only where they add clarity.
- Do not add unnecessary abstraction layers before the schema and API needs are clearly defined.
- Prefer straightforward endpoint and model code over speculative architecture.

## Validation

Use focused backend tests for each new route and persistence behavior. The current smoke tests cover the root fallback and API health paths.
