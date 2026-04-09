"""
通过A*算法解决15-puzzle问题，启发式函数使用曼哈顿距离。
https://www.luogu.com.cn/article/d22yv1jh
"""
import heapq

class PuzzleState:
    def __init__(self,board,move,space_pos: tuple):
        self.board = board
        self.space_pos = space_pos  #空格的位置
        self.move = move  #已经移动的步数
        self.size = 4
        x,y = space_pos
        if board[x][y] != 0:
            raise ValueError("空格位置不正确")
        self.goal = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0]
        self.goal_tuple = (
            (1, 2, 3, 4),
            (5, 6, 7, 8),
            (9, 10, 11, 12),
            (13, 14, 15, 0),
        )
        if self.solvable():
            self.h_value = self.h()
        else:
            self.h_value = float('inf') 


    def __lt__(self, other):
        return self.f() < other.f()  #用于优先队列

    """
    判断当前状态是否可解，可解性与逆序数和空格所在行数有关。
    如果逆序数为偶数且空格在奇数行，或者逆序数为奇数且空格在偶数行，则可解。
    """
    def solvable(self):
        #计算逆序数
        flat_board = [num for row in self.board for num in row if num != 0]
        inversions = 0
        for i in range(len(flat_board)):
            for j in range(i + 1, len(flat_board)):
                if flat_board[i] > flat_board[j]:
                    inversions += 1
        #空格所在行数
        space_row = self.size - self.space_pos[0]
        #如果逆序数为偶数且空格在奇数行，或者逆序数为奇数且空格在偶数行，则可解
        if (inversions % 2 == 0 and space_row % 2 == 1) or (inversions % 2 == 1 and space_row % 2 == 0):
            return True
        return False

    def get_possible_moves(self):
        x, y = self.space_pos
        moves = []
        if x > 0:  # 上
            moves.append((x - 1, y))
        if x < self.size - 1:  # 下
            moves.append((x + 1, y))
        if y > 0:  # 左
            moves.append((x, y - 1))
        if y < self.size - 1:  # 右
            moves.append((x, y + 1))
        return moves
    
    #曼哈顿距离
    def h(self):
        res = 0
        for i in range(self.size):
            for j in range(self.size):
                value = self.board[i][j]
                if value == 0:
                    continue
                target_i = (value - 1) // self.size
                target_j = (value - 1) % self.size
                res += abs(i - target_i) + abs(j - target_j)
        return res

    def f(self):
        return self.move + self.h_value
    
    def board_to_tuple(self):
        return tuple(tuple(row) for row in self.board)  #将二维列表转换为不可变的元组，方便加入set中
    
def ida_star(state, threshold, visited):
    if not state.solvable():
        return -2
    if state.board_to_tuple() in visited:
        return float('inf')  #已经访问过
    visited.add(state.board_to_tuple())
    f_value = state.f()
    if f_value > threshold:
        return f_value  #超过当前阈值，返回f值
    if state.board == state.goal_tuple:
        return state.move  #找到解，返回移动步数
    min_threshold = float('inf')
    for move in state.get_possible_moves():
        import copy
        new_board = copy.deepcopy(state.board)  #深复制
        x, y = state.space_pos
        new_x, new_y = move
        #交换空格和目标位置的数字
        new_board[x][y], new_board[new_x][new_y] = new_board[new_x][new_y], new_board[x][y]
        new_state = PuzzleState(new_board, state.move + 1, (new_x, new_y))
        if not new_state.solvable():
            continue  #如果新状态不可解，跳过
        result = ida_star(new_state, threshold, visited)
        if result == -1:
            return -1  #搜索超限，未找到解
        min_threshold = min(min_threshold, result)
    visited.remove(state.board_to_tuple())  #回溯，移除当前状态
    return min_threshold

   
def main():
    start_board = [
    [3,13,4,12],
    [2,5,7,10],
    [8,0,6,14],
    [15,1,11,9],
] 
    space_pos = (2,1)  #空格的位置
    start_state = PuzzleState(start_board, move=0, space_pos=space_pos)
    result = ida_star(start_state, start_state.h_value, set())
    if result >= 0:
        print(f"移动步数: {result}")
    elif result == -1:
        print("搜索超限，未找到解")
    else:
        print("不可解")

if __name__ == "__main__": 
    main()
    