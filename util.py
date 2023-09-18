import numpy as np
from scipy.stats import multivariate_normal as N
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
def kMeans(D,k,eps=0.01,mu=None,max_iter=20):
 d=D.shape[1]
 if mu is None:
  mu=np.random.rand(k,d)*(np.max(D,axis=0)-np.min(D,axis=0))+np.min(D,axis=0)
 if type(mu)==list:
  mu=np.array(mu)
 s=False
 g=0
 while not s:
  C=[np.argmin([np.linalg.norm(mu[j]-x)for j in range(k)if not any(np.isnan(mu[j]))])for x in D]
  n=np.zeros(mu.shape)
  s=True
  for i in range(k):
   J=[D[j]for j in range(len(D))if C[j]==i]
   if len(J)>0:
    n[i]=np.mean(J,axis=0)
   else:
    n[i]=np.random.rand(1,d)*(np.max(D,axis=0)-np.min(D,axis=0))+np.min(D,axis=0)
   if np.linalg.norm(mu[i]-n[i])>eps:
    s=False
  mu=n
  g+=1
  if g>=max_iter:
   s=True
 return C,mu
def plotClusters(D,C,dimX,dimY,dimZ=None,ax=None):
 h=type(D)==pd.DataFrame
 W=D.columns[dimX]if h else dimX
 X=D.columns[dimY]if h else dimY
 b=D.columns[dimZ]if h and not dimZ is None else dimZ
 if type(D)==pd.DataFrame:
  D=D.values
 x=np.unique(C)
 K=not dimZ is None
 if ax is None:
  if K:
   I=plt.figure()
   ax=I.add_subplot(111,projection='3d')
  else:
   I,ax=plt.subplots()
 for ci in x:
  f=np.where(C==ci)[0]
  if K:
   ax.scatter(D[f,dimX],D[f,dimY],D[f,dimZ])
  else:
   ax.scatter(D[f,dimX],D[f,dimY])
 ax.set_xlabel(W)
 ax.set_ylabel(X)
 if K:
  ax.set_zlabel(b)
