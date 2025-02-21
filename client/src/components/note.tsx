// import React from "react";
import { useEditor, EditorContent } from "@tiptap/react";
import Document from "@tiptap/extension-document";
import Paragraph from "@tiptap/extension-paragraph";
import Heading from "@tiptap/extension-heading";
import Text from "@tiptap/extension-text";
import BulletList from "@tiptap/extension-bullet-list";
import ListItem from "@tiptap/extension-list-item";

const Note = () => {
  const extensions = [
    Document,
    Paragraph,
    Heading.configure({ levels: [3] }),
    BulletList,
    Text,
    ListItem,
  ];
  const content: string = `
  <h3>
  Hi there,
  </h3>
  <p>
    This is a basic example of Tiptap. Sure, there are all kind of basic text styles you'd probably expect from a text editor. But wait until you see the lists:
    <ul>
          <li>This is a bullet list.</li>
          <li>And it has three list items.</li>
          <li>Here is the third one.</li>
    </ul>
  </p>`;

  const editor = useEditor({
    extensions: extensions,
    content: content,
    editorProps: {
      attributes: {
        class:
          "prose prose-sm sm:prose xl:prose-lg m-5 focus:outline-none prose-p:m-0",
      },
    },
  });

  return (
    <div className="overflow-auto rounded-md border">
      <EditorContent editor={editor} />
    </div>
  );
};

export default Note;
