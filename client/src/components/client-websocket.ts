const WEBSOCKET_URL = "ws://localhost:12345";

export type Socket = {
  ws: WebSocket;
  id: string;
};

export let socket: Socket | undefined = undefined;

const initializeWebsocket = () => {
  if (socket === undefined) {
    try {
      socket = { ws: new WebSocket(WEBSOCKET_URL), id: crypto.randomUUID() };
      console.log(`Websocket initialized with id: ${socket.id}`);
    } catch (error) {
      console.log("Error while initializing websocket: ", error);
      socket = undefined;
      return;
    }
  } else {
    return;
  }

  socket.ws.onopen = () => {
    console.log(`Websocket connected to ${WEBSOCKET_URL}`);
    sendMessage(`{"type": "video", "id": "${socket!.id}"}`);
  };

  socket.ws.onclose = () => {
    console.log(`Websocket disconnected to ${WEBSOCKET_URL}`);
  };

  socket.ws.addEventListener("message", (event: MessageEvent) => {
    console.log("Message from server ", event.data);
  });

  socket.ws.addEventListener("error", (event: Event) => {
    console.log("WebSocket error: ", event);
  });
};

const sendMessage = (message: string) => {
  if (socket && socket.ws.readyState === WebSocket.OPEN) {
    socket.ws.send(message);
  } else {
    console.log("Socket is not initialized or not connected");
  }
};

const sendVideoProgress = (progress: number) => {
  sendMessage(`{"type": "video", "progress": ${progress}}`);
};

const closeWebsocket = () => {
  if (
    socket &&
    (socket.ws.readyState === WebSocket.OPEN || WebSocket.CONNECTING)
  ) {
    socket.ws.close();
  }
  socket = undefined;
};

export { initializeWebsocket, sendMessage, sendVideoProgress, closeWebsocket };
