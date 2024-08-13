import React from "react";
import { VerificationData } from "../../main/background";

export default function VerificationPage() {
  const [verificationDataGlobal, setVerificationDataGlobal] =
    React.useState<VerificationData>({
      images: [],
      gts: [],
      gtContents: [],
      totalImages: 0,
      initialProgress: 0,
    });
  const [progress, setProgress] = React.useState(0);
  const [curImage, setCurImage] = React.useState(
    "C:\\Users\\samsaq\\Documents\\GitHub\\ZZZ-Drive-Disk-Scanner\\Python_Scanner\\Tesseract\\input_images_preprocessed/Partition1Scan1.png"
  );
  const [curGT, setCurGT] = React.useState("test");
  const handleGTChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCurGT(e.target.value);
  };
  const [totalImages, setTotalImages] = React.useState(100);
  const [renderKey, setRenderKey] = React.useState(0);

  //a function using useReducer to force a re-render
  //this is necessary because the image doesn't change when the state does
  const forceUpdate = React.useReducer(() => ({}), {})[1] as () => void;

  //function to move to the next image in the verification process
  //used within other functions, as we still need to handle the results that led to moving to the next image
  const nextValidation = (progress: number) => {
    if (progress + 1 < totalImages) {
      const preUpdatedProgress = progress + 1;
      setProgress(progress + 1);
      setCurImage(verificationDataGlobal.images[preUpdatedProgress]);
      if (
        verificationDataGlobal.gtContents[preUpdatedProgress] !== undefined &&
        verificationDataGlobal.gtContents[preUpdatedProgress] !== null
      ) {
        setCurGT(verificationDataGlobal.gtContents[preUpdatedProgress]);
      }
      console.log(verificationDataGlobal);
      console.log(preUpdatedProgress);
      console.log(
        "New Image: " + verificationDataGlobal.images[preUpdatedProgress]
      );
    } else {
      //if we've reached the end of the images, we can end the program
      window.ipc.send("endVerification", "end");
    }
  };

  const skipValidation = () => {
    //send the skip event to the main process
    if (typeof window !== "undefined" && window.ipc) {
      window.ipc.send("skipValidation", curImage);
    }
    nextValidation(progress);
  };

  const discardValidation = () => {
    //send the discard event to the main process
    if (typeof window !== "undefined" && window.ipc) {
      window.ipc.send("discardValidation", curImage);
    }
    nextValidation(progress);
  };

  const overwriteValidation = () => {
    //send the overwrite event to the main process
    if (typeof window !== "undefined" && window.ipc) {
      window.ipc.send("overwriteValidation", { curImage, curGT });
    }
    nextValidation(progress);
  };

  //use an effect to send the loadVerification event to the main process and await the response
  //we'll use it to set starter values for the verification page, etc
  React.useEffect(() => {
    if (typeof window !== "undefined" && window.ipc) {
      const unsubscribe = window.ipc.on(
        "loadVerification",
        (verificationData: VerificationData) => {
          console.log(verificationData);
          //lets use the verification data to set the initial values for the verification page
          setProgress(verificationData.initialProgress);
          setTotalImages(verificationData.totalImages);
          setCurImage(verificationData.images[progress]);
          setCurGT(verificationData.gtContents[progress]);
          setVerificationDataGlobal(
            JSON.parse(JSON.stringify(verificationData)) // deep copy the verification data
          );
          //if we are already at the end of the images, we can end the program
          if (
            verificationData.initialProgress + 1 >=
            verificationData.totalImages
          ) {
            window.ipc.send("endVerification", "end");
          }
        }
      );

      // Cleanup listener on component unmount
      return () => {
        unsubscribe();
      };
    }
  }, []);

  //on mount, send the loadVerification event to the main process
  React.useEffect(() => {
    if (typeof window !== "undefined" && window.ipc) {
      window.ipc.send("loadVerification", "initial");
    }
  }, []);

  return (
    <div>
      <div className="navbar bg-base-200 flex justify-between items-center">
        <div className=" border-4 p-2 mr-10">
          {progress + 1}/{totalImages}
        </div>
        <h1>Verification</h1>
        <div>
          <button className="btn m-2" onClick={discardValidation}>
            Discard
          </button>
          <button className="btn m-2" onClick={skipValidation}>
            Skip
          </button>
        </div>
      </div>

      <div className="flex justify-center items-center h-5/6">
        <div className="flex flex-col items-center">
          <img src={curImage} alt="Validation Target" className="m-4" />
          <input
            type="text"
            className="input bg-base-200 mt-4"
            value={curGT}
            onChange={handleGTChange}
          />
          <button className="btn m-2 bg-base-200" onClick={overwriteValidation}>
            Overwrite
          </button>
        </div>
      </div>
    </div>
  );
}
