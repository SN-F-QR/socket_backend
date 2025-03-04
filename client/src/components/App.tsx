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
    <div className="flex h-screen overflow-y-auto p-2 max-md:flex-col md:justify-evenly md:space-x-5 md:overflow-clip">
      <Player />
      <div className="h-full flex-none md:w-1/2">
        <Note />
      </div>
    </div>
  );
};

export default App;
