import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# RawImageGuess
#

class RawImageGuess(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Raw Image Guess"
    self.parent.categories = ["Informatics"]
    self.parent.dependencies = []
    self.parent.contributors = ["Attila Nagy (University of Szeged, Szeged, Hungary)", "Csaba Pinter (Queens's University, Kingston, Ontario, Canada)", "Andras Lasso (Queens's University, Kingston, Ontario, Canada)", "Steve Pieper (Isomics Inc., Cambridge, MA, USA)" ]
    self.parent.helpText = """
This module can help loading images stored in an unkwnon file format by allowing quickly trying various voxel types and image sizes. See more information at the <a href="https://github.com/acetylsalicyl/SlicerRawImageGuess">extension's website</a>.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Attila Nagy.
""" # replace with organization, grant and thanks.

#
# RawImageGuessWidget
#

def toLong(value):
  import sys
  if sys.version_info[0] < 3:
    return long(value)
  else:
    return int(value)

class RawImageGuessWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    self.logic = RawImageGuessLogic()

    # Load widget from .ui file (created by Qt Designer)
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/RawImageGuess.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    
    self.ui.outputVolumeNodeSelector.setMRMLScene(slicer.mrmlScene)

    self.updateButtonStates()

    # connections
    self.ui.outputVolumeNodeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onOutputNodeSelected)
    self.ui.inputFileSelector.connect('currentPathChanged(QString)', self.onCurrentPathChanged)
    self.ui.endiannessComboBox.connect('currentIndexChanged(int)', self.onImageSizeChanged)
    self.ui.imageSkipSliderWidget.connect('valueChanged(double)', self.onImageSizeChanged)
    self.ui.imageSizeXSliderWidget.connect('valueChanged(double)', self.onImageSizeChanged)
    self.ui.imageSizeYSliderWidget.connect('valueChanged(double)', self.onImageSizeChanged)
    self.ui.imageSizeZSliderWidget.connect('valueChanged(double)', self.onImageSizeChanged)
    self.ui.skipSlicesSliderWidget.connect('valueChanged(double)', self.onImageSizeChanged)
    self.ui.imageSpacingXSliderWidget.connect('valueChanged(double)', self.onImageSizeChanged)
    self.ui.imageSpacingYSliderWidget.connect('valueChanged(double)', self.onImageSizeChanged)
    self.ui.imageSpacingZSliderWidget.connect('valueChanged(double)', self.onImageSizeChanged)
    self.ui.pixelTypeComboBox.connect('currentIndexChanged(int)', self.onImageSizeChanged)
    self.ui.fitToViewsCheckBox.connect("toggled(bool)", self.onFitToViewsCheckboxClicked)
    self.ui.updateButton.connect("clicked()", self.onUpdateButtonClicked)
    self.ui.updateButton.connect("checkBoxToggled(bool)", self.onUpdateCheckboxClicked)
    self.ui.generateNrrdHeaderButton.connect("clicked()", self.onGenerateNrrdHeaderButtonClicked)

    # Add vertical spacer
    self.layout.addStretch(1)

    self.loadParametersFromSettings()

  def cleanup(self):
    pass

  def enter(self):
    pass

  def exit(self):
    # disable auto-update when exiting the module to prevent accidental
    # updates of other volumes (when the current output volume is deleted)
    self.ui.updateButton.checkState = qt.Qt.Unchecked
  
  def onCurrentPathChanged(self, path):
    self.ui.inputFileSelector.addCurrentPathToHistory()
    if not self.ui.outputVolumeNodeSelector.currentNode(): 
      return
    if self.ui.updateButton.checkState == qt.Qt.Checked:
      self.onUpdate()
      self.showOutputVolume()

  def updateButtonStates(self):
    enabled = bool(self.ui.inputFileSelector.currentPath)
    self.ui.updateButton.enabled = enabled
    if enabled:
      self.ui.updateButton.toolTip = "Read file into output volume"
    else:
      self.ui.updateButton.toolTip = "Select input file"

    enabled = ( (self.ui.outputVolumeNodeSelector.currentNode())
      and (self.ui.inputFileSelector.currentPath) )
    self.ui.generateNrrdHeaderButton.enabled = enabled
    if enabled:
      self.ui.generateNrrdHeaderButton.toolTip = "Generate NRRD header file (.nhdr)"
    else:
      self.ui.generateNrrdHeaderButton.toolTip = "Select input file and output volume"

  def showOutputVolume(self):
    selectedVolumeNode = self.ui.outputVolumeNodeSelector.currentNode()
    if selectedVolumeNode:
      fit = self.ui.fitToViewsCheckBox.checked
      slicer.util.setSliceViewerLayers(background=selectedVolumeNode, fit=fit)

  def onOutputNodeSelected(self, node):
    self.updateButtonStates()
    self.logic.newImage()
    if self.ui.updateButton.checkState == qt.Qt.Checked:
      self.onUpdate()
      self.showOutputVolume()

  def onImageSizeChanged(self, value):
    if self.ui.updateButton.checkState == qt.Qt.Checked:
      self.onUpdate()
      self.showOutputVolume()

  def saveParametersToSettings(self):
    settings = qt.QSettings()
    settings.setValue('RawImageGuess/pixelType', self.ui.pixelTypeComboBox.currentText)
    settings.setValue('RawImageGuess/endianness', self.ui.endiannessComboBox.currentText)
    settings.setValue('RawImageGuess/headerSize', self.ui.imageSkipSliderWidget.value)    
    settings.setValue('RawImageGuess/sizeX', self.ui.imageSizeXSliderWidget.value)
    settings.setValue('RawImageGuess/sizeY', self.ui.imageSizeYSliderWidget.value)
    settings.setValue('RawImageGuess/sizeZ', self.ui.imageSizeZSliderWidget.value)
    settings.setValue('RawImageGuess/skipSlices', self.ui.skipSlicesSliderWidget.value)
    settings.setValue('RawImageGuess/spacingX', self.ui.imageSpacingXSliderWidget.value)
    settings.setValue('RawImageGuess/spacingY', self.ui.imageSpacingXSliderWidget.value)
    settings.setValue('RawImageGuess/spacingZ', self.ui.imageSpacingXSliderWidget.value)

  def loadParametersFromSettings(self):
    settings = qt.QSettings()
    self.ui.pixelTypeComboBox.currentText = settings.value('RawImageGuess/pixelType')
    self.ui.endiannessComboBox.currentText = settings.value('RawImageGuess/endianness')
    self.ui.imageSkipSliderWidget.value = toLong(settings.value('RawImageGuess/headerSize', 0))
    self.ui.imageSizeXSliderWidget.value = toLong(settings.value('RawImageGuess/sizeX', 200))
    self.ui.imageSizeYSliderWidget.value = toLong(settings.value('RawImageGuess/sizeY', 200))
    self.ui.imageSizeZSliderWidget.value = toLong(settings.value('RawImageGuess/sizeZ', 1))
    self.ui.skipSlicesSliderWidget.value = toLong(settings.value('RawImageGuess/skipSlices', 0))
    self.ui.imageSpacingXSliderWidget.value = float(settings.value('RawImageGuess/spacingX', 1.0))
    self.ui.imageSpacingYSliderWidget.value = float(settings.value('RawImageGuess/spacingY', 1.0))
    self.ui.imageSpacingZSliderWidget.value = float(settings.value('RawImageGuess/spacingZ', 1.0))

  def onFitToViewsCheckboxClicked(self, enable):
    self.showOutputVolume()

  def onUpdateCheckboxClicked(self, enable):
    if enable:
      self.onUpdate()
      self.showOutputVolume()

  def onUpdateButtonClicked(self):
    if self.ui.updateButton.checkState == qt.Qt.Checked:
      # If update button is untoggled then make it unchecked, too
      self.ui.updateButton.checkState = qt.Qt.Unchecked
    self.onUpdate()
    self.showOutputVolume()

  def onGenerateNrrdHeaderButtonClicked(self):
    if not self.ui.generateNrrdHeaderButton.enabled:
      return
    if not self.ui.inputFileSelector.currentPath:
      return
    self.saveParametersToSettings()      
    generatedFilename = self.logic.generateImageHeader(
      self.ui.outputVolumeNodeSelector.currentNode(),
      self.ui.inputFileSelector.currentPath,
      self.ui.pixelTypeComboBox.currentText,
      self.ui.endiannessComboBox.currentText,
      toLong(self.ui.imageSizeXSliderWidget.value),
      toLong(self.ui.imageSizeYSliderWidget.value),
      toLong(self.ui.imageSizeZSliderWidget.value),
      toLong(self.ui.imageSkipSliderWidget.value),
      toLong(self.ui.skipSlicesSliderWidget.value),
      float(self.ui.imageSpacingXSliderWidget.value),
      float(self.ui.imageSpacingYSliderWidget.value),
      float(self.ui.imageSpacingZSliderWidget.value)
      )
    slicer.util.delayDisplay("Image header file created at "+generatedFilename, autoCloseMsec=2000)

  def onUpdate(self):
    if not self.ui.updateButton.enabled:
      return

    # Determine if we need to create a new volume
    createNewVolume = False
    pixelTypeString = self.ui.pixelTypeComboBox.currentText
    (scalarType, numberOfComponents) = RawImageGuessLogic.scalarTypeComponentFromString(pixelTypeString)
    if not self.ui.outputVolumeNodeSelector.currentNode():
      createNewVolume = True
    else:
      if (numberOfComponents > 1) != self.ui.outputVolumeNodeSelector.currentNode().IsA("vtkMRMLVectorVolumeNode"):
        createNewVolume = True
    if createNewVolume:
      self.ui.outputVolumeNodeSelector.addNode("vtkMRMLScalarVolumeNode" if numberOfComponents == 1 else "vtkMRMLVectorVolumeNode")

    if not self.ui.inputFileSelector.currentPath:
      return
    self.saveParametersToSettings()      
    self.logic.updateImage(
      self.ui.outputVolumeNodeSelector.currentNode(),
      self.ui.inputFileSelector.currentPath,
      pixelTypeString,
      self.ui.endiannessComboBox.currentText,
      toLong(self.ui.imageSizeXSliderWidget.value),
      toLong(self.ui.imageSizeYSliderWidget.value),
      toLong(self.ui.imageSizeZSliderWidget.value),
      toLong(self.ui.imageSkipSliderWidget.value),
      toLong(self.ui.skipSlicesSliderWidget.value),
      float(self.ui.imageSpacingXSliderWidget.value),
      float(self.ui.imageSpacingYSliderWidget.value),
      float(self.ui.imageSpacingZSliderWidget.value)
      )

#
# RawImageGuessLogic
#

class RawImageGuessLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  
  def __init__(self):
    self.reader = vtk.vtkImageReader2()

  def newImage(self):
    # If a new image is selected then we create an independent reader
    # (to prevent overwriting previous volumes with updateImage).
    # We do not create a new reader on each updateImage to improve performence
    # (avoid reallocation of the image).
    self.reader = vtk.vtkImageReader2()

  def updateImage(self, outputVolumeNode, imageFilePath,
      pixelTypeString, endiannessString, sizeX, sizeY, sizeZ, headerSize, skipSlices,
      spacingX, spacingY, spacingZ):
    """
    Reads image into output volume
    """
    
    (scalarType, numberOfComponents) = RawImageGuessLogic.scalarTypeComponentFromString(pixelTypeString)
    sliceSize = sizeX * sizeY * vtk.vtkDataArray.GetDataTypeSize(scalarType) * numberOfComponents
    totalHeaderSize = headerSize + skipSlices * sliceSize
    import os
    totalFilesize = os.path.getsize(imageFilePath)
    voxelDataSize = totalFilesize - totalHeaderSize
    maxNumberOfSlices = int(voxelDataSize/sliceSize)
    finalSizeZ = min(sizeZ, maxNumberOfSlices)

    self.reader.SetFileName(imageFilePath)
    self.reader.SetFileDimensionality(3)
    self.reader.SetDataExtent(0, sizeX-1, 0, sizeY-1, 0, finalSizeZ-1)
    if endiannessString == "Little endian":
      self.reader.SetDataByteOrderToLittleEndian()
    else:
      self.reader.SetDataByteOrderToBigEndian()
    self.reader.SetDataScalarType(scalarType)
    self.reader.SetNumberOfScalarComponents(numberOfComponents)
    self.reader.SetHeaderSize(totalHeaderSize)
    self.reader.SetFileLowerLeft(True) # to match input from NRRD reader
    self.reader.Update()
    outputVolumeNode.SetImageDataConnection(self.reader.GetOutputPort())
    # We assume file is in LPS and invert first and second axes
    # to get volume in RAS.
    ijkToRas = vtk.vtkMatrix4x4()
    ijkToRas.SetElement(0,0, -spacingX)
    ijkToRas.SetElement(1,1, -spacingY)
    ijkToRas.SetElement(2,2, spacingZ)
    outputVolumeNode.SetIJKToRASMatrix(ijkToRas)
    outputVolumeNode.Modified()

  def generateImageHeader(self, outputVolumeNode, imageFilePath,
      pixelTypeString, endiannessString, sizeX, sizeY, sizeZ, headerSize, skipSlices,
      spacingX, spacingY, spacingZ):
    """
    Reads image into output volume
    """
    
    (scalarType, numberOfComponents) = RawImageGuessLogic.scalarTypeComponentFromString(pixelTypeString)
    sliceSize = sizeX * sizeY * vtk.vtkDataArray.GetDataTypeSize(scalarType) * numberOfComponents
    totalHeaderSize = headerSize + skipSlices * sliceSize
    import os
    totalFilesize = os.path.getsize(imageFilePath)
    voxelDataSize = totalFilesize - totalHeaderSize
    maxNumberOfSlices = voxelDataSize/sliceSize
    finalSizeZ = min(sizeZ, maxNumberOfSlices)

    import os
    filename, file_extension = os.path.splitext(imageFilePath)
    nhdrFilename = filename + ".nhdr"

    with open(nhdrFilename, "w") as headerFile:
      headerFile.write("NRRD0004\n")
      headerFile.write("# Complete NRRD file format specification at:\n")
      headerFile.write("# http://teem.sourceforge.net/nrrd/format.html\n")

      if scalarType == vtk.VTK_UNSIGNED_CHAR:
        typeStr = "uchar"
      elif scalarType == vtk.VTK_SIGNED_CHAR:
        typeStr = "signed char"
      elif scalarType == vtk.VTK_UNSIGNED_SHORT:
        typeStr = "ushort"
      elif scalarType == vtk.VTK_SHORT:
        typeStr = "short"
      elif scalarType == vtk.VTK_FLOAT:
        typeStr = "float"
      elif scalarType == vtk.VTK_DOUBLE:
        typeStr = "double"
      else:
        raise ValueError('Unknown scalar type')
      headerFile.write("type: {0}\n".format(typeStr))

      if numberOfComponents == 1:
        headerFile.write("dimension: 3\n")
        headerFile.write("space: left-posterior-superior\n")
        headerFile.write("sizes: {0} {1} {2}\n".format(sizeX, sizeY, finalSizeZ))
        headerFile.write("space directions: ({0}, 0.0, 0.0) (0.0, {1}, 0.0) (0.0, 0.0, {2})\n".format(spacingX, spacingY, spacingZ))
        headerFile.write("kinds: domain domain domain\n")
      else:
        headerFile.write("dimension: 4\n")
        headerFile.write("space: left-posterior-superior\n")
        headerFile.write("sizes: {3} {0} {1} {2}\n".format(sizeX, sizeY, finalSizeZ, numberOfComponents))
        headerFile.write("space directions: ({0}, 0.0, 0.0) (0.0, {1}, 0.0) (0.0, 0.0, {2})\n".format(spacingX, spacingY, spacingZ))
        headerFile.write("kinds: vector domain domain domain\n")

      if endiannessString == "Little endian":
        headerFile.write("endian: little\n")
      else:
        headerFile.write("endian: big\n")

      headerFile.write("encoding: raw\n")
      headerFile.write("space origin: (0.0, 0.0, 0.0)\n")

      if totalHeaderSize > 0:
        headerFile.write("byte skip: {0}\n".format(totalHeaderSize))
      headerFile.write("data file: {0}\n".format(os.path.basename(imageFilePath)))
    
    return nhdrFilename

  @staticmethod
  def scalarTypeComponentFromString(scalarTypeStr):
    if scalarTypeStr == "8 bit unsigned":
      return (vtk.VTK_UNSIGNED_CHAR, 1)
    elif scalarTypeStr == "8 bit signed":
      return (vtk.VTK_SIGNED_CHAR, 1)
    elif scalarTypeStr == "16 bit unsigned":
      return (vtk.VTK_UNSIGNED_SHORT, 1)
    elif scalarTypeStr == "16 bit signed":
      return (vtk.VTK_SHORT, 1)
    elif scalarTypeStr == "float":
      return (vtk.VTK_FLOAT, 1)
    elif scalarTypeStr == "double":
      return (vtk.VTK_DOUBLE, 1)
    elif scalarTypeStr == "24 bit RGB":
      return (vtk.VTK_UNSIGNED_CHAR, 3)

  def hasImageData(self, volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True


class RawImageGuessTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_RawImageGuess1()

  def test_RawImageGuess1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import SampleData
    SampleData.downloadFromURL(
      nodeNames='FA',
      fileNames='FA.nrrd',
      uris='http://slicer.kitware.com/midas3/download?items=5767')
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = RawImageGuessLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')