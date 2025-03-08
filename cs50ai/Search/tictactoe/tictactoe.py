"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    return X if sum(row.count(EMPTY) for row in board) % 2 == 1 else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    available_actions = set()
    for row in range(3):
        for col in range(3):
            if board[row][col] == EMPTY:
                available_actions.add((row, col))
    return available_actions

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        raise Exception("Invalid action.")
    copy_board = [row[:] for row in board]  # ✅ 这样创建真正的新副本
    copy_board[action[0]][action[1]] = player(board)
    return copy_board



def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for row in board:
        if row.count(X)==3:
            return X
        elif row.count(O)==3:
            return O
    for col in range(3):
        if board[0][col]==board[1][col]==board[2][col]==X:
            return X
        elif board[0][col]==board[1][col]==board[2][col]==O:
            return O
    if board[0][0]==board[1][1]==board[2][2]==X or board[0][2]==board[1][1]==board[2][0]==X:
        return X
    elif board[0][0]==board[1][1]==board[2][2]==O or board[0][2]==board[1][1]==board[2][0]==O:
        return O
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) or not actions(board):
        return True
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if terminal(board):
        if winner(board)==X:
            return 1
        elif winner(board)==O:
            return -1
        else:
            return 0
        


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    if player(board) == 'X':
        best_score = -math.inf
        best_action = None
        for action in actions(board):
            score = min_value(result(board, action), -math.inf, math.inf)  # Min node follows
            if score > best_score:
                best_score = score
                best_action = action
    elif player(board) == 'O':  # current_player == O
        best_score = math.inf
        best_action = None
        for action in actions(board):
            score = max_value(result(board, action), -math.inf, math.inf)  # Max node follows
            if score < best_score:
                best_score = score
                best_action = action

    return best_action


def max_value(board, alpha, beta):
    """Returns the maximum possible score for X."""
    if terminal(board):  
        return utility(board)  # If game is over, return score.

    value = -math.inf
    for action in actions(board):
        new_board = result(board, action)  # 先计算新局面
        if terminal(new_board):  # 检查新局面是否终局
            return utility(new_board)  # 直接返回该局面的最终分数
        
        value = max(value, min_value(new_board, alpha, beta))  # 递归计算最小值
        alpha = max(alpha, value)  # 更新 α 值
        if alpha >= beta:
            break  # 进行 α-β 剪枝
    return value


def min_value(board, alpha, beta):
    """Returns the minimum possible score for O."""
    if terminal(board):  
        return utility(board)  # If game is over, return score.

    value = math.inf
    for action in actions(board):
        new_board = result(board, action)  # 先计算新局面
        if terminal(new_board):  # 检查新局面是否终局
            return utility(new_board)  # 直接返回该局面的最终分数
        
        value = min(value, max_value(new_board, alpha, beta))  # 递归计算最大值
        beta = min(beta, value)  # 更新 β 值
        if alpha >= beta:
            break  # 进行 α-β 剪枝
    return value
    
