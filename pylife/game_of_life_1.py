# %%
import numpy as np
import random
from threading import Thread, Lock, Condition, Semaphore
from IPython.display import HTML
from utils.animation import animate


# number of row and columns for matrix
SIZE = 10
# number of generations / iterations that will be runned
NUM_GEN = 50

# matrix of cells (threads)
cells = [[None for i in range(SIZE)] for j in range(SIZE)]
# matrix of states for each cell of each generation
states = [[0 for i in range(SIZE)] for j in range(SIZE)]
# array of states matrix for each generation
generations = [states]

generation_condition = Condition()
cells_done = 0
cells_done_lock = Lock()


class Cell(Thread):
    global SIZE
    global NUM_GEN
    global cells
    global states
    global generations
    global generation_condition
    global cells_done
    global cells_done_lock

    def __init__(self, x, y, state=0):
        super().__init__()
        self.coord = x, y
        self.state = state
        self.neighbours = self.find_neighbours()
        self.counter = 0
        self.counter_lock = Lock()
        self.generation_lock = Semaphore()

    def find_neighbours(self):
        '''
        find coordinates of cell's neigbours
        every cell has 8 neighbours
        '''
        neighbours = []
        x, y = self.coord

        for i in range(3):
            for j in range(3):
                if i == 1 and j == 1:
                    continue

                n = (x + i - 1) % SIZE, (y + j - 1) % SIZE
                neighbours.append(n)

        return neighbours

    def check_neighbours(self):
        '''
        get sum of states of cell's neighbours
        '''
        n_alive = 0

        for x, y in self.neighbours:
            # n_alive += states[x][y]
            n_alive += self.get_state(x, y)

        return n_alive

    def get_state(self, x, y):
        '''
        get state from states matrix on given coordinates
        '''
        self.counter_lock.acquire()
        self.counter += 1

        if self.counter == 8:
            self.counter = 0
            self.generation_lock.release()

        self.counter_lock.release()

        return states[x][y]

    def update_state(self):
        '''
        check state of each neighbour and calculate new state
        '''
        count = self.check_neighbours()
        # x, y = self.coord
        state = states[self.coord[0]][self.coord[1]]

        # come to life
        if state == 0 and count == 3:
            return 1, count

        # underpopulation / overpopulation
        if count < 2 or count > 3:
            return 0, count

        # stays alive
        if state == 1 and (count == 2 or count == 3):
            return 1, count

        return state, count

    def next_generation(self):
        global cells_done

        self.generation_lock.acquire()
        next_state, _ = self.update_state()
        self.state = next_state
        x, y = self.coord
        states[x][y] = self.state

        cells_done_lock.acquire()
        cells_done += 1
        generation_condition.acquire()

        if cells_done == SIZE ** 2:
            cells_done = 0
            cells_done_lock.release()

            new_generation = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
            for x in range(SIZE):
                for y in range(SIZE):
                    new_generation[x][y] = states[x][y]

            generations.append(new_generation)
            generation_condition.notify_all()
        else:
            cells_done_lock.release()
            generation_condition.wait()

        generation_condition.release()

    def run(self):

        for _ in range(NUM_GEN):
            self.next_generation()


def init_cells():

    for x in range(SIZE):
        for y in range(SIZE):
            state = random.randint(0, 1)
            cells[x][y] = Cell(x, y)
            states[x][y] = state


def run():

    # start
    for x in range(SIZE):
        for y in range(SIZE):
            cells[x][y].start()

    # join
    for x in range(SIZE):
        for y in range(SIZE):
            cells[x][y].join()


def main():
    init_cells()
    run()


if __name__ == '__main__':

    main()
    animation = animate(generations)


HTML(animation.to_html5_video())
