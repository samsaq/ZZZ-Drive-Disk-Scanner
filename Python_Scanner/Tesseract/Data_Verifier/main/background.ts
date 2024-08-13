import path from "path";
import { app, ipcMain, dialog, protocol } from "electron";
import serve from "electron-serve";
import { createWindow } from "./helpers";
import fs from "fs";

const isProd = process.env.NODE_ENV === "production";

let imageDir = "";
let groundTruthDir = "";

export interface VerificationData {
  images: string[];
  gts: string[];
  gtContents: string[];
  totalImages: number;
  initialProgress: number;
}

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

ipcMain.on("message", async (event, arg) => {
  event.reply("message", `${arg} World!`);
});

// when the main process receives a message from the renderer process
// open the directory selection dialog
ipcMain.on("select-image-folder", async (event) => {
  const result = await dialog.showOpenDialog({
    properties: ["openDirectory"],
  });
  console.log(result);
  imageDir = result.filePaths[0];
  event.reply("selected-image-folder", result.filePaths[0]);

  if (!result.canceled) {
    event.reply("selected-image-folder", result.filePaths[0]);
  }
});

//for the ground truth folder
ipcMain.on("select-ground-truth-folder", async (event) => {
  const result = await dialog.showOpenDialog({
    properties: ["openDirectory"],
  });
  console.log(result);
  groundTruthDir = result.filePaths[0];
  event.reply("selected-ground-truth-folder", result.filePaths[0]);

  if (!result.canceled) {
    event.reply("selected-ground-truth-folder", result.filePaths[0]);
  }
});

// on the loadVerification event
// we'll collect a list of file paths to the .png images in the selected image folder
// we'll collect a list of file paths to the .gt.txt files in the selected ground truth folder
// we'll calculate the number of images to verify (totalImages) as the length of the image list
// also, we'll ignore any images that don't have a corresponding ground truth file or vice versa
// also those that have a _synth or _done in their name will be ignored
// all of this will packaged up and sent back to the renderer process as an object
ipcMain.on("loadVerification", async (event, arg) => {
  const imageFiles = fs.readdirSync(imageDir);
  const gtFiles = fs.readdirSync(groundTruthDir);

  const images = imageFiles.filter((file) => {
    return (
      path.extname(file) === ".png" &&
      !file.includes("_synth") &&
      !file.includes("_done")
    );
  });

  const allImages = imageFiles.filter((file) => {
    return path.extname(file) === ".png";
  });
  //get inital progress value by counting the number of images in the folder that have _done in their name
  const progress = allImages.filter((file) => {
    return file.includes("_done");
  });

  const gts = gtFiles.filter((file) => {
    return (
      file.endsWith(".gt.txt") &&
      !file.includes("_done") &&
      !file.includes("_synth")
    );
  });

  // ignore images that don't have a corresponding ground truth file
  const imagesWithGt = images.filter((image) => {
    const gt = image.replace(".png", ".gt.txt");
    return gts.includes(gt);
  });
  console.log(imagesWithGt);
  const gtsWithImages = gts.filter((gt) => {
    const image = gt.replace(".gt.txt", ".png");
    return images.includes(image);
  });
  //get the text contents of the ground truth files into a list - same order as the images
  const gtContents = gtsWithImages.map((gt) => {
    return fs.readFileSync(path.join(groundTruthDir, gt), "utf8");
  });

  const totalImages = imagesWithGt;

  //return the image paths and ground truth paths that have been filtered
  const verificationData: VerificationData = {
    images: imagesWithGt.map((image) => path.join(imageDir, image)),
    gts: gtsWithImages.map((gt) => path.join(groundTruthDir, gt)),
    gtContents: gtContents,
    totalImages: totalImages.length,
    initialProgress: progress.length,
  };

  console.log(verificationData);
  event.reply("loadVerification", verificationData);
});

// on the skipValidation event - mark the given image with the _done suffix
// do the same for the ground truth file
ipcMain.on("skipValidation", async (event, arg) => {
  const image = path.basename(arg);
  const gt = image.replace(".png", ".gt.txt");

  fs.renameSync(
    path.join(imageDir, image),
    path.join(imageDir, image.replace(".png", "_done.png"))
  );
  fs.renameSync(
    path.join(groundTruthDir, gt),
    path.join(groundTruthDir, gt.replace(".gt.txt", "_done.gt.txt"))
  );
});

// on the discardValidation event - delete the given image and matching ground truth file
ipcMain.on("discardValidation", async (event, arg) => {
  const image = path.basename(arg);
  const gt = image.replace(".png", ".gt.txt");

  fs.unlinkSync(path.join(imageDir, image));
  fs.unlinkSync(path.join(groundTruthDir, gt));
});

// on the overwriteValidation event - update the ground truth file with the new contents for the given image
ipcMain.on("overwriteValidation", async (event, arg) => {
  const { curImage, curGT } = arg;
  //mark the image as done
  fs.renameSync(curImage, curImage.replace(".png", "_done.png"));
  //remove the previous ground truth file
  const oldgt = path.basename(curImage, path.extname(curImage)) + ".gt.txt";
  fs.unlinkSync(path.join(groundTruthDir, oldgt));
  //write the new ground truth file
  const gt = path.basename(curImage, path.extname(curImage)) + "_done.gt.txt";
  fs.writeFileSync(path.join(groundTruthDir, gt), curGT);
});

// on the endVerification event - close the window
ipcMain.on("endVerification", async (event, arg) => {
  app.quit();
});

//seting up a privledged channel for the renderer process to get images to show
const protocolName = "C";
protocol.registerSchemesAsPrivileged([
  { scheme: protocolName, privileges: { bypassCSP: true } },
]);

app.whenReady().then(() => {
  protocol.registerFileProtocol(protocolName, (request, callback) => {
    const url = request.url.replace(`${protocolName}:/`, "");
    try {
      return callback(decodeURIComponent(url));
    } catch (error) {
      // Handle the error as needed
      console.error(error);
    }
  });
});
