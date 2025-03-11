import { useState } from "react";
import { requestRecommend } from "./client-websocket";

type RecommenderConfig = {
  directInput: boolean;
  handleNetworkError: (id: string) => void;
};

const useRecommender = (args: RecommenderConfig) => {
  const [waitingState, setWaitingState] = useState<boolean>(false);

  const requestRecommendation = async (text: string) => {
    setWaitingState(true);
    try {
      if (!args.directInput) text = `<focus> ${text} </focus>`;
      const response = await requestRecommend(text);
      console.log(`Successfully get ${response.length} recommendations`);
    } catch (error) {
      console.error("Error while requesting recommendation: ", error as Error);
      if (error instanceof Error) {
        args.handleNetworkError(error.message);
      }
    } finally {
      setWaitingState(false);
    }
  };

  return { waitingState, requestRecommendation };
};

export default useRecommender;
