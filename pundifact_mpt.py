# -*- coding: utf-8 -*-
"""
Created on Thu May 12 19:56:03 2016

@author: dan
"""
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import numpy as np

scores = {'Pants on Fire!': 0.0, 'False': 1.0, 'Mostly False': 2.0, 'Half-True': 3.0, 'Mostly True': 4.0, 'True': 5.0}

if __name__ == '__main__':
    raw = pd.read_json('pundifact_data.json')
    
    # get subject series
    s = raw['subjects'].apply(pd.Series, 1).stack()
    s.index = s.index.droplevel(-1)
    s.name = 'subject'
    
    # merge with raw data, convert scores
    data = raw.join(s).reset_index(drop=True)
    del data['subjects']
    data.replace({'score': scores}, inplace=True)
    
    # get mean
    g1 = data.groupby('station')
    stations = sorted(g1.groups.keys())
    n = len(stations)
    p = g1.mean().as_matrix().squeeze()
    s = g1.std().as_matrix().squeeze()
    
    # get covariance matrix
    g2 = data.groupby(['station', 'subject'])
    S = g2.mean().unstack(level=0).cov().as_matrix()
    Sinv = np.linalg.inv(S)
    
    # get mvp
    #A = np.vstack((np.hstack((2.0*S, np.ones((n, 1)))), np.hstack((np.ones((1, n)), np.zeros((1, 1))))))
    #b = np.vstack((np.zeros((n, 1)), np.ones((1, 1,))))
    #m = np.dot(np.linalg.inv(A), b).flatten()[0:n]
    m = np.dot(Sinv, np.ones(n))/np.dot(np.ones(n), np.dot(Sinv, np.ones(n)))    
    rm = np.dot(p, m)
    vm = np.sqrt(np.dot(m, np.dot(S, m)).squeeze())
    
    # get tangency
    rf = 2.5
    t = np.dot(Sinv, (p - rf*np.ones(n)))/np.dot(np.ones(n), np.dot(Sinv, (p - rf*np.ones(n))))
    rt = np.dot(p, t)
    vt = np.sqrt(np.dot(t, np.dot(S, t)).squeeze())
    
    # optimal portfolios
    N = 100
    a = np.linspace(0, 3.0, N)
    xo = np.zeros((N, n))
    ro = np.zeros(N)
    vo = np.zeros(N)
    for i in range(N):
        x = (1 - a[i])*m + a[i]*t
        xo[i, :] = x
        ro[i] = np.dot(p, x)
        vo[i] = np.sqrt(np.dot(x, np.dot(S, x)).squeeze())
    
    # plot
    plt.figure(0)
    plt.axis([0.0, 2.5, 0.0, 5.0])
    for i in range(len(stations)):
        plt.plot(s[i], p[i], 'o', label=stations[i])
    plt.plot(vm, rm, 'o', label='mvp')
    plt.plot([0.0, vt], [rf, rt], 'o-', label='tan')
    plt.plot(vo, ro, '-', label='opt')

    plt.legend()
    plt.xlabel('variability')
    plt.ylabel('score')
    plt.title('pundifact mpt')