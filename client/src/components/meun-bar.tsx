import { Editor } from "@tiptap/react";
import { ArrowPathIcon, ListBulletIcon } from "@heroicons/react/24/outline";

type menuProps = {
  editor: Editor;
  disableButton: boolean;
  recommending: boolean;
  h1Toggle: () => void;
  recommend: (editor: Editor) => void;
};

type ButtonStyle = {
  true: string;
  false: string;
};

const MenuBar = (props: menuProps) => {
  const buttonCSS: ButtonStyle = {
    true: "transition shrink-0 border rounded-md bg-sky-500 px-2 max-h-8 place-self-center text-white hover:bg-sky-600 duration-300",
    false:
      "transition shrink-0 border rounded-md bg-gray-100 px-2 max-h-8 max-w-10 place-self-center hover:bg-gray-200 duration-300",
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
          {/* Bullet list */}
          <ListBulletIcon className="size-6" />
        </button>
      </div>
      <div className="flex items-center">
        <button
          className="flex min-h-8 space-x-1 rounded-md bg-sky-500 px-2 text-white transition duration-300 hover:bg-sky-600"
          onClick={() => props.recommend(props.editor)}
          disabled={props.disableButton || props.recommending}
        >
          {props.recommending ? (
            <>
              <ArrowPathIcon className="size-5 animate-spin place-self-center" />
              <p className="place-self-center">Processing</p>
            </>
          ) : (
            <p className="place-self-center">Recommend</p>
          )}
        </button>
        <span className="mr-2"></span>
      </div>
    </div>
  );
};

export default MenuBar;
