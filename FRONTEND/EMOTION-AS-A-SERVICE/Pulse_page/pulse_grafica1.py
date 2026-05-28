import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud, STOPWORDS
from sklearn.feature_extraction.text import CountVectorizer
import pickle
import os
import pandas as pd

# Definimos el identificador del dataset de Kaggle (viene en tu URL)
dataset_slug = "kaushiksuresh147/formula-1-trending-tweets"
archivo_csv = "F1_tweets.csv"

# Si el archivo no se ha descargado a tu proyecto, la API lo descarga en un segundo
if not os.path.exists(archivo_csv):
    print("🏎️ Conectando con Kaggle para traer los tweets...")
    import kaggle
    kaggle.api.dataset_download_files(dataset_slug, path='.', unzip=True)

# Cargamos el dataframe de manera normal
f1 = pd.read_csv(archivo_csv)
print(f"✅ ¡Cargado con éxito desde la API! Total de registros: {len(f1)}")