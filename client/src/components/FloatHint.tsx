import { Editor, FloatingMenu } from "@tiptap/react";
import { EditorState } from "@tiptap/pm/state";
import { EditorView } from "@tiptap/pm/view";

type FloatHintProps = {
  editor: Editor;
};

export const FloatHint = (props: FloatHintProps) => {
  const whenShouldShow = ({
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
  return (
    <FloatingMenu
      shouldShow={whenShouldShow}
      editor={props.editor}
      tippyOptions={{ duration: 100 }}
    >
      <div className="rounded bg-gray-100 p-1 shadow">
        <p className="text-sm">Press "↵" to recommend</p>
      </div>
    </FloatingMenu>
  );
};
