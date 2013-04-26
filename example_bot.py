import time

MOVES = {
    'U' : (0, 1),
    'D' : (0, -1),
    'L' : (-1, 0),
    'R' : (1, 0)
}
def example_bot(board, (myX, myY), (enemyX, enemyY)):
    """Takes in a square 2d grid of booleans saying whether a
    square is blocked, a tuple containing my position (x, y),
    and a tuple containing the enemy's position (x, y).
    Board can be indexed using board[y][x]
    Outputs "U", "L", "D", or "R" to move, or a tuple of the form
    (x, y) in order to place a block at (x, y)
    """
    size = len(board)
    time.sleep(0.2)
    if board[(myY+1) % size][myX]:
        return "L"
    else:
        return "U"

if __name__ == "__main__":
    import blockade
    blockade.run("127.0.0.1", example_bot, "example_bot", (128, 128, 128))

