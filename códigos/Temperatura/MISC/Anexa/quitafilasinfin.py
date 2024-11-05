import pandas as pd
import os
import warnings

# Eliminate UserWarnings from openpyxl
warnings.simplefilter('ignore', category=UserWarning)

datos_crudos = r'C:\\MeteoRBD.v1.0.0\\raw_data_rbd'

# Find the .xlsx file in datos_crudos that contains 'Cuenca' and 'Estación' as columns
ruta_archivo = next((os.path.join(datos_crudos, archivo) for archivo in os.listdir(datos_crudos) if archivo.endswith(".xlsx")), None)

if ruta_archivo:
    archivo_excel = pd.read_excel(ruta_archivo)
    if all(col in archivo_excel.columns for col in ['Cuenca', 'Estación']):
        # Get the station number from the Excel file
        cuenca = str(archivo_excel['Cuenca'].iloc[0])
        estacion = str(archivo_excel['Estación'].iloc[0])
        if len(estacion) == 2:
            estacion = '0' + estacion  # Add leading zero if 'Estación' has only two digits
        num_estacion = cuenca + estacion
        num_estacion = int(num_estacion)

# Set the path for temperature files based on the station number obtained from the Excel file
ruta_analisis_T = f"C:\\MeteoRBD.v1.0.0\\Data_Lake\\{num_estacion}-ema\\base_datos\\Temperatura\\análisis_datos"

# Encuentra el archivo T.d.bd2.csv de temperatura en la ruta de la estación
ruta_T_d_bd3 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.d.bd3' in archivo), None)


def elimina_fila_anumerica_T_d():
    if ruta_T_d_bd3:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_T_d_bd3 = pd.read_csv(ruta_T_d_bd3, na_values=['NA'])

        # Filtra las filas sin valores numéricos al principio y al final en ciertas columnas
        indices_numericos_T_d = df_T_d_bd3[df_T_d_bd3[['Temp.degC.max.dm.s1', 'Temp.degC.min.dm.s1']].apply(pd.to_numeric, errors='coerce').notnull().any(axis=1)].index
        
        if not indices_numericos_T_d.empty:
            primer_indice_numerico_T_d = indices_numericos_T_d[0]
            ultimo_indice_numerico_T_d = indices_numericos_T_d[-1]

            # Conserva las filas con valores numéricos
            df_T_d_bd3 = df_T_d_bd3.iloc[primer_indice_numerico_T_d:ultimo_indice_numerico_T_d + 1]

            # Rellena valores no numéricos con 'NA' en ciertas columnas y agrega el número de estación en la columna ESTACION
            rellena_caracteres_NA_T_d = ['Temp.degC.max.dm.s1', 'Temp.degC.min.dm.s1']
            for col in rellena_caracteres_NA_T_d:
                df_T_d_bd3[col] = pd.to_numeric(df_T_d_bd3[col], errors='coerce').fillna('NA')

            # Guarda el archivo CSV
            df_T_d_bd3.to_csv(ruta_T_d_bd3, index=False)
    else:
        print('-----------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de temperatura horaria T.d.bd3.csv")

elimina_fila_anumerica_T_d()

