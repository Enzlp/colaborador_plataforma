import os
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, save_npz
from math import log1p
from api.models import MvIaCoauthorshipLatam


def build_author_knn_data(
    output_dir,
    use_log_weight=True
):
    """
    Construye matriz sparse autor × autor + pares únicos
    para ItemKNN (implicit)

    Parámetros
    ----------
    output_dir : str
        Carpeta donde se guardan los archivos
    use_log_weight : bool
        Si True: w = log(1 + shared_works)
        Si False: w = shared_works
    """

    os.makedirs(output_dir, exist_ok=True)

    print("==============================================")
    print("📌 Construyendo datos para ItemKNN (implicit)")
    print("==============================================\n")

    # --------------------------------------------------------
    # 1) Cargar datos desde la BD
    # --------------------------------------------------------
    print("🔹 Cargando datos desde la BD...")

    qs = MvIaCoauthorshipLatam.objects.all().values(
        "coauthor_1",
        "coauthor_2",
        "shared_works"
    )

    all_authors = set()
    rows, cols, data = [], [], []
    pairs_for_df = []

    for row in qs:
        a = str(row["coauthor_1"])
        b = str(row["coauthor_2"])

        if a == b:
            continue

        cnt = row["shared_works"] or 0
        w = log1p(cnt) if use_log_weight else float(cnt)

        all_authors.add(a)
        all_authors.add(b)

        pairs_for_df.append({
            "pair_min": min(a, b),
            "pair_max": max(a, b),
            "count": float(cnt)
        })

    # --------------------------------------------------------
    # 2) Crear mapping CONSISTENTE
    # --------------------------------------------------------
    author_list = sorted(all_authors)
    author_to_idx = {a: i for i, a in enumerate(author_list)}
    idx_to_author = {i: a for i, a in enumerate(author_list)}

    n = len(author_list)
    print(f"Autores únicos: {n:,}")

    # --------------------------------------------------------
    # 3) Construir matriz sparse (simétrica)
    # --------------------------------------------------------
    print("🔹 Construyendo matriz sparse...")

    for p in pairs_for_df:
        i = author_to_idx[p["pair_min"]]
        j = author_to_idx[p["pair_max"]]

        w = log1p(p["count"]) if use_log_weight else p["count"]

        rows.append(i)
        cols.append(j)
        data.append(w)

        rows.append(j)
        cols.append(i)
        data.append(w)

    R = csr_matrix(
        (np.array(data, dtype=np.float32),
         (np.array(rows, dtype=np.int32),
          np.array(cols, dtype=np.int32))),
        shape=(n, n)
    )

    # Tipos críticos para Colab / implicit
    R.indices = R.indices.astype(np.int32)
    R.indptr = R.indptr.astype(np.int32)

    print(f"Matriz: shape={R.shape}, nnz={R.nnz:,}")

    # --------------------------------------------------------
    # 4) DataFrame de pares únicos (GROUND TRUTH)
    # --------------------------------------------------------
    df_pairs_unique = (
        pd.DataFrame(pairs_for_df)
        .drop_duplicates(subset=["pair_min", "pair_max"])
        .reset_index(drop=True)
    )

    print(f"Pares únicos: {len(df_pairs_unique):,}")

    # --------------------------------------------------------
    # 5) Guardar archivos
    # --------------------------------------------------------
    print("🔹 Guardando archivos...")

    save_npz(
        os.path.join(output_dir, "author_author_matrix.npz"),
        R
    )

    np.save(
        os.path.join(output_dir, "author_to_idx.npy"),
        author_to_idx,
        allow_pickle=True
    )

    np.save(
        os.path.join(output_dir, "idx_to_author.npy"),
        idx_to_author,
        allow_pickle=True
    )

    df_pairs_unique.to_pickle(
        os.path.join(output_dir, "df_pairs_unique.pkl")
    )

    print("\n==============================================")
    print("✅ Archivos generados correctamente:")
    print("  - author_author_matrix.npz")
    print("  - author_to_idx.npy")
    print("  - idx_to_author.npy")
    print("  - df_pairs_unique.pkl")
    print("==============================================\n")