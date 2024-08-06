import { Icon } from "@iconify/react";
import React from "react";
import Drawer from "react-modern-drawer";

//Drawer Styles
import "react-modern-drawer/dist/index.css";

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
        size={400}
        overlayOpacity={0}
      >
        <div className="w-full h-full bg-background flex flex-col border-l-2 border-white bg-black">
          <span className="text-xl font-DOS my-6">Settings</span>
        </div>
      </Drawer>
    </>
  );
}
