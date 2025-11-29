import { useEffect, useRef, useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import api from "../services/api";
import { createWebSocket } from "../services/ws";
import { encryptMessage, decryptMessage } from "../services/crypto";

export default function Chat({ chatId, onBack }) {

  const { token } = useContext(AuthContext);

  const [symmetricKey, setSymmetricKey] = useState(null);
  const [filterEnabled, setFilterEnabled] = useState(false);
  const [currentUserId, setCurrentUserId] = useState(null);

  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);

  const wsRef = useRef(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (!token) return;
    try {
      const [, payload] = token.split(".");
      const decoded = JSON.parse(atob(payload));
      setCurrentUserId(Number(decoded.uid));
    } catch (e) {
      console.error("JWT decode error:", e);
    }
  }, [token]);

  const loadHistory = async (key) => {
    try {
      const resp = await api.get(`/chat/${chatId}/history`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      setFilterEnabled(resp.data.filter_enabled);

      const decrypted = resp.data.messages.map((m) => {
        let text = m.text;

        if (m.ciphertext) {
          try {
            text = decryptMessage(key, m.ciphertext);
          } catch {
            text = "[decrypt_error]";
          }
        }

        return {
          id: m.id,
          fromUser: m.from,
          fromUserId: m.sender_id ?? null,
          text,
          timestamp: m.timestamp,
        };
      });

      setChat(decrypted);
    } catch (e) {
      console.error("History load error:", e);
    }
  };

  useEffect(() => {
    if (!token) return;

    const init = async () => {
      try {
        setChat([]);

        const res = await api.get(`/chat/${chatId}/key`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        const key = res.data.symmetric_key;
        setSymmetricKey(key);
        setFilterEnabled(res.data.user_filter);

        await loadHistory(key);
      } catch (e) {
        console.error("Init error:", e);
      }
    };

    init();
  }, [token, chatId]);

  useEffect(() => {
    if (symmetricKey) {
      loadHistory(symmetricKey);
    }
  }, [filterEnabled]);

  useEffect(() => {
    if (!token || !symmetricKey) return;

    const ws = createWebSocket(chatId, token, {
      onOpen: () => console.log("WS connected:", chatId),

      onMessage: (payload) => {
        if (!payload || typeof payload !== "object") return;

        if (payload.type === "message") {
          let text = "[decrypt_error]";
          try {
            text = decryptMessage(symmetricKey, payload.ciphertext);
          } catch {}

          setChat((prev) => [
            ...prev,
            {
              id: payload.id,
              fromUserId: payload.from_user_id,
              fromUser: payload.from_username,
              text,
              timestamp: payload.timestamp,
            },
          ]);
        }

        if (payload.type === "message_hidden") {
          setChat((prev) => [
            ...prev,
            { id: payload.id, fromUserId: null, text: payload.note },
          ]);
        }
      },

      onClose: () => console.log("WS closed:", chatId),
      onError: (e) => console.error("WS error:", e),
    });

    wsRef.current = ws;

    return () => {
      try {
        ws.close();
      } catch {}
      wsRef.current = null;
    };
  }, [token, symmetricKey, chatId, filterEnabled]);

  useEffect(() => {
    if (scrollRef.current)
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [chat]);

  const handleSend = () => {
    if (!message.trim()) return;
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      alert("Socket not connected");
      return;
    }

    wsRef.current.send(
      JSON.stringify({ ciphertext: encryptMessage(symmetricKey, message) })
    );
    setMessage("");
  };

  const toggleFilter = async () => {
    try {
      const resp = await api.post(
        `/chat/${chatId}/filter`,
        null,
        {
          params: { enabled: !filterEnabled },
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setFilterEnabled(resp.data.filter_enabled);
    } catch (e) {
      console.error("Filter toggle error:", e);
    }
  };

  return (
    <div className="h-screen bg-gray-900 text-white flex flex-col">

      <div className="p-4 bg-gray-800 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="px-2 py-1 bg-gray-700 rounded hover:bg-gray-600"
          >
            ← Back
          </button>

          <h1 className="text-xl">Chat Room: {chatId}</h1>
        </div>

        <div className="flex gap-3">
          <button
            onClick={toggleFilter}
            className={`px-3 py-1 rounded ${
              filterEnabled ? "bg-green-600" : "bg-gray-700"
            }`}
          >
            Filter: {filterEnabled ? "ON" : "OFF"}
          </button>
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 chat-scroll">
        {chat.map((m, i) => {
          const isMe = m.fromUserId === currentUserId;
          return (
            <div key={i} className={`flex items-end ${isMe ? 'justify-end' : 'justify-start'}`}>
              {!isMe && (
                <div className="mr-3">
                  <div className="avatar-initials">Ø</div>
                </div>
              )}

              <div className={`px-4 py-2 rounded-lg max-w-[75%] ${isMe ? 'bg-gradient-to-br from-blue-600 to-blue-500 text-white ml-4 text-right' : 'bg-gray-800 text-gray-100 mr-4'} msg-shadow`}>
                {!isMe && (
                  <div className="text-sm text-gray-300 mb-1">
                  </div>
                )}

                <div className="whitespace-pre-wrap break-words">{m.text}</div>

                {m.timestamp && (
                  <div className="text-xs text-gray-400 mt-2">
                    {new Date(m.timestamp).toLocaleTimeString()}
                  </div>
                )}
              </div>

              {isMe && (
                <div className="ml-3">
                  <div className="avatar-initials">⊕</div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="p-4 flex gap-2 bg-gray-800">
        <input
          className="flex-1 p-2 bg-gray-700 rounded"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type a message..."
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />

        <button
          onClick={handleSend}
          className="bg-blue-600 px-4 py-2 rounded hover:bg-blue-700"
        >
          Send
        </button>
      </div>
    </div>
  );
}
