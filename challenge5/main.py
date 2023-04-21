from multiprocessing import Process, Manager
import time

from map import WalkingPath

# Keep track of the current state of the map
current_map = []
map_rows = 0
map_cols = 0
start = None
destination = None

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
    start_mount = time.time()
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

    print(f'Mounting: {time.time() - start_mount}')
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
        for index, result_particle in enumerate(result):
            f.write(result_particle.get_result_data())
            if index < len(result)-1:
                f.write('\n')


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


def check_position_walkable(position, can_enter_destination):
    # if 0 <= position[0] < map_rows and 0 <= position[1] < map_cols:
    #     print(f'{(position[0],position[1])} : {current_map[position[0]][position[1]]}')
    if can_enter_destination:
        return current_map[position[0]][position[1]] != 1
    return position != destination and current_map[position[0]][position[1]] != 1


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main_start = time.time()
    init_map('input5.txt')

    # Start initial path
    start = get_starting_position()
    possible_movements.append([WalkingPath(start, 0)])

    # Set goal point
    destination = get_destination()
    print(destination)

    particle_at_start = True
    finished_particles = []

    # How many possible branching paths can we test per particle
    branching_limit = 12

    found_destination = [False]
    current_loop = 1
    while not all(found_destination):
        # print(f'Iteration {current_loop}: Particle {len(finished_particles)+1} '
        #       f'with {len(possible_movements[0])} paths available')
        print(f'Iteration {current_loop}: {len(possible_movements)} Particles '
              f'{[i for i in range(len(finished_particles)+1, len(finished_particles)+1 + len(possible_movements))]}')
        # for particle in possible_movements:
        #     print([p.path for p in particle])

        # Prepare next iteration of the map
        current_map = prepare_next_map()

        # write_map_to_file(current_map, f'test{current_loop+1}.txt')

        # Ensures paths that end the same node during this iteration are removed
        stepped_nodes = {}

        if not any(found_destination) and not particle_at_start:
            # print('Added particle')
            # Add another particle while destination not found yet
            possible_movements.append([WalkingPath(start, current_loop-1)])
            found_destination.append(False)

        # Check if particles can enter destination now
        destination_available = current_loop > 30000

        # Walk every possible direction
        start_walk = time.time()
        for particle in possible_movements:
            for movement_index in reversed(range(len(particle))):
                movement = particle[movement_index]

                # Check possible directions
                if current_loop % 2 == 0:
                    next_directions = {k: v for k, v in
                                       movement.get_possible_moves_down_first(map_rows, map_cols).items()
                                       if check_position_walkable(v, destination_available) and v not in stepped_nodes}
                else:
                    next_directions = {k: v for k, v in
                                       movement.get_possible_moves_right_first(map_rows, map_cols).items()
                                       if check_position_walkable(v, destination_available) and v not in stepped_nodes}

                if next_directions:
                    # Add walkable steps to stepped nodes
                    stepped_nodes.update({v: True for v in next_directions.values()})

                    # Set next directions as a list
                    next_directions = [(direction, pos) for direction, pos in next_directions.items()]

                    # Check if any direction is available
                    for direction, pos in next_directions[1:]:
                        # Check if particle can branch new movement tests
                        if len(particle) == branching_limit:
                            # Do not continue path and remove from stepped nodes
                            del stepped_nodes[pos]
                            continue

                        # If there are more possible nodes to walk to, add to the other paths list
                        particle.append(WalkingPath(pos, movement.turn_added, movement.path + [direction]))

                    movement.walk(*next_directions[0])

                    # Destination never counts as a stepped node
                    if destination in stepped_nodes:
                        del stepped_nodes[destination]

                else:
                    # Remove path as it has nowhere to go
                    del particle[movement_index]
        # Check if any particle stopped at starting point
        if not any(found_destination):
            particle_at_start = get_starting_position() in stepped_nodes

        # Remove particles without available path
        initial_len = len(possible_movements)
        possible_movements[:] = [particle for particle in possible_movements if particle]

        # Check if particle was removed
        if initial_len > len(possible_movements):
            # print('Removed particle')
            found_destination[:] = found_destination[:len(possible_movements) - initial_len]

        print(f'Walking: {time.time() - start_walk}')

        # Check if any path has the destination
        for particle_index in reversed(range(len(possible_movements))):
            particle = possible_movements[particle_index]
            remove_particle = False

            for finished_move in [move for move in particle
                                  if move.current_pos == destination]:
                print(finished_move)
                finished_particles.append(finished_move)
                found_destination[len(finished_particles)-1] = True
                remove_particle = True

                break

            # Remove particle
            if remove_particle:
                possible_movements.remove(particle)

        # Update current loop
        current_loop += 1

    # Sort finished particles to write in the file in ascending order
    finished_particles.sort(key=lambda x: x.turn_added)
    write_result_to_file(finished_particles, 'output5.txt')

    print(time.time() - main_start)
