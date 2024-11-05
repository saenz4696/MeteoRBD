import pandas as pd
import os
import warnings
import numpy as np

# Ignora los UserWarnings
warnings.simplefilter('ignore', category=UserWarning)

# Directorio de los datos crudos
datos_crudos = r'C:\MeteoRBD.v1.0.0\datos_rbd'

# Ruta del archivo Excel para extraer datos
archivo_crudo_R = next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Radiación" in file and file.endswith(".xlsx")), None)

if archivo_crudo_R:
    archivo_excel = pd.read_excel(archivo_crudo_R)
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
directorio_salida_R = os.path.join(directorio_base, 'Radiación Solar')
       
def Formatear_R_h():
    # Columnas originales esperadas en los datos de la Radiacion horaria
    columnas_originales_R_h = ['Cuenca', 'Estación', 'Fecha', 'Hora', 'Radiación', 'Brillo', 'Radiación Máxima', 'Radiación Mínima']
    # Directorios de entrada y salida
    datos_formateados_R_h = []
    archivo_R_h = False

    # Crea el directorio de salida si no existe
    if not os.path.exists(directorio_salida_R):
        os.makedirs(directorio_salida_R)

    for nombre_original_R_h in os.listdir(datos_crudos):
        archivo_crudo_R = os.path.join(datos_crudos, nombre_original_R_h)
        
        try:
            if nombre_original_R_h.endswith(".xlsx"):
                df = pd.read_excel(archivo_crudo_R, keep_default_na=False)
                
                if all(col in df.columns for col in columnas_originales_R_h) and "Radiación" in nombre_original_R_h and "Horaria" in nombre_original_R_h:
                    # Formateo de los datos de la Radiacion horaria
                    df_R_h = df.copy()
                    df_R_h['Hora'] = df_R_h['Hora'].apply(lambda x: f"{x:04d}" if x != 2400 else '0000')
                    df_R_h['Fecha'] = pd.to_datetime(df_R_h['Fecha'], format='%d/%m/%Y', errors='coerce')
                    df_R_h.loc[df_R_h['Hora'] == '0000', 'Fecha'] += pd.to_timedelta(1, unit='d')
                    df_R_h['TIMESTAMP'] = pd.to_datetime(df_R_h['Fecha'].dt.strftime('%Y-%m-%d') + ' ' + df_R_h['Hora'], errors='coerce')
                    df_R_h.sort_values(by='TIMESTAMP', inplace=True)
                    df_R_h['ESTACION'] = df_R_h['Cuenca'].astype(str).str.zfill(3) + df_R_h['Estación'].astype(str).str.zfill(3)
                    df_R_h.rename(columns={'Radiación': 'Rad.MJ_m2.tot.1h.s1', 'Brillo': 'Rad-int_sol.min_hour.tot.1h.s1', 'Radiación Máxima': 'Rad.kW_m2.max.1h.s1', 'Radiación Mínima': 'Rad.kW_m2.min.1h.s1'}, inplace=True)
                    df_R_h = df_R_h[['TIMESTAMP', 'ESTACION', 'Rad.MJ_m2.tot.1h.s1', 'Rad.kW_m2.max.1h.s1', 'Rad.kW_m2.min.1h.s1', 'Rad-int_sol.min_hour.tot.1h.s1']]
                    
                    tiempo_inicial_R_h = df_R_h['TIMESTAMP'].min()
                    tiempo_final_R_h = df_R_h['TIMESTAMP'].max()
                    nombre_formateado_R_h = f"{num_estacion}.{tiempo_inicial_R_h.strftime('%Y%m%d-%H')}.{tiempo_final_R_h.strftime('%Y%m%d-%H')}.R.h.bd0.csv"
                    nombre_formateado_R_h = ''.join([c for c in nombre_formateado_R_h if c.isalnum() or c in ['-', '.', '_']]).rstrip()
                    archivo_salida_R_h = os.path.join(directorio_salida_R, nombre_formateado_R_h)
                    
                    df_R_h.replace({np.nan: '', pd.NA: '', ' ': ''}, inplace=True)
                    df_R_h.to_csv(archivo_salida_R_h, index=False, na_rep='', float_format='%.2f') 
                    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                    print(f"Se ha formateado exitosamente el archivo de la radiación solar horaria crudo como: {nombre_formateado_R_h}.")
                    print('')
                    datos_formateados_R_h.append(df_R_h)
                    archivo_R_h = True

        except Exception as e:
            print(f"Error procesando el archivo '{nombre_original_R_h}': {str(e)}")
    
    if not archivo_R_h:
        print('\nAviso: No se encontró algún archivo de la radiación solar horaria.\n')

    return datos_formateados_R_h

Formatear_R_h()


