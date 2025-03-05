import { useEffect } from "react";
import { initializeWebsocket, closeWebsocket } from "./client-websocket";
import { useNoteEditor } from "./useNoteEditor";

import Player from "./player";
import Note from "./note";

const App = () => {
  useEffect(() => {
    initializeWebsocket();
    return () => {
      closeWebsocket();
    };
  }, []);

  const {
    editor,
    typeState,
    updateCount,
    recommending,
    setUpdateCount,
    selectedRecommend,
    handleH1Toggle,
  } = useNoteEditor();

  return (
    <div className="flex h-screen overflow-y-auto p-2 max-md:flex-col md:justify-evenly md:space-x-5 md:overflow-clip">
      <Player />
      <div className="h-full flex-none md:w-1/2">
        <Note
          editor={editor}
          typeState={typeState}
          updateCount={updateCount}
          recommending={recommending}
          setUpdateCount={setUpdateCount}
          selectedRecommend={selectedRecommend}
          handleH1Toggle={handleH1Toggle}
        />
      </div>
    </div>
  );
};

export default App;
