import random
import os
import math

SCREEN_WIDTH, SCREEN_HEIGHT = os.get_terminal_size()

NUMBER_COLOURS = {
    2 : "\033[0m",
    4 : "\033[0m",
    8 : "\033[030m\033[43m",
    16 : "\033[030m\033[43m",
    32 : "\033[030m\033[101m",
    64 : "\033[030m\033[41m",
    128 : "\033[030m\033[103m",
    256 : "\033[030m\033[103m",
    512 : "\033[030m\033[43m",
    1024 : "\033[030m\033[43m",
    2048 : "\033[030m\033[43m"
}

def add2DTuple(tuple1, tuple2):
    return (tuple1[0] + tuple2[0], tuple1[1] + tuple2[1])

def clearConsole():
    [print("\n") for x in range(SCREEN_HEIGHT)]

class Screen:
    def __init__(self, size : tuple[int, int], fillChar : str = " "):
        self.width, self.height = size
        self.screen = self.generateScreen(fillChar)
        self.offset = (0, 0)

    def generateScreen(self, char : str):
        sc = {}
        for y in range(self.height):
            for x in range(self.width):
                sc[(x, y)] = {"char":char,"color":"\033[0m"}
        return sc
    
    def renderText(self, text : str, position : tuple[int, int] = (0, 0), color : str = "\033[0m"):
        for i, char in enumerate(list(text)):
            newX, newY = position[0]+i, position[1]
            if (newX >= 0 and newX < self.width) and (newY >= 0 and newY < self.height):
                self.screen[(newX, newY)] = {"char":char,"color":color}
    
    def renderToConsole(self, consoleSize : tuple[int, int]):
        consoleWidth, consoleHeight = consoleSize
        offsetX, offsetY = self.offset
        for y in range(consoleHeight):
            line = ""
            for x in range(consoleWidth):
                writeData = " "
                if offsetX <= x < offsetX + self.width and offsetY <= y < offsetY + self.height:
                    actualX, actualY = x-offsetX, y-offsetY
                    color, character = self.screen[(actualX, actualY)]["color"], self.screen[(actualX, actualY)]["char"]
                    writeData = color + character + "\033[0m"
                line += writeData
            print(line)

class Board:
    def __init__(self, size : tuple[int, int], boxSize : tuple[int, int]):
        self.width, self.height = size
        self.boxWidth, self.boxHeight = boxSize
        self.board = {}
        self.generateBoard()
        [self.generatePiece() for x in range(2)]
    
    def centreNumber(num):
        pass

    def generateBoard(self):
        for y in range(self.height):
            for x in range(self.width):
                self.board[(x, y)] = 0
    
    def generatePiece(self, allowFour : bool = False):

        chosenPiece = 4 if allowFour and random.random() <= 0.5 else 2

        for iter in range(self.width * self.height):
            randomX, randomY = random.randint(0, self.width-1), random.randint(0, self.height-1)
            if not self.board[(randomX, randomY)]:
                self.board[(randomX, randomY)] = chosenPiece
                break

    def generateHeaderFooter(self):
        header = "/"+ "+".join(["-"*self.boxWidth for x in range(self.width)])+"\\"
        footer = "\\"+ "+".join(["-"*self.boxWidth for x in range(self.width)])+"/"
        return header, footer
    
    def generateFillerJoiner(self):
        filler = "|"+ "|".join([" "*self.boxWidth for x in range(self.width)])+"|"
        joiner = "|"+ "+".join(["-"*self.boxWidth for x in range(self.width)])+"|"
        return filler, joiner

    def renderBoard(self, screen : Screen, offset : tuple[int, int]):
        header, footer = self.generateHeaderFooter()
        filler, joiner = self.generateFillerJoiner()
        screen.renderText(header,(0,0))

        for y in range(self.height*(self.boxHeight+1)):
            screen.renderText(filler,(0,y+1))
            if y % (self.boxHeight+1) == 0 and y > 0:
                screen.renderText(joiner,(0,y))
        screen.renderText(footer, (0, y+1))

        cellCentreY = [math.ceil(self.boxHeight / 2)+(self.boxHeight+1) * x for x in range(self.height)]
        cellCentreX = [1 + (self.boxWidth+1)*x for x in range(self.width)]
        halfCellWidth = math.ceil(self.boxWidth / 2)

        for y in range(self.height):
            for x in range(self.width):
                number = self.board[(x, y)]
                if not number:
                    continue
                numberOffsetX = halfCellWidth - math.ceil(len(str(number)) / 2)
                posX, posY = cellCentreX[x], cellCentreY[y]
                screen.renderText(str(number),(posX+numberOffsetX, posY),NUMBER_COLOURS[number])

    def generateOrder(self, direction : tuple[int, int]):
        if direction == (1, 0):
            return [(x, y) for y in range(self.height) for x in range(self.width-1, -1, -1)]
        elif direction == (-1, 0):
            return [(x, y) for y in range(self.height) for x in range(self.width)]
        elif direction == (0, 1):
            return [(x, y) for x in range(self.width) for y in range(self.height-1, -1, -1)]
        elif direction == (0, -1):
            return [(x, y) for x in range(self.width) for y in range(self.height)]

    def makeMove(self, direction : tuple[int, int]):
        #(1, 0) RIGHT
        #(-1, 0) LEFT
        #(0, 1) DOWN
        #(0, -1) UP
        order = self.generateOrder(direction)

        changedPos = []

        for position in order:
            currentPos = position
            while True:
                newPos = add2DTuple(currentPos, direction)

                if newPos not in self.board:
                    break
                
                if not self.board[newPos]:
                    self.board[newPos], self.board[currentPos] = self.board[currentPos], 0
                    currentPos = newPos
                elif self.board[newPos] == self.board[currentPos] and newPos not in changedPos:
                    self.board[newPos], self.board[currentPos] = 2 * self.board[newPos], 0
                    changedPos.append(newPos)
                    currentPos = newPos
                else:
                    break
    
    def handleInput(self, userInput : str):
        userInput = userInput.lower()
        if userInput in ["l","left"]:
            self.makeMove((-1, 0))
        elif userInput in ["r","right"]:
            self.makeMove((1, 0))
        elif userInput in ["u","up"]:
            self.makeMove((0, -1))
        elif userInput in ["d","down"]:
            self.makeMove((0, 1))

screen = Screen((SCREEN_WIDTH, SCREEN_HEIGHT-1), " ")

board = Board((4, 4),(6, 3))

while True:

    clearConsole()

    board.renderBoard(screen, (0, 0))

    screen.renderToConsole((SCREEN_WIDTH, SCREEN_HEIGHT-1))

    userInput = input("Enter (l, r, u, d) > ")

    board.handleInput(userInput)

    board.generatePiece(True)

    #Naughty Naughty
    SCREEN_WIDTH, SCREEN_HEIGHT = os.get_terminal_size()