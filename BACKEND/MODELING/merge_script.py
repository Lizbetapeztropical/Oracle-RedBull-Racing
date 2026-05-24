# merge_script.py
# Script que replica el merged realizado en MongoDB

import pandas as pd
import os

print("="*60)
print(" SCRIPT DE MERGED")
print("="*60)

# Rutas
base = os.path.dirname(os.path.abspath(__file__))
data_prep = os.path.join(base, "../DATA PREP/")

# Cargar datos
print("\n📂 Cargando datasets...")
lt = pd.read_csv(os.path.join(data_prep, "lt_mod.csv"))
ps = pd.read_csv(os.path.join(data_prep, "ps_mod.csv"))
print(f"   lt_mod.csv: {lt.shape}")
print(f"   ps_mod.csv: {ps.shape}")

# Merge
print("\n🔗 Fusionando...")
merged = pd.merge(lt, ps, on=['RACEID'], how='outer')
print(f"   Resultado: {merged.shape[0]} filas, {merged.shape[1]} columnas")

# Guardar
merged.to_csv(os.path.join(base, "merged_dataset.csv"), index=False)
print("\n✅ Merge completado! Archivo: merged_dataset.csv")

