# %%

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from IPython.display import HTML
import numpy as np

cells = []
active_states = []


def animate(steps):

    def init():
        im.set_data(steps[0])
        return [im]

    def animate(i):
        im.set_data(steps[i])
        return [im]

    im = plt.matshow(steps[0], interpolation='None', animated=True)
    figure = im.get_figure()

    return FuncAnimation(figure, animate, init_func=init, frames=len(steps), interval=500, blit=True, repeat=False)


def init_steps(n):
    return [(np.random.rand(n**2).reshape(n, n) > 0.5).astype(np.int8) for i in range(50)]


def main():
    pass


if __name__ == '__main__':
    # main()
    steps = init_steps(20)
    animation = animate(steps)

HTML(animation.to_html5_video())
