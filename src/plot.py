# plotting utilities for the lid-driven cavity solver (post-processing)
# dependencies
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter
import re
import sys

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

# define a function to read the metadata about the solution
def read_parameters(datafile):
    # initialize the dictionary
    res = {}

    # open the file, and iterate through each line
    with open(datafile, 'r') as fi:
        for line in fi:
            # read the line, and split it into the name and value
            line = line.strip()
            name, val = line.split("=")

            # turn the value into a float if "." in it, otherwise into an int
            if "." in val:
                val_num = float(val)
            else:
                val_num = int(val)

            # read in the name and value into the result dictionary
            res[name] = val_num

    return res

# define a function to read the solution
def read_solution(datafile, n=-1):
    # set the columns, and check if it is an exact solution or not
    with open(datafile, 'r') as fi:
        next(fi)
        if "-exact" in fi.readline():
            columns = ['x', 'y', 'p', 'u', 'v', 'pe', 'ue', 've', 'dep', 'deu', 'dev']
        else:
            columns = ['x', 'y', 'p', 'u', 'v']

    # initialize the "blocks" corresponding to an iteration
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
                        current_block.append([float(value) for value in values])
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
def plot_solution(res, nx, ny, savefile=None, axes=None, streamlines=True):
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

    # plot streamlines (if applicable)
    U = np.sqrt(np.square(u) + np.square(v))
    if streamlines:
        ax2.streamplot(x[:,0], y[0,:], u, v, color='k', linewidth=U, density=0.7, broken_streamlines=False)
        ax3.streamplot(x[:,0], y[0,:], u, v, color='k', linewidth=U, density=0.7, broken_streamlines=False)

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




# define a plotting utility to take a solution data file and plot the results
def plot_de(res, nx, ny, savefile=None, axes=None):
    # if the axis is none, create it
    if axes is None:
        fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
        
    ax1, ax2, ax3 = axes

    # make a meshgrid of the x and y values
    x = res.x.values.reshape((nx, ny))
    y = res.y.values.reshape((nx, ny))

    # reshape each of the results so that they are readable by the
    p = res.dep.values.reshape((nx, ny))
    u = res.deu.values.reshape((nx, ny))
    v = res.dev.values.reshape((nx, ny))
        
    # plot the plot
    im1 = ax1.contourf(x, y, p, cmap='Reds')
    im2 = ax2.contourf(x, y, u, cmap='Reds')
    im3 = ax3.contourf(x, y, v, cmap='Reds')
    ims = [im1, im2, im3]

    # format the plot
    ax1.set_ylabel("y [m]")
    ax1.set_title("Pressure\nDiscretization Error")
    ax2.set_title("u Velocity\nDiscretization Error")
    ax3.set_title("v Velocity\nDiscretization Error")
    
    for ax, im in zip(axes, ims):
        ax.set_xlabel("x [m]")
        ax.set_aspect(ny/nx)
        plt.colorbar(im, ax=ax)
    
    # save it (if applicable) and show it
    if savefile is not None:
        plt.savefig(savefile, dpi=600, bbox_inches='tight')
    plt.show()


 
    
    

if __name__ == "__main__":
    # parse in the filename
    if len(sys.argv) > 1:
        datapath = sys.argv[1]
    else:
        datapath = "data/"

    # define the history and results file
    historyfile = f"{datapath}/history.dat"
    resultsfile = f"{datapath}/cavity.dat"
    paramsfile  = f"{datapath}/parameters.dat"

    # read the parameters
    params = read_parameters(paramsfile)
    
    # read and plot the history
    history = read_convergence_history(historyfile)
    plot_iteration_history(history)

    # read in the results
    res = read_solution(resultsfile)
    nx, ny = read_soln_size(resultsfile)
    # plot_solution(res, nx, ny, streamlines=False) # don't plot streamlines
    plot_solution(res, nx, ny)

    # plot the discretization error (if applicable)
    if "dep" in res.columns:
        plot_de(res, nx, ny)
