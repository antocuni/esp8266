import py
import sys
import dateutil.parser
from matplotlib import pyplot as plt
import matplotlib.dates as mdates

def parse(infile):
    values = []
    with infile.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                date, topic, val = line.rsplit(' ', 2)
                if topic != '/antocuni/fridge':
                    raise ValueError
            except ValueError:
                print 'Invalid line', line
                continue

            try:
                date = dateutil.parser.parse(date)
            except ValueError:
                print 'Invalid date', date
                continue

            val = float(val)
            values.append((date, val))
    return values

def plot(values):
    X = [date for date, val in values]
    Y = [val for date, val in values]

    fig, ax = plt.subplots()
    ax.set_xlabel('Time')
    ax.set_ylabel('Temperature')
    ax.grid(True)

    fmt = mdates.DateFormatter('%d/%m %H:%M')
    ax.format_xdata = fmt
    ax.xaxis.set_major_locator(mdates.HourLocator())
    ax.xaxis.set_major_formatter(fmt)
    ax.plot(X, Y)
    plt.show()

def main():
    infile = py.path.local(sys.argv[1])
    values = parse(infile)
    plot(values)

if __name__ == '__main__':
    main()
