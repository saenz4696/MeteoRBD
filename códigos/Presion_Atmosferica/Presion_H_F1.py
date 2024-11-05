import pandas as pd
import os
import warnings
import numpy as np

# Ignora los UserWarnings
warnings.simplefilter('ignore', category=UserWarning)

# Directorio de los datos crudos
datos_crudos = r'C:\MeteoRBD.v1.0.0\datos_rbd'

# Ruta del archivo Excel para extraer datos
archivo_crudo_PA = next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Presión" in file and file.endswith(".xlsx")), None)

if archivo_crudo_PA:
    archivo_excel = pd.read_excel(archivo_crudo_PA)
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
directorio_salida_PA = os.path.join(directorio_base, 'Presión Atmosférica')
       
def Formatear_PA_h():
    # Columnas originales esperadas en los datos de la presión atmosférica horaria
    columnas_originales_PA_h = ['Cuenca', 'Estación', 'Fecha', 'Hora', 'Presión Aire']
    # Directorios de entrada y salida
    datos_formateados_PA_h = []
    archivo_PA_h = False

    # Crea el directorio de salida si no existe
    if not os.path.exists(directorio_salida_PA):
        os.makedirs(directorio_salida_PA)

    for nombre_original_PA_h in os.listdir(datos_crudos):
        archivo_crudo_PA = os.path.join(datos_crudos, nombre_original_PA_h)
        
        try:
            if nombre_original_PA_h.endswith(".xlsx"):
                df = pd.read_excel(archivo_crudo_PA, keep_default_na=False)
                
                if all(col in df.columns for col in columnas_originales_PA_h) and "Presión" in nombre_original_PA_h and "Horaria" in nombre_original_PA_h:
                    # Formateo de los datos de la presión atmosférica horaria
                    df_PA_h = df.copy()
                    df_PA_h['Hora'] = df_PA_h['Hora'].apply(lambda x: f"{x:04d}" if x != 2400 else '0000')
                    df_PA_h['Fecha'] = pd.to_datetime(df_PA_h['Fecha'], format='%d/%m/%Y', errors='coerce')
                    df_PA_h.loc[df_PA_h['Hora'] == '0000', 'Fecha'] += pd.to_timedelta(1, unit='d')
                    df_PA_h['TIMESTAMP'] = pd.to_datetime(df_PA_h['Fecha'].dt.strftime('%Y-%m-%d') + ' ' + df_PA_h['Hora'], errors='coerce')
                    df_PA_h.sort_values(by='TIMESTAMP', inplace=True)
                    df_PA_h['ESTACION'] = df_PA_h['Cuenca'].astype(str).str.zfill(3) + df_PA_h['Estación'].astype(str).str.zfill(3)
                    df_PA_h.rename(columns={'Presión Aire': 'Press.mbar.avg.1h.s1'}, inplace=True)
                    df_PA_h = df_PA_h[['TIMESTAMP', 'ESTACION', 'Press.mbar.avg.1h.s1']]
                    
                    tiempo_inicial_PA_h = df_PA_h['TIMESTAMP'].min()
                    tiempo_final_PA_h = df_PA_h['TIMESTAMP'].max()
                    nombre_formateado_PA_h = f"{num_estacion}.{tiempo_inicial_PA_h.strftime('%Y%m%d-%H')}.{tiempo_final_PA_h.strftime('%Y%m%d-%H')}.PA.h.bd0.csv"
                    nombre_formateado_PA_h = ''.join([c for c in nombre_formateado_PA_h if c.isalnum() or c in ['-', '.', '_']]).rstrip()
                    archivo_salida_PA_h = os.path.join(directorio_salida_PA, nombre_formateado_PA_h)
                    
                    df_PA_h.replace({np.nan: '', pd.NA: '', ' ': ''}, inplace=True)
                    df_PA_h.to_csv(archivo_salida_PA_h, index=False, na_rep='', float_format='%.2f') 
                    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                    print(f"Se ha formateado exitosamente el archivo de la presión atmosférica horaria crudo como: {nombre_formateado_PA_h}.")
                    print('')
                    datos_formateados_PA_h.append(df_PA_h)
                    archivo_PA_h = True

        except Exception as e:
            print(f"Error procesando el archivo '{nombre_original_PA_h}': {str(e)}")
    
    if not archivo_PA_h:
        print('\nAviso: No se encontró algún archivo de la presión atmosférica horaria.\n')

    return datos_formateados_PA_h

Formatear_PA_h()

