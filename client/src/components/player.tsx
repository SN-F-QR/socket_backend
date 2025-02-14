import React, { useState, useRef } from "react";
import { sendVideoProgress } from "./client-websocket";

const Player = () => {
  const [videoPath, setVideoPath] = useState<string | undefined>(undefined); // fake path
  // const [subtitlePath, setSubtitlePath] = useState<string | undefined>(
  //   undefined,
  // );
  const progress = useRef<number>(0); // current video progress

  const handleVideoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const path = URL.createObjectURL(file);
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
    <div className="flex h-screen flex-col justify-center space-y-1 place-self-center py-2">
      <input
        name="upload"
        type="file"
        accept="video/*"
        onChange={handleVideoUpload}
      ></input>
      {videoPath && (
        <video
          className="max-h-[480px] w-full"
          controls
          src={videoPath}
          onTimeUpdate={getCurrentTime}
        />
      )}
    </div>
  );
};

export default Player;
