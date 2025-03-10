import { useEffect, useState } from "react";
import { EditorContent, Editor } from "@tiptap/react";
import shortUUID from "short-uuid";

import { NoteData } from "./note-manager";
import MenuBar from "./meun-bar";
import { TypeState } from "./useNoteEditor";
import { FloatHint } from "./FloatHint";
import SettingMenu from "./SettingMenu";
import { requestSaveNote } from "./client-websocket";

type NoteProps = {
  editor: Editor | null;
  typeState: React.RefObject<TypeState>;
  updateCount: number;
  recommending: boolean;
  setUpdateCount: React.Dispatch<React.SetStateAction<number>>;
  selectedRecommend: (editor: Editor) => Promise<void>;
  handleH1Toggle: () => void;
};

const Note = (props: NoteProps) => {
  const {
    editor,
    typeState,
    updateCount,
    recommending,
    setUpdateCount,
    selectedRecommend,
    handleH1Toggle,
  } = props;

  const [savedNote, setSavedNote] = useState<NoteData | undefined>({
    id: shortUUID.generate(),
    content: "",
    date: 0,
  });

  const saveNoteToLocal = () => {
    if (editor && savedNote && editor.getHTML().length > 10) {
      const updatedNote = {
        ...savedNote,
        content: editor.getHTML(),
        date: Date.now(),
      };
      setSavedNote(updatedNote);
      localStorage.setItem(
        "note-" + updatedNote.id,
        JSON.stringify(updatedNote),
      );
      console.log("Note Saved with Id: ", updatedNote.id);
      console.log("Note Content: ", updatedNote.content);
      console.log("Note Date: ", updatedNote.date);
    }
  };

  const saveNoteToServer = async () => {
    saveNoteToLocal();
    if (savedNote && editor) {
      try {
        const textNoteContent: string = editor.getText();
        const textNote: NoteData = {
          ...savedNote,
          content: textNoteContent,
        };
        requestSaveNote(textNote);
        console.log("Note Saved to Server with Id: ", savedNote.id);
      } catch (e) {
        console.error("Cannot save note since:", e);
      }
    }
  };

  // const {
  //   editor,
  //   typeState,
  //   updateCount,
  //   recommending,
  //   setUpdateCount,
  //   selectedRecommend,
  //   handleH1Toggle,
  // } = useNoteEditor();

  const autoSaveNote = () => {
    if (updateCount > 10) {
      saveNoteToLocal();
      setUpdateCount(0);
    }
  };

  useEffect(() => {
    autoSaveNote();
  }, [updateCount]);

  const loadNoteFromLocal = (id: string) => {
    // clean the current empty note
    if (savedNote && savedNote.content.length < 20) {
      localStorage.removeItem("note-" + savedNote.id);
    }

    const noteJson: string | null = localStorage.getItem("note-" + id);
    if (noteJson) {
      const note: NoteData = JSON.parse(noteJson);
      setSavedNote(note);
      if (editor) {
        editor.commands.setContent(note.content);
        editor.commands.focus();
      }
    }
  };

  return (
    <div className="relative h-full w-full overflow-y-scroll rounded-md border">
      <div className="sticky top-0 z-50 px-2 py-2">
        <MenuBar
          editor={editor as Editor}
          recommending={recommending}
          disableButton={typeState.current.typingNewH1}
          h1Toggle={handleH1Toggle}
          recommend={selectedRecommend}
        />
      </div>
      <div className="">
        <FloatHint
          editor={editor as Editor}
          recommending={recommending}
          selectedRecommend={selectedRecommend}
        />
        <EditorContent editor={editor} />
      </div>
      <div className="fixed bottom-4 right-6 z-50">
        <div className="relative">
          <div className="absolute bottom-4 right-4">
            <SettingMenu
              loadNoteToEditor={loadNoteFromLocal}
              saveNoteToServer={saveNoteToServer}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Note;
