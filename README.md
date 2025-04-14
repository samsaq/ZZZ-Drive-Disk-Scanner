# ZZZ-Drive-Disk-Scanner

A program that scans your drive discs in [Zenless Zone Zero](https://zenless.hoyoverse.com/) & saves them for use in the [Zenless Optimizer](https://github.com/samsaq/ZZZ-Drive-Disk-Optimizer)

## How to use

Download the latest portable zip or installer from the releases page and use the .exe from there as admin. You might need to alter the page load speed (time to wait for the equipment screen to load) or disk scan speed (time to wait in between taking snapshots of disks so that the game can load the next one) if your computer is a little slow.

Once you click the start scan button **DON'T TOUCH ANYTHING** until the scanner finishes moving - it'll break the scan otherwise and you'll need to restart. Once it does, alt tab back to the scanner & the file explorer window opened with the scan_data.json file you'll upload to the [Zenless Optimizer](https://github.com/samsaq/ZZZ-Drive-Disk-Optimizer) to analyze.

## Compatibility

The scanner is just for PC, and works on **1080p and 1440p screens**. If you want support for another resolution, you can send me a few UI images snipped from ZZZ at fullscreen at that resolution (see the Python Scanner's Target Images folder) for me to use, or get them and edit the getImages.py file to use the new resolution's images (as is already done for 1080p and 1440p) and submit a PR.

## Branch Scope

This branch is working to add weapon data (wengines, upgrade levels (weapon fusion), levels/mod-level) and character data (characters, their levels/promotions, talent levels, and what wengines & discs they are equipped with), so that they can be used by the [Zenless Optimizer](https://github.com/samsaq/ZZZ-Drive-Disk-Optimizer).

### TODOs

1. The character scanner needs to handle cases where some disk drives / the wengine isn't equipped
2. We need the 1440p images for this case
3. Consider finding an alternative method of image matching that is not practically resolution dependent
4. Add a periodic check to see if a new version of the scanner is available on github so folks don't use an out of date version
5. Seperate out set strings and similar data that is changed version to version from validMetaData into a seperate json file
6. See if we can get that version data JSON to be downloadable-on-click from the electron frontend if a new version is available (and no other code changes are present between versions)
