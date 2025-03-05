import { useState } from "react";
import { SparklesIcon } from "@heroicons/react/24/outline";

type VideoKeyBarProps = {
  keywords: string[];
  isPaused: boolean;
  requestKeywords: () => void;
  requestRecommend: (keyword: string) => void;
};

const VideoKeyBar = (props: VideoKeyBarProps) => {
  const baseStyle =
    "transition-all duration-300 cursor-pointer whitespace-nowrap";

  const keywordButtons = props.keywords.map((keyword) => {
    return (
      <button
        className={`${baseStyle} rounded-full border border-gray-200 bg-white/90 px-3 py-1.5 text-gray-700 shadow-sm backdrop-blur-sm hover:scale-[1.02] hover:text-sky-500 hover:shadow-md`}
        key={keyword}
        onClick={(e) => {
          e.currentTarget.disabled = true;
          props.requestRecommend(keyword);
        }}
      >
        {keyword}
      </button>
    );
  });

  return (
    <div
      className={`flex flex-wrap space-x-2 ${props.isPaused ? "opacity-100" : "invisible translate-y-2 opacity-0"} transform-all duration-300`}
    >
      <button
        className={`${baseStyle} rounded-full border border-gray-200 bg-sky-500 p-2 text-white shadow-sm transition duration-300 hover:bg-sky-600`}
        onClick={props.requestKeywords}
      >
        <SparklesIcon className="size-5" />
      </button>
      {keywordButtons}
    </div>
  );
};

export default VideoKeyBar;
