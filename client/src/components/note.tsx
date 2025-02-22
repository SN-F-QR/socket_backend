// import React from "react";
import { useEditor, EditorContent, Editor } from "@tiptap/react";
import Document from "@tiptap/extension-document";
import Paragraph from "@tiptap/extension-paragraph";
import Heading from "@tiptap/extension-heading";
import Text from "@tiptap/extension-text";
import BulletList from "@tiptap/extension-bullet-list";
import ListItem from "@tiptap/extension-list-item";

import MenuBar from "./meun-bar";

const Note = () => {
  const extensions = [
    Document,
    Paragraph,
    Heading.configure({ levels: [1] }),
    BulletList,
    Text,
    ListItem,
  ];
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
          "prose prose-sm sm:prose xl:prose-lg m-5 focus:outline-none prose-p:m-0 prose-h1:text-2xl",
      },
    },
  });

  return (
    <div className="relative w-full overflow-y-scroll rounded-md border">
      <div className="sticky top-0 z-50 px-2 py-2">
        <MenuBar editor={editor as Editor} />
      </div>
      <div className="">
        <EditorContent editor={editor} />
      </div>
    </div>
  );
};

export default Note;
