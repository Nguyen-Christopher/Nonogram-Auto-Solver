from win32gui import FindWindow, GetWindowRect, ShowWindow, SetForegroundWindow, GetWindowPlacement
import win32con
import time
import pyautogui
import cv2
import numpy as np
from Constants import DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT

windowHandler = 0

windowWidth = 0
windowHeight = 0

scaleX = 1.0
scaleY = 1.0

gameScreenRect : tuple[int,int,int,int] = None

def __getWindowHandler() -> int:
    global windowHandler

    if(windowHandler == 0):
        windowHandler = FindWindow(None, "BlueStacks App Player")
        if(windowHandler == 0):
            raise RuntimeError("Cannot find the game screen window.\nPlease make sure it's open.")
        
    return windowHandler


def __getWindowRect() -> tuple[tuple[int, int, int, int]]:
    windowHandler = __getWindowHandler()

    #Used to handle if the game window is minimized.
    windowPlacement = GetWindowPlacement(windowHandler)
    if(windowPlacement[1] == win32con.SW_SHOWMINIMIZED):
        ShowWindow(windowHandler, 9)
        windowPlacement = GetWindowPlacement(windowHandler)

    left, top, right, bottom = GetWindowRect(windowHandler) if windowPlacement[1] == win32con.SW_MAXIMIZE else windowPlacement[4]
    return (left, top, right - left, bottom - top)


#Returns the game image as well as two rects.
#First rect is relative to the game screen.
#Second rect is relative to the whole monitor.
def getGridImageRect() -> tuple[cv2.typing.MatLike, tuple[int,int,int,int], tuple[int, int, int, int]]:
    gameScreenRect = getGameScreenRect()
    gameScreenImage = getGameScreenImage(getGameScreenRect())
    
    #Gets only the grid portion of the game screen.
    gridContours = cv2.findContours(cv2.threshold(gameScreenImage, 40, 255, cv2.THRESH_BINARY_INV)[1], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    if(len(gridContours) == 0):
        raise RuntimeError("Couldn't find the grid for the puzzle. Make sure the whole grid is on screen.")

    #Ensures that we only get the grid and not any letters.
    gx, gy, gw, gh = cv2.boundingRect(next(grid for grid in gridContours if cv2.boundingRect(grid)[2] >= 400 and cv2.boundingRect(grid)[3] >= 400))
    return(gameScreenImage,(gx, gy, gw, gh),(gx + gameScreenRect[0], gy + gameScreenRect[1], gw, gh))


def getGameScreenRect(windowRect : tuple[int,int,int,int] = None) -> tuple[int,int,int,int]:
    global windowWidth, windowHeight, windowHandler

    if(windowRect == None):
        windowRect = __getWindowRect()

    windowWidth = windowRect[2]
    windowHeight = windowRect[3]

    pyautogui.press("alt")
    SetForegroundWindow(__getWindowHandler())

    time.sleep(0.25)

    #Get the white screen portion of the window.
    windowScreen = cv2.cvtColor(np.array(pyautogui.screenshot(region=windowRect)), cv2.COLOR_RGB2GRAY)
    whiteScreen = cv2.threshold(windowScreen, 70, 255, cv2.THRESH_BINARY)[1]
    whiteContours = cv2.findContours(whiteScreen, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    try:
        screenX, screenY, screenW, screenH = next(cv2.boundingRect(c) for c in whiteContours if (cv2.boundingRect(c)[2] >= 400 and cv2.boundingRect(c)[3] >= 800))
    except:
        raise RuntimeError("Could not find the game screen.\nMake sure that the app is started up.")

    return (screenX + windowRect[0], screenY + windowRect[1], screenW, screenH)


def getGameScale() -> tuple[float, float]:
    global windowWidth, windowHeight, scaleX, scaleY

    windowRect = __getWindowRect()

    if(windowRect != windowWidth or windowRect != windowHeight):
        gameScreenRect = getGameScreenRect(windowRect)
        scaleX = gameScreenRect[2] / DEFAULT_SCREEN_WIDTH
        scaleY = gameScreenRect[3] / DEFAULT_SCREEN_HEIGHT

    return (scaleX, scaleY)


def getGameScreenImage(gameScreenRect : tuple[int,int,int,int]):
    windowScreen = cv2.cvtColor(np.array(pyautogui.screenshot(region=gameScreenRect)), cv2.COLOR_RGB2GRAY)
    return windowScreen