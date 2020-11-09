# %%
import numpy as np
import random
from queue import Queue
from threading import Thread, Lock, Condition
from IPython.display import HTML
from utils.animation import animate

N = 10
N_CELLS = N ** 2
N_GEN = 50

glider_coords = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]

cells = [[None for _ in range(N)] for _ in range(N)]
generations = [[[0 for _ in range(N)] for _ in range(N)] for _ in range(N_GEN)]

cells_done = 0

cells_done_lock = Lock()
generation_condition = Condition()


class Cell(Thread):
    global cells
    global cells_done

    def __init__(self, x, y, state=0):
        super().__init__()
        self.coord = x, y
        self.state = state
        self.neighbors = self.find_neighbours()
        self.queue = Queue()

    def find_neighbours(self):

        neighbours = []
        x, y = self.coord

        for i in range(3):
            for j in range(3):
                if i == 1 and j == 1:
                    continue

                n = (x + i - 1) % N, (y + j - 1) % N
                neighbours.append(n)

        return neighbours

    def check_neightbours(self):
        '''
        put cells's state in queue of each neighbour
        '''
        for x, y in self.neighbors:
            cells[x][y].put_state(self.state)

    def put_state(self, state):
        '''
        put state in cells queue
        '''
        self.queue.put(state)

    def read_queue(self):
        '''
        get neighbours states from queue
        '''
        n_alive = 0

        for _ in range(8):
            n_alive += self.queue.get()

        return n_alive

    def next_state(self):

        count = self.read_queue()

        if self.state == 1 and (count == 2 or count == 3):
            return

        if count < 2 or count > 3:
            self.state = 0
            return

        if self.state == 0 and count == 3:
            self.state = 1

    def update_state(self, generation):
        '''
        update matrix of states for current generation
        '''
        global cells_done

        self.check_neightbours()
        self.next_state()

        x, y = self.coord
        generations[generation][x][y] = self.state

        cells_done_lock.acquire()
        cells_done += 1
        generation_condition.acquire()

        if cells_done == N_CELLS:
            cells_done = 0
            cells_done_lock.release()
            generation_condition.notify_all()
        else:
            cells_done_lock.release()
            generation_condition.wait()

        generation_condition.release()

    def run(self):
        for i in range(N_GEN):
            self.update_state(i)


class GameOfLife():
    global N
    global cells

    def __init__(self):
        self.init_cells()

    def init_cells(self):

        for x in range(N):
            for y in range(N):
                cells[x][y] = Cell(x, y)

        for x, y in glider_coords:
            cells[x][y].state = 1

    def run(self):

        for x in range(N):
            for y in range(N):
                cells[x][y].start()

        for x in range(N):
            for y in range(N):
                cells[x][y].join()


if __name__ == '__main__':

    game_of_life = GameOfLife()
    game_of_life.run()


animation = animate(generations)
HTML(animation.to_html5_video())
