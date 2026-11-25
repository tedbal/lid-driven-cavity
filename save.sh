#!/bin/bash

# simple bash script to move the current results into a user-passed directory
mkdir $1
cp ./data/history.dat ./data/cavity.dat ./data/restart.out ./data/Debug.dat ./data/parameters.dat $1
rm ./data/history.dat ./data/cavity.dat ./data/restart.out ./data/Debug.dat ./data/parameters.dat
