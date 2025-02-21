import React, { useState, useRef } from "react";
import { sendVideoProgress } from "./client-websocket";

const Player = () => {
  const [videoPath, setVideoPath] = useState<string | undefined>(undefined); // fake path
  const [videoName, setVideoName] = useState<string | undefined>(undefined);
  const [subtitlePath, setSubtitlePath] = useState<string | undefined>(
    undefined,
  );
  const progress = useRef<number>(0); // current video progress

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
  };

  const getCurrentTime = (e: React.ChangeEvent<HTMLVideoElement>) => {
    const curSec = Math.round(e.target.currentTime);
    if (curSec !== progress.current) {
      progress.current = curSec;
      sendVideoProgress(curSec);
      console.log("current time", curSec);
    }
  };

  return (
    <div className="flex h-screen shrink-0 basis-1/2 flex-col justify-center space-y-3 place-self-center p-2">
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
          className="block shrink-0 rounded-md border-0 bg-sky-500 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-500/75"
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
            src={videoPath}
            onTimeUpdate={getCurrentTime}
          >
            <track default src={subtitlePath} srcLang="en" />
          </video>
        </div>
      )}
    </div>
  );
};

export default Player;
