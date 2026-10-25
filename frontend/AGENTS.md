# Frontend agent guide

This directory contains the Next.js frontend for the project management MVP. The current implementation is a demo Kanban board, and it is intentionally simple and local-only before backend persistence and AI features are added.

## Project purpose

The frontend should ultimately:
- render a sign-in screen before authentication
- show the kanban board only after the user signs in
- allow column renaming and drag-and-drop card movement
- support creating and deleting cards
- connect to backend APIs for persisted board state
- support AI chat in a sidebar that can update the board through structured output

## Current codebase structure

- src/app/page.tsx
  - Top-level page entry.
  - Renders the Kanban board component.

- src/components/KanbanBoard.tsx
  - Main interactive board component.
  - Uses dnd-kit for drag and drop.
  - Maintains local board state and emits column/card updates.

- src/components/KanbanColumn.tsx
  - Renders a single board column.
  - Supports inline renaming and card creation.

- src/components/KanbanCard.tsx
  - Card display for an individual task.

- src/components/KanbanCardPreview.tsx
  - Used during drag operations as an overlay preview.

- src/components/NewCardForm.tsx
  - Form for adding a new card to a column.

- src/lib/kanban.ts
  - Core board data model and helper logic.
  - Includes initial sample board data, card movement logic, and ID generation.

- src/test/setup.ts
  - Test bootstrap and DOM setup for Vitest.

- tests/
  - Playwright or end-to-end test scaffolding.

## Current behaviors

The current frontend already demonstrates the following:
- five fixed columns with sample content
- drag and drop between columns and within a column
- renaming column titles
- adding a card with title and details
- deleting a card
- keyboard and mouse-friendly interaction patterns through the component UI

## Important implementation notes

- This app uses Next.js 16 and React 19.
- The app is a client-side demo at this stage; it is not yet connected to a backend database or auth system.
- Board state is local in memory and is intentionally replaced during later phases with persisted API-backed state.
- Keep the code simple; do not over-engineer this area before the backend API and AI integration are in place.
- Do not mix server-side data fetching into this layer until the project reaches the backend integration stages.

## Testing setup

- Unit tests run with Vitest.
- Interactive browser tests use Playwright.
- Coverage should be collected and measured for the core board logic, component flows, and user journeys.
- Coverage target for high-value modules: 80% or higher.

## Commands

From this directory:
- npm run dev
  - starts the Next.js development server
- npm run build
  - creates the production build
- npm run test
  - runs the unit test suite
- npm run test:e2e
  - runs browser-based integration tests
- npm run test:all
  - runs both unit and e2e tests

## Development guidance

When working in this folder:
- preserve the existing board and drag-drop experience
- prefer small, focused changes to the component tree and board logic
- update tests when behavior changes
- maintain the current visual design language and color palette
- keep the app aligned with MVP requirements rather than adding non-essential features

## Known current state

This frontend is a working demo but not yet production-ready for the final MVP. The next phases should progressively replace the local demo state with:
1. login gate
2. backend persistence
3. structured AI assistance
4. sidebar chat integration

Follow the project plan in docs/PLAN.md for the sequence of changes.
