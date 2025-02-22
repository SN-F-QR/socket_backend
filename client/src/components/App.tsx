import { useEffect } from "react";
import { initializeWebsocket, closeWebsocket } from "./client-websocket";

import Player from "./player";
import Note from "./note";

const App = () => {
  useEffect(() => {
    initializeWebsocket();
    return () => {
      closeWebsocket();
    };
  }, []);

  return (
    <div className="flex h-screen justify-evenly space-x-5 p-2">
      <Player />
      <Note />
    </div>
  );
};

export default App;
