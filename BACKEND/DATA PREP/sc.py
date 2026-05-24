
"""

SAFETY CAR CLEANING

"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sc = pd.read_csv('/content/sc.csv')

rcs = pd.read_csv('/content/rcs.csv')

rcs.shape

sc = sc.rename(columns={'RACE': 'NAME'})
sc = pd.merge(sc, rcs[['RACEID', 'YEAR', 'NAME']], on=['YEAR', 'NAME'], how='left')

sc.to_csv('sc.csv')