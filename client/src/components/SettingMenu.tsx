import { useState } from "react";
import { NoteData, cleanOutdatedNotes, loadLocalNotes } from "./note-manager";
import { CogIcon, ChevronRightIcon } from "@heroicons/react/24/outline";

type SettingMenuProps = {
  loadNoteToEditor: (id: string) => void;
  saveNoteToServer: () => void;
};

const SettingMenu = (props: SettingMenuProps) => {
  const buttonStyle =
    "w-full py-2 text-left text-sm font-semibold transition duration-300 hover:text-sky-500";
  const activeList =
    "text-md flex w-48 flex-col rounded-md border bg-white py-2 px-4 shadow-lg scale-100 max-h-96 overflow-hidden";

  const [isActive, setIsActive] = useState<boolean>(false);
  const [activeHistory, setActiveHistory] = useState<boolean>(false);
  const [noteList, setNoteList] = useState<NoteData[]>([]);

  const resetButtonStatus = () => {
    setIsActive(false);
    setActiveHistory(false);
  };

  const updateNoteList = () => {
    setNoteList(loadLocalNotes(true));
  };

  const noteListButtons = noteList.map((note) => {
    const timeStamp: string = new Date(note.date).toLocaleString();
    return (
      <button
        key={note.id}
        className="w-full pt-1 text-left text-xs transition duration-300 hover:text-sky-500"
        onClick={() => {
          props.loadNoteToEditor(note.id);
          resetButtonStatus();
        }}
      >
        {timeStamp}
        <span className="inline-flex w-full justify-between space-x-2">
          <p className="truncate text-gray-500">{note.id}</p>
          <p className="text-gray-500">{note.content.length}</p>
        </span>
      </button>
    );
  });

  return (
    <div className="relative inline-block">
      <div
        className={`transform transition-all duration-300 ${
          isActive
            ? "max-h-48 opacity-100"
            : "pointer-events-none max-h-0 opacity-0"
        } ${activeList} `}
      >
        <button
          className={`${buttonStyle} flex place-items-center justify-between`}
          onClick={() => {
            updateNoteList();
            setActiveHistory(!activeHistory);
          }}
        >
          <p>History</p>
          <ChevronRightIcon
            className={`size-4 text-gray-500 transition-all ${activeHistory && "rotate-90"} duration-300`}
          />
        </button>

        {
          <div
            className={`pointer-events-none mx-2 max-h-0 opacity-0 transition-all duration-300 ${activeHistory && "pointer-events-auto max-h-96 opacity-100"}`}
          >
            {noteListButtons}
          </div>
        }

        <button
          className={buttonStyle}
          onClick={() => {
            cleanOutdatedNotes();
            resetButtonStatus();
          }}
        >
          Clear
        </button>

        <button
          className={`${buttonStyle} text-red-500 hover:text-red-500`}
          onClick={() => {
            props.saveNoteToServer();
            resetButtonStatus();
          }}
        >
          Finish
        </button>

        <button className={buttonStyle} onClick={() => setIsActive(false)}>
          Cancel
        </button>
      </div>

      <div className="justify-self-end">
        <button
          className={`place-items-center rounded-full border p-1 shadow backdrop-blur transition-all duration-300 hover:text-sky-500 ${isActive ? "pointer-events-none rotate-90 scale-0 opacity-0" : "rotate-0 scale-100 opacity-100"} `}
          onClick={() => setIsActive(true)}
        >
          <CogIcon className="size-5" />
        </button>
      </div>
    </div>
  );
};

export default SettingMenu;
