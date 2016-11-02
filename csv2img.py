#!/usr/bin/env python
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys

csv = sys.argv[1]
img = sys.argv[2]

df = pd.read_csv(csv)

def label_sel_generator(df):
    for label in np.unique(df['label']):
        sel = df['label'] == label
        yield label, sel

def X_Y_label_generator(df):
    for label, sel in label_sel_generator(df):
        X = df['x'][sel]
        Y = df['y'][sel]
        text = None
        if 'text' in df:
            text = df['text'][sel]
        yield X, Y, text, label

plt.figure()
for (X,Y,text,label) in X_Y_label_generator(df):
	try:
		X = X.values
		X = np.array(X, dtype='datetime64')
	except Exception as e:
		pass
	plt.plot(X,Y,label=label)
plt.legend()
plt.savefig(img)
