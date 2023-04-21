import time
from map import WalkingPathPuzzle


def solve_puzzle(puzzle):
    initial_puzzle = [[col for col in row] for row in puzzle]
    print('Initial')
    print_puzzle(puzzle)

    # Call check first to ensure all fixed positions are set
    check_rule_of_4(puzzle)

    # Start error list with dummy value just to make sure it runs
    errors = [True]
    for i in range(6):
        puzzle = unite_elements(puzzle, '1')
        errors = check_rule_of_4(puzzle)
        puzzle = unite_elements(puzzle, '0')
        errors = check_rule_of_4(puzzle)

        # # Look for undefined cells to set them as dead
        # force_undefined_into(puzzle, 'D')
        # errors = check_rule_of_4(puzzle)

    # Set mutable values fixed
    for i, row in enumerate(puzzle):
        for j, col in enumerate(row):
            if puzzle[i][j] == 'A':
                puzzle[i][j] = '1'
            elif puzzle[i][j] == 'D':
                puzzle[i][j] = '0'

    print('Comparison')
    comparison = []
    for i, row in enumerate(puzzle):
        comparison.append(initial_puzzle[i])
        comparison[i].extend(['.' for _ in range(5)])
        comparison[i].extend(row)

    print_puzzle(comparison)


def force_undefined_into(puzzle, mark):
    for i, row in enumerate(puzzle):
        for j, col in enumerate(row):
            if puzzle[i][j] == 'x':
                puzzle[i][j] = mark


def unite_elements(puzzle, mark):
    unite_done = False

    # Convert base fixed mark to the mark that can be changed
    mutable_mark = 'A' if mark == '1' else 'D'

    # Shows how many conversions paths should start with
    base_conversions = 0
    while not unite_done:
        # if base_conversions == 102:
        #     break

        # Find marks (0s or 1s)
        location_marks = []
        for i in range(len(puzzle)):
            for j in range(len(puzzle[0])):
                if puzzle[i][j] in [mark, mutable_mark]:
                    location_marks.append((i, j))
        # print(location_marks)

        # Prepare copy of puzzle
        new_puzzle = [[col for col in row] for row in puzzle]

        cur_location = location_marks.pop(0)

        # Check if every path that was deleted couldn't go farther even if it had more conversions
        could_use_more_conversions = False

        # Unite every mark with the closest not connected
        while location_marks:
            # Find nearest mark in original marks
            location_marks.sort(key=lambda x: distance(cur_location, x))
            # print(f'{cur_location} to {location_marks}')
            next_location = location_marks.pop(0)

            found_destination = False
            current_loop = 1

            # Start paths
            paths = [WalkingPathPuzzle(cur_location, new_puzzle, mutable_mark, base_conversions)]

            stepped_nodes = {}
            while not found_destination:
                # print(f'Iteration {current_loop}: {len(paths)} paths available')

                # Walk every possible direction
                start_walk = time.time()
                for movement_index in reversed(range(len(paths))):
                    movement = paths[movement_index]

                    # Check possible directions
                    if mark == '1':
                        next_directions = {k: v for k, v in movement.get_possible_moves(10, 10).items()
                                           if check_position_alive_walkable(v, movement.current_puzzle,
                                                                            movement.conversions)
                                           and v not in stepped_nodes}
                    elif mark == '0':
                        next_directions = {k: v for k, v in movement.get_possible_moves(10, 10).items()
                                           if check_position_dead_walkable(v, movement.current_puzzle,
                                                                           movement.conversions)
                                           and v not in stepped_nodes}
                        # if (3, 4) == movement.current_pos:
                        #     print(check_position_dead_walkable((4,4), movement.current_puzzle,
                        #                                  movement.conversions, True))
                        #     print((4,4) not in stepped_nodes)

                    if next_directions:
                        # Add walkable steps to stepped nodes
                        stepped_nodes.update({v: True for v in next_directions.values()})

                        # Set next directions as a list
                        next_directions = [(direction, pos) for direction, pos in next_directions.items()]

                        # Check if any direction is available
                        for direction, pos in next_directions[1:]:
                            # If there are more possible nodes to walk to, add to the other paths list
                            paths.append(WalkingPathPuzzle(pos, movement.current_puzzle, movement.mark,
                                                           movement.conversions, movement.path + [direction]))

                        movement.walk(*next_directions[0])

                    else:
                        # Checks if path could have used more conversions
                        could_use_more_conversions = could_use_more_conversions \
                                                     or paths[movement_index].conversions == 0
                        # Remove path as it has nowhere to go
                        del paths[movement_index]

                # print(f'Current paths: {len(paths)}')
                # for path in paths:
                #     print(path)
                # print('---------')
                # print(f'Walking: {time.time() - start_walk}')

                # Check if no paths were found
                if not paths:
                    # Check if should retry with more conversions or if it is useless
                    if could_use_more_conversions:
                        # Increase conversion number for next tries
                        base_conversions += 1
                    else:
                        # print(f'Reset puzzle on cell {next_location}')
                        # Reset base conversions
                        base_conversions = 0
                        if new_puzzle[next_location[0]][next_location[1]] != mutable_mark:
                            print_puzzle(new_puzzle)
                            raise Exception(f'Unreachable fixed {mark} cell at {next_location} '
                                            f'coming from {cur_location}!')
                        # Swap cell dead/alive state because it can't be reached
                        puzzle[next_location[0]][next_location[1]] = 'A' if mark == '0' else 'D'
                        # print_puzzle(puzzle)
                    location_marks = []
                    break


                # Check if any path has the destination
                for finished_move in [move for move in paths
                                      if move.current_pos == next_location]:
                    # print(f'Finished {finished_move}')

                    # Current location now points to next location to look for the next closer 1
                    cur_location = next_location
                    new_puzzle = [[col for col in row] for row in finished_move.current_puzzle]

                    # Print puzzle for every finished interaction
                    # print_puzzle(new_puzzle)

                    found_destination = True

                    # Check if all cells were united
                    if not location_marks:
                        unite_done = True

                # Update current loop
                current_loop += 1

    # Make mutable marks fixed
    # for i, row in enumerate(puzzle):
    #     for j, col in enumerate(row):
    #         if new_puzzle[i][j] == mutable_mark:
    #             new_puzzle[i][j] = mark
    print(f'Finished uniting {mark}')
    print_puzzle(new_puzzle)
    return new_puzzle


def check_position_alive_walkable(position, base_puzzle, conversions, log=False):
    # Create puzzle copy
    puzzle = [[col for col in row] for row in base_puzzle]

    x, y = position
    if puzzle[x][y] == '0':
        return False
    if puzzle[x][y] in ['1', 'A']:
        return True
    if puzzle[x][y] == 'D':
        # Mutable dead cells can be converted if there are conversions still available
        if conversions > 0:
            puzzle[x][y] = 'A'
        else:
            return False
    if puzzle[x][y] == 'x':
        puzzle[x][y] = 'A'

    # If undetermined, check rule of 4 for every group of 4 cells involving position
    for i in range(max(0, x-1), min(9, x+1)):
        for j in range(max(0, y-1), min(9, y+1)):
            # Check for right to bottom square
            elements = []
            elements.extend([puzzle[i][j], puzzle[i][j + 1], puzzle[i + 1][j], puzzle[i + 1][j + 1]])
            num_1 = elements.count('1') + elements.count('A')

            if log:
                print(elements)
            if num_1 == 4:
                # After converting this x to 1 the first rule would be broken
                return False
    return True


def check_position_dead_walkable(position, base_puzzle, conversions, log=False):
    # Create puzzle copy
    puzzle = [[col for col in row] for row in base_puzzle]

    x, y = position
    if puzzle[x][y] == '1':
        return False
    if puzzle[x][y] in ['0', 'D']:
        return True
    if puzzle[x][y] == 'A':
        # Mutable alive cells can be converted if there are conversions still available
        if conversions > 0:
            puzzle[x][y] = 'D'
        else:
            return False
    if puzzle[x][y] == 'x':
        puzzle[x][y] = 'D'

    # If undetermined or mutable alive, check rule of 4 for every group of 4 cells involving position
    for i in range(max(0, x-1), min(9, x+1)):
        for j in range(max(0, y-1), min(9, y+1)):
            # Check for right to bottom square
            elements = []
            elements.extend([puzzle[i][j], puzzle[i][j + 1], puzzle[i + 1][j], puzzle[i + 1][j + 1]])
            num_0 = elements.count('0') + elements.count('D')

            if log:
                print(elements)
            if num_0 == 4:
                # After converting this x to 1 the first rule would be broken
                return False
    return True


def distance(location_1, location_2):
    return abs(location_1[0] - location_2[0]) + \
           abs(location_1[1] - location_2[1])


def print_puzzle(puzzle):
    for row in puzzle:
        print([row[col] for col in range(len(row))])

    print('-----------------------------------------------------------------------------')


def check_rule_of_4(puzzle):
    errors = []
    # Check for rule 1 (no square with same values)
    for i in range(len(puzzle) - 1):
        for j in range(len(puzzle[0]) - 1):
            # Check for right to bottom square
            elements = []
            elements.extend([puzzle[i][j], puzzle[i][j + 1], puzzle[i + 1][j], puzzle[i + 1][j + 1]])
            num_x = elements.count('x')
            num_0 = elements.count('0')
            num_d = elements.count('D')
            num_1 = elements.count('1')
            num_a = elements.count('A')

            # Rule of 4 adjacent broken by dead
            if num_0 + num_d == 4:
                errors.append((i, j))
                # Prepare swap coordinates
                x, y = i, j

                # If cell is fixed, swap one of its neighbors
                if puzzle[i][j] == '0':
                    if puzzle[i+1][j] != '0':
                        x += 1
                    elif puzzle[i][j+1] != '0':
                        y += 1
                    elif puzzle[i+1][j+1] != '0':
                        x += 1
                        y += 1

                # Swap
                puzzle[x][y] = 'A'

                print(f'ERROR on cell {i,j}, swapped {x, y} to A')
                # raise Exception('ERROR')
            # Rule of 4 adjacent broken by alive
            elif num_1 + num_a == 4:
                errors.append((i, j))
                # Prepare swap coordinates
                x, y = i, j

                # If cell is fixed, swap one of its neighbors
                if puzzle[i][j] == '1':
                    if puzzle[i+1][j] != '1':
                        x += 1
                    elif puzzle[i][j+1] != '1':
                        y += 1
                    elif puzzle[i+1][j+1] != '1':
                        x += 1
                        y += 1

                # Swap
                puzzle[x][y] = 'D'

                print(f'ERROR on cell {i,j}, swapped {x, y} to D')
                # raise Exception('ERROR')
            elif num_0 + num_d == 3 and num_x == 1:
                # print(f'{elements} {elements.count("x")} {elements.count("0")} {elements.count("1")}')
                # Other element has to be 1 or A
                x, y = convert_index_to_coordinates(i, j, elements.index('x'))

                # If no D is available, it means it should be fixed
                mark = '1' if num_d == 0 else 'A'
                puzzle[x][y] = mark
                print(f'Added {mark} at {x,y}')
            elif num_1 + num_a == 3 and num_x == 1:
                # print(f'{elements} {elements.count("x")} {elements.count("0")} {elements.count("1")}')
                # Other element has to be 0 or D
                x, y = convert_index_to_coordinates(i, j, elements.index('x'))

                # If no A is available, it means it should be fixed
                mark = '0' if num_a == 0 else 'D'
                puzzle[x][y] = mark
                print(f'Added {mark} at {x,y}')

    print('After rule of 4')
    print_puzzle(puzzle)
    return errors


def convert_index_to_coordinates(i, j, index):
    if index == 1:
        return i, j+1
    elif index == 2:
        return i+1, j
    elif index == 3:
        return i+1, j+1
    else:
        return i, j