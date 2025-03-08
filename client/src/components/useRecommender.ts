import { useState } from "react";
import { requestRecommend } from "./client-websocket";

const useRecommender = () => {
  const [waitingState, setWaitingState] = useState<boolean>(false);

  const requestRecommendation = async (text: string) => {
    setWaitingState(true);
    try {
      text = `<focus> ${text} </focus>`;
      const response = await requestRecommend(text);
      console.log(`Successfully get ${response.length} recommendations`);
    } catch (error) {
      console.error("Error while requesting recommendation: ", error);
    } finally {
      setWaitingState(false);
    }
  };

  return { waitingState, requestRecommendation };
};

export default useRecommender;
