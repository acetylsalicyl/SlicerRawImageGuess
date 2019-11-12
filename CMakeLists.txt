cmake_minimum_required(VERSION 3.5)

project(RawImageGuess)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/acetylsalicyl/SlicerRawImageGuess")
set(EXTENSION_CATEGORY "Visualization")
set(EXTENSION_CONTRIBUTORS "Attila Nagy (University of Szeged, Szeged, Hungary), Csaba Pintér (Qeen's University, Kingston, Ontario, Canada), Andras Lasso (Qeen's University, Kingston, Ontario, Canada), Steve Pieper (Isomics Inc., Cambridge, MA, USA)")
set(EXTENSION_DESCRIPTION "This extension allows loading images from unknown file formats. Image dimensions, bit depth, etc. parameters can be determined by trial and error, based on live preview.")
set(EXTENSION_ICONURL "https://github.com/acetylsalicyl/SlicerRawImageGuess/raw/master/RawImageGuess.png")
set(EXTENSION_SCREENSHOTURLS "https://github.com/acetylsalicyl/SlicerRawImageGuess/raw/master/Screenshot01.png https://github.com/acetylsalicyl/SlicerRawImageGuess/raw/master/Screenshot02.png")
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
