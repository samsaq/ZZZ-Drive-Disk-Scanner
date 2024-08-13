import React from "react";
import Head from "next/head";
import { useAtom } from "jotai";

import { imageDir, groundTruthDir } from "../atoms";

import crtStyles from "../styles/crt.module.css";

export default function HomePage() {
  const [imgDir, setImgDir] = useAtom(imageDir);
  const [gtDir, setGtDir] = useAtom(groundTruthDir);

  function selectImageFolder() {
    window.ipc.send("select-image-folder", "open");
  }
  function selectGroundTruthFolder() {
    window.ipc.send("select-ground-truth-folder", "open");
  }
  function startVerification() {
    console.log("Starting Verification");
    // if both directories are selected, go to the verification page
    if (imgDir && gtDir) {
      window.location.href = "/verification";
    } else {
      alert("Please select both image and ground truth folders");
    }
  }

  // wait for the main process to send the selected folders
  React.useEffect(() => {
    if (typeof window !== "undefined" && window.ipc) {
      const unsubscribeImg = window.ipc.on("selected-image-folder", (arg) => {
        setImgDir(arg as string);
        console.log(arg);
      });
      const unsubscribeGT = window.ipc.on(
        "selected-ground-truth-folder",
        (arg) => {
          setGtDir(arg as string);
          console.log(arg);
        }
      );

      // Cleanup listener on component unmount
      return () => {
        unsubscribeImg();
        unsubscribeGT();
      };
    }
  }, []);

  return (
    <React.Fragment>
      <Head>
        <title>Tesseract Data Verifier</title>
      </Head>
      <div className="flex flex-col w-full h-full items-center justify-center text-2xl text-center">
        <div className={crtStyles.crt}></div>
        <span className="text-4xl font-bold">Tesseract Data</span>
        <span className="text-4xl font-bold">Verifier</span>
        <button
          className="text-lg border-2 p-2 my-4"
          onClick={selectImageFolder}
        >
          Select Image Folder
        </button>
        <button
          className="text-lg border-2 p-2 my-4"
          onClick={selectGroundTruthFolder}
        >
          Select Ground Truth Folder
        </button>
        <button
          className="text-lg border-2 p-2 my-4"
          onClick={startVerification}
        >
          Start Verification
        </button>
      </div>
    </React.Fragment>
  );
}
