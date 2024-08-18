//create a command line style field for outputting scan log error messages

export function TerminalOutput() {
  return (
    <div className="flex flex-row items-center">
      <span className="text-xl font-DOS my-4">&gt;</span>
      <input
        type="text"
        className="w-full h-8 font-DOS focus:outline-none text-white bg-transparent text-xl"
        defaultValue={"..."}
        placeholder="Scan output will appear here"
        readOnly={true}
      />
    </div>
  );
}
