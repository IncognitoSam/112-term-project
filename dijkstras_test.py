#########################
### Author: Sam Banks ###
#########################

# Dijkstra's Algorithm test

# CITATION: I referenced algorithm explanation at 
# https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm

# CITATION: print2dList and helper from 112 course website 
# https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html#printing

# Helper function for print2dList.
# This finds the maximum length of the string
# representation of any item in the 2d list
def maxItemLength(a):
    maxLen = 0
    rows = len(a)
    cols = len(a[0])
    for row in range(rows):
        for col in range(cols):
            maxLen = max(maxLen, len(str(a[row][col])))
    return maxLen

# Because Python prints 2d lists on one row,
# we might want to write our own function
# that prints 2d lists a bit nicer.
def print2dList(a):
    if (a == []):
        # So we don't crash accessing a[0]
        print([])
        return
    rows = len(a)
    cols = len(a[0])
    fieldWidth = maxItemLength(a)
    print("[ ", end="")
    for row in range(rows):
        if (row > 0): print("\n  ", end="")
        print("[ ", end="")
        for col in range(cols):
            if (col > 0): print(", ", end="")
            # The next 2 lines print a[row][col] with the given fieldWidth
            formatSpec = "%" + str(fieldWidth) + "s"
            print(formatSpec % str(a[row][col]), end="")
        print(" ]", end="")
    print("]")

# Returns map
def setup():
    board = [["-"] * 10 for i in range(10)]
    board[0][3] = "#"
    board[1][3] = "#"
    board[2][3] = "#"
    board[3][4] = "#"
    board[4][4] = "#"
    board[5][4] = "#"
    board[6][4] = "#"
    board[7][4] = "#"
    board[8][4] = "#"
    # board[9][4] = "#"
    board[8][3] = "#"
    board[8][2] = "#"
    board[8][1] = "#"
    board[4][2] = "#"
    # board[8][0] = "#"

    return board

# def print2dList(L):
#     for line in L: print(line)

# Takes 2d list of empty spaces (_) and obstacles (#)
def dijkstras(board, start, end):
    distances = [[-1] * len(board[0]) for i in range(len(board))]
    distances[start[0]][start[1]] = 0
    paths = [[0] * len(board[0]) for i in range(len(board))]

    unvisited = set([])
    for i in range(len(distances)):
        for j in range(len(distances[0])):
            if board[i][j] != "#":
                unvisited.add((i, j))
    current = start
    
    while True:
        result = doStep(board, distances, paths, unvisited, end)
        if result or result == False: break
    if not result: return False
    return result, distances, getPath(board, distances, paths, start, end), paths

# Determines current cell, then visits cell.
def doStep(board, distances, paths, unvisited, end):
    
    # Determine current cell.
    shortest = None
    shortestDistance = -1
    for row, col in unvisited:
        if distances[row][col] != -1:
            if shortest == None or distances[row][col] < shortestDistance:
                shortest = (row, col)
                shortestDistance = distances[row][col]
    current = shortest
    if current == None: return False

    visitCell(board, distances, paths, unvisited, current)
    if end not in unvisited: return True
    elif len(unvisited) == 0: return False

# Marks all neighbors of a given cell with distances from the start.
def visitCell(board, distances, paths, unvisited, current):
    # Check up, down, left right
    row, col = current
    for drow in (-1, 0, 1):
        for dcol in (-1, 0, 1):
            newRow, newCol = row + drow, col + dcol
            if (abs(drow) + abs(dcol) == 1 and 0 <= newRow < len(board) and
                0 <= newCol < len(board[0])):
                if ((distances[newRow][newCol] == -1 or 
                    distances[newRow][newCol] > distances[row][col] + 1) and
                    board[newRow][newCol] != "#"):

                    distances[newRow][newCol] = distances[row][col] + 1
                    paths[newRow][newCol] = (-drow, -dcol)
                    
    unvisited.remove(current)

# CHECK FOR DIAGONAL ISSUE
def getPath(board, distance, paths, start, end):
    path = [end]
    row, col = end
    while True:
        drow = paths[row][col][0]
        dcol = paths[row][col][1]
        row += drow
        col += dcol
        path = [(row, col)] + path
        if start == (row, col): return path

def test():
    board = setup()
    start = (4, 3)
    end = (4, 6)
    board[start[0]][start[1]] = "@"
    board[end[0]][end[1]] = "*"
    result = dijkstras(board, start, end)
    if not result:
        print("No path found")
        return
    path = result[2]
    for i in range(len(path)):
        step = path[i]
        board[step[0]][step[1]] = i
    print2dList(board)

test()