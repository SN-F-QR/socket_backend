import shortUUID from "short-uuid";
import { NoteData } from "./note-manager";

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

type EchoMessage = {
  echo: string;
};

type SendOutMessage = {
  type: string;
};

export let socket: Socket | undefined = undefined;

let waitingStatus: boolean = false; // true after recommend, reject all other sending requests if waiting
let responsePromise:
  | Promise<ResponseMessage[]>
  | Promise<EchoMessage>
  | undefined = undefined;
let responseResolve: (value: ResponseMessage[]) => void = () => {}; // change state of promise, and return the value for await
let echoResolve: (value: EchoMessage) => void = () => {};
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
    if (waitingStatus) {
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
    } else {
      const response: EchoMessage = JSON.parse(event.data);
      if (response.echo) echoResolve(response);
      echoResolve = () => {};
      responsePromise = undefined;
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

const sendMessage = (
  message: SendOutMessage,
): Promise<ResponseMessage[]> | Promise<EchoMessage> => {
  if (waitingStatus && responsePromise) {
    return responsePromise;
  }

  if (message.type === "recommend") {
    responsePromise = new Promise<ResponseMessage[]>((resolve, reject) => {
      if (socket && socket.ws.readyState === WebSocket.OPEN) {
        socket.ws.send(JSON.stringify(message));
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
  } else {
    responsePromise = new Promise<EchoMessage>((resolve, reject) => {
      if (socket && socket.ws.readyState === WebSocket.OPEN) {
        socket.ws.send(JSON.stringify(message));
        echoResolve = resolve;
      } else {
        reject(new Error("Websocket is not connected or ready"));
      }
    });
  }

  return responsePromise;
};

const sendVideoProgress = (progress: number) => {
  const message = {
    type: "time",
    value: progress,
  };
  sendMessage(message);
};

const requestRecommend = (note: string): Promise<ResponseMessage[]> => {
  const message = {
    type: "recommend",
    value: note,
  };
  return sendMessage(message) as Promise<ResponseMessage[]>;
};

const requestSaveNote = (note: NoteData): Promise<EchoMessage> => {
  const message = {
    type: "save",
    ...note,
  };
  return sendMessage(message) as Promise<EchoMessage>;
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
  requestSaveNote,
  requestRecommend,
  closeWebsocket,
};
