import pandas as pd
import os
import warnings
import numpy as np

# Ignora los UserWarnings
warnings.simplefilter('ignore', category=UserWarning)

# Directorio de los datos crudos
datos_crudos = r'C:\MeteoRBD.v1.0.0\datos_rbd'

# Ruta del archivo Excel para extraer datos
archivo_crudo_T = next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Temperatura" in file and file.endswith(".xlsx")), None)

if archivo_crudo_T:
    archivo_excel = pd.read_excel(archivo_crudo_T)
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

directorio_base = rf"C:\MeteoRBD.v1.0.0\revisión\{num_estacion}-ema"
directorio_salida_T = os.path.join(directorio_base, 'Temperatura')
       
def Formatear_T_h():
    # Columnas originales esperadas en los datos de la temperatura horaria
    columnas_originales_T_h = ['Cuenca', 'Estación', 'Fecha', 'Hora', 'Temperatura', 'Temp Punto Rocio']
    # Directorios de entrada y salida
    datos_formateados_T_h = []
    archivo_T_h = False

    # Crea el directorio de salida si no existe
    if not os.path.exists(directorio_salida_T):
        os.makedirs(directorio_salida_T)

    for nombre_original_T_h in os.listdir(datos_crudos):
        archivo_crudo_T = os.path.join(datos_crudos, nombre_original_T_h)
        
        try:
            if nombre_original_T_h.endswith(".xlsx"):
                df = pd.read_excel(archivo_crudo_T, keep_default_na=False)
                
                if all(col in df.columns for col in columnas_originales_T_h) and "Temperatura" in nombre_original_T_h and "Horaria" in nombre_original_T_h:
                    # Formateo de los datos de la temperatura horaria
                    df_T_h = df.copy()
                    df_T_h['Hora'] = df_T_h['Hora'].apply(lambda x: f"{x:04d}" if x != 2400 else '0000')
                    df_T_h['Fecha'] = pd.to_datetime(df_T_h['Fecha'], format='%d/%m/%Y', errors='coerce')
                    df_T_h.loc[df_T_h['Hora'] == '0000', 'Fecha'] += pd.to_timedelta(1, unit='d')
                    df_T_h['TIMESTAMP'] = pd.to_datetime(df_T_h['Fecha'].dt.strftime('%Y-%m-%d') + ' ' + df_T_h['Hora'], errors='coerce')
                    df_T_h.sort_values(by='TIMESTAMP', inplace=True)
                    df_T_h['ESTACION'] = df_T_h['Cuenca'].astype(str).str.zfill(3) + df_T_h['Estación'].astype(str).str.zfill(3)
                    df_T_h.rename(columns={'Temperatura': 'Temp.degC.avg.1h.s1', 'Temp Punto Rocio': 'Td.degC.avg.1h.c1'}, inplace=True)
                    df_T_h = df_T_h[['TIMESTAMP', 'ESTACION', 'Temp.degC.avg.1h.s1', 'Td.degC.avg.1h.c1']]
                    
                    tiempo_inicial_T_h = df_T_h['TIMESTAMP'].min()
                    tiempo_final_T_h = df_T_h['TIMESTAMP'].max()
                    nombre_formateado_T_h = f"{num_estacion}.{tiempo_inicial_T_h.strftime('%Y%m%d-%H')}.{tiempo_final_T_h.strftime('%Y%m%d-%H')}.T.h.bd0.csv"
                    nombre_formateado_T_h = ''.join([c for c in nombre_formateado_T_h if c.isalnum() or c in ['-', '.', '_']]).rstrip()
                    archivo_salida_T_h = os.path.join(directorio_salida_T, nombre_formateado_T_h)
                    
                    df_T_h.replace({np.nan: '', pd.NA: '', ' ': ''}, inplace=True)
                    df_T_h.to_csv(archivo_salida_T_h, index=False, na_rep='', float_format='%.2f') 
                    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                    print(f"Se ha formateado exitosamente el archivo de la temperatura horaria crudo como: {nombre_formateado_T_h}.")
                    print('')
                    datos_formateados_T_h.append(df_T_h)
                    archivo_T_h = True

        except Exception as e:
            print(f"Error procesando el archivo '{nombre_original_T_h}': {str(e)}")
    
    if not archivo_T_h:
        print('\nAviso: No se encontró algún archivo de la temperatura horaria.\n')

    return datos_formateados_T_h

Formatear_T_h()

def Formatear_T_d():
    # Columnas originales esperadas en los datos de la temperatura diaria
    columnas_originales_T_d = ['Cuenca', 'Estación', 'Fecha', 'Temperatura Maxima (°C)', 'Fecha Temp Max', 'Hora Temp Max', 'Temperatura Minima (°C)', 'Fecha Temp Min', 'Hora Temp Min']
    # Directorios de entrada y salida
    datos_formateados_T_d = []
    archivo_T_d = False

    # Verifica si el directorio 'Temperatura' existe, si no, créalo
    if not os.path.exists(directorio_salida_T):
        os.makedirs(directorio_salida_T)

    for nombre_original_T_d in os.listdir(datos_crudos):
        archivo_crudo_T = os.path.join(datos_crudos, nombre_original_T_d)
        
        try:
            if nombre_original_T_d.endswith(".xlsx"):
                df = pd.read_excel(archivo_crudo_T, keep_default_na=False)  # Leer archivo Excel
                
                # Procesamiento de Datos de la temperatura Diaria
                if all(col in df.columns for col in columnas_originales_T_d) and "Temperatura" in nombre_original_T_d and "Diaria" in nombre_original_T_d:
                    df_T_d = df.copy()
                    
                    # Replace 'NULL' with -9 in 'Hora Temp Max' and 'Hora Temp Min' columns
                    df_T_d['Hora Temp Max'] = pd.to_numeric(df_T_d['Hora Temp Max'], errors='coerce').fillna(-9).astype(int)
                    df_T_d['Hora Temp Min'] = pd.to_numeric(df_T_d['Hora Temp Min'], errors='coerce').fillna(-9).astype(int)

                    df_T_d['Hora Temp Max'] = df_T_d['Hora Temp Max'].apply(lambda x: f"{x:04d}" if x != 2400 else '0000')
                    df_T_d['Hora Temp Min'] = df_T_d['Hora Temp Min'].apply(lambda x: f"{x:04d}" if x != 2400 else '0000')
                    df_T_d['Fecha'] = pd.to_datetime(df_T_d['Fecha'], format='%d/%m/%Y', errors='coerce')
                    df_T_d['TIMESTAMP'] = df_T_d['Fecha'] + pd.to_timedelta('07:00:00')
                    # Ordenar DataFrame por TIMESTAMP

                    #df_T_d['Temp.CST.max.dm.s1.fecha'] = pd.to_datetime(df_T_d['Fecha Temp Max'], format='%Y-%m-%d') + pd.to_timedelta(df_T_d['Hora Temp Max'].astype(str).str.pad(4, fillchar='0').str[:2].astype(int), unit='h') + pd.to_timedelta(df_T_d['Hora Temp Max'].astype(str).str.pad(4, fillchar='0').str[2:].astype(int), unit='m')
                    #df_T_d['Temp.CST.min.dm.s1.fecha'] = pd.to_datetime(df_T_d['Fecha Temp Min'], format='%Y-%m-%d') + pd.to_timedelta(df_T_d['Hora Temp Min'].astype(str).str.pad(4, fillchar='0').str[:2].astype(int), unit='h') + pd.to_timedelta(df_T_d['Hora Temp Min'].astype(str).str.pad(4, fillchar='0').str[2:].astype(int), unit='m')
                    df_T_d['Temp.CST.max.dm.s1.fecha'] = pd.to_datetime(df_T_d['Fecha Temp Max'], format='%d/%m/%Y') + pd.to_timedelta(df_T_d['Hora Temp Max'].astype(str).str.pad(4, fillchar='0').str[:2].astype(int), unit='h') + pd.to_timedelta(df_T_d['Hora Temp Max'].astype(str).str.pad(4, fillchar='0').str[2:].astype(int), unit='m')
                    df_T_d['Temp.CST.min.dm.s1.fecha'] = pd.to_datetime(df_T_d['Fecha Temp Min'], format='%d/%m/%Y') + pd.to_timedelta(df_T_d['Hora Temp Min'].astype(str).str.pad(4, fillchar='0').str[:2].astype(int), unit='h') + pd.to_timedelta(df_T_d['Hora Temp Min'].astype(str).str.pad(4, fillchar='0').str[2:].astype(int), unit='m')

                    df_T_d['ESTACION'] = df_T_d['Cuenca'].astype(str).str.zfill(3) + df_T_d['Estación'].astype(str).str.zfill(3)
                    df_T_d.rename(columns={'Temperatura Maxima (°C)': 'Temp.degC.max.dm.s1', 'Temperatura Minima (°C)': 'Temp.degC.min.dm.s1', 'Temp.CST.max.dm.s1.fecha': 'Temp.CST.max.dm.s1', 'Temp.CST.min.dm.s1.fecha': 'Temp.CST.min.dm.s1'}, inplace=True)
                    df_T_d = df_T_d[['TIMESTAMP', 'ESTACION','Temp.degC.max.dm.s1', 'Temp.CST.max.dm.s1','Temp.degC.min.dm.s1', 'Temp.CST.min.dm.s1']]
            
                    tiempo_inicial_T_d = df_T_d['TIMESTAMP'].min()
                    tiempo_final_T_d = df_T_d['TIMESTAMP'].max()
                    nombre_formateado_T_d = f"{num_estacion}.{tiempo_inicial_T_d.strftime('%Y%m%d-%H')}.{tiempo_final_T_d.strftime('%Y%m%d-%H')}.T.d.bd0.csv"
                    nombre_formateado_T_d = ''.join([c for c in nombre_formateado_T_d if c.isalnum() or c in ['-', '.', '_']]).rstrip()
                    archivo_salida_T_d = os.path.join(directorio_salida_T, nombre_formateado_T_d)
                    
                    df_T_d.replace({np.nan: '', pd.NA: '', ' ': ''}, inplace=True)
                    df_T_d.to_csv(archivo_salida_T_d, index=False, na_rep='', float_format='%.2f')
                    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                    print(f"Se ha formateado exitosamente el archivo de la temperatura diaria crudo como: {nombre_formateado_T_d}.")
                    print('')
                    datos_formateados_T_d.append(df_T_d)
                    archivo_T_d = True             
 
        except Exception as e:
            print(f"Error procesando el archivo '{nombre_original_T_d}': {str(e)}")
    
    if not archivo_T_d:
        print('\nAviso: No se encontró algún archivo de la temperatura diaria.\n')

    return datos_formateados_T_d

Formatear_T_d()
