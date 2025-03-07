from itertools import combinations
import numpy as np

def __PrintGrid(grid):
    for row in range(len(grid)):
        for col in range(len(grid)):
            print(grid[row][col], end="")
        print()
    print()


def __GenerateHintCombination(hint : list[int], gridLength: int) -> list[list[int]]:

    patterns = []

    #Represents the number of groups for each hint, and how many empty space blocks are between each group.
    groups = len(hint)
    patternSpaces = groups - 1

    #Get the total pattern length counting all the blocks in the hint plus the pattern spaces.
    #Get the remaining spaces factoring in the total pattern length.
    patternLength = sum(hint) + patternSpaces 
    remainingSpaces = gridLength - patternLength

    #Get all combinations from the given information in the form of a tuple.
    hintCombinations = list(combinations(range(groups + remainingSpaces), groups))

    #Generate the hint pattern based on each tuple.
    for combination in hintCombinations:
        patterns.append(__GenerateHintPattern(combination, hint, gridLength))
    
    return patterns


def __GenerateHintPattern(combination : list[tuple], hint : list[int], gridLength: int) -> list[int]:
    pattern = []
    
    #Represents the row or column, the current square in the row/column and the offset to add spaces between blocks.
    currentGroupIndex = 0
    offset = 0
    currentIndex = 0

    while currentIndex < gridLength:
        if(currentIndex - offset == combination[currentGroupIndex]):
            #Fill in the number of blocks of the current group.
            for i in range(hint[currentGroupIndex]):
                pattern.append(1)
                currentIndex += 1

            #If we filled in all the groups, fill the rest of the spaces with zeros.
            #Otherwise, add an offset based on the current block group total and add one zero to seperate it from the other groups.
            if(currentGroupIndex != len(hint) - 1):
                offset += hint[currentGroupIndex]
                currentGroupIndex += 1
                pattern.append(0)
            else:
                for i in range(gridLength - len(pattern)):
                    pattern.append(0)
                    currentIndex += 1
        else:
            pattern.append(0)
        currentIndex += 1

    return pattern


def __SetValidPattern(hintPatterns : list[list[int]], currentRowCol : list[str], hint : list[int], rowColIndex : int, isRow : bool):

    validPatterns = []

    for i in range(len(hintPatterns)):

        #Check if the current pattern is valid on the current board.
        #(0s and 1s match up, ? is a wildcard that can fit both.)
        #If so, add it as a potential solution.

        currentPattern = hintPatterns[i]
        if all((currentPattern[rowCol] == currentRowCol[rowCol] or currentRowCol[rowCol] == '?') for rowCol in range(len(currentRowCol))):
            validPatterns.append(currentPattern)
    
    #If there's only one valid pattern, that pattern is the correct one.
    if(len(validPatterns) == 1):
        return validPatterns[0]

    #If there are no valid patterns, that means that a hint has been parsed incorrectly.
    if(len(validPatterns) == 0):
        raise Exception(f"No valid solution could be found.\nThe hints may have been parsed incorrectly.\n{f"Row: {rowColIndex + 1}; Hint: {hint}" if isRow else f"Col: {rowColIndex + 1} ;Hint: {hint}"}")

    #Generate an array containing all valid patterns, and count the number of 0s and 1s for each.
    #If the sum of all ones or zeros for each place equals the number of valid patterns, that means that that value exists at that location.
    #If not, keep a wild card at that location.

    patternArray = np.array(validPatterns)
    patternCount = len(patternArray)

    filledSum = np.sum(np.array(validPatterns) == 1, axis=0)
    unfilledSum = np.sum(np.array(validPatterns) == 0, axis=0)

    result = []

    for i in range(len(currentRowCol)):
        result.append(1 if filledSum[i] == patternCount else 0 if unfilledSum[i] == patternCount else '?')
    return result


def __isGridSolved(grid : list[list[str]]):
    return np.sum(np.array(grid) == '?') == 0


def getBoardSolution(rowHints : list[list[int]], colHints : list[list[int]]):

    #Generate the initial grid.
    grid = [['?' for i in range(len(colHints))] for j in range(len(rowHints))]

    rowPatternList : list[list[int]] = []
    colPatternList : list[list[int]] = []

    #Get all combinations for each row and column hint.
    for row in range(len(rowHints)): 
        rowPatternList.append(__GenerateHintCombination(rowHints[row], len(rowHints)))

    for col in range(len(colHints)): 
        colPatternList.append(__GenerateHintCombination(colHints[col], len(colHints)))

    #While the board is still unfinished keep filling in each row and column and check if the grid is solved yet.
    while(True):

        for row in range(len(rowHints)):
            grid[row] = __SetValidPattern(rowPatternList[row], grid[row], rowHints[row], row, True)
            
            if(__isGridSolved(grid)):
                return grid

        for col in range(len(colHints)):
            currentCol = [row[col] for row in grid]
            validCol = __SetValidPattern(colPatternList[col], currentCol, colHints[col], col, False)

            for validColRow in range(len(rowHints)):
                grid[validColRow][col] = validCol[validColRow]

            if(__isGridSolved(grid)):
                return grid

if __name__ == "__main__":

    rowHints = [[4],[4],[2,1],[5],[4]]
    colHints = [[1,3],[5],[2,2],[5],[1,1]]

    grid = getBoardSolution(rowHints,colHints)

    __PrintGrid(grid)