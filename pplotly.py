import plotly.offline # import download_plotlyjs, init_notebook_mode, iplot, plot
import plotly.graph_objs # import Scatter, Layout, Figure
import pandas as pd
import numpy as np
import sys

def label_sel_generator(df):
    for label in np.unique(df['label']):
        sel = df['label'] == label
        yield label, sel
def X_Y_label_generator(df):
    for label, sel in label_sel_generator(df):
        X = df['x'][sel]
        Y = df['y'][sel]
        yield X, Y, label

csv = sys.argv[1]
html = sys.argv[2]

df = pd.read_csv(csv)
data = [plotly.graph_objs.Scatter(x=X, y=Y, name=label, visible="legendonly") for X, Y, label in X_Y_label_generator(df)]
layout = plotly.graph_objs.Layout(showlegend=True)
figure = plotly.graph_objs.Figure(data=data, layout=layout)
plotly.offline.plot(figure, filename=html, auto_open=False)
