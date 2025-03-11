import { useEffect } from "react";
import { ExclamationCircleIcon } from "@heroicons/react/24/outline";

type NetworkErrorProps = {
  messageId: string;
  onClose: () => void;
};

const NetworkError = (props: NetworkErrorProps) => {
  useEffect(() => {
    const timeout: number = setTimeout(() => {
      props.onClose();
    }, 3000);
    return () => {
      clearTimeout(timeout);
    };
  }, [props.messageId]);

  return (
    <div className="fixed bottom-4 z-30 max-w-40 place-self-center text-nowrap">
      <div className="inline-flex place-items-center rounded-md bg-red-500 px-4 py-2 text-white shadow-lg">
        <ExclamationCircleIcon className="size-5" />
        <p className="pl-1 text-lg">Server Error</p>
      </div>
    </div>
  );
};

export default NetworkError;
