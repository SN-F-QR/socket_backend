import { useEffect } from "react";
import { initializeWebsocket, closeWebsocket } from "./client-websocket";

import Player from "./player";

const App = () => {
  useEffect(() => {
    initializeWebsocket();
    return () => {
      closeWebsocket();
    };
  }, []);

  return (
    <div className="flex h-screen justify-center">
      <Player />
    </div>
  );
};

export default App;
