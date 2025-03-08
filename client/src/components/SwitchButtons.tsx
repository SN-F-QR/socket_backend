import { DocumentIcon, FilmIcon } from "@heroicons/react/24/outline";

type SwitchProps = {
  activeFirst: boolean;
  switchActive: () => void;
};

const SwitchButtons = (props: SwitchProps) => {
  const baseStyle: string =
    "transition duration-300 cursor-pointer ease-in-out";
  const activeStyle: string = "rounded-full  p-2 text-white z-10 bg-opacity-0";
  const deActiveStyle: string =
    "rounded-full border-gray-200 bg-white p-2 bg-opacity-0 z-10";

  return (
    <span className="relative flex justify-between rounded-full border">
      <button
        className={`${baseStyle} ${props.activeFirst ? activeStyle : deActiveStyle}`}
        onClick={() => props.switchActive()}
      >
        <DocumentIcon className="size-4 place-self-center"></DocumentIcon>
      </button>
      <button
        className={`${baseStyle} ${!props.activeFirst ? activeStyle : deActiveStyle}`}
        onClick={() => props.switchActive()}
      >
        <FilmIcon className="size-4 place-self-center"></FilmIcon>
      </button>
      <div
        className={`absolute left-0 top-0 h-full w-1/2 rounded-full bg-sky-500 shadow ${!props.activeFirst && "translate-x-8"} ${baseStyle}`}
      ></div>
    </span>
  );
};

export default SwitchButtons;
