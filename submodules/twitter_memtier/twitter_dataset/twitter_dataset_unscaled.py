import sys
import numpy as np
import matplotlib.pyplot as plt

input_filename = sys.argv[1]

def load(file_name):
    def func():
        for line in open(file_name):
            x,y = line.split(' ')
            x = float(x)
            y = int(y)
            yield x,y
    X = [x for x,y in func()]
    Y = [y for x,y in func()]
    return X, Y

X, Y = np.array(load(input_filename))
plt.figure()
# Theoretical perf as a function of memory in MB
plt.plot(np.cumsum(Y[:-1]) / 2**20, np.cumsum(-np.diff(X)))

plt.show()

# plt.figure()
# plt.plot(X, marker=".", linestyle='None', markersize=1)
# X = - np.diff(X)
# plt.figure()
# plt.plot(X, marker=".", linestyle='None', markersize=1)
# plt.figure()
# plt.plot(Y, marker=".", linestyle='None', markersize=1)
# plt.show()

