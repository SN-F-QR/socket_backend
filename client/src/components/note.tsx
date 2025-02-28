import { EditorContent, Editor } from "@tiptap/react";

import MenuBar from "./meun-bar";
import { useNoteEditor } from "./useNoteEditor";
import { FloatHint } from "./FloatHint";

const Note = () => {
  const { editor, typeState, selectedRecommend, handleH1Toggle } =
    useNoteEditor();

  return (
    <div className="relative w-full overflow-y-scroll rounded-md border">
      <div className="sticky top-0 z-50 px-2 py-2">
        <MenuBar
          editor={editor as Editor}
          disableButton={typeState.current.typingNewH1}
          h1Toggle={handleH1Toggle}
          recommend={selectedRecommend}
        />
      </div>
      <div className="">
        <FloatHint
          editor={editor as Editor}
          selectedRecommend={selectedRecommend}
        />
        <EditorContent editor={editor} />
      </div>
    </div>
  );
};

export default Note;
