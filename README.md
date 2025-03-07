# Nonogram-Auto-Solver
This python program can parse Nonogram.com puzzles and auto solve them.\
This program can also auto solve an infinte amount of a specific types of puzzle.

# Dependencies

This program uses the following dependencies and additional programs.
- pyautogui - Used to get screenshots of the screen as well as detecting elements and controlling mouse movement and clicking.
- opencv - Used to transform images in order to get specific elements and detect bounding rectangles.
- scikit-image - Used with the ImageNumberLibrary to more efficiently parse numbers that have been parsed before. 
- pytesseract - Used to parse the hint numbers retrieved from the grid.
- pillow - Used in order to access the Assets folder and get button and text images for the infinite solver.
- itertools - Used in order to generate combinations used to solve the puzzle.
- numpy - Used various array methods in the NonogramSolver module in order to calculate the answer.
- pywin32 - Used in order to get the window position and size for the BlueStacks window.
- tkinter - Used to provide a gui to more easily solve puzzles for the user.
- BlueStacks - Represents the game screen for the Nonogram.com puzzle.

# How It Works
## Grid Parsing

Example using a 10x10 Nonogram:

1. We first retrieve the game screen by finding the position and size of the BlueStacks App, getting the image of the app in grayscale, and cropping it down to the white screen only.

<img src="https://github.com/user-attachments/assets/6f27f4f4-340a-4c9d-8133-21b31728d1c0" width=33% height=33%></br>

2. We find the bounding rects of the hint regions using OpenCV. 
   This allows us to get the numbers directly as well as shrink the game screen to the area we needed.
   Error checking is used to handle cases where we can't find any rows or columns or if the two don't have the same count.

<img src="https://github.com/user-attachments/assets/d76dbf31-464f-443f-81cb-6e640075a0d2" width=40% height=40%>
<img src="https://github.com/user-attachments/assets/0b34ca23-8889-4507-bed7-2fec7553f4af" width=40% height=40%></br>

3. Using the bounding rects retrieved, we get the minimum area for all the numbers only. 
   We add space around each slice and scale it to a set constant size to better parse each number.
   Scaling the slices allows us to parse grids of different sizes consistently

Row 6:\
<img src="https://github.com/user-attachments/assets/c636070a-45bf-4cf1-bdd0-6e79d3047bdc" width=20% height=20%></br>

Col 4:\
<img src="https://github.com/user-attachments/assets/2cd447ea-515a-40b0-964e-bb2244107752" width=5% height=5%></br>

4. We transform each hint slice, turning the numbers white and the background black, in order to get the bounding rects for each individual number.
   Each number rect is stored in a list corresponding to the associated row or column.

Row 6:\
<img src="https://github.com/user-attachments/assets/cb78ba99-bd64-4869-9e03-8044223355ad" width=20% height=20%></br>

5. Going through each number rect in each row and column, we determine which two numbers are part of a single double digit number using different methods.
   Number rects that are counted as double digits are combined into one single bounding rect.

	* For columns, we can easily determine double digit numbers by finding which two number rects are close enough on the y-axis.
	  We first sort the rects top to bottom, left to right before detecting the double digit numbers.

	* For rows, we find the spacing between each number rect on the x-axis and determine if they're close enough.
          Because the numbers are scaled to a specific size, we can consistently find a threshold for double digit numbers.

6. We seperate each number from the slice, single or double digit, and parse each individually using Pytesseract.
	
	* If a number can't be parsed from the image, scale it up and try again for a total of 3 times.
	
	* We also include error handling for when a number larger than the grid box length is parsed, due to some error when checking spacing for double digit numbers.

7. We then have all of our row and column hints as a list of integer lists:  

   Rows: [2], [3, 4], [1, 8], [6, 1], [3, 5], [2, 1, 2, 2], [1, 1, 2, 1], [2], [3], [5]  
   Columns: [1, 2], [1, 4], [4], [3, 2, 1], [3, 1], [5, 2], [10], [3, 1, 4], [2, 2], [2, 2]  
     
   We pass this to our solver algorithm module in order to generate the answer as a binary 2D grid.  
   More details about the solver algorithm is discussed in the next section.

   [0, 0, 0, 0, 0, 0, 1, 1, 0, 0]  
   [0, 1, 1, 1, 0, 1, 1, 1, 1, 0]  
   [1, 0, 1, 1, 1, 1, 1, 1, 1, 1]  
   [0, 1, 1, 1, 1, 1, 1, 0, 0, 1]  
   [1, 1, 1, 0, 1, 1, 1, 1, 1, 0]  
   [1, 1, 0, 1, 0, 1, 1, 0, 1, 1]  
   [0, 1, 0, 1, 0, 0, 1, 1, 0, 1]  
   [0, 0, 0, 0, 0, 0, 1, 1, 0, 0]  
   [0, 0, 0, 0, 0, 1, 1, 1, 0, 0]  
   [0, 0, 0, 1, 1, 1, 1, 1, 0, 0]  

8. With the grid, we generate coordinates to click on the game screen to fill in the squares.
	
	* We get the game screen image again in the event it's resized when the puzzle is being parsed. 

	* By getting the pixel value of the top left part of each box, we can determine which squares need to be filled or empty.
	  This allows us to solve a partially filled grid.

	* What we get back are two lists of coordinates relative to the screen:
	  The areas where we need to empty the box and the areas where we fill them in.

9. With the coordinates generated, we use PyAutoGUI in order to click on the boxes in the puzzle and solve it.
   We first click on boxes that are filled that should be empty before clicking on the empty boxes as the game will prevent you from filling in too many boxes.

<img src="https://github.com/user-attachments/assets/f24453cb-eec4-4e60-80d3-793ee65d6808" width=40% height=40%></br>

## Solver:

The algorithm for solving a nonogram puzzle is similar to how we would solve it in real life using specific techniques.\
Suppose that for a 10x10 grid, we have a row with the hint [3, 4].\
The following patterns below are valid answers for this hint.  

<img src="https://github.com/user-attachments/assets/797dd17e-fbdb-4efe-b210-c35143479a6d" width=40% height=40%></br>
<img src="https://github.com/user-attachments/assets/7dea7f2a-c20c-464c-91b5-f563f1a7cd1f" width=40% height=40%></br>
<img src="https://github.com/user-attachments/assets/789de793-6886-47e5-9531-bb23c4d96062" width=40% height=40%></br>
<img src="https://github.com/user-attachments/assets/9909db46-a2bd-4025-94a5-aa0efc8d46fe" width=40% height=40%></br>
<img src="https://github.com/user-attachments/assets/d1367086-2e1d-4b68-bb48-ac3b8be82444" width=40% height=40%></br>
<img src="https://github.com/user-attachments/assets/88d92566-fda5-4fb0-9516-10e7c73842f3" width=40% height=40%></br>

If you look closely, you notice that specific boxes are always filled in or are always blank between all patterns.\
That means that at the very least, those boxes are filled in, leaving us with this partial answer.  

<img src="https://github.com/user-attachments/assets/8c02fcb0-0691-4b29-91b2-7d9b09934fc3" width=40% height=40%></br>

If we keep repeating this for every row and every column hint, we can slowly fill in the grid until we are able to fill in all the required squares.

The solver algorithm works like this:

1. We initialize the grid as a 2D list that be set to 3 values, 0 for empty, 1 for filled, and ? for undetermined or a wild card.  
   All the rows and columns are set to undetermined by default.

2. We first read each row and column hints and generate all possible patterns for each of them using combinations from itertools.

3. We get the current row or column, and find which patterns match the current row or column state (Which boxes are always filled or empty, with the ? being a wild card).

	* If there is only one valid pattern, that pattern is the correct one for the current row or column.

	* If there are multiple valid patterns, we determine which squares are always filled or empty in each pattern and set it in the assocated place.  
	  We leave the undetermined boxes as is if the associated box doesn't have all filled or all empty values.

	* If there are no valid patterns matched, that means that there is no solution for the current puzzle with the given hints.  
	  A common occurrence of this is when the hints have been parsed incorrectly, so we raise an error.

4. We go to the next row or column and repeat the previous step. After checking a row or column, we determine if the grid is filled in yet.  
   If so, the grid is solved, and we return it to whatever module needs it.

## Nonogram Solver Window App

The window app itself is built with Tkinter, and allows for solving the current on screen puzzle, as well as solving infinite types of puzzles.  
When selecting to solve infinite puzzles, you are given two options to choose from, solving regular levels, and solving Daily Challenges.  
The app uses PyAutoGui to locate specific buttons and navigate to the correct mode to start solving puzzles.  

  * For regular levels, after we solve a puzzle, we wait for the next level button to show up and click on it.
  * Sometimes we might end up in a challenge level, where we have to solve 4 puzzles back to back.
	  We can adjust our logic to handle that.
  * The process is similar when solving Daily Challenges, but with different buttons to press and check.
    * If we complete a month, we get an award popup. In that scenario, we automatically collect the award and move to the next month.
    * We also move to the next month if the month we're in is already completed, as pressing play will bring up a menu to restart the level.

A label is shown detailing the current status of the puzzle, as well as how many levels have we completed in the solver.  

We can cancel the On-Screen Solver and the Infinite Solver by hitting cancel, which brings us back to the menu.  

# Solver App In Action

Below are two videos showcasing the app solving grids of various difficulties and sizes, as well as a demo of the infinite solver functionality.

[Solving Puzzles of Different Sizes](https://youtu.be/11uGO6z3-38)  
\
[Solving Multiple Puzzles in a Row](https://youtu.be/VlVrmgnZo_M)  

# Future Plans

There might be a few puzzles where the solver might run into an error that I would like to address in the future.  
A double digit number may be mistakenly be parsed as seperate numbers or vice versa due to variance in the spacing between two numbers.  
Additionally, I would like to add an additional Infinite Solver Mode that goes through event levels in the game app.  
