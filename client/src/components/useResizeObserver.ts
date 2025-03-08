import { useRef, useEffect } from "react";

export const useResizeObserver = (
  containerRef: React.RefObject<HTMLElement | null>,
  callback: (entries: ResizeObserverEntry[]) => void,
) => {
  const observer = useRef<ResizeObserver>(new ResizeObserver(callback));

  useEffect(() => {
    if (containerRef.current) {
      observer.current.observe(containerRef.current);
    }

    return () => {
      observer.current.disconnect();
    };
  }, []);
};
