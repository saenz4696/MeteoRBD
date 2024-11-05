import pandas as pd
import os
import warnings
import numpy as np

# Ignora los UserWarnings
warnings.simplefilter('ignore', category=UserWarning)

# Directorio de los datos crudos
datos_crudos = r'C:\MeteoRBD.v1.0.0\datos_rbd'

# Ruta del archivo Excel para extraer datos
archivo_crudo_V = next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Viento" in file and file.endswith(".xlsx")), None)

if archivo_crudo_V:
    archivo_excel = pd.read_excel(archivo_crudo_V)
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
directorio_salida_V = os.path.join(directorio_base, 'Viento')
       
def Formatear_V_h():
    # Columnas originales esperadas en los datos de la Viento horaria
    columnas_originales_V_h = ['Cuenca', 'Estación', 'Fecha', 'Hora', 'Dirección', 'Casos (°)',	'Promedio Escalar (m/s)',	'Magnitud Vector',	'Dirección Vector',	'DS Dirección']
    # Directorios de entrada y salida
    datos_formateados_V_h = []
    archivo_V_h = False

    # Crea el directorio de salida si no existe
    if not os.path.exists(directorio_salida_V):
        os.makedirs(directorio_salida_V)

    for nombre_original_V_h in os.listdir(datos_crudos):
        archivo_crudo_V = os.path.join(datos_crudos, nombre_original_V_h)
        
        try:
            if nombre_original_V_h.endswith(".xlsx"):
                df = pd.read_excel(archivo_crudo_V, keep_default_na=False)
                
                if all(col in df.columns for col in columnas_originales_V_h) and "Viento" in nombre_original_V_h and "Horaria" in nombre_original_V_h:
                    # Formateo de los datos de la Viento horaria
                    df_V_h = df.copy()
                    df_V_h['Hora'] = df_V_h['Hora'].apply(lambda x: f"{x:04d}" if x != 2400 else '0000')
                    df_V_h['Fecha'] = pd.to_datetime(df_V_h['Fecha'], format='%d/%m/%Y', errors='coerce')
                    df_V_h.loc[df_V_h['Hora'] == '0000', 'Fecha'] += pd.to_timedelta(1, unit='d')
                    df_V_h['TIMESTAMP'] = pd.to_datetime(df_V_h['Fecha'].dt.strftime('%Y-%m-%d') + ' ' + df_V_h['Hora'], errors='coerce')
                    df_V_h.sort_values(by='TIMESTAMP', inplace=True)
                    df_V_h['ESTACION'] = df_V_h['Cuenca'].astype(str).str.zfill(3) + df_V_h['Estación'].astype(str).str.zfill(3)
                    df_V_h.rename(columns={'Dirección': 'Wind-dir_pred', 'Casos (°)': 'Wind-freq.fs.tot.1h.s1','Promedio Escalar (m/s)': 'Wind-scalar.m_s.avg.1h.s1','Magnitud Vector': 'Wind-vector.m_s.wvc.1h.s1','Dirección Vector': 'Wind-dir.deg.wvc.1h.s1','DS Dirección': 'Wind-dir.sd.deg.std.1h.s1'}, inplace=True)
                    df_V_h = df_V_h[['TIMESTAMP', 'ESTACION', 'Wind-dir_pred', 'Wind-freq.fs.tot.1h.s1','Wind-scalar.m_s.avg.1h.s1','Wind-vector.m_s.wvc.1h.s1','Wind-dir.deg.wvc.1h.s1','Wind-dir.sd.deg.std.1h.s1']]
                    
                    tiempo_inicial_V_h = df_V_h['TIMESTAMP'].min()
                    tiempo_final_V_h = df_V_h['TIMESTAMP'].max()
                    nombre_formateado_V_h = f"{num_estacion}.{tiempo_inicial_V_h.strftime('%Y%m%d-%H')}.{tiempo_final_V_h.strftime('%Y%m%d-%H')}.V.h.bd0.csv"
                    nombre_formateado_V_h = ''.join([c for c in nombre_formateado_V_h if c.isalnum() or c in ['-', '.', '_']]).rstrip()
                    archivo_salida_V_h = os.path.join(directorio_salida_V, nombre_formateado_V_h)
                    
                    df_V_h.replace({np.nan: '', pd.NA: '', ' ': ''}, inplace=True)
                    df_V_h.to_csv(archivo_salida_V_h, index=False, na_rep='', float_format='%.2f') 
                    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                    print(f"Se ha formateado exitosamente el archivo del viento horario crudo como: {nombre_formateado_V_h}.")
                    print('')
                    datos_formateados_V_h.append(df_V_h)
                    archivo_V_h = True

        except Exception as e:
            print(f"Error procesando el archivo '{nombre_original_V_h}': {str(e)}")
    
    if not archivo_V_h:
        print('\nAviso: No se encontró algún archivo del viento horario.\n')

    return datos_formateados_V_h

Formatear_V_h()

def Formatear_V_d():
    # Columnas originales esperadas en los datos de la Viento diaria
    columnas_originales_V_d = ['Cuenca', 'Estación', 'Fecha', 'Velocidad Maxima (m/s)',	'Fecha Vel Max', 'Hora Vel Max']
    # Directorios de entrada y salida
    datos_formateados_V_d = []
    archivo_V_d = False

    # Verifica si el directorio 'Viento' existe, si no, créalo
    if not os.path.exists(directorio_salida_V):
        os.makedirs(directorio_salida_V)

    for nombre_original_V_d in os.listdir(datos_crudos):
        archivo_crudo_V = os.path.join(datos_crudos, nombre_original_V_d)
        
        try:
            if nombre_original_V_d.endswith(".xlsx"):
                df = pd.read_excel(archivo_crudo_V, keep_default_na=False)  # Leer archivo Excel
                
                # Procesamiento de Datos de la Viento Diaria
                if all(col in df.columns for col in columnas_originales_V_d) and "Viento" in nombre_original_V_d and "Diaria" in nombre_original_V_d:
                    df_V_d = df.copy()
                    
                    # Replace 'NULL' with -9 in 'Hora Temp Max' and 'Hora Temp Min' columns
                    df_V_d['Hora Vel Max'] = df_V_d['Hora Vel Max'].replace('NULL', -9).astype(int)
                    
                    df_V_d['Hora Vel Max'] = df_V_d['Hora Vel Max'].apply(lambda x: f"{x:04d}" if x != 2400 else '0000')
                    df_V_d['Fecha'] = pd.to_datetime(df_V_d['Fecha'], format='%d/%m/%Y', errors='coerce')
                    df_V_d['TIMESTAMP'] = df_V_d['Fecha'] + pd.to_timedelta('07:00:00')
                    # Ordenar DataFrame por TIMESTAMP

             
                    df_V_d['Vel.CST.max.dm.s1.fecha'] = pd.to_datetime(df_V_d['Fecha Vel Max'], format='%d/%m/%Y') + pd.to_timedelta(df_V_d['Hora Vel Max'].astype(str).str.pad(4, fillchar='0').str[:2].astype(int), unit='h') + pd.to_timedelta(df_V_d['Hora Vel Max'].astype(str).str.pad(4, fillchar='0').str[2:].astype(int), unit='m')
                 
                    df_V_d['ESTACION'] = df_V_d['Cuenca'].astype(str).str.zfill(3) + df_V_d['Estación'].astype(str).str.zfill(3)
                    df_V_d.rename(columns={'Velocidad Maxima (m/s)': 'Wind.m_s.max.dm.s1',	'Vel.CST.max.dm.s1.fecha': 'Wind.CST.max.dm.s1'}, inplace=True)
                    df_V_d = df_V_d[['TIMESTAMP', 'ESTACION','Wind.m_s.max.dm.s1', 'Wind.CST.max.dm.s1']]
            
                    tiempo_inicial_V_d = df_V_d['TIMESTAMP'].min()
                    tiempo_final_V_d = df_V_d['TIMESTAMP'].max()
                    nombre_formateado_V_d = f"{num_estacion}.{tiempo_inicial_V_d.strftime('%Y%m%d-%H')}.{tiempo_final_V_d.strftime('%Y%m%d-%H')}.V.d.bd0.csv"
                    nombre_formateado_V_d = ''.join([c for c in nombre_formateado_V_d if c.isalnum() or c in ['-', '.', '_']]).rstrip()
                    archivo_salida_V_d = os.path.join(directorio_salida_V, nombre_formateado_V_d)
                    
                    df_V_d.replace({np.nan: '', pd.NA: '', ' ': ''}, inplace=True)
                    df_V_d.to_csv(archivo_salida_V_d, index=False, na_rep='', float_format='%.2f')
                    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                    print(f"Se ha formateado exitosamente el archivo del viento diario crudo como: {nombre_formateado_V_d}.")
                    print('')
                    datos_formateados_V_d.append(df_V_d)
                    archivo_V_d = True             
 
        except Exception as e:
            print(f"Error procesando el archivo '{nombre_original_V_d}': {str(e)}")
    
    if not archivo_V_d:
        print('\nAviso: No se encontró algún archivo del viento diario.\n')

    return datos_formateados_V_d

Formatear_V_d()
