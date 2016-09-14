# Projecto Integrado 2015/16
# Jogadas de Xadrez Gravadas com SimpleCV
# Rúben Januário - 32426
# António Peixe - 34164
#
#
from SimpleCV import *
from PIL import Image as img
import requests
from StringIO import StringIO
import time
import numpy as np
from datetime import datetime


# Method to get an image from the stream
def getNewImage():
    xpto =requests.get('http://peixe:peixe123@192.168.1.108:8080/shot.jpg')
    imgdata = xpto.content
    return Image(img.open(StringIO(imgdata)))

# Method to calibrate the board
# Returns an array with the calibration
def calibrate():
    
    output = []

    image = getNewImage()

    dl = DrawingLayer((image.width, image.height))
    
    redimagedistance = image.colorDistance((255,0,0)).binarize(110)
    redBlobs = redimagedistance.findBlobs()
    if redBlobs is None:
        print 'CALIBRATION FAILED'
        print 'NO RED DOT FOUND'
        return 0
    else:
        b = redBlobs[-1].coordinates()  
        dl.text('X', b, color = (255,0,0), alpha = -1)
        red = b

    blueimagedistance = image.colorDistance((0,0,255)).binarize(150)
    blueBlobs = blueimagedistance.findBlobs()
    if blueBlobs is None:
        print 'CALIBRATION FAILED'
        print 'NO BLUE DOT FOUND'
        return 0
    else:
        b = blueBlobs[-1].coordinates()    
        dl.text('X', b, color = (0,0,255), alpha = -1)
        blue = b
    
    x = (blue[0]+red[0])/2
    y = (blue[1]+red[1])/2
    centre = [x,y]
    square_side = (red[0]-blue[0])/8
    dl.text('X', centre, color = (0,255,0), alpha = -1)
    
    image.addDrawingLayer(dl)
    image.show()

    output.append(blue)
    output.append(red)
    output.append(centre)
    output.append(square_side)
    
    return output
    
# Method to calculate the distance between two points of the image
def getDistance(ref, point):
    return sqrt(pow(ref[0]-point[0],2) + pow(ref[1]-point[1],2))  

# Method to get the side of the black pieces
def getSide(image, calib):
    image = image.colorDistance().binarize(75)
    blob = image.findBlobs(minsize=50)
    blob = blob[-1]
    blob_coord = blob.coordinates()
    reddistance = getDistance(calib[1], blob_coord)
    bluedistance = getDistance(calib[0], blob_coord)
    return 0 if reddistance<bluedistance else 1

#Method to generate the board (depending on the side)
def generateBoard(side):
    board = np.zeros((8,8), dtype='a3')
    if side == 0:
        b = ['Br2','Bn2','Bb2','Bk ','Bq ','Bb1','Bn1','Br1','Bp8','Bp7','Bp6','Bp5','Bp4','Bp3','Bp2','Bp1']
        w = ['Wp8','Wp7','Wp6','Wp5','Wp4','Wp3','Wp2','Wp1','Wr2','Wn2','Wb2','Wk ','Wq ','Wb1','Wn1','Wr1']

        for col in range(0,2):
            for row in range(0,8):
                board[row, col] = w.pop()
                board[row, col+6] = b.pop()
                board[row, col+2] = '   '
                board[row, col+4] = '   '
    else:
        b = ['Bp8','Bp7','Bp6','Bp5','Bp4','Bp3','Bp2','Bp1','Br2','Bn2','Bb2','Bq ','Bk ','Bb1','Bn1','Br1']
        w = ['Wr2','Wn2','Wb2','Wq ','Wk ','Wb1','Wn1','Wr1','Wp8','Wp7','Wp6','Wp5','Wp4','Wp3','Wp2','Wp1']

        for col in range(0,2):
            for row in range(0,8):
                board[row, col] = b.pop()
                board[row, col+6] = w.pop()
                board[row, col+2] = '   '
                board[row, col+4] = '   '

    return board

# Method to calculate the board index with the pixels
def coordToBoard(centre, size, coord):
    x = coord[0]-centre[0]
    y = coord[1]-centre[1]

    l , c = (y/size)+4, (x/size)+4

    if l == 8:
        l = 7         
    if c == 8:
        c = 7 
    return [l, c]

# Method to trade two positions of the board
def trade(board, origin, destiny):
    board[destiny[0], destiny[1]] = board[origin[0],origin[1]]
    board[origin[0],origin[1]]  = '   '
    return board

# Method to return the name of the board places
def moveString(board, coords):
    letter = coords[0]
    if letter == 0:
        letter = 'A'
    elif letter == 1:
        letter = 'B'
    elif letter == 2:
        letter = 'C'
    elif letter == 3:
        letter = 'D'
    elif letter == 4:
        letter = 'E'
    elif letter == 5:
        letter = 'F'
    elif letter == 6:
        letter = 'G'
    elif letter == 7:
        letter = 'H'

    number = coords[1]
    if number == 0:
        number += 1
    elif number == 1:
        number += 1
    elif number == 2:
        number += 1
    elif number == 3:
        number += 1
    elif number == 4:
        number += 1
    elif number == 5:
        number += 1
    elif number == 6:
        number += 1
    elif number == 7:
        number += 1

    piece = board[coords[0],coords[1]]
    piece = piece[1:]
    return piece + "->" + letter + str(number)


# main Method (runs the program)
def main():
    
    d = Display()
    clicks = 0
    end = d.isDone()
    whites = True
    moveCount = 0
    output_file = open(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'w')
    
    while not end:
        end = d.isDone()
        if d.mouseLeft:
            clicks += 1
            
        
        if clicks == 1:
            calib = calibrate()
            clicks = 0 if calib == 0 else 2
        
        elif clicks == 3:
            image = getNewImage()
            side = getSide(image, calib)
            image = getNewImage()
            side2 = getSide(image, calib)
            image.show()
            if side != side2:
                print "CAN'T KNOW THE SIDES"
                print "REMOVE PIECES TO CALIBRATE AGAIN"
                clicks = 0
            else:
                if side == 0:
                    s =  "WHITES -> A BLACK"
                    print s
                    output_file.write(s+"\n")
                    s = "BLACKS -> A WHITE"
                    print s
                    output_file.write(s+"\n")
                    board = generateBoard(side)
                else:
                    s = "WHITES -> A WHITE"
                    print s
                    output_file.write(s+"\n")
                    s = "BLACKS -> A BLACK"
                    print s
                    output_file.write(s+"\n")
                    board = generateBoard(side)
                clicks += 1
                print board
        
        elif clicks >= 5 and clicks%2 != 0:
            secimage = getNewImage()
            dif = (secimage-image) + (image-secimage)
            dif_blobs = dif.findBlobs()
            
            if dif_blobs is not None:
                if len(dif_blobs) > 1:
                    blob1 = dif_blobs[-1].coordinates()
                    blob2 = dif_blobs[-2].coordinates()
                    dot1 = coordToBoard(calib[2], calib[3], blob1)
                    dot2 = coordToBoard(calib[2], calib[3], blob2)
                    print dot1, dot2
                    
                    if whites:
                        moveStr = ""
                        moveCount += 1
                        moveStr += str(moveCount) +") "
                        if 'W' in board[dot1[0], dot1[1]]:
                            board = trade(board, dot1, dot2)
                            moveStr += moveString(board,dot2) + " // "
                        else:
                            board = trade(board, dot2, dot1)
                            moveStr += moveString(board,dot1) + " // "
                        
                        output_file.write(moveStr)

                    else:
                        moveStr = ""
                        if 'B' in board[dot1[0], dot1[1]]:
                            board = trade(board, dot1, dot2)
                            moveStr += moveString(board,dot2) + "\n"
                        else:
                            board = trade(board, dot2, dot1)
                            moveStr += moveString(board,dot1) + "\n"

                        output_file.write(moveStr)

                    whites = not whites
                    image = secimage
                    image.show()
                    print board
                
                else:   
                    print "CAN'T SEE MOVED PIECES"
                    print "CLICK TO TRY AGAIN"
            
            else:
                print "CAN'T SEE MOVED PIECES"
                print "CLICK TO TRY AGAIN"
            
            clicks += 1

    output_file.close()


if __name__=="__main__":
    main()