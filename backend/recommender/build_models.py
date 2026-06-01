import sys 
import os

# Establece raiz del proyecto como path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

import django
django.setup()

# Generamos los archivos para cada modelo de recomendacion
from recommender.content_based.vector_builder import map_concepts, train_model

# directorio de archivos
#files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")

# Archivo de mapeo de conceptos
#map_concepts(files_dir)

#train_model(files_dir)


#from recommender.matrix_factorization.training_test import run_full_recommendation_system, evaluate_final_full
#import numpy as np

#from recommender.ItemKNN.load_data import build_author_knn_data
#files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ItemKNN/files")
#print(files_dir)
#build_author_knn_data(files_dir)

#from recommender.turbo_cf.data_loader import prepare_turbocf_loo
#files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "turbo_cf/files")
#prepare_turbocf_loo(files_dir)

# Hiperparametros 
#factors_list = [128, 200, 256]
#reg_list = [0.02, 0.05, 0.1, 0.2]
#iterations = 10  # mejor que 10

# Ejecutar grid search CORRECTO
#out = run_full_recommendation_system(
#    factors_list=factors_list,
#    reg_list=reg_list,
#    iterations=iterations,
#    K=20,
#    sample_users_eval=20000,
#    random_state=42,
#    save_dir=files_dir,
#    num_threads=0,
#    use_gpu=False
#)
# U_final = np.load(f"{files_dir}/cf_U_als.npy").astype(np.float32)
# evaluate_final_full(U_final, files_dir, 20, 42)

#print(out)
#from recommender.graph_based.train_lightgcn import (
#    leave_one_out_split,
#    train_and_tune_lightgcn,
#    save_model,
#    build_interaction_dict,
#    load_graph_data_efficient,
#    load_graph_data_from_files
#)


#CONFIG = {
#    'embedding_dims': [32, 64],       
#    'Ks': [2, 3],                      
#    'reg_lambdas': [1e-6, 1e-5],   
#   'epochs': 30,             # Subido un poco para dar tiempo a converger
#    'batch_size': 2048,       
#    'batches_per_epoch': 200, # Subido para procesar más datos por época
#    'lr': 1e-3,
#    'eval_K': 20,
#    'eval_every': 5,          # Evaluamos con menos frecuencia porque la evaluación global es costosa
#    'early_stopping_patience': 3,
#    'seed': 42,
#    'sample_size': 10000       # Reducido para que la evaluación no tarde horas
#}

# 1. Cargar datos (RAM Efficient)
#df_pairs_unique, author_to_idx, author_list = load_graph_data_efficient(files_dir=files_dir)
#df_pairs_unique, author_to_idx, author_list = load_graph_data_from_files(files_dir=files_dir)


# 2. Split train/val/test (Pandas Efficient)
#df_train, df_val, df_test = leave_one_out_split(
#    df_pairs_unique, author_to_idx, seed=CONFIG['seed']
#)

# 3. Entrenamiento + tuning
# Importante: train_and_tune_lightgcn ya no recibe candidate_dict en sus argumentos
#results = train_and_tune_lightgcn(
 #   df_train=df_train,
 #   df_val=df_val,
 #   df_test=df_test,
#    author_to_idx=author_to_idx,
#    **CONFIG
#)

# 4. Guardar resultados
# Construimos el diccionario de entrenamiento para saber qué items ignorar en recomendación futura
#train_dict = build_interaction_dict(df_train, author_to_idx)
#save_model(results, author_to_idx, train_dict, output_dir=files_dir)


#from recommender.graph_based_2.train_lightgcn import(
#  export_to_recbole_inter,
#  run_grid_search
#)

#export_to_recbole_inter(files_dir)
#run_grid_search()


#TESTS:
import pandas as pd
from api.models import MvIaCoauthorshipLatam  # reemplaza 'your_app' por tu app

# 1️⃣ Cargar todos los pares desde la base de datos
qs = MvIaCoauthorshipLatam.objects.all().values('coauthor_1', 'coauthor_2', 'shared_works')
df = pd.DataFrame.from_records(qs)

# 2️⃣ Contar todos los autores únicos
all_authors = pd.unique(df[['coauthor_1', 'coauthor_2']].values.ravel())
num_authors = len(all_authors)

# 3️⃣ Contar pares únicos (cada fila es un par único)
num_unique_pairs = len(df)

print(f"Total de autores (incluyendo 1 colaboración): {num_authors}")
print(f"Total de pares únicos (incluyendo 1 colaboración): {num_unique_pairs}")

