import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def animate(i):
    data = pd.read_csv('data.csv')
    x = data['time']

    plt.cla()
    for c in data.columns[1:]:
        plt.plot(x, data[c], label=c)
    
    plt.legend(loc='upper left')
    plt.tight_layout()


def main():
    plt.style.use('fivethirtyeight')
    ani = FuncAnimation(plt.gcf(), animate, interval=10000)
    plt.show()


if __name__ == "__main__":
    main()