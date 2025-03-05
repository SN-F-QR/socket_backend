import shortUUID from "short-uuid";
import { NoteData } from "./note-manager";

const WEBSOCKET_URL = "ws://localhost:12345";

export type Socket = {
  ws: WebSocket;
  id: string;
};

type ResponseMessage = VideoMessage | RecommendMessage[];

type RecommendTypes = "pre-defined" | "defined" | "serper";

export type RecommendMessage = Message & {
  type: RecommendTypes;
  target: string;
  value: string;
};

export type VideoMessage = Message & {
  type: "video";
  keywords: string[];
};

type EchoMessage = Message & {
  type: "echo";
  value: string;
};

type Message = {
  id: string;
  type: string;
};

const isValidRecommendType = (type: any): type is RecommendTypes => {
  return type === "pre-defined" || type === "defined" || type === "serper";
};

export let socket: Socket | undefined = undefined;

let waitingRecommend: boolean = false; // true after recommend, reject all other sending recommend requests if waiting
let responseResolve: Map<string, (value: ResponseMessage) => void> = new Map(); // id-resolve map for handling multiple requests
let timeouts: Map<string, number> = new Map(); // id-timeout map
let responseRecommends: Array<RecommendMessage> = []; // only used for the recommend request

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
    // console.log("Message from server ", event.data);
    const response: Message = JSON.parse(event.data);
    if (response.type === "echo") {
      const echoResponse: EchoMessage = response as EchoMessage;
      console.log("Echo response received: ", echoResponse.id);
    } else if (isValidRecommendType(response.type)) {
      const recommendResponse: RecommendMessage = response as RecommendMessage;
      responseRecommends.push(recommendResponse);
      if (responseRecommends.length === 3) {
        console.log("All recommend received");
        tryResolve(response.id, responseRecommends);
        resetRecStatus();
      }
    } else if (response.type === "video") {
      console.log("Video response received");
      const videoResponse: VideoMessage = response as VideoMessage;
      tryResolve(response.id, videoResponse);
    } else {
      console.warn("Unknown response message: ", event.data);
    }
  });

  socket.ws.addEventListener("error", (event: Event) => {
    console.log("WebSocket error: ", event);
  });
};

/**
 * Try to resolve the response message, if success, delete the resolve function and timeout
 * @param response message from server
 */
const tryResolve = (id: string, response: ResponseMessage) => {
  const resolve: ((value: ResponseMessage) => void) | undefined =
    responseResolve.get(id);
  if (resolve) {
    resolve(response);
    responseResolve.delete(id);
    clearTimeout(timeouts.get(id));
    timeouts.delete(id);
  } else {
    console.error("Failed to get resolve function for id: ", id);
  }
};

const resetRecStatus = () => {
  waitingRecommend = false;
  responseRecommends = [];
};

const sendMessage = (message: Message): Promise<ResponseMessage> => {
  const promise: Promise<ResponseMessage> = new Promise<ResponseMessage>(
    (resolve, reject) => {
      if (socket && socket.ws.readyState === WebSocket.OPEN) {
        message.id = shortUUID.generate();
        socket.ws.send(JSON.stringify(message));
        console.log(`Message ${message.id} sent, type: ${message.type}`);
        if (message.type === "recommend") {
          waitingRecommend = true;
        }
        if (message.type === "video" || message.type === "recommend") {
          const timeOutId: number = window.setTimeout(() => {
            reject(new Error("Timeout for message: " + message.id));
            if (message.type === "recommend") {
              resetRecStatus();
            }
            responseResolve.delete(message.id);
            timeouts.delete(message.id);
          }, 10 * 1000);
          timeouts.set(message.id, timeOutId);
          responseResolve.set(message.id, resolve);
        }
      } else {
        reject(new Error("Websocket is not connected or ready"));
      }
    },
  );

  return promise;
};

const sendVideoProgress = (progress: number): Promise<VideoMessage> => {
  if (waitingRecommend) {
    return Promise.reject(new Error("Already request for recommend"));
  }
  const message = {
    id: "",
    type: "video",
    value: progress,
  };
  return sendMessage(message) as Promise<VideoMessage>;
};

const requestRecommend = (note: string): Promise<RecommendMessage[]> => {
  if (waitingRecommend) {
    return Promise.reject(new Error("Already request for recommend"));
  }
  const message = {
    id: "",
    type: "recommend",
    value: note,
  };
  return sendMessage(message) as Promise<RecommendMessage[]>;
};

const requestSaveNote = (note: NoteData) => {
  const message = {
    id: "",
    type: "save",
    value: note,
  };

  sendMessage(message);
};

const isWaiting = () => waitingRecommend;

const closeWebsocket = () => {
  if (
    socket &&
    (socket.ws.readyState === WebSocket.OPEN || WebSocket.CONNECTING)
  ) {
    responseResolve.clear();
    timeouts.forEach((timeout) => {
      clearTimeout(timeout);
    });
    timeouts.clear();
    resetRecStatus();
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
