import pandas as pd
import os
import warnings
import seaborn as sns
import matplotlib
import scipy.stats as stats
import numpy as np

sns.seR_style("whitegrid")
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
    os.makedirs(ruta_pruebas_b, exisR_ok=True)
    
# Encuentra el archivo T.h.bd3.csv de temperatura en la ruta de la estación
ruta_R_h_bd3 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.h.bd3' in archivo), None)

# Encuentra el archivo T.d.bd3.csv de temperatura en la ruta de la estación
ruta_R_d_bd3 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.d.bd3' in archivo), None)
    
unidad = '°C'
#-----------------------------------------------------------------------------------------------------------------

if ruta_R_h_bd3 or ruta_R_d_bd3:
    # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if ruta_R_h_bd3:
            df_R_h_bd3 = pd.read_csv(ruta_R_h_bd3, na_values=['NA'])
            df_R_h_bd3['TIMESTAMP'] = pd.to_datetime(df_R_h_bd3['TIMESTAMP'])  # Convertir a tipo de dato de fecha y hora
            df_R_h_bd3 = df_R_h_bd3.dropna()

        if ruta_R_d_bd3:
            df_R_d_bd3 = pd.read_csv(ruta_R_d_bd3, na_values=['NA'])
            df_R_d_bd3['TIMESTAMP'] = pd.to_datetime(df_R_d_bd3['TIMESTAMP'])
            df_R_d_bd3 = df_R_d_bd3.dropna()  # Eliminar filas con valores faltantes

# Variables para R.h
Variables_R_h = ['Precip.mm.tot.1h.s1']
# Variables para R.d
Variables_R_d = ['Precip.mm.tot.dm.s1']

# Definir los nombres de los meses en español
nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

def Estadisticos_R_h_d(ruta_pruebas_b, num_estacion):

    # Inicializar diccionarios para almacenar estadísticas de R_h y R_d
    estadisticos_R_h_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_R_h + Variables_R_d}

    # Iterar sobre cada mes en los datos de R_h y R_d
    for mes in range(1, 13):
        # Filtrar datos por mes para R_h y R_d
        df_mes_R_h = df_R_h_bd3[df_R_h_bd3['TIMESTAMP'].dt.month == mes]
        df_mes_R_d = df_R_d_bd3[df_R_d_bd3['TIMESTAMP'].dt.month == mes]

        # Iterar sobre cada variable en Variables_R_h y Variables_R_d
        for variable in Variables_R_h + Variables_R_d:
            # Seleccionar el dataframe correspondiente
            df_mes = df_mes_R_h if variable in Variables_R_h else df_mes_R_d

            # Calcular estadísticas si hay valores que no son NaN
            if not df_mes[variable].dropna().empty:
                # Calcular máximo, mínimo, media y desviación estándar
                max_val = df_mes[variable].max()
                min_val = df_mes[variable].min()
                mean_val = df_mes[variable].mean()
                std_val = df_mes[variable].std()

                # Almacenar estadísticas en el diccionario
                estadisticos_R_h_d[variable][nombres_meses[mes - 1]] = [max_val, min_val, mean_val, std_val]

    # Guardar estadísticas para R_h y R_d en un archivo de texto
    with open(os.path.join(ruta_pruebas_b, "Estadisticos_R_E1.txt"), "w") as file:
        for variable in Variables_R_h + Variables_R_d:
            file.write(f"\nEstación: {num_estacion} - Variable: {variable}\n")
            file.write("{:<12} {:<8} {:<8} {:<17} {:<17}\n".format("Mes", "Máximo", "Mínimo", "Media aritmética", "Desviación estándar"))
            for mes in range(1, 13):
                max_val, min_val, mean_val, std_val = estadisticos_R_h_d[variable][nombres_meses[mes - 1]]
                file.write("{:<12} {:<8.2f} {:<8.2f} {:<17.2f} {:<17.2f}\n".format(nombres_meses[mes - 1], max_val, min_val, mean_val, std_val))

# Ramada a la función
Estadisticos_R_h_d(ruta_pruebas_b, num_estacion)
