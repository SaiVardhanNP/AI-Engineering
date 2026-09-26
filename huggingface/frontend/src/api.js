const BASE = "/api";

async function request(path, options) {
  const response = await fetch(BASE + path, options);

  if (!response.ok) {
    let detail = null;
    try {
      detail = (await response.json()).detail;
    } catch {
      detail = null;
    }
    const message = typeof detail === "string" ? detail : `Request failed (${response.status})`;
    throw new Error(message);
  }

  return response.status === 204 ? null : response.json();
}

export const checkHealth = () => request("/health");

export const documentFileUrl = (docId) => `${BASE}/documents/${docId}/file`;

export const listDocuments = () => request("/documents");

export function uploadDocument(file) {
  const body = new FormData();
  body.append("file", file);
  return request("/documents", { method: "POST", body });
}

export const listModels = () => request("/models");

export function sendChat({ docId, question, sessionId, model }) {
  return request("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ doc_id: docId, question, session_id: sessionId, model }),
  });
}

export const getHistory = (sessionId) => request(`/chat/${sessionId}/history`);

export const clearHistory = (sessionId) => request(`/chat/${sessionId}/history`, { method: "DELETE" });
