

#
#  Simple Pirate worker
#  Connects REQ socket to tcp://*:5556
#  Implements worker part of LRU queueing
#
#   Author: Daniel Lundin <dln(at)eintr(dot)org>
#


from random import randint
import time
import zmq
import binascii


	

import struct

class DataStream(bytearray):

    def append(self, v, fmt='>B'):
        self.extend(struct.pack(fmt, v))



def print_board(board) :
    toto = ""
    for i in range(9):
        if int(board[i*7 + 3]) == 2:
            toto += "MM "
        else:
            toto += "   "
    print(toto)

    for i in range(7):
        line = ""
        for j in range(9):
            if i == 3:
                if int(board[j*7 + i]) == 0:
                    line += "MM "
                else:
                    line += "   "
            else: 
                line += str(int(board[j*7 + i])).ljust(2,'0') + " "
        print(line)
    
    tata = ""
    for i in range(9):
        if int(board[i*7 + 3]) == 1:
            tata += "MM "
        else:
            tata += "   "
    print(tata)
    
    hand = "    "
    for i in range(6):
        hand += str(int(board[9*7+ i])).ljust(2,'0') + " "
    print(hand)


context = zmq.Context(1)
worker = context.socket(zmq.REQ)

identity = "%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000))
worker.setsockopt_string(zmq.IDENTITY, identity)
worker.connect("tcp://localhost:5555")

print("I: (%s) worker ready" % identity)

# empty keys means that we don't have game id nor client id
worker.send_multipart([b"",b""])

def getValueFromUser(prompt, validValues, initialValue = -1):
    choice = initialValue
    while choice not in validValues:    
        print(prompt)
        try:
            choice = int(input())
        except ValueError:
            pass
    return choice

cycles = 0
while True:
    [playerKey, gameKey, errorCode, board] = worker.recv_multipart()
    if not playerKey:
        break

    print("\n@@@@@@@@@ NEW TURN @@@@@@@@@@@@@@@@\n")
    print("Player Key : ", binascii.hexlify(playerKey).decode())
    print("Game Key : ", binascii.hexlify(gameKey).decode())
    errorCode = int(errorCode[0])
    if errorCode == 1:
        print("You won!")
        break
    if errorCode == 2:
        print("You lost!")
        break
    if errorCode == 3:
        print("Coup invalide!")
        errorCode = 0
    if errorCode == 0:
        print("##########################")
        print_board(board)
        print("##########################")
    
    moveType = getValueFromUser("\nYour choice? 1) reclaim totem 2) play card", [1, 2])

    cardId = 255
    milestoneId = -1

    if moveType == 1:
        milestoneId = getValueFromUser("Which milestone do you want to reclaim (0, 1, ..., 8)?", range(9))
    else:
        cardId = getValueFromUser("What card do you want to play (0, 1, ..., 6)?", range(7))
        milestoneId = getValueFromUser("On what milestone do you want to put the card (0, 1, ..., 8)?", range(9))
    
    buffer = DataStream()
    buffer.append(moveType)
    buffer.append(cardId)
    buffer.append(milestoneId)

    worker.send_multipart([buffer])

    print(" Wating for other player to play ...")




