# SlicerRawImageGuess

Extension that helps with loading an image in an unknown image format into 3D Slicer.

How to use:
- Download this repository to your computer, unzip to a folder
- Add RawImageGuess to Additional module paths (in menu: Edit / Application settings / Modules)
- Restart Slicer
- Switch to "RawImageGuess" module
- Select input file and output volume
- Experiment with image parameters (click the checkbox on Update button to automatically update output volume when any parameter is changed)
- When the correct combination of parameters is found then either save the current output volume or click "Generate NRRD header" to create a header file that can be loaded directly into Slicer

Notes:
- To increase number of decimal digits in a numeric input box, click <kbd>Ctrl</kbd> + <kbd>+</kbd>.
