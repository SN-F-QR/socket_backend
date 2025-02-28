import { EditorContent, Editor } from "@tiptap/react";

import MenuBar from "./meun-bar";
import { useNoteEditor } from "./useNoteEditor";

const Note = () => {
  const { editor, typeState, extractText, handleH1Toggle } = useNoteEditor();

  return (
    <div className="relative w-full overflow-y-scroll rounded-md border">
      <div className="sticky top-0 z-50 px-2 py-2">
        <MenuBar
          editor={editor as Editor}
          disableButton={typeState.current.typingNewH1}
          h1Toggle={handleH1Toggle}
          recommend={extractText}
        />
      </div>
      <div className="">
        <EditorContent editor={editor} />
      </div>
    </div>
  );
};

export default Note;
