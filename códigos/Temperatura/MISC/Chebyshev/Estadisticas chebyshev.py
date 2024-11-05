import pandas as pd
import os
import warnings
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
from distfit import distfit
import scipy.stats as stats
import numpy as np
from scipy.stats import describe, skew, kurtosis

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

# Función para calcular n según la Asimetría
def calculate_n(Asimetría_value):
    rangos_positivos = [(-0.5, 0.5, 3.5), (0.5, 1, 4), (1, 1.5, 4.5), (1.5, 2, 5), (2, 2.5, 5.5), (2.5, 3, 6),
                       (3, 3.5, 6.5), (3.5, 4, 7), (4, 4.5, 7.5), (4.5, 5, 8), (5, 5.5, 8.5), (5.5, 6, 9),
                       (6, 6.5, 9.5), (6.5, 7, 10), (7, 7.5, 10.5), (7.5, 8, 11), (8, 8.5, 11.5), (8.5, 9, 12),
                       (9, 9.5, 12.5), (9.5, 10, 13), (10, 10.5, 13.5)]
    
    rangos_negativos = [(-11, -10.5, 14), (-10.5, -10, 13.5), (-10, -9.5, 13), (-9.5, -9, 12.5), (-9, -8.5, 12),
                       (-8.5, -8, 11.5), (-8, -7.5, 11), (-7.5, -7, 10.5), (-7, -6.5, 10), (-6.5, -6, 9.5),
                       (-6, -5.5, 9), (-5.5, -5, 8.5), (-5, -4.5, 8), (-4.5, -4, 7.5), (-4, -3.5, 7), (-3.5, -3, 6.5),
                       (-3, -2.5, 6), (-2.5, -2, 5.5), (-2, -1.5, 5), (-1.5, -1, 4.5), (-1, -0.5, 4)]
    
    if Asimetría_value == -0.5:
        return 3.5
    elif Asimetría_value == 10.5:
        return 13.5
    
    if -11 <= Asimetría_value < -0.5:
        for inferior, superior, value in rangos_negativos:
            if inferior <= Asimetría_value < superior:
                return value
    elif -0.5 <= Asimetría_value < 10.5:
        for inferior, superior, value in rangos_positivos:
            if inferior < Asimetría_value <= superior:
                return value
    elif Asimetría_value > 10.5:
        return 14
    else:
        return None

# Función para calcular los límites Chebyshev
def cheby_lim(promedio, desvest, n):
    limite_inferior_chebyshev = promedio - n * desvest
    limite_superior_chebyshev = promedio + n * desvest
    return limite_inferior_chebyshev, limite_superior_chebyshev

# Ruta donde se guardarán los archivos CSV
ruta_guardado = os.path.join(ruta_analisis_T, "Pruebas_estadisticas")

# Inicializar el DataFrame fuera del bucle para acumular datos de todos los meses
valores_fuera_total = pd.DataFrame(columns=['TIMESTAMP', 'Valor_Original', 'Limite', 'ELEMENTO'])

# Definir los nombres de los meses en español
nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

# Inicializar un diccionario para almacenar los límites por mes para cada variable
limits_per_month = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_h}
Asimetría_per_month = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_h}
std_per_month = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_h}
mean_per_month = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_h}
median_per_month = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_h}
n_per_month = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_h}

# Iterar sobre cada mes en tus datos
for mes in range(1, 13):
    # Filtrar datos por mes
    df_mes = df_T_h_bd2[df_T_h_bd2['TIMESTAMP'].dt.month == mes]

    # Iterar sobre cada variable en Variables_T_h
    for variable in Variables_T_h:
        # Calcular promedio, mediana y desviación estándar si hay datos
        if not df_mes.empty:
            promedio = df_mes[variable].mean()
            mediana = df_mes[variable].median()
            desvest = df_mes[variable].std()

            # Calcular n para Chebyshev
            Asimetría_value = (3 * (promedio - mediana)) / desvest
            n = calculate_n(Asimetría_value)

            # Calcular límites Chebyshev
            lim_inf, lim_sup = cheby_lim(promedio, desvest, n)

            # Almacenar los límites en el diccionario
            limits_per_month[variable][nombres_meses[mes - 1]].append((lim_inf, lim_sup))
            Asimetría_per_month[variable][nombres_meses[mes - 1]].append(Asimetría_value)
            std_per_month[variable][nombres_meses[mes - 1]].append(desvest)
            mean_per_month[variable][nombres_meses[mes - 1]].append(promedio)
            median_per_month[variable][nombres_meses[mes - 1]].append(mediana)
            n_per_month[variable][nombres_meses[mes - 1]].append(n)

# Mostrar la tabla de límites por mes para cada variable
print("Tabla de límites, Asimetría, desviación estándar, promedio, mediana y n por mes para cada variable:")
for variable, limits in limits_per_month.items():
    print(f"\nVariable: {variable}")
    print("{:<10} {:<10} {:<15} {:<15} {:<15} {:<15} {:<10} {:<5}".format("Mes", "Limite Inf", "Limite Sup", "Asimetría", "Desv. Estándar", "Promedio", "Mediana", "k"))
    for mes, mes_limits in limits.items():
        if mes_limits:
            for i, (lim_inf, lim_sup) in enumerate(mes_limits):
                Asimetría_val = Asimetría_per_month[variable][mes][i]
                std_dev = std_per_month[variable][mes][i]
                mean_val = mean_per_month[variable][mes][i]
                median_val = median_per_month[variable][mes][i]
                n_val = n_per_month[variable][mes][i]
                print("{:<10} {:<10} {:<15} {:<15} {:<15} {:<15} {:<10} {:<5}".format(mes, round(lim_inf, 2), round(lim_sup, 2), round(Asimetría_val, 2), round(std_dev, 2), round(mean_val, 2), round(median_val, 2), n_val))
                

# Inicializar un diccionario para almacenar los límites por mes para cada variable en Variables_T_d
limits_per_month_T_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_d}
Asimetría_per_month_T_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_d}
std_per_month_T_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_d}
mean_per_month_T_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_d}
median_per_month_T_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_d}
n_per_month_T_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_d}

# Iterar sobre cada mes en tus datos
for mes in range(1, 13):
    # Filtrar datos por mes
    df_mes_T_d = df_T_d_bd2[df_T_d_bd2['TIMESTAMP'].dt.month == mes]

    # Iterar sobre cada variable en Variables_T_d
    for variable in Variables_T_d:
        # Calcular promedio y desviación estándar si hay datos
        if not df_mes_T_d.empty:
            promedio_T_d = df_mes_T_d[variable].mean()
            mediana_T_d = df_mes_T_d[variable].median()
            desvest_T_d = df_mes_T_d[variable].std()

            # Calcular n para Chebyshev
            Asimetría_value_T_d = (3*(promedio_T_d-mediana_T_d)) / desvest_T_d
            n_T_d = calculate_n(Asimetría_value_T_d)

            # Calcular límites Chebyshev
            lim_inf_T_d, lim_sup_T_d = cheby_lim(promedio_T_d, desvest_T_d, n_T_d)

            # Almacenar los límites en el diccionario
            limits_per_month_T_d[variable][nombres_meses[mes - 1]].append((lim_inf_T_d, lim_sup_T_d))
            Asimetría_per_month_T_d[variable][nombres_meses[mes - 1]].append(Asimetría_value_T_d)
            std_per_month_T_d[variable][nombres_meses[mes - 1]].append(desvest_T_d)
            mean_per_month_T_d[variable][nombres_meses[mes - 1]].append(promedio_T_d)
            median_per_month_T_d[variable][nombres_meses[mes - 1]].append(mediana_T_d)
            n_per_month_T_d[variable][nombres_meses[mes - 1]].append(n_T_d)

# Mostrar la tabla de límites por mes para cada variable en Variables_T_d
print("Tabla de límites, Asimetría, desviación estándar, promedio y n por mes para cada variable en Variables_T_d:")
for variable, limits_T_d in limits_per_month_T_d.items():
    print(f"\nVariable: {variable}")
    print("{:<10} {:<10} {:<15} {:<15} {:<15} {:<15} {:<10} {:<5}".format("Mes", "Limite Inf", "Limite Sup", "Asimetría", "Desv. Estándar", "Promedio", "Mediana", "k"))
    for mes, mes_limits_T_d in limits_T_d.items():
        if mes_limits_T_d:
            for i, (lim_inf_T_d, lim_sup_T_d) in enumerate(mes_limits_T_d):
                Asimetría_val_T_d = Asimetría_per_month_T_d[variable][mes][i]
                std_dev_T_d = std_per_month_T_d[variable][mes][i]
                mean_val_T_d = mean_per_month_T_d[variable][mes][i]
                median_val_T_d = median_per_month_T_d[variable][mes][i]
                n_val_T_d = n_per_month_T_d[variable][mes][i]
                print("{:<10} {:<10} {:<15} {:<15} {:<15} {:<15} {:<10} {:<5}".format(mes, round(lim_inf_T_d, 2), round(lim_sup_T_d, 2), round(Asimetría_val_T_d, 2), round(std_dev_T_d, 2), round(mean_val_T_d, 2), round(median_val_T_d, 2), n_val_T_d))