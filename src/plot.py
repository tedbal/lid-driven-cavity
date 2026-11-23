# plotting utilities for the lid-driven cavity solver (post-processing)
# dependencies
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter
import re

# convert all columns in a df to numeric
def convert_all_numeric(df):
    for col in df.columns:
        df[col] = pd.to_numeric(df[col])
    return df

# create a helper function to read the size of the solution from the data file
def read_soln_size(datafile):
    # open the file and iterate line by line
    with open(datafile, 'r') as file:
        for line in file:
            # check if we fine the "schema" for the 
            match = re.search(r'I=\s*(\d+)\s+J=\s*(\d+)', line)

            # if the line matches, parse it and break the loop
            if match:
                i = int(match.group(1))
                j = int(match.group(2))
                break
            
    # return the results of the size of each index
    return i, j


# define a function to read the solution
def read_solution(datafile, n=-1):
    # set the columns, and initialize the "blocks" corresponding to an iteration
    columns = ['x', 'y', 'p', 'u', 'v']
    blocks = []
    current_block = []
    reading_data = False # flag to see if you are reading the data now

    # open the file
    with open(datafile, 'r') as file:
        # iterate through each line
        for line in file:
            # check if we are at the beginning of the zone
            if re.match(r'\s*zone\b', line, re.IGNORECASE):
                # save the previous block
                if current_block:
                    blocks.append(current_block)

                # reset the block and stop "reading data"
                current_block = []
                reading_data = False
                continue

            # start reading numerical data if we get to the datapacking line
            if 'DATAPACKING=POINT' in line.upper():
                reading_data = True
                continue

            # if reading the data, read it in
            if reading_data:
                values = line.split()
                
                if len(values) == len(columns):
                    try:
                        current_block.append(
                            [float(value) for value in values]
                        )
                    except ValueError:
                        continue

        # save final block
        if current_block:
            blocks.append(current_block)

    # return the requested block as DataFrame
    df = pd.DataFrame(blocks[n], columns=columns)
    df = convert_all_numeric(df)
    return df

# define a function to read the iterative convergence history
def read_convergence_history(datafile):
    # read in the data as a pd dataframe
    cols = ["iteration", "time", "resp", "resu", "resv"]
    df = pd.read_csv(datafile, sep=r"\s+", skiprows=2, names=cols, header=None)
    df = convert_all_numeric(df)
    return df

# define a plotting utility to take a history data file and plot the iteration convergence
def plot_iteration_history(history, savefile=None, ax=None):
    # if the axis is none, create it
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(8,8))

    # plot the plot
    ax.plot(history.iteration, history.resp, color='r', label='p')
    ax.plot(history.iteration, history.resu, color='b', label='u')
    ax.plot(history.iteration, history.resv, color='g', label='v')

    # format the plot
    ax.set_yscale("log")
    ax.set_xlabel("Iterations")
    ax.set_ylabel("Residual")
    ax.get_xaxis().set_major_formatter(FuncFormatter(lambda x, p: "{:,.0f}".format(x)))
    ax.legend()

    # save it (if applicable) and show it
    if savefile is not None:
        plt.savefig(savefile, dpi=600, bbox_inches='tight')
    plt.show()


# define a plotting utility to take a solution data file and plot the results
def plot_solution(res, nx, ny, savefile=None, axes=None):
    # if the axis is none, create it
    if axes is None:
        fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
        
    ax1, ax2, ax3 = axes

    # make a meshgrid of the x and y values
    x = res.x.values.reshape((nx, ny))
    y = res.y.values.reshape((nx, ny))

    # reshape each of the results so that they are readable by the
    p = res.p.values.reshape((nx, ny))
    u = res.u.values.reshape((nx, ny))
    v = res.v.values.reshape((nx, ny))
        
    # plot the plot
    im1 = ax1.contourf(x, y, p, cmap='coolwarm')
    im2 = ax2.contourf(x, y, u, cmap='coolwarm')
    im3 = ax3.contourf(x, y, v, cmap='coolwarm')
    ims = [im1, im2, im3]

    # format the plot
    ax1.set_ylabel("y [m]")
    ax1.set_title("Pressure [Pa]")
    ax2.set_title("u Velocity [m/s]")
    ax3.set_title("v Velocity [m/s]")
    
    for ax, im in zip(axes, ims):
        ax.set_xlabel("x [m]")
        ax.set_aspect(ny/nx)
        plt.colorbar(im, ax=ax)
    

    # save it (if applicable) and show it
    if savefile is not None:
        plt.savefig(savefile, dpi=600, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    # read and plot the history
    history = read_convergence_history("data/history.dat")
    plot_iteration_history(history)

    # read in the results
    res = read_solution("data/cavity.dat")
    nx, ny = read_soln_size("data/cavity.dat")
    plot_solution(res, nx, ny)
