import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import Home from "@/app/page";
import { KanbanBoard } from "@/components/KanbanBoard";

const getFirstColumn = () => screen.getAllByTestId(/column-/i)[0];

describe("KanbanBoard", () => {
  it("renders five columns", () => {
    render(<KanbanBoard />);
    expect(screen.getAllByTestId(/column-/i)).toHaveLength(5);
  });

  it("renames a column", async () => {
    render(<KanbanBoard />);
    const column = getFirstColumn();
    const input = within(column).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    expect(input).toHaveValue("New Name");
  });

  it("adds and removes a card", async () => {
    render(<KanbanBoard />);
    const column = getFirstColumn();
    const addButton = within(column).getByRole("button", {
      name: /add a card/i,
    });
    await userEvent.click(addButton);

    const titleInput = within(column).getByPlaceholderText(/card title/i);
    await userEvent.type(titleInput, "New card");
    const detailsInput = within(column).getByPlaceholderText(/details/i);
    await userEvent.type(detailsInput, "Notes");

    await userEvent.click(within(column).getByRole("button", { name: /add card/i }));

    expect(within(column).getByText("New card")).toBeInTheDocument();

    const deleteButton = within(column).getByRole("button", {
      name: /delete new card/i,
    });
    await userEvent.click(deleteButton);

    expect(within(column).queryByText("New card")).not.toBeInTheDocument();
  });
});

describe("Home login flow", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("requires valid credentials before showing the board", async () => {
    const user = userEvent.setup();
    render(<Home />);

    await user.type(screen.getByLabelText("Username"), "wrong");
    await user.type(screen.getByLabelText("Password"), "wrong");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    expect(screen.getByText(/invalid username or password/i)).toBeInTheDocument();
    expect(screen.queryByText(/kanban studio/i)).not.toBeInTheDocument();
  });

  it("loads the board from the API after a valid sign in and allows logout", async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        columns: [
          { id: "col-backlog", title: "Backlog", cardIds: ["card-1"] },
          { id: "col-progress", title: "In Progress", cardIds: [] },
        ],
        cards: {
          "card-1": { id: "card-1", title: "Loaded from API", details: "Fetched details" },
        },
      }),
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    await user.type(screen.getByLabelText("Username"), "user");
    await user.type(screen.getByLabelText("Password"), "password");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/api/users/user/board");
    });

    expect(screen.getByText(/kanban studio/i)).toBeInTheDocument();
    expect(screen.getByText("Loaded from API")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /log out/i }));
    expect(screen.getByRole("heading", { name: /sign in/i })).toBeInTheDocument();
  });

  it("asks the AI assistant and applies a returned board update", async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn().mockImplementation((url: string, options?: RequestInit) => {
      if (url === "http://localhost:8000/api/users/user/board") {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            columns: [
              { id: "col-backlog", title: "Backlog", cardIds: ["card-1"] },
              { id: "col-progress", title: "In Progress", cardIds: [] },
            ],
            cards: {
              "card-1": { id: "card-1", title: "Original task", details: "Fetched details" },
            },
          }),
        }) as Response;
      }

      if (url === "http://localhost:8000/api/users/user/ai") {
        expect(options?.method).toBe("POST");
        return Promise.resolve({
          ok: true,
          json: async () => ({
            answer: "Updated the task.",
            board: {
              columns: [
                { id: "col-backlog", title: "Backlog", cardIds: ["card-1"] },
                { id: "col-progress", title: "In Progress", cardIds: [] },
              ],
              cards: {
                "card-1": { id: "card-1", title: "Renamed task", details: "Updated details" },
              },
            },
          }),
        }) as Response;
      }

      return Promise.resolve({ ok: false, json: async () => ({ detail: "Unexpected URL" }) }) as Response;
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    await user.type(screen.getByLabelText("Username"), "user");
    await user.type(screen.getByLabelText("Password"), "password");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => expect(screen.getByText("Original task")).toBeInTheDocument());

    await user.type(screen.getByPlaceholderText(/rename the launch card/i), "Rename the first task to Renamed task.");
    await user.click(screen.getByRole("button", { name: /ask ai/i }));

    await waitFor(() => {
      expect(screen.getByText("Updated the task.")).toBeInTheDocument();
      expect(screen.getByText("Renamed task")).toBeInTheDocument();
    });
  });
});
