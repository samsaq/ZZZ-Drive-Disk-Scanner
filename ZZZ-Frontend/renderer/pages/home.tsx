import React from "react";
import Head from "next/head";

import crtStyles from "../styles/crt.module.css";
import { TerminalInput } from "../components/terminalInput";
import { SettingsDrawer } from "../components/settingsDrawer";

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
        <footer className="fixed bottom-0 left-0 p-6 text-xs text-left w-full">
          <TerminalInput />
        </footer>
      </div>
    </React.Fragment>
  );
}
