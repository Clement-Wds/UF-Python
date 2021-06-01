import pygame
import socket
import time
import threading

s = socket.socket()
host = input("Entrez l'IP du serveur:")
port = 9999

playerOne = 1
playerOneColor = (255, 0, 0)
playerTwo = 2
playerTwoColor = (0, 0, 255)
bottomMsg = ""
msg = "En attente"
currentPlayer = 0
xy = (-1, -1)
allow = 0  # Autoriser l'interaction ( events de la souris)
matrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]


def create_thread(target):
    t = threading.Thread(target=target)
    t.daemon = True
    t.start()


pygame.init()

width = 600
height = 550
screen = pygame.display.set_mode((width, height))


pygame.display.set_caption("Tic Tac Toe Ynov")


# fonts
bigfont = pygame.font.Font('freesansbold.ttf', 64)
smallfont = pygame.font.Font('freesansbold.ttf', 32)
backgroundColor = (255, 255, 255)
titleColor = (0, 0, 0)
subtitleColor = (128, 0, 255)
lineColor = (0, 0, 0)


def buildScreen(bottomMsg, string, playerColor=subtitleColor):
    screen.fill(backgroundColor)
    if "One" in string or "1" in string:
        playerColor = playerOneColor
    elif "Two" in string or "2" in string:
        playerColor = playerTwoColor

    # vertical lines
    pygame.draw.line(screen, lineColor, (250-2, 150), (250-2, 450), 4)
    pygame.draw.line(screen, lineColor, (350-2, 150), (350-2, 450), 4)
    # horizontal lines
    pygame.draw.line(screen, lineColor, (150, 250-2), (450, 250-2), 4)
    pygame.draw.line(screen, lineColor, (150, 350-2), (450, 350-2), 4)

    title = bigfont.render("TIC TAC TOE", True, titleColor)
    screen.blit(title, (110, 0))
    subtitle = smallfont.render(str.upper(string), True, playerColor)
    screen.blit(subtitle, (150, 70))
    centerMessage(bottomMsg, playerColor)


def centerMessage(msg, color=titleColor):
    pos = (100, 480)
    if "One" in msg or "1" in msg:
        color = playerOneColor
    elif "Two" in msg or "2" in msg:
        color = playerTwoColor
    msgRendered = smallfont.render(msg, True, color)
    screen.blit(msgRendered, pos)


def printCurrent(current, pos, color):
    currentRendered = bigfont.render(str.upper(current), True, color)
    screen.blit(currentRendered, pos)


def printMatrix(matrix):
    for i in range(3):
        # Quand X augmente, y change
        y = int((i + 1.75) * 100)
        for j in range(3):
            # Quand colonne augemente, x change
            x = int((j + 1.75) * 100)
            current = " "
            color = titleColor
            if matrix[i][j] == playerOne:
                current = "X"
                color = playerOneColor
            elif matrix[i][j] == playerTwo:
                current = "O"
                color = playerTwoColor
            printCurrent(current, (x, y), color)


def validate_input(x, y):
    if x > 3 or y > 3:
        print("\nOut of bound! Enter again...\n")
        return False
    elif matrix[x][y] != 0:
        print("\nAlready entered! Try again...\n")
        return False
    return True


def handleMouseEvent(pos):
    x = pos[0]
    y = pos[1]
    global currentPlayer
    global xy
    if(x < 150 or x > 450 or y < 150 or y > 450):
        xy = (-1, -1)
    else:
        # Quand X augmente, y change
        col = int(x/100 - 1.5)
        # Quand colonne augemente, x changes
        row = int(y/100 - 1.5)
        print("({}, {})".format(row, col))
        if validate_input(row, col):
            matrix[row][col] = currentPlayer
            xy = (row, col)


def start_player():
    global currentPlayer
    global bottomMsg
    try:
        s.connect((host, port))
        print("Connecte a :", host, ":", port)
        recvData = s.recv(2048 * 10)
        bottomMsg = recvData.decode()
        if "1" in bottomMsg:
            currentPlayer = 1
        else:
            currentPlayer = 2
        start_game()
        s.close()
    except socket.error as e:
        print("Erreur de connection socket:", e)


def start_game():
    running = True
    global msg
    global matrix
    global bottomMsg
    create_thread(accept_msg)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if allow:
                    handleMouseEvent(pos)

        if msg == "":
            break

        buildScreen(bottomMsg, msg)
        printMatrix(matrix)
        pygame.display.update()


def accept_msg():
    global matrix
    global msg
    global bottomMsg
    global allow
    global xy
    while True:
        try:
            recvData = s.recv(2048 * 10)
            recvDataDecode = recvData.decode()
            buildScreen(bottomMsg, recvDataDecode)

            if recvDataDecode == "Input":
                failed = 1
                allow = 1
                xy = (-1, -1)
                while failed:
                    try:
                        if xy != (-1, -1):
                            coordinates = str(xy[0])+"," + str(xy[1])
                            s.send(coordinates.encode())
                            failed = 0
                            allow = 0
                    except:
                        print("Erreur , reessayez encore une fois")

            elif recvDataDecode == "Error":
                print("Erreur , reessayez encore une fois")

            elif recvDataDecode == "matrix":
                print(recvDataDecode)
                matrixRecv = s.recv(2048 * 100)
                matrixRecvDecoded = matrixRecv.decode("utf-8")
                matrix = eval(matrixRecvDecoded)

            elif recvDataDecode == "Over":
                msgRecv = s.recv(2048 * 100)
                msgRecvDecoded = msgRecv.decode("utf-8")
                bottomMsg = msgRecvDecoded
                msg = "~~~GG WP~~~"
                break
            else:
                msg = recvDataDecode

        except KeyboardInterrupt:
            print("\nKeyboard Interrupt")
            time.sleep(1)
            break

        except:
            print("Erreur")
            break


start_player()