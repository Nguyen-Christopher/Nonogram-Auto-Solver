from enum import Enum
import cv2
from skimage.metrics import structural_similarity as compare_ssim
from tkinter import ttk
from abc import ABC, abstractmethod
import threading

class StoppableThread(threading.Thread):

    stopEvent : threading.Event

    def __init__(self, group = None, target = None, name = None, args = ..., kwargs = None, *, daemon = None):
        self.stopEvent = threading.Event()
        super().__init__(group, target, name, [*args, self.stopEvent], kwargs, daemon=daemon)

    def stopThread(self):
        self.stopEvent.set()


class FrameWithInfoLabels(ttk.Frame):
    infoLabel1 : ttk.Label
    infoLabel2 : ttk.Label

    @abstractmethod
    def updateLabel(self, message : str, frameLabel : ttk.Label = None, stopEvent : threading.Event = None):
        pass
    
    @abstractmethod
    def showButtons(self):
        pass


class InfiniteSolverModes(Enum):
    Regular = 1
    DailyChallenges = 2


class GameScreenInfo():
    gameScreenImage : cv2.typing.MatLike
    rowRects : list[tuple[int,int,int,int]]
    colRects: list[tuple[int,int,int,int]]

    def __init__(self, gameScreenImage : cv2.typing.MatLike, rowRects : list[tuple[int,int,int,int]], colRects : list[tuple[int,int,int,int]]):
        self.gameScreenImage = gameScreenImage
        self.rowRects = rowRects
        self.colRects = colRects


class ImageNumberLibrary():
    imageNumberLibrary : list[tuple[cv2.typing.MatLike,int]]
    
    def __init__(self):
        self.imageNumberLibrary = []

    def findNumber(self, image : cv2.typing.MatLike) -> int:
        for imageNum in self.imageNumberLibrary:

            resizedImage = cv2.resize(image, (imageNum[0].shape[1], imageNum[0].shape[0]))
            (score, diff) = compare_ssim(imageNum[0], resizedImage, full=True)
            
            if(score > .8):
                return imageNum[1]
            
        return None

    def addNumber(self, image : cv2.typing.MatLike, number: int):
        self.imageNumberLibrary.append((image, number))

    def clearLibrary(self):
        self.imageNumberLibrary.clear()