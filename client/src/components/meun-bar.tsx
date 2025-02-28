import { Editor } from "@tiptap/react";
type menuProps = {
  editor: Editor;
  disableButton: boolean;
  h1Toggle: () => void;
  recommend: () => void;
};

type ButtonStyle = {
  true: string;
  false: string;
};

const MenuBar = (props: menuProps) => {
  const buttonCSS: ButtonStyle = {
    true: "transition shrink-0 border rounded-md bg-sky-500 px-2 max-h-8 place-self-center text-white hover:bg-sky-600 duration-300",
    false:
      "transition shrink-0 border rounded-md bg-gray-100 px-2 max-h-8 place-self-center hover:bg-gray-200 duration-300",
  };

  const getButtonCSS = (isActive: boolean): string =>
    buttonCSS[isActive.toString() as keyof ButtonStyle];

  return (
    <div className="flex min-h-12 justify-between rounded-md border shadow backdrop-blur-md">
      <div className="flex space-x-2">
        <span className=""></span>
        <button
          className={getButtonCSS(
            props.editor.isActive("heading", { level: 1 }),
          )}
          onClick={() => {
            if (!props.editor.isActive("heading", { level: 1 })) {
              props.h1Toggle();
            }
            props.editor.chain().focus().toggleHeading({ level: 1 }).run();
          }}
          disabled={props.disableButton}
        >
          H1
        </button>
        <button
          className={getButtonCSS(props.editor.isActive("bulletList"))}
          onClick={() => props.editor.chain().focus().toggleBulletList().run()}
          disabled={props.disableButton}
        >
          Bullet list
        </button>
      </div>
      <div className="place-self-center">
        <button
          className="min-h-8 rounded-md bg-sky-500 px-2 text-white transition duration-300 hover:bg-sky-600"
          onClick={props.recommend}
        >
          Recommend
        </button>
        <span className="mr-2"></span>
      </div>
    </div>
  );
};

export default MenuBar;
