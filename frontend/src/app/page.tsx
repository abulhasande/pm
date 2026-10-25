"use client";

import { useState } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";

const VALID_USERNAME = "user";
const VALID_PASSWORD = "password";

export default function Home() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (username === VALID_USERNAME && password === VALID_PASSWORD) {
      setError("");
      setIsAuthenticated(true);
      return;
    }

    setError("Invalid username or password.");
  };

  if (isAuthenticated) {
    return (
      <div>
        <button
          type="button"
          onClick={() => setIsAuthenticated(false)}
          className="absolute right-6 top-6 rounded-full bg-[var(--navy-dark)] px-4 py-2 text-sm font-semibold text-white"
        >
          Log out
        </button>
        <KanbanBoard username={username} />
      </div>
    );
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_rgba(32,157,215,0.12),_transparent_45%),linear-gradient(135deg,#f5f7fb,#edf3ff)] px-4 py-12">
      <div className="w-full max-w-md rounded-[28px] border border-[var(--stroke)] bg-white p-8 shadow-[var(--shadow)]">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[var(--gray-text)]">
          Project board
        </p>
        <h1 className="mt-4 font-display text-3xl font-semibold text-[var(--navy-dark)]">
          Sign in
        </h1>
        <p className="mt-3 text-sm text-[var(--gray-text)]">
          Use your workspace credentials to continue.
        </p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-5">
          <div>
            <label htmlFor="username" className="mb-2 block text-sm font-medium text-[var(--navy-dark)]">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="user"
              className="w-full rounded-xl border border-[var(--stroke)] bg-[var(--surface)] px-3 py-3 text-base text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
              autoComplete="username"
            />
          </div>

          <div>
            <label htmlFor="password" className="mb-2 block text-sm font-medium text-[var(--navy-dark)]">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="password"
              className="w-full rounded-xl border border-[var(--stroke)] bg-[var(--surface)] px-3 py-3 text-base text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
              autoComplete="current-password"
            />
          </div>

          {error ? (
            <p className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </p>
          ) : null}

          <button
            type="submit"
            className="w-full rounded-xl bg-[var(--purple-secondary)] px-4 py-3 text-sm font-semibold uppercase tracking-[0.12em] text-white transition hover:opacity-95"
          >
            Sign in
          </button>
        </form>
      </div>
    </main>
  );
}
