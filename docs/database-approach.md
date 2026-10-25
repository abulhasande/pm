# Database approach

## Overview

The project uses SQLite for the local MVP database. SQLite is a good fit because the application runs locally in Docker, the database is lightweight, and the data model is small enough to manage without a separate database server.

## Design goals

- support the current single-board-per-user MVP
- remain compatible with a future multi-user model
- keep the schema simple enough for direct SQLite access and easy test setup
- allow the frontend to load and update board state through backend endpoints

## Proposed schema

The schema is defined in [kanban-schema.json](./kanban-schema.json).

### Users

The `users` table stores account data for the current and future user model. The MVP login is hardcoded to `user` and `password`, but the data model is intentionally designed so a real user database can be introduced later without restructuring the core board schema.

### Boards

The `boards` table stores the board metadata for each user. For the MVP, there is exactly one active board per user, but the relationship is already set up for future support of multiple boards per user.

### Columns

The `columns` table stores the board's column definitions. Each column belongs to a board and includes a `position` field to preserve ordering.

The default board includes:
- Backlog
- Discovery
- In Progress
- Review
- Done

These names are editable in the UI, so the title is not locked to a constant. The column identity remains stable even if the label changes.

### Cards

The `cards` table stores task content and the column placement of each card. Each card includes:
- title
- details
- position within a column
- board and column references
- timestamps for creation and update tracking

## Data flow

1. The backend creates the SQLite database if it does not already exist.
2. The backend initializes the required tables and default columns when a new user or board is created.
3. The frontend loads the board state through a backend API.
4. Drag-and-drop, card creation, and column renaming all write back to the same persistence layer.

## Future considerations

- Replace the current hardcoded login with real password hashing and session management.
- Add additional board relationships and card history if the product expands beyond the MVP.
- Add indexes for common reads such as board lookup by user and column lookup by board.

## Approval status

This proposal is intentionally minimal but extensible. It is ready for review before the backend persistence layer is implemented.
