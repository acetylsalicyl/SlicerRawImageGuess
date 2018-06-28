import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# RawImageGuessModule
#

class RawImageGuessModule(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Raw Image Guess Module" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Informatics"]
    self.parent.dependencies = []
    self.parent.contributors = ["Attila Nagy (University of Szeged, Szeged, Hungary)", "Csaba Pinter (Queens's University, Kingston, Ontario, Canada)", "Andras Lasso (Queens's University, Kingston, Ontario, Canada)", "Steve Pieper (Isomics Inc., Cambridge, MA, USA)" ] # replace with "Firstname Lastname (Organization)"
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
# RawImageGuessModuleWidget
#

class RawImageGuessModuleWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    loadImageCollapsibleButton = ctk.ctkCollapsibleButton()
    loadImageCollapsibleButton.text = "Load the image"
    self.layout.addWidget(loadImageCollapsibleButton)

    # Layout within the dummy collapsible button
    loadImageFormLayout = qt.QFormLayout(loadImageCollapsibleButton)

    # https://github.com/SlicerHeart/SlicerHeart/blob/master/DicomUltrasoundPlugin/DicomUltrasoundPlugin.py
    # from line 262
    # ctk widget: ple=ctk.ctkPathLineEdit()
    # ple.show()
    # https://github.com/PerkLab/PerkLabBootcamp/blob/master/Doc/day3_2_SlicerProgramming.pptx
    # qt.QRadioButton()
    # https://github.com/Slicer/Slicer/blob/master/Modules/Loadable/Segmentations/EditorEffects/Python/SegmentEditorIslandsEffect.py
    # lines 31-
  
    # Load an image
  
    self.inputFileSelector = ctk.ctkPathLineEdit()
    self.inputFileSelector.filters = ctk.ctkPathLineEdit.Files
    self.inputFileSelector.settingKey = 'RawImageGuessInputFile'
    loadImageFormLayout.addRow("Choose the file:", self.inputFileSelector)
    
    # Choose image parameters
    
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Set/choose image parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the collapsible button
    parametersGridLayout = qt.QGridLayout(parametersCollapsibleButton)

    
    self.operationRadioButtons = []
    self.widgetToOperationNameMap = {}

    self.radioButton8bit = qt.QRadioButton("8 bits per pixel")
    self.radioButton8bit.setToolTip(
      "Choose this option to set the pixel depth to be 8 bits.")
    self.operationRadioButtons.append(self.radioButton8bit)
    self.widgetToOperationNameMap[self.radioButton8bit] = BITS_8

    #TODO: Rename variables to convention radioButtonNBit (done? :) )
    self.RadioButton16BitSigned = qt.QRadioButton("16 bits signed bits per pixel")
    self.RadioButton16BitSigned.setToolTip(
      "Choose this option to set the pixel color depth to be 16 bits signed.")
    self.operationRadioButtons.append(self.RadioButton16BitSigned)
    self.widgetToOperationNameMap[self.RadioButton16BitSigned] = BITS_SIGNED_16

    self.RadioButton16BitUnSigned = qt.QRadioButton("16 bits unsigned bits per pixel")
    self.RadioButton16BitUnSigned.setToolTip(
      "Choose this option to set the pixel color depth to be 16 bits unsigned.")
    self.operationRadioButtons.append(self.RadioButton16BitUnSigned)
    self.widgetToOperationNameMap[self.RadioButton16BitUnSigned] = BITS_UNSIGNED_16

    self.RadioButton32BitSigned = qt.QRadioButton("32 bits signed color depth")
    self.RadioButton32BitSigned.setToolTip(
      "Choose this option to set the pixel color depth to be 32 bits signed.")
    self.operationRadioButtons.append(self.RadioButton32BitSigned)
    self.widgetToOperationNameMap[self.RadioButton32BitSigned] = BITS_SIGNED_32

    self.RadioButton32BitUnSigned = qt.QRadioButton("32 bits unsigned color depth")
    self.RadioButton32BitUnSigned.setToolTip(
      "Choose this option to set the pixel color depth to be 32 bits unsigned.")
    self.operationRadioButtons.append(self.RadioButton32BitUnSigned)
    self.widgetToOperationNameMap[self.RadioButton32BitUnSigned] = BITS_UNSIGNED_32


    operationLayout = qt.QGridLayout()
    operationLayout.addWidget(self.radioButton8bit,0,0,1,2)
    operationLayout.addWidget(self.RadioButton16BitSigned,1,0)
    operationLayout.addWidget(self.RadioButton16BitUnSigned,2,0)
    operationLayout.addWidget(self.RadioButton32BitSigned,1,1)
    operationLayout.addWidget(self.RadioButton32BitUnSigned,2,1)

    self.operationRadioButtons[0].setChecked(True)

    parametersGridLayout.addLayout(operationLayout, 0, 0, 1, 2)

    # self.applyButton = qt.QPushButton("Apply")
    # self.applyButton.objectName = self.__class__.__name__ + 'Apply'


    for operationRadioButton in self.operationRadioButtons:
      operationRadioButton.connect('toggled(bool)',
      lambda toggle, operationName=self.widgetToOperationNameMap[operationRadioButton]: self.onOperationSelectionChanged(operationName, toggle))


    # self.minimumSizeSpinBox.connect('valueChanged(int)', self.updateMRMLFromGUI)
    # self.applyButton.connect('clicked()', self.onApply)
  
    #
    # Image X and Y values
    #

    self.imageThresholdSliderWidgetX = ctk.ctkSliderWidget()
    self.imageThresholdSliderWidgetX.singleStep = 1
    self.imageThresholdSliderWidgetX.minimum = 1
    self.imageThresholdSliderWidgetX.maximum = 4000
    self.imageThresholdSliderWidgetX.value = 1
    self.imageThresholdSliderWidgetX.setToolTip("Set the X value for the image")
    parametersGridLayout.addWidget(qt.QLabel("X resolution: "), 1, 0)
    parametersGridLayout.addWidget(self.imageThresholdSliderWidgetX, 1, 1)

    self.imageThresholdSliderWidgetY = ctk.ctkSliderWidget()
    self.imageThresholdSliderWidgetY.singleStep = 1
    self.imageThresholdSliderWidgetY.minimum = 1
    self.imageThresholdSliderWidgetY.maximum = 4000
    self.imageThresholdSliderWidgetY.value = 1
    self.imageThresholdSliderWidgetY.setToolTip("Set the Y value for the image")
    parametersGridLayout.addWidget(qt.QLabel("Y resolution: "), 2, 0)
    parametersGridLayout.addWidget(self.imageThresholdSliderWidgetY, 2, 1)
        
    
    #
    # check box to trigger taking screen shots for later use in tutorials
    #
   
    self.ShowFileContents = qt.QPlainTextEdit()
    self.ShowFileContents.placeholderText = ("Placeholder")
    self.ShowFileContents.readOnly = True
    parametersGridLayout.addWidget(qt.QLabel("The first 100 bytes of the file"), 3, 0)
    parametersGridLayout.addWidget(self.ShowFileContents, 3, 1)

    self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
    self.enableScreenshotsFlagCheckBox.checked = 0
    self.enableScreenshotsFlagCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
    parametersGridLayout.addWidget(qt.QLabel("Enable screenshots: "), 4, 0)
    parametersGridLayout.addWidget(self.enableScreenshotsFlagCheckBox, 4, 1)
    
  def cleanup(self):
    pass

  def onSelect(self):
    #self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()
    pass

  def onOperationSelectionChanged(self, operationName, toggle):
    # logging.warning("ZZZ 2 " + str(widget) + ' ' + str(toggle))
    # operationName = self.widgetToOperationNameMap[widget]
    if not toggle:
      return
    logging.warning("ZZZ 4")
    if operationName == BITS_8:
      #something here
      logging.warning("ZZZ 8")
    if operationName == BITS_UNSIGNED_16:
      #something here
      logging.warning("ZZZ U16")
    if operationName == BITS_SIGNED_16:
      #something here
      logging.warning("ZZZ S16")
    if operationName == BITS_SIGNED_32:
      #something here
      logging.warning("ZZZ S32")
    if operationName == BITS_UNSIGNED_32:
      #something here
      logging.warning("ZZZ U32")

  def onApplyButton(self):
    logic = RawImageGuessModuleLogic()
    enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    imageThreshold = self.imageThresholdSliderWidget.value
    logic.run(self.inputSelector.currentNode(), self.outputSelector.currentNode(), imageThreshold, enableScreenshotsFlag)

#
# RawImageGuessModuleLogic
#

class RawImageGuessModuleLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  
  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    slicer.util.delayDisplay('Take screenshot: '+description+'.\nResult is available in the Annotations module.', 3000)

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
    qimage = ctk.ctkWidgetsUtils.grabWidget(widget)
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, 1, imageData)

  def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('RawImageGuessModuleTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True


class RawImageGuessModuleTest(ScriptedLoadableModuleTest):
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
    self.test_RawImageGuessModule1()

  def test_RawImageGuessModule1(self):
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
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = RawImageGuessModuleLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')

BITS_8 = "BITS_8"
BITS_SIGNED_16 = "BITS_SIGNED_16"
BITS_UNSIGNED_16 = "BITS_UNSIGNED_16"
BITS_SIGNED_32 = "BITS_SIGNED_32"
BITS_UNSIGNED_32 = "BITS_UNSIGNED_32"
