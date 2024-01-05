#Zijie Zhang, Sep.24/2023

import numpy as np
import socket, pickle
from reversi import reversi

MAX_DEPTH = 3
POSITIONAL_STRATEGY = [[150, -20,  10,  5,  5, 10, -20, 150],
                       [-20, -50,  -2, -2, -2, -2, -50, -20],
                       [10,   -2,  -1, -1, -1, -1,  -2,  10],
                       [5,    -2,  -1,  0,  0, -1,  -2,   5],
                       [5,    -2,  -1,  0,  0, -1,  -2,   5],
                       [10,   -2,  -1, -1, -1, -1,  -2,  10],
                       [-20,  -50, -2, -2, -2, -2, -50, -20],
                       [150,  -20, 10,  5,  5, 10, -20, 150]]

def heuristic(board):
    sum = 0
    for i in range(8):
        for j in range(8):
            sum += board[i][j]
    return sum


# return is in the form (x, y, heuristic, [next turns])
def next_turns(game, turn, depth):

    # base case
    if(depth == MAX_DEPTH):
        return []
    
    p_turns = []

    # player turn
    for i in range(8):
        for j in range(8):
            temp_game = reversi()
            temp_game.board = np.copy(game.board)
            cur_p = temp_game.step(i, j, turn, False)

            if cur_p > 0:
                temp_game.step(i, j, turn, True)
                h = heuristic(temp_game.board)
                o_turns = next_turns(temp_game, (-1)*turn, depth+1)                 # gets the next level of opponent turns
                num = turn
                if(depth%2 == 0):
                    if(num == -1):
                        num = 1
                        h = (-1)*h   
                if(depth%2 == 1):
                    if(num == 1):
                        num = -1
                        h = (-1)*h 
                p_turns.append((i,j,h+(num)*POSITIONAL_STRATEGY[i][j], o_turns))   # ADD TO HEURISTC HERE! or in heuristic function
                # positional strategy is hardcoded array with values ^^^

    return p_turns

def min_max(turns, depth):
    # base case
    if(depth == MAX_DEPTH):
        return turns[2]
    
    max = -300
    min = 300
    index = 0

    # max
    if(depth%2 == 0):
        # finds maximum heurisitc of each of the opponent turns
        for i in range(len(turns[3])):
            if(len(turns[3][i][3]) == 0):               # in case there is not further turns for player after opponent turn
                h = turns[3][i][2]
            else:
                h = min_max(turns[3][i][3], depth+1)

            h += turns[2]

            if(h > max):
                max = h
                index = i
        return turns[0], turns[1], max


    # min
    if(depth%2 == 1):
        # finds the minimum of players turn because greedy will choose the best possible turn for itself, so we want to minimize greedys points
        for i in range(len(turns)):
            if(turns[i][2] < min):
                min = turns[i][2]
                index = i
        return turns[index][2]

    return -1,-1,1

def main():
    game_socket = socket.socket()
    game_socket.connect(('127.0.0.1', 33333))
    game = reversi()



    while True:

        #Receive play request from the server
        #turn : 1 --> you are playing as white | -1 --> you are playing as black
        #board : 8*8 numpy array
        data = game_socket.recv(4096)
        turn, board = pickle.loads(data)

        #Turn = 0 indicates game ended
        if turn == 0:
            game_socket.close()
            return
        
        #Debug info
        print(turn)
        print(board)

        #AI algorithm
        x = -1
        y = -1
        max = 0
        game.board = board

        turns = next_turns(game, turn, 0)

        print("Turns" + str(turns))

        max = -300
        hs = []

        if(len(turns) == 0):                # No turns avalible
            x = -1
            y = -1
        if(len(turns) == 1):                # If there is just one avalible turn
            x = turns[0][0]
            y = turns[0][1] 
        else:                               # all else
            for i in turns:
                a = -1
                b = -1
                h = -64
                if(len(i[3]) == 0):         # if there are no opponent turns
                    a = i[0]
                    b = i[1]
                    h = i[2]
                else:
                    a,b,h = min_max(i, 0)
                      
                hs.append((a,b,h))          # just adding to a list so we can see the results of all heuristics of each turn :)

                if h > max:
                    max = h
                    x = a
                    y = b

            print("X: " + str(x))           # best x value
            print("Y: " + str(y))           # best y value
            print("Turn hs: " + str(hs))         # (x,y,h) all heuristic values of each move and their coords

        #Send your move to the server. Send (x,y) = (-1,-1) to tell the server you have no hand to play
        game_socket.send(pickle.dumps([x,y]))

        
if __name__ == '__main__':
    main()