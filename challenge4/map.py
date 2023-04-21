class WalkingPath:
    def __init__(self, current_position, path=[]):
        # Position is a tuple with (row, col)
        self.current_pos = current_position
        # Keeps a list of moves (U, D, R or L)
        # self.path = [step for step in path]
        self.path = path
        self.distance = 0

    def __str__(self):
        return f'At {self.current_pos} with path: {" ".join(self.path)}'

    def walk(self, direction, position):
        # Append move in specific direction to path and update current position
        self.path.append(direction)
        self.current_pos = position

    def get_possible_moves(self, n_rows, n_cols):
        moves = {}
        if self.current_pos[0] > 0:
            moves['U'] = self.current_pos[0]-1, self.current_pos[1]
        if self.current_pos[0] < n_rows-1:
            moves['D'] = self.current_pos[0]+1, self.current_pos[1]
        if self.current_pos[1] < n_cols-1:
            moves['R'] = self.current_pos[0], self.current_pos[1]+1
        if self.current_pos[1] > 0:
            moves['L'] = self.current_pos[0], self.current_pos[1]-1
        return moves

    def get_distance(self, destination, calculate=False):
        if calculate:
            self.distance = abs(destination[0] - self.current_pos[0]) +\
                            abs(destination[1] - self.current_pos[1])
        return self.distance


class WalkingPathPuzzle:
    def __init__(self, current_position, puzzle, mark, path=None):
        # Position is a tuple with (row, col)
        self.current_pos = current_position
        # Keeps a list of moves (U, D, R or L)
        # self.path = [step for step in path]
        self.path = path if path else []
        self.distance = 0
        self.mark = mark
        self.current_puzzle = [[col for col in row] for row in puzzle]

        # Update current position
        self.update_current_position()

    def __str__(self):
        return f'At {self.current_pos} with path: {" ".join(self.path)}'

    def walk(self, direction, position):
        # Append move in specific direction to path and update current position
        self.path.append(direction)
        self.current_pos = position

        # Update current position
        self.update_current_position()

    def get_possible_moves(self, n_rows, n_cols):
        moves = {}
        if self.current_pos[0] > 0:
            moves['U'] = self.current_pos[0]-1, self.current_pos[1]
        if self.current_pos[0] < n_rows-1:
            moves['D'] = self.current_pos[0]+1, self.current_pos[1]
        if self.current_pos[1] < n_cols-1:
            moves['R'] = self.current_pos[0], self.current_pos[1]+1
        if self.current_pos[1] > 0:
            moves['L'] = self.current_pos[0], self.current_pos[1]-1
        return moves

    def get_distance(self, destination, calculate=False):
        if calculate:
            self.distance = abs(destination[0] - self.current_pos[0]) +\
                            abs(destination[1] - self.current_pos[1])
        return self.distance

    def update_current_position(self):
        x, y = self.current_pos
        if self.current_puzzle[x][y] == 'x':
            self.current_puzzle[x][y] = self.mark