# Project plan and execution checklist

This document maps the full MVP delivery plan for the project management app. Each part includes execution steps, a checklist for the agent, test expectations, and success criteria. The plan is designed to be reviewed and approved before implementation begins.

## Quality gates

- Target unit test coverage: at least 80% across project-critical areas.
- Use automated frontend unit tests and browser-based integration tests for user flows.
- Use backend unit tests for API and persistence behavior.
- Run focused validation after each phase; do not wait until the end to discover breakage.
- Keep changes small and reversible; avoid speculative architecture.

## Part 1: Plan and approval

Checklist
- [ ] Review the current repository state, frontend baseline, and existing docs.
- [ ] Confirm requirements, scope, and MVP constraints from AGENTS.md and project brief.
- [ ] Enrich this plan with detailed implementation steps, verification, and acceptance criteria.
- [ ] Create a frontend-specific AGENTS.md document that describes the current codebase and how to work in it.
- [ ] Confirm the plan with the user before implementation begins.

Tests
- Documentation review: verify all required major phases are covered.
- Manual check: confirm AGENTS.md clearly describes the frontend architecture and developer workflow.

Success criteria
- The user explicitly approves the plan.
- The implementation roadmap is concrete enough for the agent to execute without additional clarification.

## Part 2: Scaffolding and local runtime

Goal
Set up Docker, the Python/FastAPI backend, and the local start/stop scripts so the app can run locally and serve a "hello world" proof-of-life before the real product is added.

Checklist
- [ ] Create Docker configuration needed to run the app locally.
- [ ] Add backend/ with FastAPI app structure and dependency management using uv.
- [ ] Add a minimal health endpoint and a simple hello-world route.
- [ ] Ensure the app serves static content as a fallback or root route for local testing.
- [ ] Add scripts/ for start and stop operations for Mac, Windows, and Linux.
- [ ] Confirm startup, shutdown, and port binding are reliable and documented.
- [ ] Verify the app responds at / and /api/health or equivalent.

Tests
- Backend smoke test: verify the root route returns expected HTML or text.
- Backend smoke test: verify the API route returns JSON.
- Script validation: start script runs without error and the app is reachable on the configured local port.

Success criteria
- A developer can start the app with the provided scripts.
- The app runs locally in Docker.
- The basic health endpoint and static serve path respond correctly.

## Part 3: Add the frontend app and production serving

Goal
Integrate the existing frontend demo, ensure it builds and serves as the default application, and add strong automated validation.

Checklist
- [ ] Review the existing Next.js frontend implementation and identify current demo features.
- [ ] Wire the frontend to be statically built and served through the FastAPI app at /.
- [ ] Ensure the app renders the demo Kanban board at the root route.
- [ ] Keep the app simple and aligned with the project’s color palette and MVP scope.
- [ ] Add unit tests for the board logic, card behavior, and component rendering.
- [ ] Add integration tests covering the main board view and key interactions.
- [ ] Configure coverage collection and confirm the project targets at least 80% coverage in critical frontend modules.

Tests
- Unit tests for board state mutations and drag logic.
- Component tests for rendering column titles, cards, and edit/add flows.
- Integration tests that load the page, verify board presence, and interact with cards and columns.
- Coverage run: confirm threshold is reached for frontend files.

Success criteria
- The app loads at /, shows the Kanban board, and is served from the production stack.
- Frontend features are verified by automated tests.
- Coverage target is met or exceeded.

## Part 4: Fake login experience

Goal
Add a basic sign-in flow that blocks access to the board unless the user enters the dummy credentials ("user" / "password"), and allow logout.

Checklist
- [ ] Add a minimal authentication gate that prevents access to the main board unless signed in.
- [ ] Implement sign-in with the fixed credentials defined in the spec.
- [ ] Add sign-out flow and ensure board access is revoked after logout.
- [ ] Keep the implementation simple; no full auth framework is required for the MVP.
- [ ] Add tests covering successful login, failed login, and logout.
- [ ] Add integration tests for the first-load login flow.

Tests
- Attempt to visit the board without signing in: user is redirected or blocked.
- Sign in with valid credentials: board is shown.
- Sign in with invalid credentials: error or retry path is shown.
- Sign out: user returns to the sign-in screen and cannot access the board again.
- Coverage for auth logic and route gating.

Success criteria
- The app enforces the required dummy login experience.
- Login and logout logic is covered by automated tests.
- The board remains inaccessible until authentication succeeds.

## Part 5: Database modeling and schema proposal

Goal
Define the Kanban data model as structured JSON and document the database approach before backend implementation proceeds.

Checklist
- [ ] Define the required entities for users, boards, columns, cards, and card state.
- [ ] Design the schema to support future multi-user growth while fitting the MVP single-board-per-user limitation.
- [ ] Save the schema as JSON in docs/ or another agreed location.
- [ ] Write a short design document describing SQLite usage, tables, relationships, and future considerations.
- [ ] Get explicit user sign-off on the schema and data model before coding backend APIs.

Tests
- Schema validation: JSON parses correctly and matches required entities.
- Design review: confirm the schema supports the required board operations and future extension.

Success criteria
- A clear, reviewed schema exists.
- The backend implementation uses the agreed data model.
- The user signs off before API implementation begins.

## Part 6: Backend persistence and API routes

Goal
Implement backend routes for reading and changing the Kanban board for a logged-in user, while creating the SQLite database if it does not already exist.

Checklist
- [ ] Create the SQLite database initialization path.
- [ ] Build model layer for users, board state, columns, and cards.
- [ ] Add API endpoints to fetch the board for a user.
- [ ] Add API endpoints to create, update, move, and delete cards.
- [ ] Add API endpoints to rename columns or otherwise update board metadata.
- [ ] Keep the API simple and aligned with the front-end usage pattern.
- [ ] Add backend unit tests for API response correctness and persistence behavior.
- [ ] Add integration tests for core board operations.

Tests
- Unit tests for database initialization and schema creation.
- Unit tests for creating a board/user record.
- Unit tests for reading and updating board state.
- API tests for success and validation-error scenarios.
- Coverage run targeting backend modules at or above 80%.

Success criteria
- The backend can create the database automatically.
- API routes change board data correctly and persist it.
- Backend logic is thoroughly tested and coverage threshold is met.

## Part 7: Frontend connected to backend persistence

Goal
Replace the local in-memory board with backend-backed data so the app behaves as a proper persistent Kanban system.

Checklist
- [ ] Replace local board state with API calls for load, update, move, rename, and delete actions.
- [ ] Keep the user experience consistent with the existing UI while integrating with the backend.
- [ ] Handle loading, error, and retry states gracefully without over-engineering.
- [ ] Ensure sign-in state is respected when fetching the board.
- [ ] Add frontend tests covering board loading from the API and post-action refresh behavior.
- [ ] Add browser-based integration tests that validate a realistic user flow.

Tests
- Frontend integration tests loading the board after sign-in and verifying persisted state.
- Mutation tests for create, move, rename, and delete actions using the API.
- Error-state tests for failed network or backend responses.
- Coverage check for frontend logic and data-fetching modules.

Success criteria
- The app reflects real persisted Kanban state instead of demo-only memory state.
- Core user flows work end-to-end with the backend.
- Coverage and integration requirements are satisfied.

## Part 8: AI connectivity via OpenRouter

Goal
Enable backend connectivity to OpenRouter and verify the integration with a simple test prompt such as "2 + 2".

Checklist
- [ ] Add backend configuration for the OpenRouter API key and model selection.
- [ ] Implement a minimal AI client that can send a basic prompt and receive a response.
- [ ] Confirm the request is authenticated correctly and returns structured output or text as expected.
- [ ] Add a simple health/test route or helper to validate the AI connection.
- [ ] Add tests for failure handling, configuration validation, and successful connection path.

Tests
- Local AI smoke test using a trivial prompt like "2 + 2".
- Failure path: missing or invalid key should fail gracefully.
- Coverage for the AI configuration and client wrapper.

Success criteria
- The backend can successfully call OpenRouter.
- AI connectivity is proven with a simple prompt.
- Errors are surfaced in a safe, actionable way.

## Part 9: Structured AI board assistance

Goal
Pass the Kanban board JSON and the current user question (plus conversation history) to the LLM, and require a structured response containing an answer and optional board updates.

Checklist
- [ ] Build a request payload that includes board JSON, user message, and relevant conversation history.
- [ ] Use a structured output contract for the AI response, including the user-facing answer and optional Kanban modifications.
- [ ] Implement validation for AI output before applying changes to the board.
- [ ] Add backend logic to apply safe board updates when the AI returns them.
- [ ] Add tests for valid AI responses, invalid schema responses, and no-op responses.
- [ ] Add backend tests covering conversation-aware prompts and state updates.

Tests
- Unit tests for payload creation and schema validation.
- Integration tests for AI -> backend -> board update flow.
- Negative tests for malformed AI responses.
- Coverage threshold maintained for backend logic.

Success criteria
- The AI can answer user questions using board context.
- Optional board updates are applied only when valid and safe.
- The backend handles structured AI responses predictably and testably.

## Part 10: AI sidebar and automatic UI refresh

Goal
Add the polished sidebar chat UI, allow the model to propose board changes, and refresh the board automatically when the AI updates it.

Checklist
- [ ] Add a sidebar-based AI chat panel that lives alongside the board.
- [ ] Send user queries and conversation context to the backend AI endpoint.
- [ ] Render AI responses in the UI and surface board updates clearly.
- [ ] If the AI updates the board, trigger a refresh and re-render the board automatically.
- [ ] Ensure the experience remains clean and usable without overbuilding the UI.
- [ ] Add frontend and integration tests for chat submission, response rendering, and auto-refresh behavior.

Tests
- Browser test for opening the sidebar and sending a prompt.
- Response rendering test for AI text and optional board updates.
- Board refresh test after the AI modifies tasks or columns.
- End-to-end validation of sign-in + board + AI chat flow.

Success criteria
- A user can interact with the AI from the board UI.
- AI-generated board updates are accepted safely and reflected instantly.
- The final MVP meets the business requirements and UX goals.

## Final validation checklist

Before completion, confirm all of the following:
- [ ] Docker startup works reliably.
- [ ] Frontend is served correctly and board renders at /.
- [ ] Dummy sign-in requirement is enforced.
- [ ] Database is initialized and persisted.
- [ ] API endpoints support board operations.
- [ ] AI integration is functional.
- [ ] Structured AI output drives board updates safely.
- [ ] Frontend chat UI refreshes the board automatically when updates occur.
- [ ] Test coverage target of at least 80% is met for critical modules.
- [ ] Integration tests validate the central user journeys.

## Notes

The current frontend is a demo-only local board with drag-and-drop mechanics, local state, and test scaffolding already in place. The implementation work should build from this baseline without over-engineering. The product should remain lightweight, local-first, and easy to operate in Docker.
