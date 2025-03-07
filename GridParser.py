from Constants import *
from ScreenCapture import getGameScreenImage, getGameScreenRect
from Classes import ImageNumberLibrary, GameScreenInfo
import pytesseract
import cv2

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

imageNumberLibrary : ImageNumberLibrary = ImageNumberLibrary()


def __getNumberImages(imageList : list[cv2.typing.MatLike], rectPoints : list[list[tuple[int,int]]]) -> list[list[cv2.typing.MatLike]]:
    result = []

    for i, rectPointSlice in enumerate(rectPoints):
        numImages = []
        for p in rectPointSlice:
            currentImage = imageList[i]

            #Leave a 7 pixel space around the number in order to better parse it.
            left = p[0][0] - 7
            top = p[0][1] - 7
            right = p[1][0] + 7
            bottom = p[1][1] + 7

            numImages.append(currentImage[top:bottom,left:right])
        result.append(numImages)

    return result


def __parseImagesAsNumbers(numberImageList : list[list[cv2.typing.MatLike]]) -> list[tuple[int]]:
    
    global imageNumberLibrary
    result = []

    #Process each number in the slice in order to get the int value.
    for i, sliceNumImages in enumerate(numberImageList):
        sliceResult = []
        for j, im in enumerate(sliceNumImages):
            
            #Checks the image number library if a similar image has been parsed.
            #If so, use that number.
            numValue = imageNumberLibrary.findNumber(im)
            if(numValue != None):
                sliceResult.append(numValue)
                continue
            
            scaleAttempts = 0
            numString = None
            currentImage = im.copy()

            while(not numString):
                #Attempt to parse the number from the image. If it can't parse it, scale it up to a total of 3 times.
                numString = pytesseract.image_to_string(cv2.bitwise_not(currentImage), config="-c tessedit_char_whitelist=0123456789 --psm 6")
                if(not numString):
                    if(scaleAttempts < 3):
                        scaleAttempts += 1
                        currentImage = cv2.resize(currentImage, None, fx=1.25, fy=1.25)
                    else:
                        raise Exception("Number could not be identified.")

            numValue = int(numString)

            #Used in situations where two seperate numbers are mistaken for a double digit number.
            if(numValue > len(numberImageList)):
                raise Exception(f"A number higher than the length of the board has been parsed: {numValue}")
            
            imageNumberLibrary.addNumber(im, numValue)
            sliceResult.append(numValue)

        result.append(sliceResult)

    return result


def __generateParsableSlice(imageSlice : cv2.typing.MatLike, isRow : bool = False) -> cv2.typing.MatLike:
    #Get every hint that's not filled in (Solid).
    nonFilledNumbers = cv2.threshold(imageSlice, 170, 255, cv2.THRESH_BINARY_INV)[1]

    #Generate a mask to prevent operations on the filled in mask.
    filledMask = nonFilledNumbers.copy()
    nonFilledRects = [cv2.boundingRect(c) for c in cv2.findContours(nonFilledNumbers.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]]
    for rect in nonFilledRects:
        imageSliceShape = imageSlice.shape
        
        point1 = (rect[0] - 10, 0) if isRow else (0, rect[1] - 10)
        point2 = (rect[0] + rect[2] + 10, imageSliceShape[0]) if isRow else (imageSliceShape[1], rect[1] + rect[3] + 10)

        cv2.rectangle(filledMask, point1, point2, (255), -1)
    filledMask = cv2.bitwise_not(filledMask)

    #Get every hint number and their outline, and subtract them to get the filled hints.
    everyNumber = cv2.threshold(imageSlice, 235, 255, cv2.THRESH_BINARY_INV)[1] - cv2.inRange(imageSlice, 217, 235)
    filledNumbers = cv2.bitwise_and(everyNumber, everyNumber, mask=filledMask)

    #Return the combination of the two.
    parsableSlice = cv2.bitwise_or(nonFilledNumbers, filledNumbers)
    return parsableSlice


def parseRowHints(hintImageList : list[cv2.typing.MatLike]) -> list[tuple[int]]:
    #Stores the coordinates of each rect in order to retrieve the number.
    rowPoints = []
    thresholdSections : list[cv2.typing.MatLike] = []

    for r, hintImage in enumerate(hintImageList):

        hintImage = __generateParsableSlice(hintImage, True)
        thresholdSections.append(hintImage)

        hintContours = cv2.findContours(hintImage.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        hintRects = [cv2.boundingRect(c) for c in hintContours[0]]
        
        #Get and sort each rect from left to right.
        hintRects.sort(key=lambda x: x[0])

        newRow = []

        for i, numberRect in enumerate(hintRects):
            #Get the current and the next number in order to determine if it's part of a single double digit number.
            #Get the point if at the end.
            if(i < len(hintRects) - 1):
                x1, y1, w1, h1 = numberRect
                x2, y2, w2, h2 = hintRects[i + 1]

                numberSpacing = x2 - x1 - w1

                #Double digit numbers are determined by if the rects are close enough on the x-axis.
                if(numberSpacing < 15):

                    p1 = (min(x1, x2),min(y1,y2))
                    p2 = (max(x2 + w2, x1 + w1),max(y1 + h1, y2 + h2))

                    #With a maximum of a 20x20 grid on expert, there can only be a max of 1 double digit number in each row/column. Process the rest as single numbers.
                    newRow.append([p1,p2])
                    newRow += [[(restRect[0], restRect[1]),(restRect[0] + restRect[2], restRect[1] + restRect[3])] for restRect in hintRects[i + 2:]]
                    break

                else:
                    newRow.append([(x1,y1),(x1 + w1, y1 + h2)])
            else:
                x, y, w, h = numberRect
                newRow.append([(x,y),(x+w,y+h)])

        rowPoints.append(newRow)

    numberImages = __getNumberImages(thresholdSections, rowPoints)
    return __parseImagesAsNumbers(numberImages)


#This function is used to sort rects from top to bottom, left to right.
def __getRectPrecedence(rect, cols):
    tolerance_factor = 15
    return ((rect[1] // tolerance_factor) * tolerance_factor) * cols + rect[0]


def parseColHints(hintImageList : list[cv2.typing.MatLike]) -> list[tuple[int]]:

    #Stores the coordinates of each rect in order to retrieve the number.
    colPoints = []
    thresholdSections : list[cv2.typing.MatLike] = []

    for hintImage in hintImageList:
        hintImage = __generateParsableSlice(hintImage)
        thresholdSections.append(hintImage)

        hintContours = cv2.findContours(hintImage.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        hintRects = [cv2.boundingRect(c) for c in hintContours[0]]

        #Get and sort each rect from top to bottom, left to right.
        hintRects.sort(key=lambda x: __getRectPrecedence(x, hintImage.shape[1]))

        newCol = []

        for i, numberRect in enumerate(hintRects):
            #Get the current and the next number in order to determine if it's part of a single double digit number.
            #Get the point if at the end.
            if(i < len(hintRects) - 1):

                x1, y1, w1, h1 = numberRect
                x2, y2, w2, h2 = hintRects[i + 1]

                #Double digit numbers are determined by if the rects are close enough on the y-axis.
                if(abs(y1 - y2) < 36):
                    p1 = (min(x1, x2),min(y1,y2))
                    p2 = (max(x2 + w2, x1 + w1),max(y1 + h1, y2 + h2))

                    #With a maximum of a 20x20 grid, there can only be a max of 1 double digit number in each row/column. Process the rest as single numbers.
                    newCol.append([p1,p2])
                    newCol += [[(restRect[0], restRect[1]),(restRect[0] + restRect[2], restRect[1] + restRect[3])] for restRect in hintRects[i + 2:]]
                    break
                else:
                    newCol.append([(x1,y1),(x1 + w1, y1 + h2)])
            else:
                x, y, w, h = numberRect
                newCol.append([(x,y),(x+w,y+h)])

        colPoints.append(newCol)

    numberImages = __getNumberImages(thresholdSections, colPoints)
    return __parseImagesAsNumbers(numberImages)


#Retrieves the list of row and column hint slices.
def getHintImageList(gameScreenInfo : GameScreenInfo) -> tuple[list[cv2.typing.MatLike],list[cv2.typing.MatLike]]:
    global imageNumberLibrary
    imageNumberLibrary.clearLibrary()

    image = gameScreenInfo.gameScreenImage
    rowHintImageList = [__cutAndResizeImage(image[r[1] + 1:r[1] + r[3] - 1 ,r[0] + 1 : r[0] + r[2] - 1], 100, True) for r in gameScreenInfo.rowRects]
    colHintImageList = [__cutAndResizeImage(image[r[1] + 1:r[1] + r[3] - 1,r[0] + 1:r[0] + r[2] - 1], 100) for r in gameScreenInfo.colRects]

    return (rowHintImageList, colHintImageList)


def __cutAndResizeImage(image : cv2.typing.MatLike, size: int, isRow : bool = False) -> cv2.typing.MatLike:
    numberRects = [cv2.boundingRect(c) for c in cv2.findContours(cv2.threshold(image, 225, 255, cv2.THRESH_BINARY_INV)[1], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]]

    #Maintain space around the numbers for easier parsing.
    top = min(r[1] for r in numberRects) - 3
    left = min(r[0] for r in numberRects) - 3
    right = max((r[0] + r[2]) for r in numberRects) + 3
    bottom = max((r[1] + r[3]) for r in numberRects) + 3

    #Resize all numbers to similar font sizes in order to more easily parse numbers regardless of the font size.
    #Add extra white space around the numbers.
    cutImage = cv2.copyMakeBorder(image[top:bottom,left:right],10,10,10,10,cv2.BORDER_REPLICATE)
    aspectRatio = (cutImage.shape[1] / cutImage.shape[0]) if isRow else (cutImage.shape[0] / cutImage.shape[1])
    newSize = int(size * aspectRatio)
    
    return cv2.resize(cutImage, (newSize, size) if isRow else (size, newSize))


#Gets all information relating to the game screen.
def getGameScreenInfo() -> GameScreenInfo:

    gameScreenImage = getGameScreenImage(getGameScreenRect())
    rowColParseAttempts = 0

    while(True):
        #Gets the boxes around the hints in order to get the minimal play area.
        hintContours = cv2.findContours(cv2.inRange(gameScreenImage.copy(), 227, 228), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        hintRects = [cv2.boundingRect(c) for c in hintContours if (cv2.boundingRect(c)[3] * cv2.boundingRect(c)[2]) > 250]

        #If it can't find any rows or columns, try again up to 3 times.
        if(len(hintRects) == 0):
            if(rowColParseAttempts >= 3):
                raise RuntimeError("Couldn't find any rows and columns. Make sure the puzzle is visible.")
            else:
                rowColParseAttempts += 1
                gameScreenImage = getGameScreenImage(getGameScreenRect())
                continue

        #Calculate the borders of the game screen.
        top = min(r[1] for r in hintRects) - 30
        bottom = max((r[1] + r[3]) for r in hintRects) + 30

        #Used in scenarios in which something may be blocking part of the screen.
        rowHints : list[tuple[int,int,int,int]] = [r for r in hintRects if abs(r[0]) < 25]
        colHints : list[tuple[int,int,int,int]] = [c for c in hintRects if abs(c[1] - 30 - top) < 25]

        #Ensures that we get any hints of both rows and columns and that they have the same count.
        #If not, get the game screen again.
        
        if(len(rowHints) == 0 or len(colHints) == 0):
            if(rowColParseAttempts >= 3):
                raise RuntimeError("Couldn't find all rows and columns, make sure that the game screen is unobstructed.")
            else:
                rowColParseAttempts += 1
                gameScreenImage = getGameScreenImage(getGameScreenRect())
                continue
        elif(len(rowHints) != len(colHints)):
            if(rowColParseAttempts >= 3):
                raise RuntimeError(f"The number of hint columns and rows don't match. Make sure the whole game screen is visible.\nRows: {len(rowHints)} Cols: {len(colHints)}")
            else:
                rowColParseAttempts += 1
                gameScreenImage = getGameScreenImage(getGameScreenRect())
                continue
        else:
            break

    #Adjust the hint rects based on the new border of the game screen.
    #Sort rows by top to bottom and columns by left to right.
    rowHints = list((row[0], row[1] - top, row[2], row[3]) for row in rowHints)
    colHints = list((col[0], col[1] - top, col[2], col[3]) for col in colHints)

    rowHints.sort(key=lambda rect: rect[1])
    colHints.sort(key=lambda rect: rect[0])

    return GameScreenInfo(gameScreenImage[top:bottom,:], rowHints, colHints)