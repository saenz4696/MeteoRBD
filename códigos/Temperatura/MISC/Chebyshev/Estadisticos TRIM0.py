import pandas as pd
import os
import warnings
import seaborn as sns
import matplotlib
from distfit import distfit
import scipy.stats as stats
import numpy as np


sns.set_style("whitegrid")
matplotlib.use('Agg')

# -------------------------------Rutas generales

# Eliminar UserWarnings de openpyxl
warnings.simplefilter('ignore', category=UserWarning)

datos_crudos = r'C:\MeteoRBD.v1.0.0\raw_data_rbd'

# Encuentra el archivo .xlsx en la datos_crudos que contiene 'Cuenca' y 'Estación' como columnas
ruta_archivo = next((os.path.join(datos_crudos, archivo) for archivo in os.listdir(datos_crudos) if archivo.endswith(".xlsx")), None)

if ruta_archivo:
    archivo_excel = pd.read_excel(ruta_archivo)
    if all(col in archivo_excel.columns for col in ['Cuenca', 'Estación']):
        # Obtiene el número de estación a partir del archivo Excel
        cuenca = str(archivo_excel['Cuenca'].iloc[0])
        estacion = str(archivo_excel['Estación'].iloc[0])
        if len(estacion) == 2:
            estacion = '0' + estacion  # Add leading zero if 'Estación' has only two digits
        num_estacion = cuenca + estacion
        num_estacion = int(num_estacion)

# Establece la ruta para los archivos de temperatura según el número de estación obtenido del archivo Excel
ruta_analisis_T = f"C:\MeteoRBD.v1.0.0\Data_Lake\{num_estacion}-ema\\base_datos\\Temperatura\\análisis_datos"

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

# Variables para T.h which are in df_T_h_bd2
Variables_T_h = ['Temp.degC.avg.1h.s1', 'Td.degC.avg.1h.c1']
# Variables para T.d which are in df_T_d_bd2
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
            df_T_d_bd2 = df_T_d_bd2.dropna()  # Drop rows with missing value


# Ruta donde se guardarán los archivos CSV
ruta_guardado = os.path.join(ruta_analisis_T, "Pruebas_estadisticas")

# Inicializar el DataFrame fuera del bucle para acumular datos de todos los meses
valores_fuera_total = pd.DataFrame(columns=['TIMESTAMP', 'Valor_Original', 'Limite', 'ELEMENTO'])

# Definir los nombres de los meses en español
nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

# Initialize dictionaries to store statistics for T_h

Maximo_T_h = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_h}
Minimo_T_h = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_h}
Media_aritmetica_T_h = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_h}
Desviacion_estandarT_h = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_h}

# Iterate over each month in your data for T_h
for mes in range(1, 13):
    # Filter data by month
    df_mes_T_h = df_T_h_bd2[df_T_h_bd2['TIMESTAMP'].dt.month == mes]

    # Iterate over each variable in Variables_T_h
    for variable in Variables_T_h:
        # Replace zeros with NaN for each variable separately
        #df_mes_T_h[variable] = df_mes_T_h[variable].replace(0, np.nan)

        # Calculate statistics if there are non-NaN values
        if not df_mes_T_h[variable].dropna().empty:
            # Calculate trimmed mean, median, and standard deviation for each variable separately
            # Obtener los cuantiles 1% y 99% de tus datos
            q01 = df_mes_T_h[variable].quantile(0.4)
            q99 = df_mes_T_h[variable].quantile(0.95)

# Aplicar el recorte (trimming) utilizando clip
            Datos_T_h = df_mes_T_h[variable]

# Calcular el promedio de los datos recortados
            promedio = Datos_T_h.mean()
            
            promedio = Datos_T_h.mean()
            mediana = Datos_T_h.median()
            
            desvest = Datos_T_h.std()

            # Store statistics in dictionaries for each variable separately
            limits_per_month_T_h[variable][nombres_meses[mes - 1]].append((lim_inf, lim_sup))
            Asimetría_per_month_T_h[variable][nombres_meses[mes - 1]].append(Asimetría_value)
            Desviacion_estandarT_h[variable][nombres_meses[mes - 1]].append(desvest)
            Media_aritmetica_T_h[variable][nombres_meses[mes - 1]].append(promedio)
            median_per_month_T_h[variable][nombres_meses[mes - 1]].append(mediana)
            n_per_month_T_h[variable][nombres_meses[mes - 1]].append(n)
            q01_per_month_T_h[variable][nombres_meses[mes - 1]].append(q01)
            q99_per_month_T_h[variable][nombres_meses[mes - 1]].append(q99)

# Add the "NCERO" column to the original DataFrame for T_h for each variable separately
for variable in Variables_T_h:
    df_T_h_bd2[f'NCERO_{variable}'] = df_T_h_bd2['TIMESTAMP'].dt.month.map(lambda x: ncero_per_month_T_h[variable][nombres_meses[x - 1]])

# Print the table of limits per month for each variable in T_h
print("Tabla de límites, Asimetría, desviación estándar, promedio, mediana, q01 y q99 por mes para cada variable en T_h:")
for variable, limits_T_h in limits_per_month_T_h.items():
    print(f"\nVariable: {variable}")
    print("{:<10} {:<10} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<10} {:<5} {:<10}".format("Mes", "Limite Inf", "Limite Sup", "Asimetría", "Desv. Estándar", "Promedio", "Mediana", "q01", "q99", "k", "NCERO"))
    for mes, mes_limits_T_h in limits_T_h.items():
        if mes_limits_T_h:
            for i, (lim_inf_T_h, lim_sup_T_h) in enumerate(mes_limits_T_h):
                Asimetría_val_T_h = Asimetría_per_month_T_h[variable][mes][i]
                std_dev_T_h = Desviacion_estandarT_h[variable][mes][i]
                mean_val_T_h = Media_aritmetica_T_h[variable][mes][i]
                median_val_T_h = median_per_month_T_h[variable][mes][i]
                q01_val_T_h = q01_per_month_T_h[variable][mes][i]
                q99_val_T_h = q99_per_month_T_h[variable][mes][i]
                n_val_T_h = n_per_month_T_h[variable][mes][i]
                ncero_val_T_h = ncero_per_month_T_h[variable][mes]
                print("{:<10} {:<10} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<10} {:<5} {:<10}".format(mes, round(lim_inf_T_h, 2), round(lim_sup_T_h, 2), round(Asimetría_val_T_h, 2), round(std_dev_T_h, 2), round(mean_val_T_h, 2), round(median_val_T_h, 2), round(q01_val_T_h, 2), round(q99_val_T_h, 2), n_val_T_h, ncero_val_T_h))

# Initialize dictionaries to store statistics for T_d
limits_per_month_T_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_d}
Asimetría_per_month_T_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_d}
Desviacion_estandarT_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_d}
Media_aritmetica_T_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_d}
median_per_month_T_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_d}
n_per_month_T_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_d}
ncero_per_month_T_d = {var: {mes: 0 for mes in nombres_meses} for var in Variables_T_d}  # Separate count for each variable

# Iterate over each month in your data for T_d
for mes in range(1, 13):
    # Filter data by month
    df_mes_T_d = df_T_d_bd2[df_T_d_bd2['TIMESTAMP'].dt.month == mes]

    # Iterate over each variable in Variables_T_d
    for variable in Variables_T_d:
        # Replace zeros with NaN for each variable separately
        df_mes_T_d[variable] = df_mes_T_d[variable].replace(0, np.nan)

        # Count the number of zeros for NCERO for each variable separately
        zeros_count_T_d = df_mes_T_d[variable].isna().sum()
        ncero_per_month_T_d[variable][nombres_meses[mes - 1]] += zeros_count_T_d

        # Calculate statistics if there are non-NaN values
        if not df_mes_T_d[variable].dropna().empty:
            # Calculate trimmed mean, median, and standard deviation for each variable separately
            trim_pro_T_d = df_mes_T_d[variable].quantile([0, 1])
            q01_pro_T_d = trim_pro_T_d.iloc[0]
            q99_pro_T_d = trim_pro_T_d.iloc[1]
            Datos_T_h_pro_T_d = df_mes_T_d[(df_mes_T_d[variable] >= q01_pro_T_d) & (df_mes_T_d[variable] <= q99_pro_T_d)]
            
            promedio_T_d = Datos_T_h_pro_T_d[variable].mean()
            mediana_T_d = Datos_T_h_pro_T_d[variable].median()
            trim_std_T_d = df_mes_T_d[variable].quantile([0, 1])
            q01_std_T_d = trim_std_T_d.iloc[0]
            q99_std_T_d = trim_std_T_d.iloc[1]
            Datos_T_h_std_T_d = df_mes_T_d[(df_mes_T_d[variable] >= q01_std_T_d) & (df_mes_T_d[variable] <= q99_std_T_d)]
            desvest_T_d = Datos_T_h_std_T_d[variable].std()
            Asimetría_value_T_d = ((df_mes_T_d[variable] - promedio_T_d) ** 3 / desvest_T_d ** 3).mean()

            # Store statistics in dictionaries for each variable separately
            limits_per_month_T_d[variable][nombres_meses[mes - 1]].append((lim_inf, lim_sup))
            Asimetría_per_month_T_d[variable][nombres_meses[mes - 1]].append(Asimetría_value_T_d)
            Desviacion_estandarT_d[variable][nombres_meses[mes - 1]].append(desvest_T_d)
            Media_aritmetica_T_d[variable][nombres_meses[mes - 1]].append(promedio_T_d)
            median_per_month_T_d[variable][nombres_meses[mes - 1]].append(mediana_T_d)
            n_per_month_T_d[variable][nombres_meses[mes - 1]].append(n)

# Add the "NCERO" column to the original DataFrame for T_d for each variable separately
for variable in Variables_T_d:
    df_T_d_bd2[f'NCERO_{variable}'] = df_T_d_bd2['TIMESTAMP'].dt.month.map(lambda x: ncero_per_month_T_d[variable][nombres_meses[x - 1]])

# Print the table of limits per month for each variable in T_d
print("Tabla de límites, Asimetría, desviación estándar, promedio, mediana y n por mes para cada variable en T_d:")
for variable, limits_T_d in limits_per_month_T_d.items():
    print(f"\nVariable: {variable}")
    print("{:<10} {:<10} {:<15} {:<15} {:<15} {:<15} {:<10} {:<5} {:<10}".format("Mes", "Limite Inf", "Limite Sup", "Asimetría", "Desv. Estándar", "Promedio", "Mediana", "k", "NCERO"))
    for mes, mes_limits_T_d in limits_T_d.items():
        if mes_limits_T_d:
            for i, (lim_inf_T_d, lim_sup_T_d) in enumerate(mes_limits_T_d):
                Asimetría_val_T_d = Asimetría_per_month_T_d[variable][mes][i]
                std_dev_T_d = Desviacion_estandarT_d[variable][mes][i]
                mean_val_T_d = Media_aritmetica_T_d[variable][mes][i]
                median_val_T_d = median_per_month_T_d[variable][mes][i]
                n_val_T_d = n_per_month_T_d[variable][mes][i]
                ncero_val_T_d = ncero_per_month_T_d[variable][mes]
                print("{:<10} {:<10} {:<15} {:<15} {:<15} {:<15} {:<10} {:<5} {:<10}".format(mes, round(lim_inf_T_d, 2), round(lim_sup_T_d, 2), round(Asimetría_val_T_d, 2), round(std_dev_T_d, 2), round(mean_val_T_d, 2), round(median_val_T_d, 2), n_val_T_d, ncero_val_T_d))