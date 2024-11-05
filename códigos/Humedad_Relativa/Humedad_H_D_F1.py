import pandas as pd
import os
import warnings
import numpy as np

# Ignora los UserWarnings
warnings.simplefilter('ignore', category=UserWarning)

# Directorio de los datos crudos
datos_crudos = r'C:\MeteoRBD.v1.0.0\datos_rbd'

# Ruta del archivo Excel para extraer datos
archivo_crudo_HR = next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Humedad" in file and file.endswith(".xlsx")), None)

if archivo_crudo_HR:
    archivo_excel = pd.read_excel(archivo_crudo_HR)
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
directorio_salida_HR = os.path.join(directorio_base, 'Humedad relativa')
       
def Formatear_HR_h():
    # Columnas originales esperadas en los datos de la humedad horaria
    columnas_originales_HR_h = ['Cuenca', 'Estación', 'Fecha', 'Hora', 'Humedad (%)']
    # Directorios de entrada y salida
    datos_formateados_HR_h = []
    archivo_HR_h = False

    # Crea el directorio de salida si no existe
    if not os.path.exists(directorio_salida_HR):
        os.makedirs(directorio_salida_HR)

    for nombre_original_HR_h in os.listdir(datos_crudos):
        archivo_crudo_HR = os.path.join(datos_crudos, nombre_original_HR_h)
        
        try:
            if nombre_original_HR_h.endswith(".xlsx"):
                df = pd.read_excel(archivo_crudo_HR, keep_default_na=False)
                
                if all(col in df.columns for col in columnas_originales_HR_h) and "Humedad" in nombre_original_HR_h and "Horaria" in nombre_original_HR_h:
                    # Formateo de los datos de la humedad horaria
                    df_HR_h = df.copy()
                    df_HR_h['Hora'] = df_HR_h['Hora'].apply(lambda x: f"{x:04d}" if x != 2400 else '0000')
                    df_HR_h['Fecha'] = pd.to_datetime(df_HR_h['Fecha'], format='%d/%m/%Y', errors='coerce')
                    df_HR_h.loc[df_HR_h['Hora'] == '0000', 'Fecha'] += pd.to_timedelta(1, unit='d')
                    df_HR_h['TIMESTAMP'] = pd.to_datetime(df_HR_h['Fecha'].dt.strftime('%Y-%m-%d') + ' ' + df_HR_h['Hora'], errors='coerce')
                    df_HR_h.sort_values(by='TIMESTAMP', inplace=True)
                    df_HR_h['ESTACION'] = df_HR_h['Cuenca'].astype(str).str.zfill(3) + df_HR_h['Estación'].astype(str).str.zfill(3)
                    df_HR_h.rename(columns={'Humedad (%)': 'RH.perc.avg.1h.s1'}, inplace=True)
                    df_HR_h = df_HR_h[['TIMESTAMP', 'ESTACION', 'RH.perc.avg.1h.s1']]
                    
                    tiempo_inicial_HR_h = df_HR_h['TIMESTAMP'].min()
                    tiempo_final_HR_h = df_HR_h['TIMESTAMP'].max()
                    nombre_formateado_HR_h = f"{num_estacion}.{tiempo_inicial_HR_h.strftime('%Y%m%d-%H')}.{tiempo_final_HR_h.strftime('%Y%m%d-%H')}.HR.h.bd0.csv"
                    nombre_formateado_HR_h = ''.join([c for c in nombre_formateado_HR_h if c.isalnum() or c in ['-', '.', '_']]).rstrip()
                    archivo_salida_HR_h = os.path.join(directorio_salida_HR, nombre_formateado_HR_h)
                    
                    df_HR_h.replace({np.nan: '', pd.NA: '', ' ': ''}, inplace=True)
                    df_HR_h.to_csv(archivo_salida_HR_h, index=False, na_rep='', float_format='%.2f') 
                    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                    print(f"Se ha formateado exitosamente el archivo de la humedad relativa horaria crudo como: {nombre_formateado_HR_h}.")
                    print('')
                    datos_formateados_HR_h.append(df_HR_h)
                    archivo_HR_h = True

        except Exception as e:
            print(f"Error procesando el archivo '{nombre_original_HR_h}': {str(e)}")
    
    if not archivo_HR_h:
        print('\nAviso: No se encontró algún archivo de la humedad horaria.\n')

    return datos_formateados_HR_h

Formatear_HR_h()

def Formatear_HR_d():
    # Columnas originales esperadas en los datos de la humedad diaria
    columnas_originales_HR_d = ['Cuenca', 'Estación', 'Fecha', 'Humedad Max (%)', 'Fecha Hum Max', 'Hora Hum Max', 'Humedad Min  (%)', 'Fecha Hum Min', 'Hora Hum Min']
    # Directorios de entrada y salida
    datos_formateados_HR_d = []
    archivo_HR_d = False

    # Verifica si el directorio 'Humedad' existe, si no, créalo
    if not os.path.exists(directorio_salida_HR):
        os.makedirs(directorio_salida_HR)

    for nombre_original_HR_d in os.listdir(datos_crudos):
        archivo_crudo_HR = os.path.join(datos_crudos, nombre_original_HR_d)
        
        try:
            if nombre_original_HR_d.endswith(".xlsx"):
                df = pd.read_excel(archivo_crudo_HR, keep_default_na=False)  # Leer archivo Excel
                
                # Procesamiento de Datos de la humedad Diaria
                if all(col in df.columns for col in columnas_originales_HR_d) and "Humedad" in nombre_original_HR_d and "Diaria" in nombre_original_HR_d:
                    df_HR_d = df.copy()
                    
                    # Replace 'NULL' with -9 in 'Hora Temp Max' and 'Hora Temp Min' columns
                    df_HR_d['Hora Hum Max'] = df_HR_d['Hora Temp Max'].replace('NULL', -9).astype(int)
                    df_HR_d['Hora Hum Min'] = df_HR_d['Hora Temp Min'].replace('NULL', -9).astype(int)
                    
                    df_HR_d['Hora Hum Max'] = df_HR_d['Hora Hum Max'].apply(lambda x: f"{x:04d}" if x != 2400 else '0000')
                    df_HR_d['Hora Hum Min'] = df_HR_d['Hora Hum Min'].apply(lambda x: f"{x:04d}" if x != 2400 else '0000')
                    df_HR_d['Fecha'] = pd.to_datetime(df_HR_d['Fecha'], format='%d/%m/%Y', errors='coerce')
                    df_HR_d['TIMESTAMP'] = df_HR_d['Fecha'] + pd.to_timedelta('07:00:00')
                    # Ordenar DataFrame por TIMESTAMP

                    #df_HR_d['RH.CST.max.dm.s1.fecha'] = pd.to_datetime(df_HR_d['Fecha Hum Max'], format='%Y-%m-%d') + pd.to_timedelta(df_HR_d['Hora Hum Max'].astype(str).str.pad(4, fillchar='0').str[:2].astype(int), unit='h') + pd.to_timedelta(df_HR_d['Hora Hum Max'].astype(str).str.pad(4, fillchar='0').str[2:].astype(int), unit='m')
                    #df_HR_d['RH.CST.min.dm.s1.fecha'] = pd.to_datetime(df_HR_d['Fecha Hum Min'], format='%Y-%m-%d') + pd.to_timedelta(df_HR_d['Hora Hum Min'].astype(str).str.pad(4, fillchar='0').str[:2].astype(int), unit='h') + pd.to_timedelta(df_HR_d['Hora Hum Min'].astype(str).str.pad(4, fillchar='0').str[2:].astype(int), unit='m')
                    df_HR_d['RH.CST.max.dm.s1.fecha'] = pd.to_datetime(df_HR_d['Fecha Hum Max'], format='%d/%m/%Y') + pd.to_timedelta(df_HR_d['Hora Hum Max'].astype(str).str.pad(4, fillchar='0').str[:2].astype(int), unit='h') + pd.to_timedelta(df_HR_d['Hora Hum Max'].astype(str).str.pad(4, fillchar='0').str[2:].astype(int), unit='m')
                    df_HR_d['RH.CST.min.dm.s1.fecha'] = pd.to_datetime(df_HR_d['Fecha Hum Min'], format='%d/%m/%Y') + pd.to_timedelta(df_HR_d['Hora Hum Min'].astype(str).str.pad(4, fillchar='0').str[:2].astype(int), unit='h') + pd.to_timedelta(df_HR_d['Hora Hum Min'].astype(str).str.pad(4, fillchar='0').str[2:].astype(int), unit='m')
                    df_HR_d['ESTACION'] = df_HR_d['Cuenca'].astype(str).str.zfill(3) + df_HR_d['Estación'].astype(str).str.zfill(3)
                    df_HR_d.rename(columns={'Humedad Max (%)': 'RH.perc.max.dm.s1', 'Humedad Min  (%)': 'RH.perc.min.dm.s1', 'RH.CST.max.dm.s1.fecha': 'RH.CST.max.dm.s1', 'RH.CST.min.dm.s1.fecha': 'RH.CST.min.dm.s1'}, inplace=True)
                    df_HR_d = df_HR_d[['TIMESTAMP', 'ESTACION','RH.perc.max.dm.s1', 'RH.CST.max.dm.s1','RH.perc.min.dm.s1', 'RH.CST.min.dm.s1']]
            
                    tiempo_inicial_HR_d = df_HR_d['TIMESTAMP'].min()
                    tiempo_final_HR_d = df_HR_d['TIMESTAMP'].max()
                    nombre_formateado_HR_d = f"{num_estacion}.{tiempo_inicial_HR_d.strftime('%Y%m%d-%H')}.{tiempo_final_HR_d.strftime('%Y%m%d-%H')}.HR.d.bd0.csv"
                    nombre_formateado_HR_d = ''.join([c for c in nombre_formateado_HR_d if c.isalnum() or c in ['-', '.', '_']]).rstrip()
                    archivo_salida_HR_d = os.path.join(directorio_salida_HR, nombre_formateado_HR_d)
                    
                    df_HR_d.replace({np.nan: '', pd.NA: '', ' ': ''}, inplace=True)
                    df_HR_d.to_csv(archivo_salida_HR_d, index=False, na_rep='', float_format='%.2f')
                    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                    print(f"Se ha formateado exitosamente el archivo de la humedad relativa diaria crudo como: {nombre_formateado_HR_d}.")
                    print('')
                    datos_formateados_HR_d.append(df_HR_d)
                    archivo_HR_d = True             
 
        except Exception as e:
            print(f"Error procesando el archivo '{nombre_original_HR_d}': {str(e)}")
    
    if not archivo_HR_d:
        print('\nAviso: No se encontró algún archivo de la humedad diaria.\n')

    return datos_formateados_HR_d

Formatear_HR_d()
