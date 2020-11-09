# %%
from multiprocessing import Process, Queue, Manager, Value, Lock, Condition
from IPython.display import HTML
from utils.animation import animate

N = 10
N_CELLS = N ** 2
N_GEN = 50

glider_coords = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]

cells = [[None for _ in range(N)] for _ in range(N)]


class Service(Process):

    def __init__(self):
        super().__init__()
        self.generations = self.init_generations()
        self.receive_q = Queue()
        self.send_q = Queue()

    def init_generations(self):
        '''
        initialize array of states matrix for each generation
        '''
        return [[[0 for _ in range(N)] for _ in range(N)] for _ in range(N_GEN)]

    def next_generation(self, gen):
        '''
        updates generation matrix with states read from queue
        '''
        for _ in range(N_CELLS):
            x, y, state = self.receive_q.get()
            self.generations[gen][x][y] = state

    def run(self):

        for i in range(N_GEN):
            self.next_generation(i)

        self.send_q.put(self.generations)


class Cell(Process):
    global cells

    def __init__(self, x, y, service_q, cells_done, cells_done_lock, generation_condition, state=0):
        super().__init__()
        self.coord = x, y
        self.state = state
        self.neighbours = self.find_neighbours()
        self.cells_done = cells_done
        self.cells_done_lock = cells_done_lock
        self.generation_condition = generation_condition
        self.service_q = service_q
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

        for x, y in self.neighbours:
            cells[x][y].put_state(self.state)

    def put_state(self, state):
        self.queue.put(state)

    def read_queue(self):

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

    def update_state(self, gen):

        self.check_neightbours()
        self.next_state()

        x, y = self.coord
        self.service_q.put((x, y, self.state))

        self.cells_done_lock.acquire()
        self.cells_done.value += 1
        self.generation_condition.acquire()

        if self.cells_done.value == N_CELLS:
            self.cells_done.value = 0
            self.cells_done_lock.release()
            self.generation_condition.notify_all()
        else:
            self.cells_done_lock.release()
            self.generation_condition.wait()

        self.generation_condition.release()

    def run(self):

        for i in range(N_GEN):
            self.update_state(i)


class GameOfLife():
    global cells

    def __init__(self):
        self.service = Service()
        self.init_cells()
        self.generations = []

    def init_cells(self):

        cells_done = Value('i', 0)
        cells_done_lock = Lock()
        generation_condition = Condition()
        queue = self.service.receive_q

        for x in range(N):
            for y in range(N):
                cell = Cell(x, y, queue, cells_done,
                            cells_done_lock, generation_condition)
                cells[x][y] = cell

        for x, y in glider_coords:
            cells[x][y].state = 1

    def run(self):

        self.service.start()

        for x in range(N):
            for y in range(N):
                cells[x][y].start()

        for x in range(N):
            for y in range(N):
                cells[x][y].join()

        self.service.join()

        self.generations = self.service.send_q.get()


if __name__ == '__main__':

    game_of_life = GameOfLife()
    game_of_life.run()


animation = animate(game_of_life.generations)
HTML(animation.to_html5_video())
