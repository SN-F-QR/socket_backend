import { pdfjs } from "react-pdf";
import { Document, Page } from "react-pdf";
import { useState, useRef } from "react";
import { useResizeObserver } from "./useResizeObserver";

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
  const [numPages, setNumPages] = useState<number | undefined>(undefined);

  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState<number>();

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
      {/* <button
        className="absolute bottom-4 right-4 z-30 border"
        onClick={() => console.log(window.getSelection()?.toString())}
      >
        Test
      </button> */}
    </div>
  );
};

export default PdfReader;
