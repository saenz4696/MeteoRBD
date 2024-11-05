import pandas as pd
import os
import warnings
import seaborn as sns
import matplotlib
import scipy.stats as stats
import numpy as np

sns.set_style("whitegrid")
matplotlib.use('Agg')

# -------------------------------Rutas generales

# Eliminar UserWarnings de openpyxl
warnings.simplefilter('ignore', category=UserWarning)

datos_crudos = r'C:\\MeteoRBD.v1.0.0\\data_rbd'

# Encuentra el archivo .xlsx en la datos_crudos que contiene 'Cuenca' y 'Estación' como columnas
ruta_archivo = next((os.path.join(datos_crudos, archivo) for archivo in os.listdir(datos_crudos) if archivo.endswith(".xlsx")), None)

if ruta_archivo:
    archivo_excel = pd.read_excel(ruta_archivo)
    if all(col in archivo_excel.columns for col in ['Cuenca', 'Estación']):
        # Obtiene el número de estación a partir del archivo Excel
        cuenca = str(archivo_excel['Cuenca'].iloc[0])
        estacion = str(archivo_excel['Estación'].iloc[0])
        if len(estacion) == 2:
            estacion = '0' + estacion  # Agregar cero al principio si 'Estación' tiene solo dos dígitos
        elif len(estacion) == 1:
            estacion = '00' + estacion
        num_estacion = cuenca + estacion
        num_estacion = int(num_estacion)

# Establece la ruta para los archivos de temperatura según el número de estación obtenido del archivo Excel
ruta_analisis_T = f"C:\\MeteoRBD.v1.0.0\\Data_Lake\\{num_estacion}-ema\\base_datos\\Temperatura\\análisis_datos"

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
            df_T_d_bd2 = df_T_d_bd2.dropna()  # Eliminar filas con valores faltantes

# Definir los nombres de los meses en español
nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

# Variables para T.h que están en df_T_h_bd2
Variables_T_h = ['Temp.degC.avg.1h.s1', 'Td.degC.avg.1h.c1']

# Variables para T.d que están en df_T_d_bd2
Variables_T_d = ['Temp.degC.max.dm.s1', 'Temp.degC.min.dm.s1']

def Estadisticos_T_h(ruta_pruebas_b, num_estacion):

        # Inicializar diccionarios para almacenar estadísticas de T_h
        Maximo_T_h = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_h}
        Minimo_T_h = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_h}
        Media_aritmetica_T_h = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_h}
        Desviacion_estandarT_h = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_h}
        
        # Iterar sobre cada mes en los datos de T_h
        for mes in range(1, 13):
            # Filtrar datos por mes para T_h
            df_mes_T_h = df_T_h_bd2[df_T_h_bd2['TIMESTAMP'].dt.month == mes]

            # Iterar sobre cada variable en Variables_T_h
            for variable in Variables_T_h:
                # Calcular estadísticas si hay valores que no son NaN
                if not df_mes_T_h[variable].dropna().empty:
                    # Calcular máximo, mínimo, media y desviación estándar para cada variable por separado
                    Max_T_h = df_mes_T_h[variable].max()
                    Min_T_h = df_mes_T_h[variable].min()
                    Media_T_h = df_mes_T_h[variable].mean()
                    Desvest_T_h = df_mes_T_h[variable].std()

                    # Almacenar estadísticas en diccionarios para cada variable por separado
                    Maximo_T_h[variable][nombres_meses[mes - 1]].append(Max_T_h)
                    Minimo_T_h[variable][nombres_meses[mes - 1]].append(Min_T_h)
                    Media_aritmetica_T_h[variable][nombres_meses[mes - 1]].append(Media_T_h)
                    Desviacion_estandarT_h[variable][nombres_meses[mes - 1]].append(Desvest_T_h)

        # Guardar estadísticas para T_h en un archivo de texto
        with open(os.path.join(ruta_pruebas_b, "Estadisticos_T_h.txt"), "w") as file:
            for variable in Variables_T_h:
                file.write(f"\nEstación: {num_estacion} - Variable: {variable}\n")
                file.write("{:<12} {:<8} {:<8} {:<17} {:<17}\n".format("Mes", "Máximo", "Mínimo", "Media aritmética", "Desviación estándar"))
                for mes in range(1, 13):
                    Max_T_h = np.nan if not Maximo_T_h[variable][nombres_meses[mes - 1]] else round(max(Maximo_T_h[variable][nombres_meses[mes - 1]]), 2)
                    Min_T_h = np.nan if not Minimo_T_h[variable][nombres_meses[mes - 1]] else round(min(Minimo_T_h[variable][nombres_meses[mes - 1]]), 2)
                    Media_T_h = np.nan if not Media_aritmetica_T_h[variable][nombres_meses[mes - 1]] else round(np.mean(Media_aritmetica_T_h[variable][nombres_meses[mes - 1]]), 2)
                    Desvest_T_h = np.nan if not Desviacion_estandarT_h[variable][nombres_meses[mes - 1]] else round(np.mean(Desviacion_estandarT_h[variable][nombres_meses[mes - 1]]), 2)
                    file.write("{:<12} {:<8} {:<8} {:<17} {:<17}\n".format(nombres_meses[mes - 1], Max_T_h, Min_T_h, Media_T_h, Desvest_T_h))

def Estadisticos_T_d(ruta_pruebas_b, num_estacion):
        
        # Inicializar diccionarios para almacenar estadísticas para T_d
        Maximo_T_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_d}
        Minimo_T_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_d}
        Media_aritmetica_T_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_d}
        Desviacion_estandarT_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_d}
        
        # Iterar sobre cada mes en los datos para T_d
        for mes in range(1, 13):
            # Filtrar datos por mes para T_d
            df_mes_T_d = df_T_d_bd2[df_T_d_bd2['TIMESTAMP'].dt.month == mes]

            # Iterar sobre cada variable en Variables_T_d
            for variable in Variables_T_d:
                # Calcular estadísticas si hay valores que no son NaN
                if not df_mes_T_d[variable].dropna().empty:
                    # Calcular máximo, mínimo, media y desviación estándar para cada variable por separado
                    Max_T_d = df_mes_T_d[variable].max()
                    Min_T_d = df_mes_T_d[variable].min()
                    Media_T_d = df_mes_T_d[variable].mean()
                    Desvest_T_d = df_mes_T_d[variable].std()

                    # Almacenar estadísticas en diccionarios para cada variable por separado
                    Maximo_T_d[variable][nombres_meses[mes - 1]].append(Max_T_d)
                    Minimo_T_d[variable][nombres_meses[mes - 1]].append(Min_T_d)
                    Media_aritmetica_T_d[variable][nombres_meses[mes - 1]].append(Media_T_d)
                    Desviacion_estandarT_d[variable][nombres_meses[mes - 1]].append(Desvest_T_d)

        # Guardar estadísticas para T_d en un archivo de texto
        with open(os.path.join(ruta_pruebas_b, "Estadisticos_T_d.txt"), "w") as file:
            for variable in Variables_T_d:
                file.write(f"\nEstación: {num_estacion} - Variable: {variable}\n")
                file.write("{:<12} {:<8} {:<8} {:<17} {:<17}\n".format("Mes", "Máximo", "Mínimo", "Media aritmética", "Desviación estándar"))
                for mes in range(1, 13):
                    Max_T_d = np.nan if not Maximo_T_d[variable][nombres_meses[mes - 1]] else round(max(Maximo_T_d[variable][nombres_meses[mes - 1]]), 2)
                    Min_T_d = np.nan if not Minimo_T_d[variable][nombres_meses[mes - 1]] else round(min(Minimo_T_d[variable][nombres_meses[mes - 1]]), 2)
                    Media_T_d = np.nan if not Media_aritmetica_T_d[variable][nombres_meses[mes - 1]] else round(np.mean(Media_aritmetica_T_d[variable][nombres_meses[mes - 1]]), 2)
                    Desvest_T_d = np.nan if not Desviacion_estandarT_d[variable][nombres_meses[mes - 1]] else round(np.mean(Desviacion_estandarT_d[variable][nombres_meses[mes - 1]]), 2)
                    file.write("{:<12} {:<8} {:<8} {:<17} {:<17}\n".format(nombres_meses[mes - 1], Max_T_d, Min_T_d, Media_T_d, Desvest_T_d))

# Llamadas a las funciones
Estadisticos_T_h(ruta_pruebas_b, num_estacion)
Estadisticos_T_d(ruta_pruebas_b, num_estacion)
