import { useCallback, useEffect, useRef, useState } from "react";
import Sidebar from "./components/Sidebar.jsx";
import Chat from "./components/Chat.jsx";
import { useTheme } from "./useTheme.js";
import {
  checkHealth,
  clearHistory,
  getHistory,
  listDocuments,
  sendChat,
  uploadDocument,
} from "./api.js";

const SESSIONS_KEY = "folio.sessions";

function loadSessions() {
  try {
    return JSON.parse(localStorage.getItem(SESSIONS_KEY)) || {};
  } catch {
    return {};
  }
}

function saveSessions(sessions) {
  try {
    localStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions));
  } catch {
    // storage can be blocked; conversations still work until the page closes
  }
}

export default function App() {
  const { theme, toggle } = useTheme();

  const [documents, setDocuments] = useState([]);
  const [loadingDocuments, setLoadingDocuments] = useState(true);
  const [activeId, setActiveId] = useState(null);
  const [serverUp, setServerUp] = useState(true);

  const [uploading, setUploading] = useState(false);
  const [uploadNote, setUploadNote] = useState("");

  const [threads, setThreads] = useState({});
  const [busy, setBusy] = useState(false);
  const sessions = useRef(loadSessions());
  const lastQuestion = useRef(null);

  const refreshDocuments = useCallback(async () => {
    try {
      const list = await listDocuments();
      setDocuments(list);
      setServerUp(true);
      return list;
    } catch {
      setServerUp(false);
      return [];
    } finally {
      setLoadingDocuments(false);
    }
  }, []);

  useEffect(() => {
    refreshDocuments().then((list) => {
      const fromUrl = new URLSearchParams(window.location.search).get("doc");
      const preferred = list.find((item) => item.doc_id === fromUrl) || list[0];
      setActiveId((current) => current || (preferred ? preferred.doc_id : null));
    });
  }, [refreshDocuments]);

  useEffect(() => {
    if (!activeId) return;
    const url = new URL(window.location.href);
    url.searchParams.set("doc", activeId);
    window.history.replaceState(null, "", url);
  }, [activeId]);

  useEffect(() => {
    const timer = setInterval(async () => {
      try {
        await checkHealth();
        setServerUp(true);
      } catch {
        setServerUp(false);
      }
    }, 15000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const sessionId = activeId && sessions.current[activeId];
    if (!activeId || !sessionId || threads[activeId]) return;

    getHistory(sessionId)
      .then((history) => {
        const restored = history.map((item) => ({
          role: item.role === "human" ? "user" : "assistant",
          content: item.content,
        }));
        setThreads((current) => (current[activeId] ? current : { ...current, [activeId]: restored }));
      })
      .catch(() => {});
  }, [activeId, threads]);

  async function handleUpload(file) {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setUploadNote("Only PDF files are supported.");
      return;
    }

    setUploading(true);
    setUploadNote("");

    try {
      const result = await uploadDocument(file);
      await refreshDocuments();
      setActiveId(result.doc_id);
      setUploadNote(
        result.status === "already_indexed"
          ? "That file was already indexed, so the existing copy is open."
          : `Indexed ${result.pages} pages into ${result.chunks} passages.`,
      );
    } catch (error) {
      setUploadNote(`Upload failed: ${error.message}. Check that the local server is running, then try again.`);
    } finally {
      setUploading(false);
    }
  }

  async function ask(question) {
    if (!activeId || busy) return;

    const docId = activeId;
    lastQuestion.current = question;
    setBusy(true);
    setThreads((current) => ({
      ...current,
      [docId]: [...(current[docId] || []), { role: "user", content: question }],
    }));

    try {
      const result = await sendChat({ docId, question, sessionId: sessions.current[docId] });
      sessions.current[docId] = result.session_id;
      saveSessions(sessions.current);
      setThreads((current) => ({
        ...current,
        [docId]: [...(current[docId] || []), { role: "assistant", content: result.answer, sources: result.sources }],
      }));
    } catch (error) {
      setThreads((current) => ({
        ...current,
        [docId]: [
          ...(current[docId] || []),
          { role: "error", content: `${error.message}. Check that the local server is running, then try again.` },
        ],
      }));
    } finally {
      setBusy(false);
    }
  }

  function retry() {
    if (!activeId) return;
    setThreads((current) => ({
      ...current,
      [activeId]: (current[activeId] || []).filter((message, index, list) => !(message.role === "error" && index === list.length - 1)),
    }));
    ask(lastQuestion.current);
  }

  async function reset() {
    if (!activeId) return;
    const sessionId = sessions.current[activeId];

    if (sessionId) {
      try {
        await clearHistory(sessionId);
      } catch {
        // the local reset below still gives a clean thread
      }
      delete sessions.current[activeId];
      saveSessions(sessions.current);
    }

    setThreads((current) => ({ ...current, [activeId]: [] }));
  }

  const activeDocument = documents.find((document) => document.doc_id === activeId) || null;
  const messages = (activeId && threads[activeId]) || [];

  return (
    <div className="min-h-[100dvh] lg:grid lg:grid-cols-[320px_minmax(0,1fr)]">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-full focus:bg-emerald-700 focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-emerald-50"
      >
        Skip to Conversation
      </a>
      <Sidebar
        documents={documents}
        activeId={activeId}
        onSelect={setActiveId}
        onUpload={handleUpload}
        uploading={uploading}
        uploadNote={uploadNote}
        loading={loadingDocuments}
        serverUp={serverUp}
        theme={theme}
        onToggleTheme={toggle}
      />
      <main id="main" className="flex h-[100dvh] flex-col scroll-mt-4">
        <Chat
          document={activeDocument}
          messages={messages}
          busy={busy}
          onAsk={ask}
          onRetry={retry}
          onReset={reset}
        />
      </main>
    </div>
  );
}
