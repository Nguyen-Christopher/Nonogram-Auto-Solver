import tkinter as tk
from Constants import *
from HelperFunctions import findAndClickButton, findIfImageExists, initImageList
from Main import solveCurrentNonogram
from Classes import InfiniteSolverModes, FrameWithInfoLabels, StoppableThread
from threading import Event
from tkinter import ttk

class NonogramSolverApp(tk.Tk):
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)

        self.title("Nonogram Solver")
        self.resizable(width=False, height=False)
        self.minsize(600, 200)
        self.attributes(topmost=True)

        container = tk.Frame(self)  
        container.pack()

        self.frames = {
            MainMenu : MainMenu(container, self),
            InfiniteModeSelect : InfiniteModeSelect(container, self),
            SolverProgress : SolverProgress(container, self)
        }

        self.showFrame(MainMenu)


    def showFrame(self, cont, currentFrame : ttk.Frame = None):
        if(currentFrame != None):
            currentFrame.event_generate("<<on_frame_hide>>")

        frame : tk.Frame = self.frames[cont]
        frame.event_generate("<<on_frame_show>>")

        frame.tkraise()
        self.update()


    def startSolver(self, currentFrame : ttk.Frame, isInfinite : bool, infiniteMode : InfiniteSolverModes = None):
        frame : SolverProgress = self.frames[SolverProgress]
        frame.isInfinite = isInfinite
        frame.infiniteMode = infiniteMode
        self.showFrame(SolverProgress, currentFrame)


class MainMenu(tk.Frame):
    def __init__(self, parent, controller : NonogramSolverApp):
        super().__init__(parent)

        self.grid(row = 0, column = 0)

        self.label = ttk.Label(self, text = "Nonogram Puzzle Solver", font=(None, 15) )

        self.button1 = ttk.Button(self, text="Solve On-Screen Puzzle", padding=5,
        command = lambda : controller.startSolver(self, False))

        self.button2 = ttk.Button(self, text="Solve Infinite Puzzles", padding=5,
        command= lambda : controller.showFrame(InfiniteModeSelect, self))

        self.bind("<<on_frame_show>>", self.onFrameShow)
        self.bind("<<on_frame_hide>>", self.onFrameHide)

    def onFrameShow(self, event):
        self.grid()
        self.label.grid(row = 0, column = 0, pady=10, padx = 20) 
        self.button1.grid(row = 1, column = 0,pady=20)
        self.button2.grid(row = 2, column = 0,pady=20)

    def onFrameHide(self, event):
        self.label.grid_forget()
        self.button1.grid_forget()
        self.button2.grid_forget()
        self.grid_remove()


class InfiniteModeSelect(tk.Frame):
    def __init__(self, parent, controller : NonogramSolverApp):
        super().__init__(parent)

        self.grid(row = 0, column = 0)

        self.label = ttk.Label(self, text = "Select which levels to loop...", font=(None, 12) )

        self.button1 = ttk.Button(self, text="Normal Levels", padding=5,
        command = lambda : controller.startSolver(self, True, InfiniteSolverModes.Regular))

        self.button2 = ttk.Button(self, text="Daily Challenges", padding=5,
        command= lambda : controller.startSolver(self, True, InfiniteSolverModes.DailyChallenges))

        self.button3 = ttk.Button(self, text="Back to Menu", padding=5,
        command= lambda : controller.showFrame(MainMenu, self))

        self.bind("<<on_frame_show>>", self.onFrameShow)
        self.bind("<<on_frame_hide>>", self.onFrameHide)

    def onFrameShow(self, event):
        self.grid()
        self.label.grid(row = 0, column = 0, pady=10, padx = 20) 
        self.button1.grid(row = 1, column = 0,pady=20)
        self.button2.grid(row = 2, column = 0,pady=20)
        self.button3.grid(row = 3, column = 0,pady=20)

    def onFrameHide(self, event):
        self.label.grid_forget()
        self.button1.grid_forget()
        self.button2.grid_forget()
        self.button3.grid_forget()
        self.grid_remove()

class SolverProgress(FrameWithInfoLabels):
    solverThread : StoppableThread = None
    isInfinite : bool = False
    infiniteMode : InfiniteSolverModes = None
    levelsCompleted : int = 0

    def __init__(self, parent, controller : NonogramSolverApp):
        super().__init__(parent)
        
        self.controller = controller

        self.grid(row = 0, column = 0)
        self.grid_columnconfigure((0, 1, 2), weight=1)

        self.infoLabel1 = ttk.Label(self, wraplength=500)
        self.infoLabel1.grid(row=0, column=0, columnspan=3, pady=20, padx=20)
        self.infoLabel2 = ttk.Label(self)

        self.cancelButton = ttk.Button(self, text="Cancel", padding=5,
        command = lambda : self.cancelSolver())
        self.backButton = ttk.Button(self, text="Go Back", padding=5,
        command = lambda : self.controller.showFrame(MainMenu, self))
        self.tryAgainButton = ttk.Button(self, text="Try Again", padding=5,
        command = lambda : [self.startSolver()])

        self.bind("<<on_frame_show>>", self.onFrameShow)
        self.bind("<<on_frame_hide>>", self.onFrameHide)

    def onFrameShow(self, event):
        self.startSolver()

    def onFrameHide(self, event):
        self.clearFrame()        

    def startSolver(self):
        self.setUpGui()
        
        if(self.isInfinite):
            self.solverThread = StoppableThread(target=solveInfinitePuzzles, args=(self, self.infiniteMode, self.levelsCompleted), daemon=True)
        else:
            self.solverThread = StoppableThread(target=solveOnePuzzle, args=(self,), daemon=True)

        self.solverThread.start()

    def cancelSolver(self):
        self.solverThread.stopThread()
        self.controller.showFrame((MainMenu), self)

    def setUpGui(self):
        self.grid()
        self.infoLabel1.config(text ="Starting infinite solver..." if self.isInfinite else "Finding on-screen board...")
        self.infoLabel1.grid()

        self.cancelButton.grid(row=2 if self.isInfinite else 1, column=1, pady=20)

        if(self.isInfinite):
            self.infoLabel2.config(text = f"Levels Completed: {self.levelsCompleted}")
            self.infoLabel2.grid(row=1, column=0, columnspan=3, pady=40, padx=40)        
        else:
            self.infoLabel2.grid_forget()

        self.backButton.grid_forget()
        self.tryAgainButton.grid_forget()
        
    def updateLabel(self, message : str, stopEvent : Event = None, frameLabel : ttk.Label = None):
        if(stopEvent == None or not stopEvent.is_set()):
            label = self.infoLabel1 if frameLabel == None else frameLabel 
            label.config(text=message)
            label.update()

    def showButtons(self):
        self.cancelButton.grid_forget()
        self.backButton.grid(row = 2 if self.isInfinite else 1, column = 0, pady=40, padx=40)
        self.tryAgainButton.grid(row = 2 if self.isInfinite else 1, column = 2, pady=40, padx=40)

    def clearFrame(self):
        self.infoLabel1.grid_remove()
        self.infoLabel2.grid_forget()
        self.cancelButton.grid_forget()
        self.tryAgainButton.grid_forget()
        self.backButton.grid_forget()
        self.grid_remove()


def solveOnePuzzle(frame : FrameWithInfoLabels, stopEvent : Event):
    stopEvent.wait(1)
    try:
        solveCurrentNonogram(frame, stopEvent)
        if(not stopEvent.is_set()):
            frame.updateLabel("Finished!")
            frame.showButtons()
    except Exception as e:
        if(not stopEvent.is_set()):
            frame.updateLabel(str(e))
            frame.showButtons()


#Used to reset the game back to the main menu.
def moveToTitle(stopEvent : Event):
    buttons = [BACK, MY_COLLECTION_WHITE, MAIN, MAIN_BLUE, CONTINUE_WHITE]
    iterButtons = iter(buttons)

    while(not findIfImageExists([NONOGRAM_TITLE], stopEvent)):
        try:
            findAndClickButton([next(iterButtons)], stopEvent, 1)
            if(stopEvent.is_set()):
                return
        except StopIteration:
            iterButtons = iter(buttons)

def solveInfinitePuzzles(frame : FrameWithInfoLabels, solverMode : InfiniteSolverModes, startingCompleted : int, stopEvent : Event):
    try:
        #Initialize the image list.
        initImageList()

        #First move to the title screen before going to the correct puzzle module.
        moveToTitle(stopEvent)

        if(stopEvent.is_set()):
            return

        match(solverMode):
            case InfiniteSolverModes.DailyChallenges:
                solveDailyChallenges(frame, stopEvent, startingCompleted)
            case _:
                solveRegularLevels(frame, stopEvent, startingCompleted)

    except Exception as e:
        if(not stopEvent.is_set()):
            frame.updateLabel(str(e))
            frame.showButtons()


def solveRegularLevels(frame : FrameWithInfoLabels, stopEvent : Event, startingCompleted : int):
    frame.updateLabel("Solving Regular Levels...")
    stopEvent.wait(1)

    levelsCompleted = startingCompleted
    inChallengeLevel = False

    while(not stopEvent.is_set()):

        buttonClicked = findAndClickButton([LEVEL_BLUE,LEVEL_WHITE,CHALLENGE_BLUE,CHALLENGE_WHITE,CONTINUE_BLUE], stopEvent, 2)

        #Set the delay when going into the level accordingly.
        if((buttonClicked in [CHALLENGE_BLUE, CHALLENGE_WHITE] or findIfImageExists([CHALLENGE_BLACK], stopEvent))):
            frame.updateLabel(f"Currently in Challenge Level...", stopEvent)
            inChallengeLevel = True
            stopEvent.wait(3)
        else:
            stopEvent.wait(1)

        if(inChallengeLevel):
            #Loop through each section of the challenge level until we finish it.
            while(inChallengeLevel and not stopEvent.is_set()):
                solveCurrentNonogram(frame, stopEvent)

                frame.updateLabel(f"Challenge Section finished.", stopEvent)
                stopEvent.wait(7)

                frame.updateLabel(f"Checking grid state...", stopEvent)
                stopEvent.wait(1)

                if(not findIfImageExists([CHALLENGE_BLACK], stopEvent)):
                    levelsCompleted += 1
                    frame.updateLabel(f"Challenge Level Completed.", stopEvent)
                    frame.updateLabel(f"Levels Completed: {levelsCompleted}", stopEvent, frame.infoLabel2)
                    inChallengeLevel = False
        else:
            solveCurrentNonogram(frame, stopEvent)

            levelsCompleted += 1
            frame.updateLabel(f"Level Finished.", stopEvent)
            frame.updateLabel(f"Levels Completed: {levelsCompleted}", stopEvent, frame.infoLabel2)
            
            while(not findIfImageExists([LEVEL_BLUE,LEVEL_WHITE,CHALLENGE_BLUE,CHALLENGE_WHITE], stopEvent) and not stopEvent.is_set()):
                pass

            frame.updateLabel(f"Moving to next level...", stopEvent)

        if(stopEvent.is_set()):
            return


def solveDailyChallenges(frame : FrameWithInfoLabels, stopEvent : Event, startingCompleted : int):
    frame.updateLabel("Solving Daily Challenges...")
    stopEvent.wait(1)

    levelsCompleted = startingCompleted
    findAndClickButton([DAILY_CHALLENGES], stopEvent, 1)

    while(not stopEvent.is_set()):
        #Used in scenarios where we completed a month and a pop up shows for us to collect the trophy.
        if(findIfImageExists([COLLECT_WHITE], stopEvent)):
            frame.updateLabel("Month completed. Moving to the previous month.", stopEvent)
            findAndClickButton([COLLECT_WHITE], stopEvent, 1)
            findAndClickButton([PREVIOUS_MONTH_BLUE], stopEvent, 1)

        findAndClickButton([CONTINUE_WHITE], stopEvent, 2)
        findAndClickButton([PLAY_BLUE], stopEvent, 2)

        #Used in scenarios where we already completed a month.
        while(findIfImageExists([RESTART_WHITE], stopEvent)):
            frame.updateLabel(f"Month completed. Moving to the previous month.")
            findAndClickButton([CANCEL_WHITE], stopEvent, 1)
            findAndClickButton([PREVIOUS_MONTH_BLUE], stopEvent, 1)
            findAndClickButton([PLAY_BLUE], stopEvent, 3)

        solveCurrentNonogram(frame, stopEvent)

        levelsCompleted += 1
        frame.updateLabel("Daily Challenge Finished.\nMoving to another day.", stopEvent)
        frame.updateLabel(f"Levels Completed: {levelsCompleted}", stopEvent, frame.infoLabel2)

        while(not findIfImageExists([CONTINUE_WHITE], stopEvent) and not stopEvent.is_set()):
            pass

        findAndClickButton([CONTINUE_WHITE], stopEvent, 5)

        if(stopEvent.is_set()):
            return



if __name__ == "__main__":
    app = NonogramSolverApp()
    app.mainloop()