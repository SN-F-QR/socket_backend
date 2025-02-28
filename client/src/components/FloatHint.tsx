import { Editor, FloatingMenu } from "@tiptap/react";
import { EditorState } from "@tiptap/pm/state";
import { EditorView } from "@tiptap/pm/view";

type FloatHintProps = {
  editor: Editor;
  selectedRecommend: (editor: Editor) => void;
};

export const FloatHint = (props: FloatHintProps) => {
  const whenShouldHintShow = ({
    editor,
    view,
    state,
    oldState,
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
    editor,
    view,
    state,
    oldState,
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
        <div className="rounded bg-gray-100 p-1 shadow">
          <button onClick={() => props.selectedRecommend(props.editor)}>
            Recommend
          </button>
        </div>
      </FloatingMenu>
    </div>
  );
};
