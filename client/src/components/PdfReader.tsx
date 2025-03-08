import { pdfjs } from "react-pdf";
import { Document, Page } from "react-pdf";
import { useState, useRef, useEffect } from "react";
import { useResizeObserver } from "./useResizeObserver";
import { SparklesIcon, ArrowPathIcon } from "@heroicons/react/24/outline";
import useRecommender from "./useRecommender";

import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import "react-pdf/dist/esm/Page/TextLayer.css";

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url,
).toString();

const options = {
  cMapUrl: "/cmaps/",
  standardFontDataUrl: "/standard_fonts/",
};

const PdfReader = () => {
  const baseStyle =
    "transition-all duration-300 cursor-pointer whitespace-nowrap";

  const [numPages, setNumPages] = useState<number | undefined>(undefined);

  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState<number>();

  const [showRec, setShowRec] = useState<boolean>(false);
  const { waitingState, requestRecommendation } = useRecommender();

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
  };

  const onResize = (entries: ResizeObserverEntry[]) => {
    const [entry] = entries;

    if (entry) {
      setContainerWidth(entry.contentRect.width);
    }
  };

  useResizeObserver(containerRef, onResize);

  useEffect(() => {
    document.addEventListener("selectionchange", () => {
      const selection = window.getSelection();
      if (selection && selection.toString().length > 3) {
        const element: Node | null = selection.focusNode;
        if (containerRef.current?.contains(element)) {
          setShowRec(true);
        }
      } else {
        setShowRec(false);
      }
    });

    return () => {
      document.removeEventListener("selectionchange", () => {
        setShowRec(false);
      });
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className="relative h-full w-full place-self-center overflow-x-hidden overflow-y-scroll rounded border p-2"
    >
      <Document
        file={"../../London Visitor Guide.pdf"}
        onLoadSuccess={onDocumentLoadSuccess}
        options={options}
      >
        {numPages &&
          [...Array(numPages)].map((_, index) => {
            return (
              <Page
                key={`pdf_page_${index}`}
                pageNumber={index + 1}
                width={containerWidth}
              />
            );
          })}
      </Document>
      <button
        className={`fixed bottom-8 right-[53%] z-30 ${baseStyle} rounded-full bg-gradient-to-r from-sky-500 to-indigo-500 p-2 text-white shadow-lg transition duration-300 hover:scale-[1.05] ${showRec ? "opacity-100" : "invisible translate-y-3 opacity-0"}`}
        onClick={() => {
          const selectionText = window.getSelection()?.toString();
          if (selectionText) {
            requestRecommendation(selectionText);
          }
        }}
      >
        {waitingState ? (
          <ArrowPathIcon className="size-5 animate-spin" />
        ) : (
          <SparklesIcon className="size-5" />
        )}
      </button>
    </div>
  );
};

export default PdfReader;
