from Classes import FrameWithInfoLabels
from GridParser import getGameScreenInfo, getHintImageList, parseColHints, parseRowHints
from NonogramSolver import getBoardSolution
from HelperFunctions import generateCoordinates
from threading import Event
import pyautogui

pyautogui.PAUSE = 0.05

def __printProgress(message : str, frame : FrameWithInfoLabels = None, stopEvent : Event = None):
    if(frame != None and stopEvent != None):
        frame.updateLabel(message, stopEvent)
        stopEvent.wait(0.25)
    else:
        print(message)


def __isStopEventSet(stopEvent : Event = None):
    return stopEvent != None and stopEvent.is_set()


def solveCurrentNonogram(frame : FrameWithInfoLabels = None, stopEvent : Event = None):

    try:
        #Gets the game board and grid info.
        __printProgress("Getting grid info...", frame, stopEvent)
        gameScreenInfo = getGameScreenInfo()

        if(__isStopEventSet(stopEvent)):
            return

        #Get the list of hint images.
        __printProgress("Getting the list of hint images...", frame, stopEvent)
        hintImages = getHintImageList(gameScreenInfo)

        if(__isStopEventSet(stopEvent)):
            return

    except Exception as e:
        raise RuntimeError(f"Something went wrong when examining the grid.\n\n{e}")


    #Parse the row and column hints.
    try:
        __printProgress("Parsing Row Hints...", frame, stopEvent)
        rowHints = parseRowHints(hintImages[0])

        if(__isStopEventSet(stopEvent)):
            return

        __printProgress("Parsing Column Hints...", frame, stopEvent)
        colHints = parseColHints(hintImages[1])

        if(__isStopEventSet(stopEvent)):
            return

        if(len(rowHints) != len(rowHints) or not all(any(row) for row in rowHints) or not all(any(col) for col in colHints)):
            raise Exception("A row or column is missing.")
            
    except Exception as e:
        raise RuntimeError(f"Something went wrong when parsing the hints:\n\n{e}")

    #Find the solution based on the given hints.
    try:
        __printProgress("Finding Solution...", frame, stopEvent)
        solution = getBoardSolution(rowHints, colHints)

        if(__isStopEventSet(stopEvent)):
            return
        
    except Exception as e:
        raise RuntimeError(f"Something went wrong when generating a solution:\n\n{e}")

    #Generate all coordinates to click the screen.
    coordinates = generateCoordinates(solution, len(rowHints))

    #Click on the coordinates given.
    __printProgress("Printing solution...", frame, stopEvent)
    
    #Loop through all the coordinates and fill the grid.
    #Start with unclicking on the wrong filled squares to prevent from going over the limit.
    for locations in coordinates:
        for coord in locations:
            if(__isStopEventSet(stopEvent)):
                return
            pyautogui.click(coord[0], coord[1])


if __name__ == "__main__":
    solveCurrentNonogram()