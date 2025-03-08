import { pdfjs } from "react-pdf";
import { Document, Page } from "react-pdf";
import { useState, useRef, useEffect } from "react";
import { useResizeObserver } from "./useResizeObserver";
import { SparklesIcon } from "@heroicons/react/24/outline";

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
        file={"../../Reading Textbook (1).pdf"}
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
        className={`fixed bottom-8 right-[53%] z-30 ${baseStyle} rounded-full border border-gray-200 bg-sky-500 p-2 text-white shadow-sm transition duration-300 hover:bg-sky-600 ${showRec ? "opacity-100" : "invisible translate-y-3 opacity-0"}`}
        onClick={() => console.log(window.getSelection()?.toString())}
      >
        <SparklesIcon className="size-5" />
      </button>
    </div>
  );
};

export default PdfReader;
