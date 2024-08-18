// a shiny button to replace the terminal input to start the scan now that we have a seperate settings page

import shinyStyles from "../styles/shinyButton.module.scss";
export function ShinyButton({ onClick, text }) {
  return (
    <button
      className={`bg-black text-white border-2 border-white font-bold mt-2 py-2 px-4 rounded-none overflow-hidden relative ${shinyStyles.shineButton} ${shinyStyles.animateShine}`}
      onClick={onClick}
    >
      <span>{text}</span>
    </button>
  );
}
