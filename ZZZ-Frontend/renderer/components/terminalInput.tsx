//create a command line style input field

export function TerminalInput() {
  return (
    <div className="flex flex-row items-center">
      <span className="text-xl font-DOS my-4">&gt;</span>
      <input
        type="text"
        className="w-full h-8 font-DOS focus:outline-none text-white bg-transparent text-xl"
        defaultValue={"Scan"}
        placeholder="Type Scan & press enter to start"
        autoFocus={true}
      />
    </div>
  );
}
