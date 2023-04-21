from multiprocessing import Process, Manager
import time

from map import WalkingPath

# Keep track of the current state of the map
current_map = []
map_rows = 0
map_cols = 0

# Possible movements that are updated at every iteration
possible_movements = []

tests = []


# Start map
def init_map(input_file):
    # Start map with rows and columns
    with open(input_file, 'r') as file:
        for line in file:
            row = []
            for index, col in enumerate(line.strip().split(' ')):
                # row.append(Node(col, (len(current_map), index)))
                row.append(int(col))
            current_map.append(row)

    global map_rows
    map_rows = len(current_map)
    global map_cols
    map_cols = len(current_map[0])
    # fill_adjacent_nodes_info(current_map)


def fill_adjacent_nodes_info(base_map):
    # Iterate through map to fill adjacent node info
    for r_index, row in enumerate(base_map):
        for c_index, node in enumerate(row):
            # Fill adjacent nodes
            has_row_under = r_index + 1 < map_rows
            has_row_over = r_index > 0
            has_col_left = c_index > 0
            has_col_right = c_index + 1 < map_cols

            if has_col_right:
                node.adjacent_nodes.append(base_map[r_index][c_index + 1])
            if has_row_under and has_col_right:
                node.adjacent_nodes.append(base_map[r_index + 1][c_index + 1])
            if has_row_under:
                node.adjacent_nodes.append(base_map[r_index + 1][c_index])
            if has_row_under and has_col_left:
                node.adjacent_nodes.append(base_map[r_index + 1][c_index - 1])
            if has_col_left:
                node.adjacent_nodes.append(base_map[r_index][c_index - 1])
            if has_col_left and has_row_over:
                node.adjacent_nodes.append(base_map[r_index - 1][c_index - 1])
            if has_row_over:
                node.adjacent_nodes.append(base_map[r_index - 1][c_index])
            if has_row_over and has_col_right:
                node.adjacent_nodes.append(base_map[r_index - 1][c_index + 1])


def count_neighbors(i, j):
    count = 0
    min_j = j - 1 if j > 0 else 0
    max_j = j + 2 if j < map_cols - 1 else map_cols
    range_j = range(min_j, max_j)
    # for x in range(i-1 if i > 0 else 0, i + 2 if i < map_rows - 1 else map_rows):
    #     # for y in range(j-1 if j > 0 else 0, j + 2 if j < map_cols - 1 else map_cols):
    #     for y in range(min_j, max_j):
    #         if x == i and y == j:
    #             continue
    #         if current_map[x][y] == 1:
    #             count += 1

    for y in range_j:
        if y == j:
            continue
        if current_map[i][y] == 1:
            count += 1
    i -= 1
    if i >= 0:
        for y in range_j:
            if current_map[i][y] == 1:
                count += 1
    i += 2
    if i < map_rows:
        for y in range_j:
            if current_map[i][y] == 1:
                count += 1
    return count


def set_next_value(i, j):
    if current_map[i][j] == 0:
        num_neighbors = count_neighbors(i, j)
        if 1 < num_neighbors < 5:
            return 1
        return 0
    elif current_map[i][j] == 1:
        num_neighbors = count_neighbors(i, j)
        if 3 < num_neighbors < 6:
            return 1
        return 0
    return current_map[i][j]


def set_next_row(next_map, start_row, n_rows):
    # start_test = time.time()
    # print('started ' + str(i))
    # for cur_row in range(i, min(i + n_rows, map_rows)):
    #     next_map[cur_row] = [set_next_value(next_map, cur_row, j) for j in range(map_cols)]
    max_row = map_rows if start_row + n_rows > map_rows else start_row + n_rows
    next_map[start_row : max_row] = [[set_next_value(cur_row, cur_col) for cur_col in range(map_cols)]
                                     for cur_row in range(start_row, max_row)]
    # print(time.time() - start_test)


def prepare_next_map():
    n_rows = 125
    # Consider map will always be a 2-dimensional matrix of the same size as the initial map
    start = time.time()
    # next_map = [[Node(node.decide_next_state(), node.position) for node in row] for row in current_map]
    # next_map = [[0 for _ in range(map_cols)] for _ in range(map_rows)]

    with Manager() as manager:
        next_map = manager.list([0 for _ in range(map_rows)])

        ps = [Process(target=set_next_row, args=(next_map, row, n_rows)) for row in range(0, map_rows, n_rows)]
        for p in ps:
            p.start()
        for p in ps:
            p.join()

        next_map = list(next_map)

    print(f'Mounting: {time.time() - start}')
    # start = time.time()
    # fill_adjacent_nodes_info(next_map)
    # print(f'Filling: {time.time() - start}')
    return next_map


def write_map_to_file(base_map, filename):
    # Used for debugging purposes
    with open(filename, 'w') as f:
        for row in base_map:
            f.write(' '.join([str(node) for node in row]))
            f.write('\n')


def write_result_to_file(result, filename):
    # Used for debugging purposes
    with open(filename, 'w') as f:
        f.write(' '.join([step for step in result]))


def get_starting_position():
    # for row in current_map:
    #     for node in row:
    #         if node.state == 3:
    #             return node.position

    for i in range(map_rows):
        for j in range(map_cols):
            if current_map[i][j] == 3:
                return i, j
    # Return upper left as default
    return 0, 0


def get_destination():
    # for row in current_map:
    #     for node in row:
    #         if node.state == 4:
    #             return node.position

    for i in range(map_rows):
        for j in range(map_cols):
            if current_map[i][j] == 4:
                return i, j
    # Return lower right as default
    return len(current_map)-1, len(current_map[0])-1


def check_position_walkable(position):
    # if 0 <= position[0] < map_rows and 0 <= position[1] < map_cols:
    #     print(f'{(position[0],position[1])} : {current_map[position[0]][position[1]]}')
    return current_map[position[0]][position[1]] != 1


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main_start = time.time()
    init_map('input1.txt')

    # Start initial path
    possible_movements.append(WalkingPath(get_starting_position()))

    # Set goal point
    destination = get_destination()

    found_destination = False
    current_loop = 1
    while not found_destination:
        print(f'Iteration {current_loop}: {len(possible_movements)} paths available')

        # Prepare next iteration of the map
        current_map = prepare_next_map()

        # write_map_to_file(current_map, f'test{current_loop+1}.txt')

        # Ensures paths that end the same node during this iteration are removed
        stepped_nodes = {}

        # Remove worst performers
        if current_loop % 20 == 0:
            distances = [movement.get_distance(destination, True) for movement in possible_movements]
            max_distance = max(distances)
            min_distance = min(distances)
            avg_distance = (max_distance + min_distance)/2

            possible_movements[:] = [movement for movement in possible_movements if
                                     movement.get_distance(destination) < avg_distance]

        # Walk every possible direction
        start_walk = time.time()
        for movement_index in reversed(range(len(possible_movements))):
            movement = possible_movements[movement_index]

            # Check possible directions
            next_directions = {k: v for k, v in movement.get_possible_moves(map_rows, map_cols).items()
                               if check_position_walkable(v) and v not in stepped_nodes}

            if next_directions:
                # Add walkable steps to stepped nodes
                stepped_nodes.update({v: True for v in next_directions.values()})

                # Set next directions as a list
                next_directions = [(direction, pos) for direction, pos in next_directions.items()]

                # Check if any direction is available
                for direction, pos in next_directions[1:]:
                    # If there are more possible nodes to walk to, add to the other paths list
                    possible_movements.append(WalkingPath(pos, movement.path + [direction]))

                movement.walk(*next_directions[0])

            else:
                # Remove path as it has nowhere to go
                del possible_movements[movement_index]

        print(f'Walking: {time.time() - start_walk}')

        # Check if any path has the destination
        for finished_move in [move for move in possible_movements
                              if move.current_pos == destination]:
            print(finished_move)
            write_result_to_file(finished_move.path, 'output1.txt')
            found_destination = True

        # Update current loop
        current_loop += 1

    print(time.time() - main_start)
