import shortUUID from "short-uuid";

const WEBSOCKET_URL = "ws://localhost:12345";

export type Socket = {
  ws: WebSocket;
  id: string;
};

type ResponseMessage = {
  type: string;
  target: string;
  value: string;
};

export let socket: Socket | undefined = undefined;

let waitingStatus: boolean = false;
let responsePromise: Promise<ResponseMessage[]> | undefined = undefined;
let responseResolve: (value: ResponseMessage[]) => void = () => {}; // change state of promise, and return the value for await
let timeoutId: number;
let responseMessages: Array<ResponseMessage> = [];

const initializeWebsocket = () => {
  if (socket === undefined) {
    try {
      socket = { ws: new WebSocket(WEBSOCKET_URL), id: shortUUID.generate() };
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
    // sendMessage(`{"type": "id", "id": "${socket!.id}"}`);
  };

  socket.ws.onclose = () => {
    console.log(`Websocket disconnected to ${WEBSOCKET_URL}`);
  };

  socket.ws.addEventListener("message", (event: MessageEvent) => {
    console.log("Message from server ", event.data);
    const response: ResponseMessage = JSON.parse(event.data);
    if (
      response.type &&
      (response.type === "pre-defined" || "defined" || "serper")
    ) {
      responseMessages.push(response);
    }

    if (responseMessages.length === 3) {
      console.log("All response received");
      responseResolve(responseMessages);
      clearTimeout(timeoutId);
      resetStatus();
    }
  });

  socket.ws.addEventListener("error", (event: Event) => {
    console.log("WebSocket error: ", event);
  });
};

const resetStatus = () => {
  waitingStatus = false;
  responsePromise = undefined;
  responseResolve = () => {};
  responseMessages = [];
};

const sendMessage = (message: string): Promise<ResponseMessage[]> => {
  if (waitingStatus && responsePromise) {
    return responsePromise;
  }

  responsePromise = new Promise<ResponseMessage[]>((resolve, reject) => {
    if (socket && socket.ws.readyState === WebSocket.OPEN) {
      socket.ws.send(message);
      waitingStatus = true;
      responseResolve = resolve;

      timeoutId = window.setTimeout(() => {
        reject(new Error("Timeout"));
        resetStatus();
      }, 10000);
    } else {
      reject(new Error("Websocket is not connected or ready"));
    }
  });

  return responsePromise;
};

const sendVideoProgress = (progress: number) => {
  const message = {
    type: "time",
    value: progress,
  };
  sendMessage(JSON.stringify(message));
};

const requestRecommend = (note: string): Promise<ResponseMessage[]> => {
  const message = {
    type: "recommend",
    value: note,
  };
  return sendMessage(JSON.stringify(message));
};

const isWaiting = () => waitingStatus;

const closeWebsocket = () => {
  if (
    socket &&
    (socket.ws.readyState === WebSocket.OPEN || WebSocket.CONNECTING)
  ) {
    waitingStatus = false;
    responsePromise = undefined;
    responseResolve = () => {};
    socket.ws.close();
  }
  socket = undefined;
};

export {
  initializeWebsocket,
  sendMessage,
  sendVideoProgress,
  requestRecommend,
  closeWebsocket,
};
