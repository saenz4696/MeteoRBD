import pandas as pd
import os
import warnings
import shutil

# Eliminar UserWarnings de openpyxl
warnings.simplefilter('ignore', category=UserWarning)

datos_crudos = r'C:\\MeteoRBD.v1.0.0\\raw_data_rbd'

# Encuentra el archivo .xlsx en los datos_crudos que contiene 'Cuenca' y 'Estación' como columnas
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
ruta_analisis_T = f"C:\\MeteoRBD.v1.0.0\\Data_Lake\\{num_estacion}-ema\\base_datos\\Temperatura\\análisis_datos"

# Crea las carpetas si no existen
for carpeta in ["", "Pruebas_estadisticas"]:
    ruta_pruebas_b = os.path.join(ruta_analisis_T, carpeta)
    os.makedirs(ruta_pruebas_b, exist_ok=True)
    
# Encuentra el archivo T.h.bd2.csv de temperatura en la ruta de la estación
ruta_T_h_bd3 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.h.bd3' in archivo), None)

# Encuentra el archivo T.d.bd2.csv de temperatura en la ruta de la estación
ruta_T_d_bd3 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.d.bd3' in archivo), None)

def edita_T_h_db3():
    for root, dirs, files in os.walk(ruta_pruebas_b):
        for file in files:
            if 'T_h' in file and file.endswith('.csv'):
                archivos_T_h = os.path.join(root, file)
                df_mes_T_h = pd.read_csv(archivos_T_h)
                df_T_h_bd3 = pd.read_csv(ruta_T_h_bd3)  # Lee el archivo T.h.bd3.csv una vez fuera del bucle
                for index, row in df_mes_T_h.iterrows():
                    elemento = row['ELEMENTO']
                    fecha = row['FECHA']
                    valor_reemplazo = row['Valor_reemplazo']
                    # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                    if valor_reemplazo != 'NA':
                        # Realiza el reemplazo si coincide el elemento y la fecha
                        df_T_h_bd3.loc[(df_T_h_bd3['TIMESTAMP'] == fecha), elemento] = valor_reemplazo
                # Guarda el archivo T.h.bd3.csv después de realizar todos los reemplazos
                df_T_h_bd3.to_csv(ruta_T_h_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos

def edita_T_d_db3():
    for root, dirs, files in os.walk(ruta_pruebas_b):
        for file in files:
            if 'T_d' in file and file.endswith('.csv'):
                archivos_T_d = os.path.join(root, file)
                df_mes_T_d = pd.read_csv(archivos_T_d)
                df_T_d_bd3 = pd.read_csv(ruta_T_d_bd3)  # Lee el archivo T.h.bd3.csv una vez fuera del bucle
                for index, row in df_mes_T_d.iterrows():
                    elemento = row['ELEMENTO']
                    fecha = row['FECHA']
                    valor_reemplazo = row['Valor_reemplazo']
                    # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                    if valor_reemplazo != 'NA':
                        # Realiza el reemplazo si coincide el elemento y la fecha
                        df_T_d_bd3.loc[(df_T_d_bd3['TIMESTAMP'] == fecha), elemento] = valor_reemplazo
                # Guarda el archivo T.h.bd3.csv después de realizar todos los reemplazos
                df_T_d_bd3.to_csv(ruta_T_d_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos

edita_T_h_db3()
edita_T_d_db3()