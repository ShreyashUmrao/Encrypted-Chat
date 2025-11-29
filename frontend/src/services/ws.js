export function createWebSocket(chatId, token, handlers = {}) {
  const hostname = window.location.hostname || "localhost";
  const backendPort = 8000;

  const wsUrl = `ws://${hostname}:${backendPort}/chat/ws/${encodeURIComponent(chatId)}?token=${encodeURIComponent(token)}`;

  console.log("WS connecting to:", wsUrl);

  const ws = new WebSocket(wsUrl);

  ws.onopen = handlers.onOpen || (() => console.log("WS open"));
  ws.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      handlers.onMessage && handlers.onMessage(data);
    } catch (err) {
      console.error("WS JSON parse error:", err);
    }
  };
  ws.onerror = handlers.onError || ((e) => console.error("WS error", e));
  ws.onclose = handlers.onClose || (() => console.log("WS closed"));

  return ws;
}
