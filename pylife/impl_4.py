# %%
from multiprocessing import Pool, cpu_count, Manager
from IPython.display import HTML
from utils.animation import animate

N = 5
N_CELLS = N ** 2
N_GEN = 20
N_SLICES = 5

glider_coords = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]

states = [[0 for _ in range(N)] for _ in range(N)]
generations = [states]


def init_cells():
    global states

    coordinates = []

    for x, y in glider_coords:
        states[x][y] = 1

    for x in range(N):
        for y in range(N):
            coordinates.append((x, y))

    return coordinates


def init_tasks(coordinates):

    task_size = N_CELLS // N_SLICES
    tasks = []
    task_coords = []
    counter = 0

    for x in range(N):
        for y in range(N):
            if counter == task_size:
                counter = 0
                tasks.append(task_coords)
                task_coords = []

            task_coords.append(coordinates[x * N + y])
            counter += 1

    if counter == task_size:
        tasks.append(task_coords)
    else:
        last = list(tasks[len(tasks) - 1])
        tasks.pop()

        for t in task_coords:
            last.append(t)
        tasks.append(last)

    return tasks


def find_neighbours(x, y):

    neighbours = []

    for i in range(3):
        for j in range(3):
            if i == 1 and j == 1:
                continue

            n = (x + i - 1) % N, (y + j - 1) % N
            neighbours.append(n)

    return neighbours


def check_neighbours(x, y):

    n_alive = 0
    state = states[x][y]

    for n_x, n_y in find_neighbours(x, y):
        n_alive += states[n_x][n_y]

    if state == 1 and (n_alive == 2 or n_alive == 3):
        return 1

    if n_alive < 2 or n_alive > 3:
        return 0

    if state == 0 and n_alive == 3:
        return 1

    return 0


def next_generation(task):

    results = []

    for x, y in task:
        state = check_neighbours(x, y)
        results.append((x, y, state))

    return results


def run_generation(tasks, pool):

    global states
    global generations

    result = [pool.apply(next_generation, args=(task,))
              for task in tasks]

    generation_states = [[0 for _ in range(N)] for _ in range(N)]

    for array in result:
        for x, y, value in array:
            generation_states[x][y] = value

    generations.append(generation_states)
    states[:] = generation_states[:]


if __name__ == '__main__':

    pool = Pool(cpu_count())

    coordinates = init_cells()

    tasks = init_tasks(coordinates)

    for _ in range(N_GEN-1):
        run_generation(tasks, pool)

    pool.terminate()

animation = animate(generations)
HTML(animation.to_html5_video())
