import { useAtom } from "jotai";
import { pageLoadAtom, discScanAtom } from "../atoms";

//create a command line style input field

export function TerminalInput() {
  const [discScanSpeed] = useAtom(discScanAtom);
  const [pageLoadSpeed] = useAtom(pageLoadAtom);

  const handleSubmit = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      console.log("Scanning...");
      console.log("Page Load Speed: ", pageLoadSpeed);
      console.log("Disc Scan Speed: ", discScanSpeed);
    }
  };
  return (
    <div className="flex flex-row items-center">
      <span className="text-xl font-DOS my-4">&gt;</span>
      <input
        type="text"
        className="w-full h-8 font-DOS focus:outline-none text-white bg-transparent text-xl"
        defaultValue={"Scan"}
        placeholder="Type Scan & press enter to start"
        autoFocus={true}
        onKeyDown={handleSubmit}
      />
    </div>
  );
}
