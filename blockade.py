import socket
from copy import deepcopy

BUFFER_SIZE = 4096

soc = None

bot = colour = name = my_ID = board = None
pos = [(), ()]
TRANSLATE = {
    0: (0, -1),
    1: (1, 0),
    2: (0, 1),
    3: (-1, 0),
}

def dfs(pid, row):
    seen = [[False for x in range(len(board))] for y in range(len(board))]
    s = []
    s.append(pos[pid])
    while s:
        x,y = s.pop()
        if y == row:
            return True
        for i in xrange(4):
            dx, dy = TRANSLATE[i]
            nx = x + dx
            ny = y + dy
            if nx < 0 or ny < 0 or nx >= len(board) or ny >= len(board):
                continue
            if not board[ny][nx] and not seen[ny][nx]:
                s.append((nx, ny))
                seen[ny][nx] = True
    return False

def process_protocol(command):
    global board, pos, my_ID
    if command == '': return
    tokens = command.split()
    response = ''
    if tokens[0] == 'NAME':
        response = 'NAME %s %s' % (name, ' '.join(map(str, colour)))

    elif tokens[0] == 'NEWGAME':
        # player_count, boardsize, myid, key
        boardsize = int(tokens[2])
        my_ID = int(tokens[3])
        pos[my_ID] = (boardsize / 2, 0)
        pos[1-my_ID] = (boardsize / 2, boardsize - 1)
        board = [[False for j in range(boardsize)] for i in range(boardsize)]
        response = 'READY ' + tokens[4]

    elif tokens[0] == 'GAMEOVER':
        print 'Game over:', ' '.join(tokens[1:])
    
    elif tokens[0] == 'ACTION':
        pid = int(tokens[1])
        if tokens[2] == 'BLOCK':
            # BLOCK, pid, y, x
            x = int(tokens[4])
            y = int(tokens[3])
            y = y if my_ID == 0 else len(board) - y - 1
            board[y][x] = True
        elif tokens[2] == 'MOVE':
            # pid, dir
            dx, dy = TRANSLATE[int(tokens[3])]
            if my_ID == 1:
                dy *= -1
            pos[pid] = (pos[pid][0] + dx, pos[pid][1] + dy)

    elif tokens[0] == 'YOURMOVE':
        moves = {'D' : 0, 'R' : 1, 'U' : 2, 'L' : 3}
        result = bot(deepcopy(board), pos[my_ID], pos[1-my_ID])
        if result in moves:
            result = moves[result]
            x = pos[my_ID][0] + TRANSLATE[result][0]
            y = pos[my_ID][1] + TRANSLATE[result][1]
            if result % 2 == 0 and my_ID == 1: # %2 means vertical
                result = 2 - result #inverts y
            if y >= len(board) or x >= len(board) or x < 0 or y < 0:
                print "ERROR: (%d, %d) is out of bounds" % (x, y)
            elif board[y][x]:
                print "ERROR: (%d, %d) is blocked" % (x, y),
                print "You can't move there"
            response = "ACTION MOVE %d" % result
        elif len(result) == 2:
            x = int(result[0])
            y = int(result[1])
            if board[y][x]:
                print "ERROR: (%d, %d) is already blocked." % (x, y),
                print "You can't place a block there."
            if x == pos[my_ID][0] and y == pos[my_ID][1]:
                print "ERROR: you are on (%d, %d)" % (x, y)
            if x == pos[1-my_ID][0] and y == pos[1-my_ID][1]:
                print "ERROR: the enemy is on (%d, %d)" % (x, y)
            board[y][x] = True
            if not dfs(my_ID, len(board) - 1):
                print "ERROR: You can't place a block on (%d, %d)." % (x, y),
                print "It will block you off"
            if not dfs(1-my_ID, 0):
                print "ERROR: You can't place a block on (%d, %d)." % (x, y),
                print "It will block the enemy off"
            board[y][x] = False
            if my_ID == 1:
                y = len(board) - y - 1
            response = "ACTION BLOCK %d %d" % (y, x)
        else:
            print "ERROR: %s is not a valid move." % repr(result)
            print "Move must be 'U', 'L', 'D', 'R', or a tuple of form (x, y)"

    if response != '':
        soc.sendall(response + "\n")

def run(host, localbot, localname, localcolour, port=12317):
    global soc
    global colour, bot, name
    colour = localcolour
    bot = localbot
    name = localname
    bot = localbot
    soc = socket.create_connection((host, port))    
    data = ''
    while True:
        data += soc.recv(BUFFER_SIZE)
        data = data.replace("\r", '')
        if data == '':
            continue
        commands = data.split("\n")
        if data[-1] != "\n":
            data = commands[-1]
            commands = commands[:-1]
        else:
            data = ''
        for command in commands:
            process_protocol(command)
