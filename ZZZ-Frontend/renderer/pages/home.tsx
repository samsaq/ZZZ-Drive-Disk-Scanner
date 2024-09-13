import React from "react";
import Head from "next/head";

import crtStyles from "../styles/crt.module.css";
import { TerminalOutput } from "../components/terminalOutput";
import { SettingsDrawer } from "../components/settingsDrawer";
import { ShinyButton } from "../components/shinyButton";
import { useAtom } from "jotai";
import { pageLoadAtom, discScanAtom } from "../atoms";

function TextArt({ label, text }) {
  return (
    <pre aria-label={label} className=" font-mono overflow-auto whitespace-pre">
      {text}
    </pre>
  );
}

export default function HomePage() {
  const ZZZ =
    " ________  ________  ________     \n|\\_____  \\|\\_____  \\|\\_____  \\    \n \\|___/  /|\\|___/  /|\\|___/  /|   \n     /  / /    /  / /    /  / /   \n    /  /_/__  /  /_/__  /  /_/__  \n   |\\________\\\\________\\\\________\\\n    \\|_______|\\|_______|\\|_______|";
  const [pageLoad, setPageLoad] = useAtom(pageLoadAtom);
  const [discScan, setDiscScan] = useAtom(discScanAtom);
  const [finalLine, setFinalLine] = React.useState("");

  //react to scan-error and scan-complete events
  React.useEffect(() => {
    window.ipc.on("scan-error", (event: { message: string }) => {
      console.log("Scan error event: ", event);
      console.log("Scan error message: ", event.message);
      setFinalLine(event.message);
    });
    window.ipc.on("scan-complete", (event: { message: string }) => {
      console.log("Scan complete event: ", event);
      console.log("Scan complete message: ", event.message);
      setFinalLine(event.message);
    });
  }, []);

  const handleStartScan = () => {
    console.log("Starting scan...");
    console.log("Disc Scan Speed: ", discScan);
    console.log("Page Load Speed: ", pageLoad);
    window.ipc.send("start-scan", { discScan, pageLoad });
  };

  return (
    <React.Fragment>
      <Head>
        <title>ZZZ Disk Drive Scanner</title>
      </Head>
      <div className="flex flex-col w-full h-full items-center justify-center text-2xl text-center">
        <div className={crtStyles.crt}></div>
        <SettingsDrawer />
        <TextArt label={"ZZZ"} text={ZZZ} />
        <span className="text-4xl font-DOS my-4">Scanner</span>
        <ShinyButton text={"Start Scan"} onClick={handleStartScan} />
        <footer className="fixed bottom-0 left-0 p-6 text-xs text-left w-full">
          <TerminalOutput finalLine={finalLine} />
        </footer>
      </div>
    </React.Fragment>
  );
}
