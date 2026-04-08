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

    def __lt__(self, other):
        return self.f() < other.f()  #用于优先队列

    #判断当前状态是否可解
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
    
    #启发函数，计算曼哈顿距离
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
    
def run(start_state, max_search=2000000):
    if not start_state.solvable():
        return -2  #如果不可解，直接返回-2
    
    best_g = {start_state.board_to_tuple(): 0}  #记录每个状态当前已知的最优步数
    visited_set = set()  #已经访问过的状态
    search = 0

    queue = [(start_state.f(), start_state.move, start_state)] #优先队列按照f值排序

    while queue:
        if search % 100000 == 0:
            print(f"已搜索状态数: {search}")

        if search > max_search:
            return -1  #如果搜索超限，返回-1
        _, _, current_state = heapq.heappop(queue)  #取出f值最小的状态
        current_key = current_state.board_to_tuple()

        #如果当前状态不是最优步数，跳过
        if current_state.move != best_g.get(current_key, float('inf')):
            continue  
        
        if current_key in visited_set:
            continue  #如果已经访问过，跳过
        visited_set.add(current_key)  #将当前状态加入已访问集合
        search += 1

        if current_key == current_state.goal_tuple:
            return current_state.move  #如果达到目标状态，返回移动步数
        
        for move in current_state.get_possible_moves():
            import copy
            new_board = copy.deepcopy(current_state.board)  #复制当前棋盘
            x, y = current_state.space_pos
            new_x, new_y = move
            #交换空格和目标位置的数字
            new_board[x][y], new_board[new_x][new_y] = new_board[new_x][new_y], new_board[x][y]
            new_state = PuzzleState(new_board, current_state.move + 1, (new_x, new_y))  #创建新状态
            new_key = new_state.board_to_tuple()
            
            if new_key in visited_set:
                continue  #如果新状态已经访问过，跳过
            
            #如果新状态的步数更优，更新best_g并加入优先队列
            if new_state.move < best_g.get(new_key, float('inf')):
                best_g[new_key] = new_state.move  
                heapq.heappush(queue, (new_state.f(), new_state.move, new_state))  #将新状态加入优先队列

    return -1  #如果搜索完所有状态仍未找到解，返回-1

   
def main():
    start_board = [
    [3,13,4,12],
    [2,5,7,10],
    [15,6,8,14],
    [0,1,11,9],
] 
    space_pos = (3,0)  #空格的位置
    start_state = PuzzleState(start_board, move=0, space_pos=space_pos)
    result = run(start_state, 200000)
    if result >= 0:
        print(f"移动步数: {result}")
    elif result == -1:
        print("搜索超限，未找到解")
    else:
        print("不可解")

if __name__ == "__main__": 
    main()
    