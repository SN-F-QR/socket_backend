import React, { useState, useRef } from "react";
import { Editor } from "@tiptap/react";
import VideoKeyBar from "./VideoKeyBar";
import {
  sendVideoProgress,
  VideoMessage,
  requestRecommend,
} from "./client-websocket";

type PlayerProps = {
  editor: Editor | null;
};

const Player = (props: PlayerProps) => {
  const [videoPath, setVideoPath] = useState<string | undefined>(undefined); // fake path
  const [videoName, setVideoName] = useState<string | undefined>(undefined);
  const [subtitlePath, setSubtitlePath] = useState<string | undefined>(
    undefined,
  );
  const [isPaused, setIsPaused] = useState<boolean>(true);
  const videoRef = useRef<HTMLVideoElement>(null); // current video progress

  const [keywords, setKeywords] = useState<string[]>(["Hotel", "Food", "789"]);

  const handleVideoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      console.log("files", files);
      for (const file of files) {
        const url = URL.createObjectURL(file);
        if (file.type.startsWith("video/")) {
          setVideoPath(url);
          setVideoName(file.name);
        } else if (file.type.endsWith("vtt")) {
          setSubtitlePath(url);
        }
      }
    }
    setIsPaused(true);
  };

  const requestKeywords = async () => {
    if (videoRef.current && isPaused) {
      try {
        const response: VideoMessage = await sendVideoProgress(
          videoRef.current.currentTime,
        );
        setKeywords(response.keywords);
      } catch (error) {
        console.error("Error while requesting keywords: ", error);
      }
    }
  };

  const requestVideoRecommend = async (keyword: string) => {
    if (videoRef.current && isPaused && props.editor) {
      try {
        const context: string = props.editor
          .getText()
          .concat("<focus> " + keyword + " </focus>");
        const recommendations = await requestRecommend(context);
        console.log(
          `Successfully get ${recommendations.length} recommendations`,
        );
      } catch (error) {
        console.error("Error while requesting video recommend: ", error);
      }
    }
  };

  const toggleSuggest = () => {
    setIsPaused(!isPaused);
  };

  return (
    <div className="flex h-screen basis-1/2 flex-col justify-center space-y-3 place-self-center p-2">
      <div className="justify-left flex">
        <input
          className="hidden"
          name="upload"
          type="file"
          id="upload"
          accept="video/*,.vtt"
          onChange={handleVideoUpload}
          multiple
        ></input>
        <label
          htmlFor="upload"
          className="block shrink-0 rounded-md border-0 bg-sky-500 px-4 py-2 text-sm font-semibold text-white transition duration-300 hover:bg-sky-600"
        >
          上传
        </label>

        <p className="place-self-center pl-2 text-sm font-semibold">
          {videoPath ? videoName : "同时选择视频和字幕文件"}
        </p>
      </div>
      {videoPath && (
        <div className="max-w-screen-xl">
          <video
            className="aspect-video max-w-full"
            controls
            ref={videoRef}
            src={videoPath}
            onPause={toggleSuggest}
            onPlay={toggleSuggest}
            onTimeUpdate={() => setKeywords([])}
          >
            <track default src={subtitlePath} srcLang="en" />
          </video>
        </div>
      )}
      {videoPath && (
        <VideoKeyBar
          isPaused={isPaused}
          keywords={keywords}
          requestKeywords={requestKeywords}
          requestRecommend={requestVideoRecommend}
        />
      )}
    </div>
  );
};

export default Player;
