import sys
import numpy as np
import matplotlib.pyplot as plt

p = .8
N = 100
k = int((1-p) * N)

def H(k,s):
    return np.sum(np.array([1./np.power(n, s) for n in range(1,k+1)]))

def cdf(s,k,N):
    return H(k,s)/H(N,s);

def lookup(k,N,s0,s1):
    cdf0 = cdf(s0,k,N)
    cdf1 = cdf(s1,k,N)
    #print("cdf in %f %f" % (cdf0, cdf1))
    assert(cdf0 <= p), "%f > %f" % (cdf0, p)
    assert(cdf1 >= p), "%f < %f" % (cdf1, p)
    s  = s0/np.float64(2.) + s1/np.float64(2.)
    cdfs = cdf(s,k,N)
    if (cdfs >= p):
        return s0, s, cdfs
    else:
        return s, s1, cdfs

def solve(k,N):
    #print(N)
    s0 = np.float64(0.000000000001)
    s1 = np.float64(10.0)
    delta = np.float64(1)
    for i in range(15):
        delta /= np.float64(10.0)
    while(np.abs(s0 - s1) > delta):
        #print(s0,s1)
        s0, s1, cdfs = lookup(k,N,s0,s1)
    ret = [s0, s0/np.float64(2.) + s1/np.float64(2.), s1, cdfs]
    #print(ret)
    return ret

X = np.arange(10,100)
Y = np.array([solve(int((1-p)*x),x) for x in X])


plt.figure()
plt.plot(X,Y, marker="x")
plt.show()

# Theoretical perf as a function of memory in MB
# plt.plot(np.cumsum(Y[:-1]) / 2**20, np.cumsum(-np.diff(X)))

# plt.show()

# plt.figure()
# plt.plot(X, marker=".", linestyle='None', markersize=1)
# X = - np.diff(X)
# plt.figure()
# plt.plot(X, marker=".", linestyle='None', markersize=1)
# plt.figure()
# plt.plot(Y, marker=".", linestyle='None', markersize=1)
# plt.show()

