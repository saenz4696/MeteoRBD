import pandas as pd
import os
import warnings
import numpy as np

# Ignora los UserWarnings
warnings.simplefilter('ignore', category=UserWarning)

# Directorio de los datos crudos
datos_crudos = r'C:\MeteoRBD.v1.0.0\datos_rbd'

# Ruta del archivo Excel para extraer datos
archivo_crudo_Ll = next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Lluvia" in file and file.endswith(".xlsx")), None)

if archivo_crudo_Ll:
    archivo_excel = pd.read_excel(archivo_crudo_Ll)
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
directorio_salida_Ll = os.path.join(directorio_base, 'Precipitación')
       
def Formatear_Ll_h():
    # Columnas originales esperadas en los datos de la Lluvia horaria
    columnas_originales_Ll_h = ['Cuenca', 'Estación', 'Fecha', 'Hora', 'Lluvia (mm)']
    # Directorios de entrada y salida
    datos_formateados_Ll_h = []
    archivo_Ll_h = False

    # Crea el directorio de salida si no existe
    if not os.path.exists(directorio_salida_Ll):
        os.makedirs(directorio_salida_Ll)

    for nombre_original_Ll_h in os.listdir(datos_crudos):
        archivo_crudo_Ll = os.path.join(datos_crudos, nombre_original_Ll_h)
        
        try:
            if nombre_original_Ll_h.endswith(".xlsx"):
                df = pd.read_excel(archivo_crudo_Ll, keep_default_na=False)
                
                if all(col in df.columns for col in columnas_originales_Ll_h) and "Lluvia" in nombre_original_Ll_h and "Horaria" in nombre_original_Ll_h:
                    # Formateo de los datos de la Lluvia horaria
                    df_Ll_h = df.copy()
                    df_Ll_h['Hora'] = df_Ll_h['Hora'].apply(lambda x: f"{x:04d}" if x != 2400 else '0000')
                    df_Ll_h['Fecha'] = pd.to_datetime(df_Ll_h['Fecha'], format='%d/%m/%Y', errors='coerce')
                    df_Ll_h.loc[df_Ll_h['Hora'] == '0000', 'Fecha'] += pd.to_timedelta(1, unit='d')
                    df_Ll_h['TIMESTAMP'] = pd.to_datetime(df_Ll_h['Fecha'].dt.strftime('%Y-%m-%d') + ' ' + df_Ll_h['Hora'], errors='coerce')
                    df_Ll_h.sort_values(by='TIMESTAMP', inplace=True)
                    df_Ll_h['ESTACION'] = df_Ll_h['Cuenca'].astype(str).str.zfill(3) + df_Ll_h['Estación'].astype(str).str.zfill(3)
                    df_Ll_h.rename(columns={'Lluvia (mm)': 'Precip.mm.tot.1h.s1'}, inplace=True)
                    df_Ll_h = df_Ll_h[['TIMESTAMP', 'ESTACION', 'Precip.mm.tot.1h.s1']]
                    
                    tiempo_inicial_Ll_h = df_Ll_h['TIMESTAMP'].min()
                    tiempo_final_Ll_h = df_Ll_h['TIMESTAMP'].max()
                    nombre_formateado_Ll_h = f"{num_estacion}.{tiempo_inicial_Ll_h.strftime('%Y%m%d-%H')}.{tiempo_final_Ll_h.strftime('%Y%m%d-%H')}.Ll.h.bd0.csv"
                    nombre_formateado_Ll_h = ''.join([c for c in nombre_formateado_Ll_h if c.isalnum() or c in ['-', '.', '_']]).rstrip()
                    archivo_salida_Ll_h = os.path.join(directorio_salida_Ll, nombre_formateado_Ll_h)
                    
                    df_Ll_h.replace({np.nan: '', pd.NA: '', ' ': ''}, inplace=True)
                    df_Ll_h.to_csv(archivo_salida_Ll_h, index=False, na_rep='', float_format='%.2f') 
                    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                    print(f"Se ha formateado exitosamente el archivo de la lluvia horaria crudo como: {nombre_formateado_Ll_h}.")
                    print('')
                    datos_formateados_Ll_h.append(df_Ll_h)
                    archivo_Ll_h = True

        except Exception as e:
            print(f"Error procesando el archivo '{nombre_original_Ll_h}': {str(e)}")
    
    if not archivo_Ll_h:
        print('\nAviso: No se encontró algún archivo de la Lluvia horaria.\n')

    return datos_formateados_Ll_h

Formatear_Ll_h()

def Formatear_Ll_d():
    # Columnas originales esperadas en los datos de la Lluvia diaria
    columnas_originales_Ll_d = ['Cuenca', 'Estación', 'Fecha', 'Total Lluvia (mm)', 'Acum 5m  (mm)', 'Acum 10m  (mm)', 'Acum 15m  (mm)', 'Acum 30m  (mm)']
    # Directorios de entrada y salida
    datos_formateados_Ll_d = []
    archivo_Ll_d = False

    # Verifica si el directorio 'Lluvia' existe, si no, créalo
    if not os.path.exists(directorio_salida_Ll):
        os.makedirs(directorio_salida_Ll)

    for nombre_original_Ll_d in os.listdir(datos_crudos):
        archivo_crudo_Ll = os.path.join(datos_crudos, nombre_original_Ll_d)
        
        try:
            if nombre_original_Ll_d.endswith(".xlsx"):
                df = pd.read_excel(archivo_crudo_Ll, keep_default_na=False)  # Leer archivo Excel
                
                # Procesamiento de Datos de la Lluvia Diaria
                if all(col in df.columns for col in columnas_originales_Ll_d) and "Lluvia" in nombre_original_Ll_d and "diaria" in nombre_original_Ll_d:
                    df_Ll_d = df.copy()
                    df_Ll_d['Fecha'] = pd.to_datetime(df_Ll_d['Fecha'], format='%d/%m/%Y', errors='coerce')
                    df_Ll_d['TIMESTAMP'] = df_Ll_d['Fecha'] + pd.to_timedelta('07:00:00')
                    # Ordenar DataFrame por TIMESTAMP
                    
                    df_Ll_d['ESTACION'] = df_Ll_d['Cuenca'].astype(str).str.zfill(3) + df_Ll_d['Estación'].astype(str).str.zfill(3)
                    df_Ll_d.rename(columns={'Total Lluvia (mm)': 'Precip.mm.tot.dm.s1', 'Acum 5m  (mm)': 'Precip-acum5.mm_h.max.dm.s1', 'Acum 10m  (mm)': 'Precip-acum10.mm_h.max.dm.s1', 'Acum 15m  (mm)': 'Precip-acum15.mm_h.max.dm.s1', 'Acum 30m  (mm)': 'Precip-acum30.mm_h.max.dm.s1'}, inplace=True)
                    df_Ll_d = df_Ll_d[['TIMESTAMP', 'ESTACION','Precip.mm.tot.dm.s1', 'Precip-acum5.mm_h.max.dm.s1','Precip-acum10.mm_h.max.dm.s1', 'Precip-acum15.mm_h.max.dm.s1', 'Precip-acum30.mm_h.max.dm.s1']]
            
                    tiempo_inicial_Ll_d = df_Ll_d['TIMESTAMP'].min()
                    tiempo_final_Ll_d = df_Ll_d['TIMESTAMP'].max()
                    nombre_formateado_Ll_d = f"{num_estacion}.{tiempo_inicial_Ll_d.strftime('%Y%m%d-%H')}.{tiempo_final_Ll_d.strftime('%Y%m%d-%H')}.Ll.d.bd0.csv"
                    nombre_formateado_Ll_d = ''.join([c for c in nombre_formateado_Ll_d if c.isalnum() or c in ['-', '.', '_']]).rstrip()
                    archivo_salida_Ll_d = os.path.join(directorio_salida_Ll, nombre_formateado_Ll_d)
                    
                    df_Ll_d.replace({np.nan: '', pd.NA: '', ' ': ''}, inplace=True)
                    df_Ll_d.to_csv(archivo_salida_Ll_d, index=False, na_rep='', float_format='%.2f')
                    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                    print(f"Se ha formateado exitosamente el archivo de la lluvia diaria crudo como: {nombre_formateado_Ll_d}.")
                    print('')
                    datos_formateados_Ll_d.append(df_Ll_d)
                    archivo_Ll_d = True             
 
        except Exception as e:
            print(f"Error procesando el archivo '{nombre_original_Ll_d}': {str(e)}")
    
    if not archivo_Ll_d:
        print('\nAviso: No se encontró algún archivo de la lluvia diaria.\n')

    return datos_formateados_Ll_d

Formatear_Ll_d()
