import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def animate(steps):

    def init():
        im.set_data(steps[0])
        return [im]

    def animate(i):
        im.set_data(steps[i])
        return [im]

    im = plt.matshow(steps[0], interpolation='None', animated=True)
    figure = im.get_figure()

    return FuncAnimation(figure, animate, init_func=init, frames=len(steps), interval=100, blit=True, repeat=False)
