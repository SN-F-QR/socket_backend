import { Editor, FloatingMenu } from "@tiptap/react";
import { EditorState } from "@tiptap/pm/state";
import { EditorView } from "@tiptap/pm/view";

import { ArrowPathIcon, SparklesIcon } from "@heroicons/react/24/outline";
import { baseStyles, colors } from "./button";

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
        <div
          className={`${baseStyles} flex shadow hover:scale-[1.05] ${colors.spark}`}
        >
          <button
            className="p-1 text-white"
            onClick={() => props.selectedRecommend(props.editor)}
            disabled={props.recommending}
          >
            {props.recommending ? (
              <ArrowPathIcon className="size-6 animate-spin place-self-center" />
            ) : (
              <SparklesIcon className="size-6 place-self-center" />
            )}
          </button>
        </div>
      </FloatingMenu>
    </div>
  );
};
