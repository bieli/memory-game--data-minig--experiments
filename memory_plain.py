# Memory
# http://inventwithpython.com
# By Al Sweigart al@inventwithpython.com

import random
import time
import pygame
import sys
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
REVEALSPEED = 8
COLS = 10
ROWS = 6
BOXSIZE = 40
GAPSIZE = 10

DARKGRAY = (60, 60, 60)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)

BGCOLOR = DARKGRAY
BOXCOLOR = WHITE

DONUT = 1
SQUARE = 2
DIAMOND = 3
LINES = 4
OVAL = 5

def main():
    global MAINCLOCK, MAINSURF
    pygame.init()
    MAINCLOCK = pygame.time.Clock()
    MAINSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    mousex = 0
    mousey = 0
    pygame.display.set_caption('Memory')

    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)

    firstStep = True
    firstSelection = None

    MAINSURF.fill(BGCOLOR)
    startGameAnimation(mainBoard)

    # Main game loop:
    while True:
        clicked = False

        # Draw the board.
        MAINSURF.fill(BGCOLOR)
        drawBoard(mainBoard, revealedBoxes)

        # Handle any events.
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                clicked = True


        boxx, boxy = isOverBox(mousex, mousey)
        if boxx != None and boxy != None:
            # The mouse is over a box.

            highlightBox(boxx, boxy)

            if clicked and not revealedBoxes[boxx][boxy]:
                revealBoxesAnimation(mainBoard, [(boxx, boxy)], REVEALSPEED)
                #unrevealBoxesAnimation(mainBoard, [(boxx, boxy)], REVEALSPEED)
                revealedBoxes[boxx][boxy] = True

                if firstStep:
                    firstSelection = (boxx, boxy)
                    firstStep = False
                else:
                    # Check if there is a match.
                    shape1, color1 = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
                    shape2, color2 = getShapeAndColor(mainBoard, boxx, boxy)

                    if shape1 != shape2 or color1 != color2:
                        # Icons don't match. Unreveal both selections.
                        time.sleep(1)
                        unrevealBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxx, boxy)], REVEALSPEED)
                        revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                        revealedBoxes[boxx][boxy] = False
                    elif hasWon(revealedBoxes):
                        gameWonAnimation(mainBoard)
                        time.sleep(2)

                        # Reset the board
                        mainBoard = getRandomizedBoard()
                        revealedBoxes = generateRevealedBoxesData(False)

                        # Show the fully unrevealed board for a second.
                        drawBoard(mainBoard, revealedBoxes)
                        pygame.display.update()
                        time.sleep(1)

                        # Replay the start game animation.
                        startGameAnimation(mainBoard)
                    firstStep = True

        # Redraw the screen and wait a clock tick.
        pygame.display.update()
        MAINCLOCK.tick(FPS)

def generateRevealedBoxesData(val):
    dataStruct = []
    for c in range(COLS):
        dataStruct.append([val] * ROWS)
    return dataStruct


def splitIntoGroupsOf(groupSize, theList):
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i+groupSize])
    return result


def startGameAnimation(board):
    fakeRevealedBoxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(COLS):
        for y in range(ROWS):
            boxes.append( (x, y) )
    random.shuffle(boxes)

    groups = splitIntoGroupsOf(8, boxes)

    for g in groups:
        drawBoard(board, fakeRevealedBoxes)
        revealBoxesAnimation(board, g, REVEALSPEED)
        unrevealBoxesAnimation(board, g, REVEALSPEED)


def gameWonAnimation(board):
    global BGCOLOR, BOXCOLOR
    fakeRevealedBoxes = generateRevealedBoxesData(True)

    for i in range(14):
        BGCOLOR, BOXCOLOR = BOXCOLOR, BGCOLOR

        MAINSURF.fill(BGCOLOR)
        drawBoard(board, fakeRevealedBoxes)
        pygame.display.update()
        time.sleep(0.3)


def hasWon(revealed):
    for i in revealed:
        if False in i:
            return False
    return True


def getShapeAndColor(board, boxx, boxy):
    return board[boxx][boxy][0], board[boxx][boxy][1]


def revealBoxesAnimation(board, boxes, speed):
    # Do the "box reveal" animation.
    for i in range(BOXSIZE, -speed - 1, -speed):
        for b in boxes:
            drawBoxCover(board, b, i)
        pygame.display.update()
        MAINCLOCK.tick(FPS)


def unrevealBoxesAnimation(board, boxes, speed):
    # Do the "box cover" animation.
    for i in range(0, BOXSIZE, speed):
        for b in boxes:
            drawBoxCover(board, b, i)
        pygame.display.update()
        MAINCLOCK.tick(FPS)

def drawBoxCover(board, b, coverage):
    """Both the revealBoxesAnimation() and unrevealBoxesAnimation() do the exact same thing inside their nested for loops, so instead of copying and pasting that code twice, we just put the code in its own function and call that function twice. Getting rid of duplicated code this way is often a good idea, because if we want to change the code later (say, if we find a bug in it), then we only have to change it in one place instead of multiple places. It also makes our program shorter and easier to read."""
    left, top = leftTopOfBox(b[0], b[1])
    pygame.draw.rect(MAINSURF, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
    shape, color = getShapeAndColor(board, b[0], b[1])
    drawShape(shape, color, b[0], b[1])
    if coverage > 0:
        pygame.draw.rect(MAINSURF, BOXCOLOR, (left, top, coverage, BOXSIZE))

def getRandomizedBoard():
    # Get a list of every possible shape in every possible color.
    icons = []
    for c in (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN):
        for s in (DONUT, SQUARE, DIAMOND, LINES, OVAL):
            icons.append( (s, c) )

    # To decide how many icons to use, shuffle the list and then truncate it.
    random.shuffle(icons)
    numIconsUsed = int(COLS * ROWS / 2)
    icons = icons[:numIconsUsed] * 2 # going to need pairs of icons

    # Create the board data structure.
    board = []
    for x in range(COLS):
        columns = []
        for y in range(ROWS):
            randomIndex = random.randint(0, len(icons) - 1)
            columns.append(icons[randomIndex])
            del icons[randomIndex]
        board.append(columns)
    return board


def leftTopOfBox(boxx, boxy):
    # See how big the margins are for each side.
    xmargin = int((WINDOWWIDTH - (COLS * (BOXSIZE + GAPSIZE))) / 2)
    ymargin = int((WINDOWHEIGHT - (ROWS * (BOXSIZE + GAPSIZE))) / 2)
    left = boxx * (BOXSIZE + GAPSIZE) + xmargin
    top = boxy * (BOXSIZE + GAPSIZE) + ymargin
    return (left, top)


def drawBoard(board, revealed):
    for boxx in range(COLS):
        for boxy in range(ROWS):
            left, top = leftTopOfBox(boxx, boxy)
            if not revealed[boxx][boxy]:
                # Draw a covered box.
                pygame.draw.rect(MAINSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
            else:
                # Draw the icon.
                shape, color = getShapeAndColor(board, boxx, boxy)
                drawShape(shape, color, boxx, boxy)


def isOverBox(x, y):
    for boxx in range(COLS):
        for boxy in range(ROWS):
            left, top = leftTopOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)


def highlightBox(boxx, boxy):
    left, top = leftTopOfBox(boxx, boxy)
    pygame.draw.rect(MAINSURF, BLUE, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)


def drawShape(shape, color, boxx, boxy):
    quarter = int(BOXSIZE * 0.25)
    half = int(BOXSIZE * 0.5)

    left, top = leftTopOfBox(boxx, boxy)
    if shape == DONUT:
        pygame.draw.circle(MAINSURF, color, (left + half, top + half), half - 5)
        pygame.draw.circle(MAINSURF, BGCOLOR, (left + half, top + half), quarter - 5)
    elif shape == SQUARE:
        pygame.draw.rect(MAINSURF, color, (left + 10, top + 10, BOXSIZE - 20, BOXSIZE - 20))
    elif shape == DIAMOND:
        pygame.draw.polygon(MAINSURF, color, ((left + half, top), (left + BOXSIZE, top + half), (left + half, top + BOXSIZE), (left, top + half)))
    elif shape == LINES:
        for i in range(0, BOXSIZE, 4):
            pygame.draw.line(MAINSURF, color, (left, top + i), (left + i, top))
            pygame.draw.line(MAINSURF, color, (left + i, top + BOXSIZE), (left + BOXSIZE, top + i))
    elif shape == OVAL:
        pygame.draw.ellipse(MAINSURF, color, (left, top + quarter, BOXSIZE, half))


if __name__ == '__main__':
    main()