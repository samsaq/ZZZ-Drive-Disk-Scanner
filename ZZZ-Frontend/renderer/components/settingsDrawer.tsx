import { Icon } from "@iconify/react";
import React from "react";
import Drawer from "react-modern-drawer";

//Drawer Styles
import "react-modern-drawer/dist/index.css";
//CRT Styles
import crtStyles from "../styles/crt.module.css";

export function SettingsDrawer() {
  const [isSettingsOpen, setIsSettingsOpen] = React.useState(false);
  const toggleSettings = () => setIsSettingsOpen(!isSettingsOpen);
  return (
    <>
      <button onClick={toggleSettings}>
        <Icon
          icon="eos-icons:rotating-gear"
          width={32}
          height={32}
          className=" animate-spin ease-in fixed top-0 right-0 m-4"
          style={{ animationDuration: "15s" }}
        ></Icon>
      </button>
      <Drawer
        open={isSettingsOpen}
        onClose={toggleSettings}
        direction="right"
        className="settingsDrawer"
        customIdSuffix="settings"
        overlayOpacity={0}
        size={300}
      >
        <div className={crtStyles.crt}></div>
        <div className="w-full h-full bg-background flex flex-col items-center border-l-2 border-white bg-black">
          <span className="text-xl font-DOS my-6">Settings</span>
          <span className=" text-base font-DOS my-0">Disc Scan Speed</span>
          <input
            type="range"
            min="0.25"
            max="1"
            defaultValue="0.25"
            className="range m-4 max-w-[200px] w-full"
            step="0.25"
          />
          <div className="flex w-full justify-between px-2 text-xs max-w-[250px] mb-8">
            <span>0.25s</span>
            <span>0.5s</span>
            <span>0.75s</span>
            <span>1s</span>
          </div>
          <span className=" text-base font-DOS my-0">Page Load Speed</span>
          <input
            type="range"
            min="1"
            max="5"
            defaultValue="2"
            className="range m-4 max-w-[200px] w-full"
            step="1"
          />
          <div className="flex w-full justify-between px-2 text-xs max-w-[200px] mb-8">
            <span>1s</span>
            <span>2s</span>
            <span>3s</span>
            <span>4s</span>
            <span>5s</span>
          </div>
        </div>
      </Drawer>
    </>
  );
}
