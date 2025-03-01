import { Editor, FloatingMenu } from "@tiptap/react";
import { EditorState } from "@tiptap/pm/state";
import { EditorView } from "@tiptap/pm/view";

import { ArrowPathIcon } from "@heroicons/react/24/outline";

type FloatHintProps = {
  editor: Editor;
  recommending: boolean;
  selectedRecommend: (editor: Editor) => void;
};

export const FloatHint = (props: FloatHintProps) => {
  const whenShouldHintShow = ({
    state,
  }: {
    editor: Editor;
    view: EditorView;
    state: EditorState;
    oldState?: EditorState | undefined;
  }) => {
    return (
      state.selection.$anchor.parent.type.name === "heading" &&
      state.selection.$anchor.parent.firstChild?.marks !== undefined &&
      state.selection.$anchor.parent.firstChild.marks.length > 0
    );
  };

  const whenShouldRecShow = ({
    view,
  }: {
    editor: Editor;
    view: EditorView;
    state: EditorState;
    oldState?: EditorState | undefined;
  }) => {
    return view.state.selection.to - view.state.selection.from > 3;
  };

  return (
    <div>
      <FloatingMenu
        pluginKey={"floating-hint"}
        shouldShow={whenShouldHintShow}
        editor={props.editor}
        tippyOptions={{ duration: 100 }}
      >
        <div className="rounded bg-gray-100 p-1 shadow">
          <p className="text-sm">Press "↵" to recommend</p>
        </div>
      </FloatingMenu>
      <FloatingMenu
        pluginKey={"floating-recommendation"}
        shouldShow={whenShouldRecShow}
        editor={props.editor}
        tippyOptions={{ duration: 100 }}
      >
        <div className="flex rounded bg-sky-500 shadow">
          <button
            className="rounded px-[0.275rem] py-[0.325rem] text-sm text-white transition duration-300 hover:bg-sky-600"
            onClick={() => props.selectedRecommend(props.editor)}
            disabled={props.recommending}
          >
            {props.recommending ? (
              <ArrowPathIcon className="size-5 animate-spin place-self-center" />
            ) : (
              <p className="place-self-center">Recommend</p>
            )}
          </button>
        </div>
      </FloatingMenu>
    </div>
  );
};
