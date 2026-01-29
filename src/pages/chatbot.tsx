import { useState, useEffect, useRef } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  Send,
  Copy,
  Check,
  Plus,
  Trash2,
  MessageSquare,
  Menu,
  X,
  AlertTriangle,
  CheckCircle2,
  Info,
  LogOut,
} from "lucide-react";

type MessageType = "default" | "success" | "alert";

interface User {
  name: string;
  email: string;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: Date;
  type?: MessageType;
}

interface Session {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
}

const formatTime = (date: Date | string): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });
};

const detectMessageType = (content: string): MessageType => {
  const lowerContent = content.toLowerCase();
  if (
    lowerContent.includes("alert") ||
    lowerContent.includes("warning") ||
    lowerContent.includes("attention") ||
    lowerContent.includes("urgent") ||
    lowerContent.includes("issue") ||
    lowerContent.includes("error") ||
    lowerContent.includes("❌")
  ) {
    return "alert";
  }
  if (
    lowerContent.includes("success") ||
    lowerContent.includes("confirmed") ||
    lowerContent.includes("completed") ||
    lowerContent.includes("done") ||
    lowerContent.includes("approved") ||
    lowerContent.includes("✅")
  ) {
    return "success";
  }
  return "default";
};

const getMessageStyles = (type: MessageType) => {
  switch (type) {
    case "success":
      return {
        border: "border-green-200",
        bg: "bg-green-50",
        icon: CheckCircle2,
        iconColor: "text-green-500",
        accentBar: "bg-green-500",
      };
    case "alert":
      return {
        border: "border-red-200",
        bg: "bg-red-50",
        icon: AlertTriangle,
        iconColor: "text-red-500",
        accentBar: "bg-red-500",
      };
    default:
      return {
        border: "border-blue-200",
        bg: "bg-blue-50",
        icon: Info,
        iconColor: "text-blue-500",
        accentBar: "bg-blue-500",
      };
  }
};

const generateId = () => Math.random().toString(36).substring(2, 15);

export default function ChatBot() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [sessions, setSessions] = useState<Session[]>(() => {
    const saved = localStorage.getItem("chatbot_sessions");
    return saved ? JSON.parse(saved) : [];
  });

  const [activeSessionId, setActiveSessionId] = useState<string | null>(() => {
    const saved = localStorage.getItem("chatbot_active_session");
    return saved;
  });

  const [isProcessing, setIsProcessing] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const chatAreaRef = useRef<HTMLDivElement>(null);

  const activeSession = sessions.find((s) => s.id === activeSessionId);

  // Check authentication on mount
  useEffect(() => {
    checkAuth();
  }, []);

  // Save sessions to localStorage
  useEffect(() => {
    localStorage.setItem("chatbot_sessions", JSON.stringify(sessions));
  }, [sessions]);

  // Save active session ID
  useEffect(() => {
    if (activeSessionId) {
      localStorage.setItem("chatbot_active_session", activeSessionId);
    }
  }, [activeSessionId]);

  // Scroll to bottom
  useEffect(() => {
    if (chatAreaRef.current) {
      chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
    }
  }, [activeSession?.messages]);

  const checkAuth = async () => {
    try {
      // Get from URL params
      const paramUser = searchParams.get("user");
      const paramEmail = searchParams.get("email");
      const paramSession = searchParams.get("session");

      if (paramUser && paramEmail && paramSession) {
        setUser({ name: paramUser, email: paramEmail });
        setSessionId(paramSession);
        setIsAuthenticated(true);
        sessionStorage.setItem("user_session", paramSession);
        // Clean URL
        window.history.replaceState({}, document.title, "/chatbot");
        createNewSession();
        return;
      }

      // Try to get from session storage
      const storedSessionId = sessionStorage.getItem("user_session");
      if (storedSessionId) {
        try {
          const response = await fetch(`/api/auth/session/${storedSessionId}`);
          if (response.ok) {
            const data = await response.json();
            setUser(data.user);
            setSessionId(storedSessionId);
            setIsAuthenticated(true);
            return;
          }
        } catch (err) {
          console.error("Session check failed:", err);
        }
      }

      // Not authenticated
      setIsAuthenticated(false);
    } catch (err) {
      console.error("Auth check error:", err);
      setIsAuthenticated(false);
    }
  };

  const handleMicrosoftSignIn = () => {
    window.location.href = "/api/auth/microsoft";
  };

  const handleSignOut = async () => {
    try {
      if (sessionId) {
        await fetch(`/api/auth/logout/${sessionId}`, { method: "POST" });
        sessionStorage.removeItem("user_session");
      }
      setIsAuthenticated(false);
      setUser(null);
      setSessionId(null);
      setSessions([]);
      setActiveSessionId(null);
      navigate("/chatbot");
    } catch (err) {
      console.error("Sign out error:", err);
    }
  };

  const createNewSession = () => {
    const newSession: Session = {
      id: generateId(),
      title: "New Chat",
      messages: [],
      createdAt: new Date(),
    };
    setSessions([newSession, ...sessions]);
    setActiveSessionId(newSession.id);
  };

  const deleteSession = (sessionId: string) => {
    setSessions(sessions.filter((s) => s.id !== sessionId));
    if (activeSessionId === sessionId) {
      const remainingSessions = sessions.filter((s) => s.id !== sessionId);
      setActiveSessionId(remainingSessions.length > 0 ? remainingSessions[0].id : null);
    }
  };

  const updateSessionTitle = (sessionId: string, newTitle: string) => {
    setSessions(
      sessions.map((s) =>
        s.id === sessionId ? { ...s, title: newTitle } : s
      )
    );
  };

  const sendMessage = async () => {
    if (isProcessing || !activeSession) return;

    const inputElement = document.getElementById("question") as HTMLInputElement;
    if (!inputElement) return;

    const question = inputElement.value.trim();
    if (!question) return;

    // Create user message
    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content: question,
      createdAt: new Date(),
      type: "default",
    };

    // Update session with user message
    setSessions(
      sessions.map((s) =>
        s.id === activeSessionId
          ? { ...s, messages: [...s.messages, userMessage] }
          : s
      )
    );

    // Update title if it's the first message
    if (activeSession.messages.length === 0) {
      const title = question.substring(0, 50) + (question.length > 50 ? "..." : "");
      updateSessionTitle(activeSessionId!, title);
    }

    inputElement.value = "";
    setIsProcessing(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: question,
          history: activeSession.messages.map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const botMessage: Message = {
        id: generateId(),
        role: "assistant",
        content: data.response || "No response received",
        createdAt: new Date(),
        type: detectMessageType(data.response || ""),
      };

      // Update session with bot message
      setSessions(
        sessions.map((s) =>
          s.id === activeSessionId
            ? { ...s, messages: [...s.messages, botMessage] }
            : s
        )
      );
    } catch (err) {
      console.error("Chat error:", err);

      const errorMessage: Message = {
        id: generateId(),
        role: "assistant",
        content: `❌ Error: Unable to connect to chat service. Please check if the backend is running.`,
        createdAt: new Date(),
        type: "alert",
      };

      setSessions(
        sessions.map((s) =>
          s.id === activeSessionId
            ? { ...s, messages: [...s.messages, errorMessage] }
            : s
        )
      );
    } finally {
      setIsProcessing(false);
      inputElement.focus();
    }
  };

  const askQuickQuestion = (question: string) => {
    const inputElement = document.getElementById("question") as HTMLInputElement;
    if (inputElement) {
      inputElement.value = question;
      setTimeout(() => sendMessage(), 100);
    }
  };

  const handleCopy = (messageId: string, content: string) => {
    navigator.clipboard.writeText(content);
    setCopiedId(messageId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  if (!isAuthenticated || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-600 to-indigo-600 p-4">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-2xl shadow-2xl p-8 space-y-6">
            <div className="text-center space-y-2">
              <h1 className="text-3xl font-bold text-gray-800">🚗 Fleet AI</h1>
              <p className="text-gray-600">Sign in to continue</p>
            </div>

            <button
              onClick={handleMicrosoftSignIn}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold py-3 rounded-lg hover:shadow-lg transition-all"
            >
              Sign in with Microsoft
            </button>

            <p className="text-xs text-gray-500 text-center">
              You will be asked to sign in with your Microsoft account
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100 overflow-hidden">
      {/* Sidebar */}
      <div
        className={`${
          isSidebarOpen ? "w-64" : "w-0"
        } transition-all duration-300 bg-gradient-to-b from-gray-900 to-gray-800 text-white flex flex-col overflow-hidden shadow-xl`}
      >
        {/* New Chat Button */}
        <button
          onClick={createNewSession}
          className="m-4 flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-4 py-2 rounded-lg hover:shadow-lg transition-all font-semibold"
        >
          <Plus size={18} />
          New Chat
        </button>

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto space-y-2 px-2 py-4">
          {sessions.map((session) => (
            <div
              key={session.id}
              className={`group relative p-3 rounded-lg cursor-pointer transition-all ${
                activeSessionId === session.id
                  ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white"
                  : "hover:bg-gray-700 text-gray-300"
              }`}
              onClick={() => setActiveSessionId(session.id)}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <MessageSquare size={14} className="flex-shrink-0" />
                    <p className="text-sm font-medium truncate">{session.title}</p>
                  </div>
                  <p className="text-xs opacity-70 mt-1">
                    {session.messages.length} messages
                  </p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteSession(session.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-gray-600 rounded"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* User Info */}
        <div className="border-t border-gray-700 p-4 space-y-3">
          <div className="bg-gray-700 rounded-lg p-3 text-sm">
            <p className="font-semibold text-white truncate">{user.name}</p>
            <p className="text-xs text-gray-400 truncate">{user.email}</p>
          </div>
          <button
            onClick={handleSignOut}
            className="w-full flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-lg transition-all font-semibold text-sm"
          >
            <LogOut size={16} />
            Sign Out
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-4 flex items-center justify-between shadow-sm">
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
          <h1 className="text-2xl font-bold text-gray-800">Fleet AI Assistant</h1>
          <div className="w-10"></div>
        </div>

        {/* Chat Area */}
        <div
          ref={chatAreaRef}
          className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50"
        >
          {!activeSession?.messages || activeSession.messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <MessageSquare size={48} className="text-gray-400 mb-4" />
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                Welcome to Fleet AI
              </h2>
              <p className="text-gray-600 mb-6">
                Ask questions about your vehicle fleet, drivers, maintenance, and costs
              </p>

              <div className="w-full max-w-md space-y-2">
                <p className="text-sm font-semibold text-gray-700 mb-3">
                  Quick Questions:
                </p>
                <button
                  onClick={() =>
                    askQuickQuestion("How many vehicles are there in total?")
                  }
                  className="w-full text-left bg-white border border-gray-200 p-3 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all text-sm"
                >
                  📊 Total Vehicles
                </button>
                <button
                  onClick={() =>
                    askQuickQuestion("How many allocated vehicles?")
                  }
                  className="w-full text-left bg-white border border-gray-200 p-3 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all text-sm"
                >
                  🚐 Allocated Count
                </button>
                <button
                  onClick={() =>
                    askQuickQuestion("Show me spare vehicles")
                  }
                  className="w-full text-left bg-white border border-gray-200 p-3 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all text-sm"
                >
                  ⭐ Spare Vehicles
                </button>
                <button
                  onClick={() => askQuickQuestion("List all drivers")}
                  className="w-full text-left bg-white border border-gray-200 p-3 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all text-sm"
                >
                  👥 All Drivers
                </button>
                <button
                  onClick={() =>
                    askQuickQuestion("What vehicles need maintenance?")
                  }
                  className="w-full text-left bg-white border border-gray-200 p-3 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all text-sm"
                >
                  🔧 Maintenance Due
                </button>
              </div>
            </div>
          ) : (
            activeSession.messages.map((message) => {
              const messageType =
                message.role === "assistant"
                  ? message.type || detectMessageType(message.content)
                  : "default";
              const styles =
                message.role === "assistant" ? getMessageStyles(messageType) : null;
              const IconComponent = styles?.icon;

              return (
                <div
                  key={message.id}
                  className={`flex ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`group relative max-w-[85%] md:max-w-[75%] rounded-2xl shadow-sm overflow-hidden ${
                      message.role === "user"
                        ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-4 py-3"
                        : `${styles?.bg} border ${styles?.border} text-gray-800`
                    }`}
                  >
                    {/* Accent bar for bot messages */}
                    {message.role === "assistant" && (
                      <div
                        className={`absolute left-0 top-0 bottom-0 w-1 ${styles?.accentBar}`}
                      />
                    )}

                    <div
                      className={message.role === "assistant" ? "pl-4 pr-4 py-3" : ""}
                    >
                      {/* Icon for bot messages */}
                      {message.role === "assistant" && IconComponent && (
                        <div className="flex items-center gap-2 mb-1">
                          <IconComponent
                            className={`w-4 h-4 ${styles?.iconColor}`}
                          />
                          <span
                            className={`text-xs font-semibold uppercase tracking-wide ${styles?.iconColor}`}
                          >
                            {messageType === "success"
                              ? "Confirmed"
                              : messageType === "alert"
                              ? "Alert"
                              : "Info"}
                          </span>
                        </div>
                      )}

                      <p className="whitespace-pre-wrap break-words leading-relaxed">
                        {message.content}
                      </p>

                      <div
                        className={`flex items-center gap-2 mt-2 text-xs ${
                          message.role === "user"
                            ? "text-blue-100"
                            : "text-gray-400"
                        }`}
                      >
                        <span>{formatTime(message.createdAt)}</span>
                        {message.role === "assistant" && (
                          <button
                            onClick={() =>
                              handleCopy(message.id, message.content)
                            }
                            className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-lg hover:bg-gray-200"
                            title="Copy message"
                          >
                            {copiedId === message.id ? (
                              <Check className="w-3.5 h-3.5 text-green-500" />
                            ) : (
                              <Copy className="w-3.5 h-3.5" />
                            )}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}

          {isProcessing && (
            <div className="flex justify-start">
              <div className="bg-blue-50 border border-blue-200 rounded-2xl px-4 py-3">
                <div className="flex gap-1">
                  <div
                    className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                    style={{ animationDelay: "0s" }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                    style={{ animationDelay: "0.4s" }}
                  ></div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 p-4 shadow-md">
          <div className="flex gap-3">
            <input
              id="question"
              type="text"
              placeholder="Ask about vehicles, drivers, maintenance..."
              onKeyPress={(e) => {
                if (e.key === "Enter" && !isProcessing) {
                  sendMessage();
                }
              }}
              disabled={!activeSession}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <button
              onClick={sendMessage}
              disabled={isProcessing || !activeSession}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-lg hover:shadow-lg transition-all disabled:opacity-60 disabled:cursor-not-allowed font-semibold flex items-center gap-2"
            >
              <Send size={18} />
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
