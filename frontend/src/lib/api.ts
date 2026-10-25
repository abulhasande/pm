import type { BoardData } from "@/lib/kanban";

export const getApiBaseUrl = () => {
  if (typeof window === "undefined") {
    return "";
  }

  const envOverride = process.env.NEXT_PUBLIC_API_URL;
  if (envOverride) {
    return envOverride.replace(/\/$/, "");
  }

  const origin = window.location.origin;
  if (origin.includes("localhost:3000") || origin.includes("127.0.0.1:3000")) {
    return origin.replace(/:3000$/, ":8000");
  }

  return origin;
};

export const fetchBoard = async (username: string): Promise<BoardData> => {
  const baseUrl = getApiBaseUrl();
  const response = await fetch(`${baseUrl}/api/users/${encodeURIComponent(username)}/board`);

  if (!response.ok) {
    throw new Error(`Failed to load board for ${username}`);
  }

  return (await response.json()) as BoardData;
};

export const saveBoard = async (
  username: string,
  board: BoardData
): Promise<BoardData> => {
  const baseUrl = getApiBaseUrl();
  const response = await fetch(`${baseUrl}/api/users/${encodeURIComponent(username)}/board`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(board),
  });

  if (!response.ok) {
    throw new Error(`Failed to save board for ${username}`);
  }

  return (await response.json()) as BoardData;
};

export type AiMessage = {
  role: "user" | "assistant";
  content: string;
};

export const askAi = async (
  username: string,
  question: string,
  history: AiMessage[] = []
): Promise<{ answer: string; board?: BoardData }> => {
  const baseUrl = getApiBaseUrl();
  const response = await fetch(`${baseUrl}/api/users/${encodeURIComponent(username)}/ai`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, history }),
  });

  if (!response.ok) {
    const details = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(details.detail ?? "Failed to ask the AI assistant");
  }

  return (await response.json()) as { answer: string; board?: BoardData };
};
