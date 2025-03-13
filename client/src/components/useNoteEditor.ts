import { useRef, useState } from "react";
import { useEditor, Editor, NodePos } from "@tiptap/react";
import Document from "@tiptap/extension-document";
import Paragraph from "@tiptap/extension-paragraph";
import Text from "@tiptap/extension-text";
import BulletList from "@tiptap/extension-bullet-list";
import ListItem from "@tiptap/extension-list-item";
import { Color } from "@tiptap/extension-color";
import TextStyle from "@tiptap/extension-text-style";
import { FloatingMenu } from "@tiptap/extension-floating-menu";

import { CustomHeading } from "./custom-extension";
import shortUUID from "short-uuid";

import { requestRecommend } from "./client-websocket";

export type TypeState = {
  typingNewH1: boolean;
  newH1Id: string;
  newH1ByButton: boolean;
};

type EditorWrap = {
  editor: Editor;
};

export const useNoteEditor = (handleNetworkError: (id: string) => void) => {
  const extensions = [
    Document,
    Paragraph,
    CustomHeading,
    BulletList,
    Text,
    ListItem,
    TextStyle,
    Color,
    FloatingMenu,
  ];

  const typeState = useRef<TypeState>({
    typingNewH1: false,
    newH1Id: "",
    newH1ByButton: false,
  });

  const [updateCount, setUpdateCount] = useState<number>(0);
  const maxUpdateCount = 10;

  const count = () => {
    setUpdateCount((prev) => prev + 1);
    if (updateCount > maxUpdateCount) {
      // saveNoteToLocal();
      setUpdateCount(0);
    }
  };

  // track the response of recommendation
  const [recommending, setRecommending] = useState<boolean>(false);

  const handleH1Toggle = () => {
    typeState.current.newH1ByButton = true;
  };

  const resetStatus = () => {
    typeState.current = {
      typingNewH1: false,
      newH1Id: "",
      newH1ByButton: false,
    };
  };

  /**
   * Set <focus> on the user selected text and send the text
   * Abort if the user is typing a new H1
   */
  const selectedRecommend = async (editor: Editor) => {
    if (typeState.current.typingNewH1) {
      return;
    }
    const { from, to }: { from: number; to: number } =
      editor.view.state.selection;
    const taggedText = extractFocusedText(from, to, editor);
    handleRecommend(taggedText);
    resetStatus();
  };

  /**
   * Set <focus> on the new H1 and send text
   * @param h1Node the new H1 node
   */
  const autoRecommend = (h1Node: NodePos, editor: Editor) => {
    const switchLineLength: number = 1;

    const h1From: number = h1Node.from;
    const h1To: number = h1Node.to - switchLineLength; // Remove the line break
    const taggedText = extractFocusedText(h1From, h1To, editor);
    editor.commands.setTextSelection(h1To + switchLineLength * 2); // Move the cursor to the next line
    handleRecommend(taggedText);
  };

  const handleRecommend = async (note: string) => {
    try {
      const start = performance.now();
      setRecommending(true);
      const recommendations = await requestRecommend(note, "note");
      console.log(`Successfully get ${recommendations.length} recommendations`);
      const end = performance.now();
      console.log(`Recommendation time: ${(end - start) / 1000}s`);
    } catch (e) {
      console.error(`Cannot do recommendation since: ${e}`);
      if (e instanceof Error) {
        handleNetworkError(e.message);
      }
    } finally {
      setRecommending(false);
    }
  };

  /**
   * Insert <focus></focus> tag to the text and output the tagged text, then remove the tag
   * @param from position of <focus>
   * @param to position of </focus>, must be larger than from
   */
  const extractFocusedText = (
    from: number,
    to: number,
    editor: Editor,
  ): string => {
    if (from >= to) {
      return "";
    }

    const focusFixLength: number = 7;

    editor
      .chain()
      .insertContentAt(from, "\<focus\>")
      .insertContentAt(to + focusFixLength, "\<\/focus\>")
      .run();
    const taggedText: string = editor.getText();
    console.log(taggedText);
    editor
      .chain()
      .insertContentAt({ from: from, to: from + focusFixLength }, "")
      .insertContentAt({ from: to, to: to + focusFixLength + 1 }, "")
      .run();
    return taggedText;
  };

  /**
   * Check if is a new H1, if so, set the color to gray and set the type status
   * @param editor of Tiptap
   * @param curNode of editor selection
   */
  const handleNewH1 = (editor: Editor, curNode: NodePos) => {
    // 1.5. Check if the first time
    if (!typeState.current.typingNewH1) {
      // 2. Check if the H1 has any content, if not, it's a new H1
      if (curNode.textContent !== "") {
        // 2.5 If has content, check if it's converted by button so it's a new H1
        if (typeState.current.newH1ByButton) {
          console.log("New H1 by button");
          // New H1 converted from paragraph by button
          // Set the text to gray color
        } else {
          return;
        }
      }
      // We confirmed it's a new H1, start to handle status
      typeState.current.newH1ByButton = false;
      typeState.current.typingNewH1 = true;
      // 3. judge if the new H1 is deleted and retyped, or just a brand new H1
      if (curNode.attributes.id === "114514") {
        // if it is a brand new H1
        const newID: string = shortUUID.generate();
        typeState.current.newH1Id = newID;
        editor.commands.setNode("heading", { level: 1, id: newID }); // since nodePos.setAttributes has bug in current version
        console.log("A brand new H1 created with id: ", newID);
      } else {
        typeState.current.newH1Id = curNode.attributes.id;
        console.log("A H1 retyped with id: ", curNode.attributes.id);
      }
      editor.commands.setColor("gray");
      // Change the color at last, since it will call onUpdate again!
      if (curNode.textContent !== "") {
        editor
          .chain()
          .setNodeSelection(curNode.from)
          .setColor("gray")
          .setTextSelection(curNode.to - 1)
          .run();
      }
    } else {
      // 4. Now the status is typing new H1, check if still typing the same one
      if (curNode.attributes.id !== typeState.current.newH1Id) {
        resetStatus();
        console.log(
          "Firstly create new H1, then go to other H1 and type, so the status is canceled",
        );
      }
    }
  };

  /**
   * When typing a paragraph after a new H1, check if it's a new paragraph after the new H1
   */
  const handleParaWhenTypeStatus = (editor: Editor, curNode: NodePos) => {
    console.log("typing a paragraph after h1");
    // 5. Now started to type a para after H1, check if it's a **NEW** paragraph after the new H1
    try {
      const beforeNode: NodePos | null = curNode.before;
      if (
        curNode.textContent === "" && // Double check if it's a new paragraph
        beforeNode &&
        beforeNode.textContent !== "" && // Avoid empty H1
        beforeNode.attributes.id === typeState.current.newH1Id // check if this paragraph after the new H1
      ) {
        resetStatus();
        // finally set the H1 to black color since it will call onUpdate again!
        editor
          .chain()
          .focus()
          .setNodeSelection(beforeNode.from)
          .unsetColor()
          .setTextSelection(curNode.from)
          .run();
        console.log("Do recommendation?");
        autoRecommend(beforeNode, editor);
      } // else tying some other paragraph, I do not cancel the status, and then could return to the new H1
    } catch (e) {
      if (e instanceof RangeError) {
        console.log("The H1 is the first node and deleted");
      }
      resetStatus();
    }
  };

  /**
   * When typing new H1, the color will be gray and activate the recommendation after press "Enter"
   * After "Enter", set the new H1 color back to black
   * @param editor of Tiptap
   */
  const onUpdate = ({ editor }: EditorWrap) => {
    count();
    const updatePos: number = editor.state.selection.$head.pos; // Pos of ProseMirror Node
    // Use $pos to get the current NodePos in Tiptap, then can revise a many things
    const curNode: NodePos = editor.$pos(updatePos);
    // 1. Check if typing H1
    if (editor.isActive("heading", { level: 1 })) {
      handleNewH1(editor, curNode);
    } else if (editor.isActive("paragraph") && typeState.current.typingNewH1) {
      handleParaWhenTypeStatus(editor, curNode);
    } else {
      resetStatus();
    }
  };

  const onTransaction = ({ editor }: EditorWrap) => {
    if (
      !typeState.current.typingNewH1 &&
      editor.isActive("heading", { level: 1 })
    ) {
      console.log("Heading ID:", editor.getAttributes("heading").id);
    }
  };

  // const onSelectionUpdate = ({ editor }: EditorWrap) => {
  //   const { from, to }: { from: number; to: number } =
  //     editor.view.state.selection;
  //   console.log(`Selection updated: ${from} to ${to}`);
  // };

  const content: string = "";

  const editor = useEditor({
    extensions: extensions,
    content: content,
    editorProps: {
      attributes: {
        class:
          "prose prose-sm sm:prose xl:prose-lg m-5 focus:outline-none prose-li:leading-4 prose-h1:text-2xl",
      },
      transformPastedHTML: (html: string) => {
        return html.replace(/<[^>]*>/g, "");
      },
    },
    onUpdate: onUpdate,
    onTransaction: onTransaction,
    // onSelectionUpdate: onSelectionUpdate,
  });

  return {
    editor,
    typeState,
    updateCount,
    recommending,
    setUpdateCount,
    selectedRecommend,
    handleH1Toggle,
  };
};
