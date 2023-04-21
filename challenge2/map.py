class WalkingPath:
    def __init__(self, current_position, path=[], lives=6):
        # Position is a tuple with (row, col)
        self.current_pos = current_position
        # Keeps a list of moves (U, D, R or L)
        # self.path = [step for step in path]
        self.path = path
        self.distance = 0
        # Checks if path is still alive
        self.lives = lives

    def __str__(self):
        return f'At {self.current_pos} with path: {" ".join(self.path)} and {self.lives} lives'

    def walk(self, direction, position, alive_cell):
        # Append move in specific direction to path and update current position
        self.path.append(direction)
        self.current_pos = position
        if alive_cell:
            self.lives -= 1

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

