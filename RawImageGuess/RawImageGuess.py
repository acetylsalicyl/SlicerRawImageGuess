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
    self.parent.title = "RawImageGuess" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Informatics"]
    self.parent.dependencies = []
    self.parent.contributors = ["Attila Nagy (University of Szeged, Szeged, Hungary)", "Csaba Pinter (Queens's University, Kingston, Ontario, Canada)", "Andras Lasso (Queens's University, Kingston, Ontario, Canada)", "Steve Pieper (Isomics Inc., Cambridge, MA, USA)" ]
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# RawImageGuessWidget
#

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

    self.ui.imageSkipSliderWidget.enabled = False
    self.ui.imageSizeXSliderWidget.enabled = False
    self.ui.imageSizeYSliderWidget.enabled = False
    self.ui.imageSizeZSliderWidget.enabled = False
    self.ui.pixelTypeComboBox.enabled = False
    self.ui.endiannessComboBox.enabled = False
    
    self.ui.outputVolumeNodeSelector.setMRMLScene(slicer.mrmlScene)

    # connections
    self.ui.outputVolumeNodeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onOutputNodeSelected)
    self.ui.inputFileSelector.connect('currentPathChanged(QString)', self.onCurrentPathChanged)
    self.ui.endiannessComboBox.connect('valueChanged(double)', self.onImageSizeChanged)
    self.ui.imageSkipSliderWidget.connect('valueChanged(double)', self.onImageSizeChanged)
    self.ui.imageSizeXSliderWidget.connect('valueChanged(double)', self.onImageSizeChanged)
    self.ui.imageSizeYSliderWidget.connect('valueChanged(double)', self.onImageSizeChanged)
    self.ui.imageSizeZSliderWidget.connect('valueChanged(double)', self.onImageSizeChanged)
    self.ui.pixelTypeComboBox.connect('valueChanged(double)', self.onImageSizeChanged)
    self.ui.updateButton.connect("clicked()", self.onUpdate)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass
    
  
  def onCurrentPathChanged(self, path):
    self.ui.inputFileSelector.addCurrentPathToHistory()
    with open(self.ui.inputFileSelector.currentPath) as file:  
      fileHeader = file.read(5000)
      self.ui.textEdit.setText(fileHeader)
    if not self.ui.outputVolumeNodeSelector.currentNode(): 
      return
    self.onUpdate()
    
  def onOutputNodeSelected(self, node):
    self.ui.outputVolumeNodeSelector.currentNodeChanged
    self.ui.imageSkipSliderWidget.enabled = True
    self.ui.imageSizeXSliderWidget.enabled = True
    self.ui.imageSizeYSliderWidget.enabled = True
    self.ui.imageSizeZSliderWidget.enabled = True
    self.ui.pixelTypeComboBox.enabled = True
    self.ui.endiannessComboBox.enabled = True
    #slicer.util.setSliceViewerLayers(foreground=
    self.onUpdate()

  def onImageSizeChanged(self, value):
    self.onUpdate()

  def onUpdate(self):
    self.logic.updateImage(
      self.ui.outputVolumeNodeSelector.currentNode(),
      self.ui.inputFileSelector.currentPath,
      self.ui.endiannessComboBox.currentText,
      int(self.ui.imageSizeXSliderWidget.value),
      int(self.ui.imageSizeYSliderWidget.value),
      int(self.ui.imageSizeZSliderWidget.value),
      long(self.ui.imageSkipSliderWidget.value),
      self.ui.pixelTypeComboBox.currentText
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

  def updateImage(self, outputVolumeNode, imageFilePath,
      endiannessString, sizeX, sizeY, sizeZ, headerSize, pixelTypeString):
    """
    Run the actual algorithm
    """
    
    self.reader.SetFileName(imageFilePath)
    self.reader.SetDataExtent(0, sizeX-1, 0, sizeY-1, 0, sizeZ-1)
    if endiannessString == "Little endian":
      self.reader.SetDataByteOrderToLittleEndian()
    elif endiannessString == "Big endian":
      self.reader.SetDataByteOrderToBigEndian()
    if pixelTypeString == "8 bit unsigned":
      self.reader.SetDataScalarTypeToUnsignedChar()
    elif pixelTypeString == "8 bit signed":
      self.reader.SetDataScalarTypeToSignedChar()
    elif pixelTypeString == "16 bit unsigned":
      self.reader.SetDataScalarTypeToUnsignedShort()
    elif pixelTypeString == "16 bit signed":
      self.reader.SetDataScalarTypeToShort()
    elif pixelTypeString == "float":
      self.reader.SetDataScalarTypeToFloat()
    elif pixelTypeString == "double":
      self.reader.SetDataScalarTypeToDouble()
    self.reader.SetHeaderSize(headerSize)
    self.reader.Update()
    outputVolumeNode.SetImageDataConnection(self.reader.GetOutputPort())
     #outputVolumeNode.SetImageDataConnection(self.reader.GetOutputPort()) == Volume
    outputVolumeNode.Modified()

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