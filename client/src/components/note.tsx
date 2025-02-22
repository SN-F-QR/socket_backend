import { useRef } from "react";
import { useEditor, EditorContent, Editor, NodePos } from "@tiptap/react";
import Document from "@tiptap/extension-document";
import Paragraph from "@tiptap/extension-paragraph";
import Heading from "@tiptap/extension-heading";
import Text from "@tiptap/extension-text";
import BulletList from "@tiptap/extension-bullet-list";
import ListItem from "@tiptap/extension-list-item";
import { Color } from "@tiptap/extension-color";
import TextStyle from "@tiptap/extension-text-style";

import MenuBar from "./meun-bar";

type EditorWrap = {
  editor: Editor;
};

const Note = () => {
  const extensions = [
    Document,
    Paragraph,
    Heading.configure({ levels: [1] }),
    BulletList,
    Text,
    ListItem,
    TextStyle,
    Color,
  ];

  const typingNewH1 = useRef<boolean>(false);
  const newH1ByButton = useRef<boolean>(false);

  const h1Toggle = () => (newH1ByButton.current = true);

  /**
   * When typing new H1, the color will be gray and activate the recommendation after press "Enter"
   * After "Enter", set the new H1 color back to black
   * @param editor of Tiptap
   */
  const onUpdate = ({ editor }: EditorWrap) => {
    const updatePos: number = editor.state.selection.$head.pos; // Pos of ProseMirror Node
    if (editor.isActive("heading", { level: 1 })) {
      // Use $pos to get the current NodePos in Tiptap, then can revise a many things
      const node = editor.$pos(updatePos);
      if (!typingNewH1.current) {
        if (node.textContent === "") {
          // True new H1
          editor.commands.setColor("gray");
        } else if (newH1ByButton.current) {
          // New H1 converted from paragraph by button
          newH1ByButton.current = false;
          // Set the H1 to gray color
          editor
            .chain()
            .focus()
            .setNodeSelection(node.from)
            .setColor("gray")
            .setTextSelection(node.to - 1)
            .run();
        } else {
          return; // Do nothing if it's not a new H1
        }
        // else {
        //   // Edit the existing H1 (better to be handled manually by users)
        //   editor
        //     .chain()
        //     .focus()
        //     .setNodeSelection(node.from)
        //     .setColor("gray")
        //     .setTextSelection(node.to - 1)
        //     .run();
        // }
        console.log("typingNewH1 set to true");
        typingNewH1.current = true;
      }
    } else if (editor.isActive("paragraph") && typingNewH1.current) {
      console.log("typing new paragraph after h1");
      const curNode: NodePos = editor.$pos(updatePos);
      const beforeNode: NodePos | null = curNode.before;
      if (
        curNode.textContent === "" && // Double check if it's a new paragraph
        beforeNode &&
        beforeNode.textContent !== "" // Avoid empty H1
      ) {
        typingNewH1.current = false;
        // set the H1 to black color
        editor
          .chain()
          .focus()
          .setNodeSelection(beforeNode.from)
          .unsetColor()
          .setTextSelection(curNode.from)
          .run();
        console.log("Do recommendation?");
      }
    }
  };

  /**
   * Cancel the prepare for recommendation if user do not type "Enter" after H1
   * Also set the H1 color back to black
   */
  const onTransaction = ({ editor }: EditorWrap) => {
    // still has some exceptions, if user click other H1 while typing new H1, prepare is not cancelled
    if (
      typingNewH1.current &&
      !editor.isActive("heading", { level: 1 }) &&
      editor.state.selection.$head.parent.childCount > 0
    ) {
      // Cancel the prepare for recommendation if user do not type "Enter" after H1
      console.log("transaction to other than new p after h1");
      // Set all H1 to black cause there is no idea where is now
      editor.$nodes("heading", { level: 1 })?.forEach((node) => {
        editor.chain().setNodeSelection(node.from).unsetColor().run();
      });
      editor.commands.focus();
      typingNewH1.current = false;
    }
  };

  // Seems like heading and paragraph are in same level
  const content: string = `
  <h1>
  Hi there,
  </h1>
  <p>
    This is a basic example of Tiptap. Sure, there are all kind of basic text styles you'd probably expect from a text editor. But wait until you see the lists:
    <ul>
          <li>This is a bullet list.</li>
          <li>And it has three list items.</li>
          <li>Here is the third one.</li>
    </ul>
  Lorem ipsum dolor sit amet. Eos voluptates voluptatem ea sapiente nostrum sit perspiciatis iusto sed ipsa dolor et veritatis ducimus ut quia quaerat non nisi dolore. Id dolores odit est corporis dicta aut magni internos id odit velit. Sed facilis molestias qui omnis laborum aut perferendis dolore. Ut totam vitae eos deserunt asperiores non officiis iure est nostrum aliquid qui sunt assumenda ut recusandae error nam eius rerum. Qui maxime sint aut blanditiis beatae est ratione illum! Et amet saepe ea blanditiis quia et enim dolor et exercitationem optio ut laborum obcaecati qui repudiandae tenetur? In doloribus galisum est ducimus quia aut harum architecto ut voluptas ipsam eos odio itaque. Aut voluptatum impedit rem maxime tempora id corporis optio quo corrupti nesciunt aut culpa veritatis et voluptatum rerum. Ea atque facilis vel odio voluptatem sed nesciunt molestias et natus rerum rem voluptas temporibus nam quae enim. Qui molestiae molestiae id quia nihil sit dolorum totam et adipisci numquam ex ipsam maxime At architecto repellat. Aut debitis voluptas qui error pariatur et explicabo optio ut quis architecto et sint repellendus sed dolores commodi.</p>`;

  const editor = useEditor({
    extensions: extensions,
    content: content,
    editorProps: {
      attributes: {
        class:
          "prose prose-sm sm:prose xl:prose-lg m-5 focus:outline-none prose-li:leading-4 prose-h1:text-2xl",
      },
    },
    onUpdate: onUpdate,
    onTransaction: onTransaction,
  });

  return (
    <div className="relative w-full overflow-y-scroll rounded-md border">
      <div className="sticky top-0 z-50 px-2 py-2">
        <MenuBar
          editor={editor as Editor}
          disableButton={typingNewH1.current}
          h1Toggle={h1Toggle}
        />
      </div>
      <div className="">
        <EditorContent editor={editor} />
      </div>
    </div>
  );
};

export default Note;
