import pandas as pd
import os
import warnings
import seaborn as sns
import matplotlib
import math
import numpy as np


sns.set_style("whitegrid")
matplotlib.use('Agg')

# -------------------------------Rutas generales

# Eliminar UserWarnings de openpyxl
warnings.simplefilter('ignore', category=UserWarning)

datos_crudos = r'C:\MeteoRBD.v1.0.0\datos_rbd'

# Encuentra el archivo .xlsx en la datos_crudos que contiene 'Cuenca' y 'Estación' como columnas
ruta_archivo = next((os.path.join(datos_crudos, archivo) for archivo in os.listdir(datos_crudos) if archivo.endswith(".xlsx")), None)

if ruta_archivo:
    archivo_excel = pd.read_excel(ruta_archivo)
    if all(col in archivo_excel.columns for col in ['Cuenca', 'Estación']):
        # Obtiene el número de estación a partir del archivo Excel
        cuenca = str(archivo_excel['Cuenca'].iloc[0])
        estacion = str(archivo_excel['Estación'].iloc[0])

        # Asegúrate de que la cuenca tenga tres dígitos
        cuenca = cuenca.zfill(3)

        # Asegúrate de que la estación tenga tres dígitos
        estacion = estacion.zfill(3)

        # Concatenar cuenca y estación
        num_estacion = cuenca + estacion

# Establece la ruta para los archivos de temperatura según el número de estación obtenido del archivo Excel
ruta_analisis_T = f"C:\\MeteoRBD.v1.0.0\\revisión\\{num_estacion}-ema\\Temperatura"

# Crea las carpetas si no existen
for carpeta in ["", "Pruebas_estadisticas"]:
    ruta_pruebas_b = os.path.join(ruta_analisis_T, carpeta)
    os.makedirs(ruta_pruebas_b, exist_ok=True)
    
# Encuentra el archivo T.h.bd2.csv de temperatura en la ruta de la estación
ruta_T_h_bd2 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.h.bd2' in archivo), None)

# Encuentra el archivo T.d.bd2.csv de temperatura en la ruta de la estación
ruta_T_d_bd2 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.d.bd2' in archivo), None)
    
unidad = '°C'
#-----------------------------------------------------------------------------------------------------------------

# Variables para T.h que están en df_T_h_bd2
Variables_T_h = ['Temp.degC.avg.1h.s1', 'Td.degC.avg.1h.c1']
# Variables para T.d que están en df_T_d_bd2
Variables_T_d = ['Temp.degC.max.dm.s1', 'Temp.degC.min.dm.s1']

if ruta_T_h_bd2 or ruta_T_d_bd2:
    # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if ruta_T_h_bd2:
            df_T_h_bd2 = pd.read_csv(ruta_T_h_bd2, na_values=['NA'])
            df_T_h_bd2['TIMESTAMP'] = pd.to_datetime(df_T_h_bd2['TIMESTAMP'])  # Convertir a tipo de dato de fecha y hora
            df_T_h_bd2 = df_T_h_bd2.dropna()

        if ruta_T_d_bd2:
            df_T_d_bd2 = pd.read_csv(ruta_T_d_bd2, na_values=['NA'])
            df_T_d_bd2['TIMESTAMP'] = pd.to_datetime(df_T_d_bd2['TIMESTAMP'])
            df_T_d_bd2 = df_T_d_bd2.dropna()  # Eliminar filas con valor faltante

# Ruta donde se guardarán los archivos CSV
ruta_guardado = os.path.join(ruta_analisis_T, "Pruebas_estadisticas")

# Definir los nombres de los meses en español
nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

# Mostrar la tabla de límites por mes para cada variable en Variables_T_h
print("Tabla de estadísticas por mes para cada variable en Variables_T_h:")
for variable in Variables_T_h:
    print(f"\nVariable: {variable}")
    print("{:<10} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15}".format("Mes", "Media", "Desv. Estándar", "BI", "BS", "Mínimo", "Máximo", "MínZ", "MáxZ", "Lím Inf", "Lím Sup"))
    for mes in range(1, 13):
        # Filtrar datos por mes
        df_mes = df_T_h_bd2[df_T_h_bd2['TIMESTAMP'].dt.month == mes]
        
        # Calcular estadísticas si hay datos
        if not df_mes.empty:
            Media_aritmética_T_h = df_mes[variable].mean()
            Desviación_estándar_T_h = df_mes[variable].std()
            P25_T_h = df_mes[variable].quantile(0.25)
            P50_T_h = df_mes[variable].quantile(0.50)  # Median
            P75_T_h = df_mes[variable].quantile(0.75)
            IQR_T_h = P75_T_h - P25_T_h
            BI_T_h = P25_T_h - 1.5 * IQR_T_h
            BS_T_h = P75_T_h + 1.5 * IQR_T_h
            Min_T_h = df_mes[variable].min()
            Max_T_h = df_mes[variable].max()
            MinZ_T_h = (Min_T_h - Media_aritmética_T_h) / Desviación_estándar_T_h
            MaxZ_T_h = (Max_T_h - Media_aritmética_T_h) / Desviación_estándar_T_h
            lim_inf_T_h = np.fix(MinZ_T_h) * Desviación_estándar_T_h + Media_aritmética_T_h
            lim_sup_T_h = np.fix(MaxZ_T_h) * Desviación_estándar_T_h + Media_aritmética_T_h

            # Mostrar los resultados por mes
            print("{:<10} {:<15.2f} {:<15.2f} {:<15.2f} {:<15.2f} {:<15.2f} {:<15.2f} {:<15.2f} {:<15.2f} {:<15.2f} {:<15.2f}".format(
                nombres_meses[mes - 1], Media_aritmética_T_h, Desviación_estándar_T_h, BI_T_h, BS_T_h, Min_T_h, Max_T_h, MinZ_T_h, MaxZ_T_h, lim_inf_T_h, lim_sup_T_h))
        

# Mostrar la tabla de límites por mes para cada variable en Variables_T_d
print("\nTabla de estadísticas por mes para cada variable en Variables_T_d:")
for variable in Variables_T_d:
    print(f"\nVariable: {variable}")
    print("{:<10} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15}".format("Mes", "Media", "Desv. Estándar", "BI", "BS", "Mínimo", "Máximo", "MínZ", "MáxZ", "Lím Inf", "Lím Sup"))
    for mes in range(1, 13):
        # Filtrar datos por mes
        df_mes = df_T_d_bd2[df_T_d_bd2['TIMESTAMP'].dt.month == mes]
        
        # Calcular estadísticas si hay datos
        if not df_mes.empty:
            Media_aritmética_T_d = df_mes[variable].mean()
            Desviación_estándar_T_d = df_mes[variable].std()
            P25_T_d = df_mes[variable].quantile(0.25)
            P50_T_d = df_mes[variable].quantile(0.50)  # Median
            P75_T_d = df_mes[variable].quantile(0.75)
            IQR_T_d = P75_T_d - P25_T_d
            BI_T_d = P25_T_d - 1.5 * IQR_T_d
            BS_T_d = P75_T_d + 1.5 * IQR_T_d
            Min_T_d = df_mes[variable].min()
            Max_T_d = df_mes[variable].max()
            MinZ_T_d = (Min_T_d - Media_aritmética_T_d) / Desviación_estándar_T_d
            MaxZ_T_d = (Max_T_d - Media_aritmética_T_d) / Desviación_estándar_T_d
            lim_inf_T_d = np.fix(MinZ_T_d) * Desviación_estándar_T_d + Media_aritmética_T_d
            lim_sup_T_d = np.fix(MaxZ_T_d) * Desviación_estándar_T_d + Media_aritmética_T_d

            # Mostrar los resultados por mes
            print("{:<10} {:<15.2f} {:<15.2f} {:<15.2f} {:<15.2f} {:<15.2f} {:<15.2f} {:<15.2f} {:<15.2f} {:<15.2f} {:<15.2f}".format(
                nombres_meses[mes - 1], Media_aritmética_T_d, Desviación_estándar_T_d, BI_T_d, BS_T_d, Min_T_d, Max_T_d, MinZ_T_d, MaxZ_T_d, lim_inf_T_d, lim_sup_T_d))