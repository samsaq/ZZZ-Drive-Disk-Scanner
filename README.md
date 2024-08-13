# ZZZ-Drive-Disk-Scanner
An program that scans the drive discs in your backpack in Zenless Zone Zero &amp; saves them for use in a future Zenless Optimizer

# Branch Scope
- [ ] Build the scanner portion of the project to a working exe that can be used on other computers by the electron app
- [ ] Add & Test support for 1080p
* Integrate tesseract in order to remove   need for CUDA & GPU acceleration
  - [ ] Remove use of easyocr and paddleocr
  - [x] Preprocess scanned images for tesseract
  * Fine tune a tesseract model for disc drive analysis
    * Create a worflow to generate, manually review, and integrate training data
      - [x] Generate line images and ground truth files using easyocr to later verify
       - [x] Generate synthetic line images and ground truth files for set name lines to prevent set name memorization and preclude later retraining
      - [x] Create a program to help manually review training data
      - [ ] Automate all of the above together, as much as possible