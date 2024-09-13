import path from "path";
import { app, ipcMain } from "electron";
import serve from "electron-serve";
import { createWindow } from "./helpers";
import fs from "fs";

const isProd = process.env.NODE_ENV === "production";
const pathToScanner = path.join(
  __dirname,
  "../ZZZ-Scanner-Tesseract/ZZZ-Scanner-Tesseract.exe"
);
const pathToScanOutput = path.join(
  __dirname,
  "../ZZZ-Scanner-Tesseract/_internal/scan_output"
);

if (isProd) {
  serve({ directory: "app" });
} else {
  app.setPath("userData", `${app.getPath("userData")} (development)`);
}

(async () => {
  await app.whenReady();

  const mainWindow = createWindow("main", {
    width: 1000,
    height: 600,
    autoHideMenuBar: true,
    icon: path.join(
      __dirname,
      "../renderer/public/images",
      "ZZZ-Scanner-Icon.png"
    ),
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
    },
  });

  if (isProd) {
    await mainWindow.loadURL("app://./home");
  } else {
    const port = process.argv[2];
    await mainWindow.loadURL(`http://localhost:${port}/home`);
    mainWindow.webContents.openDevTools();
  }
})();

app.on("window-all-closed", () => {
  app.quit();
});
//input expected in form { discScan: number, pageLoad: number }
ipcMain.on("start-scan", (event, arg) => {
  console.log("Received start-scan event with args: ", arg);
  const { discScan, pageLoad } = arg;
  //run the scanner exe with the provided arguments in order of pageLoad, discScan
  const scannerProcess = require("child_process").spawn(pathToScanner, [
    pageLoad,
    discScan,
  ]);

  //Wait for then watch the log file for changes so we can respond to scanner events
  setTimeout(() => {
    const logFilePath = path.join(pathToScanOutput, "log.txt");
    let lastLine = "";

    console.log("Watching log file: ", logFilePath);
    fs.watch(logFilePath, (eventType) => {
      if (eventType === "change") {
        fs.readFile(logFilePath, "utf8", (err, data) => {
          if (err) {
            console.error("Error reading log file:", err);
            return;
          }

          const lines = data.split("\n");
          const newLastLine = lines[lines.length - 2].trim(); //we have an extra empty line at the end of the file
          //console.log("New last line: ", newLastLine);

          if (newLastLine !== lastLine) {
            lastLine = newLastLine;

            if (lastLine.includes("CRITICAL")) {
              console.log("Scan error: ", lastLine);
              event.reply("scan-error", { message: lastLine });
            } else if (lastLine.includes("Writing scan data to file")) {
              console.log("Scan complete: ", lastLine);
              event.reply("scan-complete", { message: lastLine });
            }
          }
        });
      }
    });
  }, 3000); //wait 3 seconds for the scanner to create the log file
});
