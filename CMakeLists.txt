cmake_minimum_required(VERSION 3.5)

project(RawImageGuess)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/RawImageGuess")
set(EXTENSION_CATEGORY "Visualization")
set(EXTENSION_CONTRIBUTORS "Attila Nagy (University of Szeged, Szeged, Hungary), Csaba Pintér (Qeen's University, Kingston, Ontario, Canada), András Lasso (Qeen's University, Kingston, Ontario, Canada), Steve Pieper (Isomics Inc., Cambridge, MA, USA)")
set(EXTENSION_DESCRIPTION "This extension is intended to help in finding out the dimensions, the bit depth and a few other needed properties of unknown image types.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/RawImageGuess.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/RawImageGuess/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(RawImageGuessModule)
add_subdirectory(RawImageGuessMdule)
add_subdirectory(RawImageGuessModule)
add_subdirectory(RawImageGuess)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
