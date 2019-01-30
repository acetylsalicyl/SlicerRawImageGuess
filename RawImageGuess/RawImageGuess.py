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
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
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

    self.ui.outputVolumeNodeSelector.setMRMLScene(slicer.mrmlScene)

    # connections
    self.ui.inputFileSelector.connect('currentPathChanged(QString)', self.onCurrentPathChanged)
    self.ui.outputVolumeNodeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onOutputNodeSelected)
    self.ui.imageSizeXSliderWidget.connect('valueChanged(double)', self.onImageSizeChanged)
    self.ui.imageSizeYSliderWidget.connect('valueChanged(double)', self.onImageSizeChanged)
    self.ui.imageSizeZSliderWidget.connect('valueChanged(double)', self.onImageSizeChanged)
    self.ui.imageSkipSliderWidget.connect('valueChanged(double)', self.onImageSizeChanged)
    #self.ui.pixelTypeComboBox.connect('valueChanged(double)', self.onImageSizeChanged) TODO
    self.ui.updateButton.connect("clicked()", self.onUpdate)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass
    
  #TODO Consider endianness
  def onCurrentPathChanged(self, path):
    self.ui.inputFileSelector.addCurrentPathToHistory()
    self.onUpdate()

  def onOutputNodeSelected(self, node):
    self.onUpdate()

  def onImageSizeChanged(self, value):
    self.onUpdate()

  def onUpdate(self):
    self.logic.updateImage(
      self.ui.outputVolumeNodeSelector.currentNode(),
      self.ui.inputFileSelector.currentPath,
      int(self.ui.imageSizeXSliderWidget.value),
      int(self.ui.imageSizeYSliderWidget.value),
      int(self.ui.imageSizeZSliderWidget.value),
      int(self.ui.imageSkipSliderWidget.value),
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
      sizeX, sizeY, sizeZ, headerSize, pixelTypeString):
    """
    Run the actual algorithm
    """
    
    self.reader.SetFileName(imageFilePath)
    self.reader.SetDataExtent(0, sizeX-1, 0, sizeY-1, 0, sizeZ-1)
    if pixelTypeString == "8 bit unsigned":
      self.reader.SetDataScalarTypeToUnsignedChar()
    elif pixelTypeString == "8 bit signed":
      self.reader.SetDataScalarTypeToSignedChar()
    elif pixelTypeString == "16 bit unsigned":
      self.reader.SetDataScalarTypeToUnsignedShort()
    elif pixelTypeString == "16 bit signed":
      self.reader.SetDataScalarTypeToShort()
    # TODO
    self.reader.SetHeaderSize(headerSize)
    self.reader.Update()
    outputVolumeNode.SetImageDataConnection(self.reader.GetOutputPort())
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
