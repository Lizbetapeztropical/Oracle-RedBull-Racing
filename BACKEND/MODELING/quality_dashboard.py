# quality_dashboard.py
# Dashboard de Calidad - Oracle Red Bull Racing
# Ejecutar: python quality_dashboard.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
import os
import json
import warnings
warnings.filterwarnings('ignore')

# ============================================
# COLORES DEL PROYECTO
# ============================================

COLORS = {
    'dark_blue': '#0A0F1F',
    'red': '#E10600',
    'white': '#FFFFFF',
    'silver': '#C0C0C0',
    'gold': '#FFD700',
    'dark_bg': '#151520',
    'card_bg': '#1A1A2E',
    'success': '#00C853',
    'warning': '#FFC107'
}

# Configurar matplotlib
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.facecolor'] = COLORS['dark_blue']
plt.rcParams['axes.facecolor'] = COLORS['dark_bg']
plt.rcParams['text.color'] = COLORS['white']
plt.rcParams['axes.labelcolor'] = COLORS['white']
plt.rcParams['axes.titlecolor'] = COLORS['gold']
plt.rcParams['xtick.color'] = COLORS['silver']
plt.rcParams['ytick.color'] = COLORS['silver']

# ============================================
# FUNCIONES PRINCIPALES
# ============================================

def print_header():
    """Imprime cabecera del dashboard"""
    print("\n" + "="*80)
    print(" DASHBOARD DE CALIDAD - ORACLE RED BULL RACING")
    print(" Fecha: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*80)

def check_files():
    """Verifica existencia de archivos clave"""
    print("\n" + "-"*80)
    print(" VERIFICACION DE ARCHIVOS")
    print("-"*80)
    
    files_to_check = [
        ("lt.py", "Script tiempos por vuelta", "../DATA PREP/lt.py"),
        ("ps.py", "Script pit stops", "../DATA PREP/ps.py"),
        ("merge_script.py", "Script de merged", "merge_script.py"),
        ("inyeccion-01.py", "Script inyeccion MongoDB", "inyeccion-01.py"),
        ("01.ipynb", "Feature engineering", "01.ipynb"),
        ("02.ipynb", "Modelos XGBoost/SVM", "02.ipynb"),
        ("03.ipynb", "Modelos avanzados", "03.ipynb")
    ]
    
    for name, description, path in files_to_check:
        exists = os.path.exists(path)
        status = "OK" if exists else "FALTA"
        print(f"  [{status}] {description}")
    
    print("\n  Nota: app-checkpoint.py se encuentra en EMOTION-AS-A-SERVICE/")

def check_datasets():
    """Verifica datasets generados"""
    print("\n" + "-"*80)
    print(" VERIFICACION DE DATASETS")
    print("-"*80)
    
    datasets = {
        "lt_mod.csv": "../DATA PREP/lt_mod.csv",
        "ps_mod.csv": "../DATA PREP/ps_mod.csv",
        "merged_dataset.csv": "merged_dataset.csv",
        "processed_dataset.csv": "processed_dataset.csv"
    }
    
    for name, path in datasets.items():
        exists = os.path.exists(path)
        if exists:
            df = pd.read_csv(path)
            rows, cols = df.shape
            print(f"  [OK] {name}: {rows} filas, {cols} columnas")
        else:
            print(f"  [FALTA] {name}")

def model_performance():
    """Tabla de rendimiento de modelos"""
    print("\n" + "-"*80)
    print(" RENDIMIENTO DE MODELOS")
    print("-"*80)
    
    models = [
        {"Modelo": "XGBoost", "R2": 0.7128, "MAE": 0.5941, "RMSE": 0.7432, "Estado": "Entrenado"},
        {"Modelo": "SVM", "R2": 0.4969, "MAE": 0.8229, "RMSE": 0.9836, "Estado": "Entrenado"},
        {"Modelo": "PyTorch NN", "R2": 0.3601, "MAE": 0.9298, "RMSE": 1.1092, "Estado": "Entrenado"},
        {"Modelo": "Random Forest", "R2": None, "MAE": None, "RMSE": None, "Estado": "Pendiente"},
        {"Modelo": "Extra Trees", "R2": None, "MAE": None, "RMSE": None, "Estado": "Pendiente"},
        {"Modelo": "Gradient Boosting", "R2": None, "MAE": None, "RMSE": None, "Estado": "Pendiente"}
    ]
    
    print(f"{'Modelo':<20} {'R2':<12} {'MAE':<12} {'RMSE':<12} {'Estado':<12}")
    print("-"*68)
    
    for m in models:
        r2 = f"{m['R2']:.4f}" if m['R2'] else "-"
        mae = f"{m['MAE']:.4f}" if m['MAE'] else "-"
        rmse = f"{m['RMSE']:.4f}" if m['RMSE'] else "-"
        print(f"{m['Modelo']:<20} {r2:<12} {mae:<12} {rmse:<12} {m['Estado']:<12}")

def task_status():
    """Estado de tareas del equipo"""
    print("\n" + "-"*80)
    print(" ESTADO DE TAREAS POR RESPONSABLE")
    print("-"*80)
    
    tasks = [
        {"Tarea": "Merged en analytics via MongoDB", "Responsable": "Liz", "Estado": "Completado"},
        {"Tarea": "Merged en Jupyter notebooks", "Responsable": "Liz", "Estado": "Completado"},
        {"Tarea": "Script de inyeccion a MongoDB", "Responsable": "Ana", "Estado": "Completado"},
        {"Tarea": "Script de merged", "Responsable": "Andy", "Estado": "Completado"},
        {"Tarea": "app.py master", "Responsable": "Ingrid y Liz", "Estado": "En progreso"},
        {"Tarea": "Diseno de app.py (CSS/HTML)", "Responsable": "Andy", "Estado": "Pendiente"}
    ]
    
    print(f"{'Tarea':<45} {'Responsable':<15} {'Estado':<12}")
    print("-"*72)
    
    for t in tasks:
        estado = t['Estado']
        if estado == "Completado":
            estado_display = "OK - Completado"
        elif estado == "En progreso":
            estado_display = ">> En progreso"
        else:
            estado_display = ".. Pendiente"
        print(f"{t['Tarea']:<45} {t['Responsable']:<15} {estado_display:<12}")

def plot_model_comparison():
    """Grafico comparativo de modelos"""
    models = ['XGBoost', 'SVM', 'PyTorch NN']
    r2_scores = [0.7128, 0.4969, 0.3601]
    mae_scores = [0.5941, 0.8229, 0.9298]
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    bars1 = axes[0].barh(models, r2_scores, color=COLORS['red'])
    axes[0].axvline(x=0.5, color=COLORS['gold'], linestyle='--', linewidth=1.5, label='Umbral 0.5')
    axes[0].set_xlabel('R2 Score', fontsize=11)
    axes[0].set_title('Comparacion de Modelos - R2', fontsize=13, fontweight='bold')
    axes[0].set_xlim(0, 1)
    axes[0].legend(loc='lower right')
    
    for bar, val in zip(bars1, r2_scores):
        axes[0].text(val + 0.02, bar.get_y() + bar.get_height()/2, f'{val:.4f}', va='center', fontsize=10)
    
    bars2 = axes[1].barh(models, mae_scores, color=COLORS['silver'])
    axes[1].set_xlabel('MAE', fontsize=11)
    axes[1].set_title('Comparacion de Modelos - MAE', fontsize=13, fontweight='bold')
    
    for bar, val in zip(bars2, mae_scores):
        axes[1].text(val + 0.02, bar.get_y() + bar.get_height()/2, f'{val:.4f}', va='center', fontsize=10)
    
    plt.suptitle('Oracle Red Bull Racing - Calidad de Modelos', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('quality_model_comparison.png', dpi=150, bbox_inches='tight', facecolor=COLORS['dark_blue'])
    plt.show()
    print("\n[OK] Grafico guardado: quality_model_comparison.png")

def plot_quality_score():
    """Grafico de puntaje de calidad"""
    categories = ['Data', 'Procesamiento', 'Modelos', 'MongoDB', 'App', 'Repo']
    scores = [85, 70, 50, 40, 30, 65]
    
    colors_bar = [COLORS['success'] if s >= 70 else COLORS['warning'] if s >= 50 else COLORS['red'] for s in scores]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(categories, scores, color=colors_bar)
    plt.ylabel('Puntaje de Calidad (%)', fontsize=11)
    plt.title('Calidad por Categoria', fontsize=13, fontweight='bold')
    plt.ylim(0, 100)
    plt.axhline(y=70, color=COLORS['gold'], linestyle='--', linewidth=1, label='Umbral Aceptable (70%)')
    plt.legend(loc='lower right')
    
    for bar, score in zip(bars, scores):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, f'{score}%', ha='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('quality_category_score.png', dpi=150, bbox_inches='tight', facecolor=COLORS['dark_blue'])
    plt.show()
    print("\n[OK] Grafico guardado: quality_category_score.png")

def generate_quality_report():
    """Genera reporte HTML de calidad"""
    
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Quality Dashboard - Oracle Red Bull Racing</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: linear-gradient(135deg, #0A0F1F 0%, #151520 100%);
            font-family: 'Segoe UI', Arial, sans-serif;
            padding: 20px;
            color: #FFFFFF;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        
        .header {{
            background: linear-gradient(90deg, #0A0F1F 0%, #E10600 100%);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            border-bottom: 3px solid #FFD700;
        }}
        .header h1 {{ font-size: 28px; letter-spacing: 2px; }}
        .header h1 span {{ color: #FFD700; }}
        .header p {{ color: #C0C0C0; margin-top: 8px; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 25px; }}
        
        .card {{
            background: #1A1A2E;
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid #E10600;
        }}
        .card-title {{ font-size: 18px; font-weight: bold; color: #FFD700; margin-bottom: 15px; border-bottom: 1px solid rgba(255,215,0,0.3); padding-bottom: 8px; }}
        
        .metric {{ display: inline-block; width: 30%; text-align: center; }}
        .metric-value {{ font-size: 28px; font-weight: bold; color: #FFD700; }}
        .metric-label {{ font-size: 11px; color: #C0C0C0; text-transform: uppercase; }}
        
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: #E10600; padding: 10px; text-align: left; }}
        td {{ padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        tr:hover td {{ background: rgba(225,6,0,0.1); }}
        
        .status-ok {{ color: #00C853; }}
        .status-progress {{ color: #FFC107; }}
        .status-pending {{ color: #E10600; }}
        
        .footer {{ text-align: center; padding: 20px; margin-top: 25px; border-top: 1px solid rgba(192,192,192,0.2); color: #C0C0C0; font-size: 12px; }}
        
        .score-badge {{
            display: inline-block;
            background: #E10600;
            border-radius: 50%;
            width: 80px;
            height: 80px;
            line-height: 80px;
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            margin: 10px auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ORACLE <span>RED BULL RACING</span></h1>
            <p>Dashboard de Calidad del Proyecto | {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <div class="card-title">Resumen General</div>
                <div class="metric"><div class="metric-value">3</div><div class="metric-label">Modelos Listos</div></div>
                <div class="metric"><div class="metric-value">71.3%</div><div class="metric-label">Mejor R2</div></div>
                <div class="metric"><div class="metric-value">3/6</div><div class="metric-label">Tareas Completadas</div></div>
            </div>
            
            <div class="card">
                <div class="card-title">Puntaje de Calidad</div>
                <div style="text-align: center;">
                    <div class="score-badge">58%</div>
                    <p style="margin-top: 10px; color: #FFC107;">Nivel: Aceptable - Mejorable</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">Rendimiento de Modelos</div>
            <table>
                <thead><tr><th>Modelo</th><th>R2</th><th>MAE</th><th>Estado</th></tr></thead>
                <tbody>
                    <tr><td>XGBoost</td><td>0.7128</td><td>0.5941</td><td class="status-ok">Entrenado</td></tr>
                    <tr><td>SVM</td><td>0.4969</td><td>0.8229</td><td class="status-ok">Entrenado</td></tr>
                    <tr><td>PyTorch NN</td><td>0.3601</td><td>0.9298</td><td class="status-ok">Entrenado</td></tr>
                    <tr><td>Random Forest</td><td>-</td><td>-</td><td class="status-pending">Pendiente</td></tr>
                    <tr><td>Extra Trees</td><td>-</td><td>-</td><td class="status-pending">Pendiente</td></tr>
                    <tr><td>Gradient Boosting</td><td>-</td><td>-</td><td class="status-pending">Pendiente</td></tr>
                </tbody>
            </table>
        </div>
        
        <div class="card">
            <div class="card-title">Estado de Tareas</div>
            <table>
                <thead><tr><th>Tarea</th><th>Responsable</th><th>Estado</th></tr></thead>
                <tbody>
                    <tr><td>Merged en analytics via MongoDB</td><td>Liz</td><td class="status-ok">Completado</td></tr>
                    <tr><td>Merged en Jupyter notebooks</td><td>Liz</td><td class="status-ok">Completado</td></tr>
                    <tr><td>Script de inyeccion a MongoDB</td><td>Ana</td><td class="status-ok">Completado</td></tr>
                    <tr><td>Script de merged</td><td>Andy</td><td class="status-ok">Completado</td></tr>
                    <tr><td>app.py master</td><td>Ingrid y Liz</td><td class="status-progress">En progreso</td></tr>
                    <tr><td>Diseno de app.py (CSS/HTML)</td><td>Andy</td><td class="status-pending">Pendiente</td></tr>
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            Oracle Red Bull Racing Project | Dashboard generado automaticamente | Calidad continua
        </div>
    </div>
</body>
</html>'''
    
    with open('quality_dashboard_report.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("\n[OK] Reporte HTML generado: quality_dashboard_report.html")

def calculate_final_score():
    """Calcula puntaje final de calidad"""
    scores = {
        'Integridad de datos': 80,
        'Procesamiento': 70,
        'Modelos': 50,
        'MongoDB': 40,
        'Aplicacion web': 30,
        'Repositorio': 65
    }
    
    total = sum(scores.values()) / len(scores)
    
    print("\n" + "-"*80)
    print(" PUNTAJE DE CALIDAD POR CATEGORIA")
    print("-"*80)
    
    for category, score in scores.items():
        if score >= 70:
            status = "Aceptable"
        elif score >= 50:
            status = "Mejorable"
        else:
            status = "Critico"
        print(f"  {category:<25} : {score}% ({status})")
    
    print("-"*80)
    print(f"  PUNTAJE TOTAL: {total:.1f}%")
    
    if total >= 70:
        print("  CALIFICACION: Aceptable - Continuar con mejoras")
    elif total >= 50:
        print("  CALIFICACION: Mejorable - Priorizar tareas pendientes")
    else:
        print("  CALIFICACION: Critico - Requiere atencion inmediata")
    
    return total

# ============================================
# EJECUCION PRINCIPAL
# ============================================

def main():
    print_header()
    check_files()
    check_datasets()
    model_performance()
    task_status()
    plot_model_comparison()
    plot_quality_score()
    calculate_final_score()
    generate_quality_report()
    
    print("\n" + "="*80)
    print(" DASHBOARD DE CALIDAD COMPLETADO")
    print("="*80)
    print("\nArchivos generados:")
    print("  - quality_model_comparison.png")
    print("  - quality_category_score.png")
    print("  - quality_dashboard_report.html")

if __name__ == "__main__":
    main()
