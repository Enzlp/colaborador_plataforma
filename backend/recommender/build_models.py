import sys 
import os
import numpy as np
import pandas as pd
from api.models import MvIaCoauthorshipLatam

# Ruta del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

import django
django.setup()

# Carpeta para guardar archivos
files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
os.makedirs(files_dir, exist_ok=True)

# Archivos para Content Based
from recommender.content_based.vector_builder import map_concepts, train_model
print("Generando archivos para el modelo Content-Based...")
map_concepts(files_dir)
train_model(files_dir)

# Archivos Itemknn
from recommender.ItemKNN.load_data import build_author_knn_data
print("Generando archivos para el modelo ItemKNN...")
build_author_knn_data(files_dir)

## Tests Finales para estadisticas (Opcional)
#print("\nCorriendo tests...")
#qs = MvIaCoauthorshipLatam.objects.all().values('coauthor_1', 'coauthor_2', 'shared_works')
#df = pd.DataFrame.from_records(qs)

#all_authors = pd.unique(df[['coauthor_1', 'coauthor_2']].values.ravel())
#num_authors = len(all_authors)
#num_unique_pairs = len(df)

#print(f"Total de autores únicos en la BD: {num_authors}")
#print(f"Total de pares únicos de coautoría: {num_unique_pairs}")