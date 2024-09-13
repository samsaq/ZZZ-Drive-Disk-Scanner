//create a command line style field for outputting scan log error messages

interface TerminalOutputProps {
  finalLine: string;
}

export function TerminalOutput({ finalLine }: TerminalOutputProps) {
  //if the final line is not empty, set the input field based on the final line
  let inputValue = finalLine;
  if (finalLine && finalLine !== "") {
    if (finalLine.includes("CRITICAL")) {
      inputValue = "Error: " + finalLine;
      if (
        finalLine.includes("try increasing the time between disc drive scans")
      ) {
        inputValue = "Error: try increasing the time between disc drive scans";
      } else if (finalLine.includes("try increasing the page load time")) {
        inputValue = "Error: try increasing the page load time";
      }
    } else if (finalLine.includes("Writing scan data to file")) {
      inputValue = "Scan complete";
    }
  }
  return (
    <div className="flex flex-row items-center">
      <span className="text-xl font-DOS my-4">&gt;</span>
      <input
        type="text"
        className="w-full h-8 font-DOS focus:outline-none text-white bg-transparent text-xl"
        value={inputValue}
        placeholder="..."
        readOnly={true}
      />
    </div>
  );
}
