"use client";

import { useEffect, useMemo, useState } from "react";
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { KanbanColumn } from "@/components/KanbanColumn";
import { KanbanCardPreview } from "@/components/KanbanCardPreview";
import { askAi, fetchBoard, saveBoard, type AiMessage } from "@/lib/api";
import { createId, initialData, moveCard, type BoardData } from "@/lib/kanban";

type KanbanBoardProps = {
  username?: string;
};

export const KanbanBoard = ({ username }: KanbanBoardProps) => {
  const [board, setBoard] = useState<BoardData | null>(null);
  const [isLoading, setIsLoading] = useState(Boolean(username));
  const [activeCardId, setActiveCardId] = useState<string | null>(null);
  const [aiInput, setAiInput] = useState("");
  const [aiMessages, setAiMessages] = useState<AiMessage[]>([]);
  const [isAiLoading, setIsAiLoading] = useState(false);
  const [aiError, setAiError] = useState("");

  useEffect(() => {
    if (!username) {
      setBoard(initialData);
      setIsLoading(false);
      return;
    }

    let isMounted = true;

    const loadBoard = async () => {
      try {
        setIsLoading(true);
        const nextBoard = await fetchBoard(username);
        if (isMounted) {
          setBoard(nextBoard);
        }
      } catch (error) {
        console.error("Failed to load board from backend", error);
        if (isMounted) {
          setBoard(initialData);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadBoard();

    return () => {
      isMounted = false;
    };
  }, [username]);

  const persistBoard = async (nextBoard: BoardData) => {
    if (!username) {
      return;
    }

    try {
      const savedBoard = await saveBoard(username, nextBoard);
      setBoard(savedBoard);
    } catch (error) {
      console.error("Failed to save board", error);
      setBoard(nextBoard);
    }
  };

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 6 },
    })
  );

  const cardsById = useMemo(() => board?.cards ?? {}, [board]);

  const handleDragStart = (event: DragStartEvent) => {
    setActiveCardId(event.active.id as string);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveCardId(null);

    if (!over || active.id === over.id || !board) {
      return;
    }

    const nextBoard: BoardData = {
      ...board,
      columns: moveCard(board.columns, active.id as string, over.id as string),
    };

    setBoard(nextBoard);
    if (username) {
      void persistBoard(nextBoard);
    }
  };

  const handleRenameColumn = (columnId: string, title: string) => {
    if (!board) {
      return;
    }

    const nextBoard: BoardData = {
      ...board,
      columns: board.columns.map((column) =>
        column.id === columnId ? { ...column, title } : column
      ),
    };

    setBoard(nextBoard);
    if (username) {
      void persistBoard(nextBoard);
    }
  };

  const handleAddCard = (columnId: string, title: string, details: string) => {
    if (!board) {
      return;
    }

    const id = createId("card");
    const nextBoard: BoardData = {
      ...board,
      cards: {
        ...board.cards,
        [id]: { id, title, details: details || "No details yet." },
      },
      columns: board.columns.map((column) =>
        column.id === columnId
          ? { ...column, cardIds: [...column.cardIds, id] }
          : column
      ),
    };

    setBoard(nextBoard);
    if (username) {
      void persistBoard(nextBoard);
    }
  };

  const handleDeleteCard = (columnId: string, cardId: string) => {
    if (!board) {
      return;
    }

    const nextBoard: BoardData = {
      ...board,
      cards: Object.fromEntries(
        Object.entries(board.cards).filter(([id]) => id !== cardId)
      ),
      columns: board.columns.map((column) =>
        column.id === columnId
          ? {
              ...column,
              cardIds: column.cardIds.filter((id) => id !== cardId),
            }
          : column
      ),
    };

    setBoard(nextBoard);
    if (username) {
      void persistBoard(nextBoard);
    }
  };

  const activeCard = activeCardId ? cardsById[activeCardId] : null;

  const handleAiSubmit = async () => {
    if (!username || !aiInput.trim() || isAiLoading) {
      return;
    }

    const question = aiInput.trim();
    const history: AiMessage[] = [...aiMessages, { role: "user", content: question }];
    setAiInput("");
    setAiMessages(history);
    setIsAiLoading(true);
    setAiError("");

    try {
      const response = await askAi(username, question, history);
      const assistantMessage: AiMessage = { role: "assistant", content: response.answer };
      setAiMessages([...history, assistantMessage]);
      if (response.board) {
        setBoard(response.board);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "The AI assistant could not help with that request.";
      setAiError(message);
      setAiMessages((current) => current.slice(0, -1));
    } finally {
      setIsAiLoading(false);
    }
  };

  if (!board || isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--surface)] text-sm font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
        Loading board...
      </div>
    );
  }

  return (
    <div className="relative overflow-hidden">
      <div className="pointer-events-none absolute left-0 top-0 h-[420px] w-[420px] -translate-x-1/3 -translate-y-1/3 rounded-full bg-[radial-gradient(circle,_rgba(32,157,215,0.25)_0%,_rgba(32,157,215,0.05)_55%,_transparent_70%)]" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-[520px] w-[520px] translate-x-1/4 translate-y-1/4 rounded-full bg-[radial-gradient(circle,_rgba(117,57,145,0.18)_0%,_rgba(117,57,145,0.05)_55%,_transparent_75%)]" />

      <main className="relative mx-auto flex min-h-screen max-w-[1500px] flex-col gap-10 px-6 pb-16 pt-12">
        <header className="flex flex-col gap-6 rounded-[32px] border border-[var(--stroke)] bg-white/80 p-8 shadow-[var(--shadow)] backdrop-blur">
          <div className="flex flex-wrap items-start justify-between gap-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
                Single Board Kanban
              </p>
              <h1 className="mt-3 font-display text-4xl font-semibold text-[var(--navy-dark)]">
                Kanban Studio
              </h1>
              <p className="mt-3 max-w-xl text-sm leading-6 text-[var(--gray-text)]">
                Keep momentum visible. Rename columns, drag cards between stages,
                and capture quick notes without getting buried in settings.
              </p>
            </div>
            <div className="rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] px-5 py-4">
              <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--gray-text)]">
                Focus
              </p>
              <p className="mt-2 text-lg font-semibold text-[var(--primary-blue)]">
                One board. Five columns. Zero clutter.
              </p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-4">
            {board.columns.map((column) => (
              <div
                key={column.id}
                className="flex items-center gap-2 rounded-full border border-[var(--stroke)] px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--navy-dark)]"
              >
                <span className="h-2 w-2 rounded-full bg-[var(--accent-yellow)]" />
                {column.title}
              </div>
            ))}
          </div>
        </header>

        <div className="flex flex-col gap-6 xl:flex-row">
          <DndContext
            sensors={sensors}
            collisionDetection={closestCorners}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
          >
            <section className="grid flex-1 gap-6 lg:grid-cols-2 2xl:grid-cols-5">
              {board.columns.map((column) => (
                <KanbanColumn
                  key={column.id}
                  column={column}
                  cards={column.cardIds.map((cardId) => board.cards[cardId]).filter(Boolean)}
                  onRename={handleRenameColumn}
                  onAddCard={handleAddCard}
                  onDeleteCard={handleDeleteCard}
                />
              ))}
            </section>
            <DragOverlay>
              {activeCard ? (
                <div className="w-[260px]">
                  <KanbanCardPreview card={activeCard} />
                </div>
              ) : null}
            </DragOverlay>
          </DndContext>

          <aside className="w-full rounded-[28px] border border-[var(--stroke)] bg-white/90 p-5 shadow-[var(--shadow)] backdrop-blur xl:max-w-[360px]">
            <div className="mb-4 flex items-center justify-between gap-4">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-[var(--gray-text)]">
                  Assistant
                </p>
                <h2 className="mt-2 text-xl font-semibold text-[var(--navy-dark)]">Project AI</h2>
              </div>
            </div>

            <div className="space-y-3 rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] p-3">
              {aiMessages.length === 0 ? (
                <p className="text-sm text-[var(--gray-text)]">
                  Ask for a quick update, like “Move the mobile launch card to Review.”
                </p>
              ) : (
                aiMessages.map((message, index) => (
                  <div
                    key={`${message.role}-${index}`}
                    className={`rounded-xl px-3 py-2 text-sm ${
                      message.role === "assistant"
                        ? "bg-white text-[var(--navy-dark)]"
                        : "bg-[var(--primary-blue)]/10 text-[var(--navy-dark)]"
                    }`}
                  >
                    <strong className="mr-2 uppercase tracking-[0.1em] text-[10px]">
                      {message.role === "assistant" ? "AI" : "You"}
                    </strong>
                    <span>{message.content}</span>
                  </div>
                ))
              )}
            </div>

            <label className="mt-4 block text-xs font-semibold uppercase tracking-[0.24em] text-[var(--gray-text)]">
              Ask the board assistant
            </label>
            <textarea
              value={aiInput}
              onChange={(event) => setAiInput(event.target.value)}
              rows={4}
              placeholder="Rename the launch card to Q4 launch plan..."
              className="mt-2 w-full rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] px-3 py-3 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
            />

            {aiError ? (
              <p className="mt-3 rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                {aiError}
              </p>
            ) : null}

            <button
              type="button"
              onClick={() => void handleAiSubmit()}
              disabled={isAiLoading || !aiInput.trim()}
              className="mt-4 w-full rounded-xl bg-[var(--purple-secondary)] px-4 py-3 text-sm font-semibold uppercase tracking-[0.12em] text-white transition hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isAiLoading ? "Thinking..." : "Ask AI"}
            </button>
          </aside>
        </div>
      </main>
    </div>
  );
};
