import React, { useState, useRef } from "react";
import { sendVideoProgress } from "./client-websocket";

const Player = () => {
  const [videoPath, setVideoPath] = useState<string | undefined>(undefined); // fake path
  const [videoName, setVideoName] = useState<string | undefined>(undefined);
  // const [subtitlePath, setSubtitlePath] = useState<string | undefined>(
  //   undefined,
  // );
  const progress = useRef<number>(0); // current video progress

  const handleVideoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const path = URL.createObjectURL(file);
      setVideoName(file.name);
      setVideoPath(path);
    }
    console.log("videoPath", videoPath);
  };

  const getCurrentTime = (e: React.ChangeEvent<HTMLVideoElement>) => {
    const curSec = Math.floor(e.target.currentTime);
    if (curSec !== progress.current) {
      progress.current = curSec;
      sendVideoProgress(curSec);
      console.log("current time", curSec);
    }
  };

  return (
    <div className="flex h-screen flex-col justify-center space-y-3 place-self-center p-2 lg:justify-between">
      <div className="justify-left flex">
        <input
          className="hidden"
          name="upload"
          type="file"
          id="upload"
          accept="video/*"
          onChange={handleVideoUpload}
        ></input>
        <label
          htmlFor="upload"
          className="block shrink-0 rounded-md border-0 bg-sky-500 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-500/75"
        >
          上传视频
        </label>
        {videoName && (
          <p className="place-self-center pl-2 text-sm font-semibold">
            {videoName}
          </p>
        )}
      </div>
      {videoPath && (
        <div className="max-w-screen-xl">
          <video
            className="aspect-video max-w-full"
            controls
            src={videoPath}
            onTimeUpdate={getCurrentTime}
          />
        </div>
      )}
    </div>
  );
};

export default Player;
