# ==========================================
# makefile for the lid-driven cavity flow solver
# ==========================================

# compiler, flags, target
CXX = g++
CXXFLAGS = -std=c++11 -O2 -Wall -Wextra
DEBUGFLAGS = -std=c++11 -O0 -g -Wall -Wextra
TARGET = ./bin/cavity
SRC = ./src/DrivenCavity.template-to-students.UPDATED.cpp
PLTTARGET = ./src/plot.py

# default target
all: $(TARGET)

# compile and link
$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) -o $(TARGET)

# debugging compilation
debug:
	$(CXX) $(DEBUGFLAGS) $(SRC) -o $(TARGET)

# run the solver using gdb
gdb: debug
	gdb $(TARGET)

# run the solver
run: $(TARGET)
	$(TARGET)

# plot the plotting utility
plt: run
	python $(PLTTARGET)

# remove binary and data files
clean:
	rm -f $(TARGET) ./data/history.dat ./data/cavity.dat ./data/restart.out ./data/Debug.dat ./data/parameters.dat

# list all targets
.PHONY: all run clean debug gdb
