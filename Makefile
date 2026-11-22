# ==========================================
# makefile for the lid-driven cavity flow solver
# ==========================================

# compiler, flags, target
CXX = g++
CXXFLAGS = -std=c++11 -O2 -Wall -Wextra
TARGET = ./bin/cavity
SRC = ./src/DrivenCavity.template-to-students.UPDATED.cpp

# default target
all: $(TARGET)

# compile and link
$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) -o $(TARGET)

# run the solver
run: $(TARGET)
	./bin/$(TARGET)

# remove binary and data files
clean:
	rm -f $(TARGET) ./data/history.dat ./data/cavity.dat ./data/restart.out ./data/Debug.dat

# list all targets
.PHONY: all run clean
