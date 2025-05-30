import { useEffect, useState } from "react";
import { initializeWebsocket, closeWebsocket } from "./client-websocket";
import { useNoteEditor } from "./useNoteEditor";

import PdfReader from "./PdfReader";
import Player from "./player";
import Note from "./note";
import SwitchButtons from "./SwitchButtons";
import StudySelection from "./StudySelection";
import NetworkError from "./NetworkError";

import { materials, Material } from "./material-manager";

type NetworkError = {
  errorId: string;
  showError: boolean;
};

const App = () => {
  useEffect(() => {
    initializeWebsocket();

    return () => {
      closeWebsocket();
    };
  }, []);

  const [material, setMaterial] = useState<Material | undefined>(undefined);
  const [showPdf, setShowPdf] = useState<boolean>(true);
  const [error, setError] = useState<NetworkError>({
    errorId: "",
    showError: false,
  });

  const handleNetworkError = (errorId: string) => {
    setError({ errorId, showError: true });
  };

  const closeError = () => {
    setError((prev) => ({ ...prev, showError: false }));
  };

  const applyMaterial = (material: Material) => {
    setMaterial(material);
  };

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
  } = useNoteEditor(handleNetworkError);

  useEffect(() => {
    if (editor && material) {
      editor.commands.setContent(
        `<h1>A trip plan from Tokyo to ${material?.city}</h1><p>June 9 - June 15</p><p>Hotel budget: 20000JPY - 30000JPY</p><p></p>`,
      );
    }
  }, [material]);

  return (
    <div className="relative flex h-screen overflow-y-auto p-2 max-md:flex-col max-md:space-y-2 md:justify-evenly md:space-x-3 md:overflow-clip">
      {material && (
        <>
          <div className="relative h-full flex-1 overflow-y-auto">
            <div className={`${!showPdf ? "h-full" : "hidden"}`}>
              <Player
                editor={editor}
                videoPath={material.video}
                subtitlePath={material.transcript}
                handleNetworkError={handleNetworkError}
              />
            </div>
            <div className={`${showPdf ? "h-full" : "hidden"}`}>
              <PdfReader
                path={material.pdf}
                handleNetworkError={handleNetworkError}
              />
            </div>
          </div>
          <div className="absolute left-1 top-4 z-30">
            <SwitchButtons activeFirst={showPdf} switchActive={switchActive} />
          </div>
        </>
      )}
      {!material && (
        <div className="h-full flex-1">
          <StudySelection materials={materials} setMaterial={applyMaterial} />
        </div>
      )}
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
      {error.showError && (
        <NetworkError messageId={error.errorId} onClose={closeError} />
      )}
    </div>
  );
};

export default App;
