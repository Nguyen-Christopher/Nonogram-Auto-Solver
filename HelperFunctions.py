from Constants import *
from threading import Event
from ScreenCapture import getGridImageRect, getGameScale
from PIL import Image
from PIL.Image import Image as IMG
import pyautogui
import os

assetImages : list[tuple[str, IMG]] = []
scaledImages : list[tuple[str, IMG]] = []

def generateCoordinates(grid : list[list[any]], gridLengthBox : int) ->tuple[list[tuple[int,int]],list[tuple[int,int]]]:

    #Get the grid rect again in case the game screen has moved or been resized.
    gridImageRect = getGridImageRect()

    #Used to find the color of the current square.
    gameScreen = gridImageRect[0]
    px, py, pw, ph = gridImageRect[1]

    #Used to calculate the coordinates for the mouse.
    wx, wy, ww, wh = gridImageRect[2]

    filledCoordinates = []
    emptyCoordinates = []

    squareSize = pw // gridLengthBox

    screenStartingPosition = (wx + squareSize // 2, wy + squareSize // 2)
    pixelStartingPosition = (px + 8, py + 8)

    for row in range(gridLengthBox):
        for col in range(gridLengthBox):

            x = screenStartingPosition[0] + (col * squareSize) + col
            y = screenStartingPosition[1] + (row * squareSize) + row

            pixelX = pixelStartingPosition[0] + (col * squareSize) + col
            pixelY = pixelStartingPosition[1] + (row * squareSize) + row

            #Get all locations where the squares should be empty or filled.
            grayValue = gameScreen[pixelY][pixelX]
            if(grid[row][col] == 1 and grayValue >= 70):
                filledCoordinates.append((x,y))
                pass
            elif(grid[row][col] == 0 and grayValue < 70):
                emptyCoordinates.append((x,y))
                pass
                
    return (emptyCoordinates, filledCoordinates)


def findAndClickButton(images : list[str], stopEvent : Event, delay : float = 0) -> str:
    for img in images:
        if(not stopEvent.is_set()):
            try:
                buttonLocation = pyautogui.locateCenterOnScreen(getImage(img), confidence=.8)
                pyautogui.leftClick((buttonLocation[0], buttonLocation[1]))
                stopEvent.wait(delay)
                return img
            except:
                continue
        else:
            return None
    return None


def findIfImageExists(images : list[str], stopEvent : Event):
    for img in images:
        if(not stopEvent.is_set()):
            try:
                pyautogui.locateOnScreen(getImage(img), confidence=.8)
                return True
            except:
                continue
        else:
            return False

    return False


def initImageList():
    global assetImages
    assetImages = [(assetImage, Image.open(getImagePath(assetImage))) for assetImage in ASSET_IMAGES] if len(assetImages) == 0 else assetImages


def getImage(imageName : str):
    global assetImages
    gameScale = getGameScale()
    image = next(im[1] for im in iter(assetImages) if im[0] == imageName)
    return image.resize((int(image.width * gameScale[0]),int(image.height * gameScale[1])))

            
def getImagePath(imageName : str) -> str:
    return f"{os.path.dirname(os.path.realpath(__file__))}\\Assets\\{imageName}.png"