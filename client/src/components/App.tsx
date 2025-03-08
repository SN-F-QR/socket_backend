import { useEffect, useState } from "react";
import { initializeWebsocket, closeWebsocket } from "./client-websocket";
import { useNoteEditor } from "./useNoteEditor";

import PdfReader from "./PdfReader";
import Player from "./player";
import Note from "./note";
import SwitchButtons from "./SwitchButtons";

const App = () => {
  useEffect(() => {
    initializeWebsocket();
    return () => {
      closeWebsocket();
    };
  }, []);

  const [showPdf, setShowPdf] = useState<boolean>(true);

  const switchActive = () => {
    setShowPdf((prev) => !prev);
  };

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
    <div className="flex h-screen overflow-y-auto p-2 max-md:flex-col max-md:space-y-2 md:justify-evenly md:space-x-3 md:overflow-clip">
      <>
        <div className="relative h-full flex-1 overflow-y-auto">
          <div className={`${!showPdf ? "h-full" : "hidden"}`}>
            <Player editor={editor} />
          </div>
          <div className={`${showPdf ? "h-full" : "hidden"}`}>
            <PdfReader />
          </div>
        </div>
        <div className="absolute left-1 top-4 z-30">
          <SwitchButtons activeFirst={showPdf} switchActive={switchActive} />
        </div>
      </>
      <div className="h-full flex-1">
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
