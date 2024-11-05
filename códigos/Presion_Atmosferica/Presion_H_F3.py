import pandas as pd
import os
import warnings

#-------------------------------Rutas generales

# Elimina UserWarnings de openpyxl
warnings.simplefilter('ignore', category=UserWarning)

datos_crudos = r'C:\\MeteoRBD.v1.0.0\\datos_rbd'

# Encuentra el archivo .xlsx en la datos_crudos que contiene 'Cuenca' y 'Estación' como columnas
ruta_archivo = next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Presión" in file and file.endswith(".xlsx")), None)

if ruta_archivo:
    archivo_excel = pd.read_excel(ruta_archivo)
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
       
# Establece la ruta para los archivos de la presión atmosférica según el número de estación obtenido del archivo Excel
ruta_analisis_PA = f"C:\\MeteoRBD.v1.0.0\\revisión\\{num_estacion}-ema\\Presión Atmosférica"

# Combine the directory path and  define folder name
ruta_pruebas_a = os.path.join(ruta_analisis_PA, "Pruebas_numericas_tiempo")

# Create the folder
os.makedirs(ruta_pruebas_a, exist_ok=True)

# Encuentra el archivo PA.h.bd1.csv de la presión atmosférica en la ruta de la estación
ruta_PA_h_db1 = next((os.path.join(ruta_analisis_PA, file) for file in os.listdir(ruta_analisis_PA) if file.endswith(".csv") and 'PA.h.bd1' in file), None)

# Define una función para procesar datos de la presión atmosférica
def Edita_tiempos_PA_h():
    if ruta_PA_h_db1:
        # Lee el archivo .csv y realiza operaciones de limpieza y corrección de timestamps
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_PA_h_bd1 = pd.read_csv(ruta_PA_h_db1)
            
            # Convertir TIMESTAMP a datetime objects
            df_PA_h_bd1['TIMESTAMP'] = pd.to_datetime(df_PA_h_bd1['TIMESTAMP'])
            
            # Eliminar filas completamente duplicadas en el DataFrame original
            df_PA_h_bd1.drop_duplicates(inplace=True)
            
            # Identificar y reemplazar timestamps duplicados_PA_h con una secuencia cronológica
            duplicados_PA_h = df_PA_h_bd1[df_PA_h_bd1.duplicated(subset='TIMESTAMP', keep=False)]
            timestamps_unicos_PA_h = duplicados_PA_h['TIMESTAMP'].unique()
            
            # Corregir los timestamps duplicados_PA_h
            for timestamp_PA_h in timestamps_unicos_PA_h:
                indices_PA_h = duplicados_PA_h[duplicados_PA_h['TIMESTAMP'] == timestamp_PA_h].index
                timestamps_nuevos_PA_h = pd.date_range(start=timestamp_PA_h, freq='H', periods=len(indices_PA_h))
                df_PA_h_bd1.loc[indices_PA_h, 'TIMESTAMP'] = timestamps_nuevos_PA_h
            
            # Ordenar el DataFrame por TIMESTAMP
            df_PA_h_bd1 = df_PA_h_bd1.sort_values('TIMESTAMP')
            
            # Rellenar o corregir los timestamps para tener un rango horario completo
            tiempo_inicial_PA_h = df_PA_h_bd1['TIMESTAMP'].min()
            tiempo_final_PA_h = df_PA_h_bd1['TIMESTAMP'].max()
            rango_deseado_PA_h = pd.date_range(start=tiempo_inicial_PA_h, end=tiempo_final_PA_h, freq='H')

            df_PA_h_bd1 = df_PA_h_bd1.set_index('TIMESTAMP').reindex(rango_deseado_PA_h).rename_axis('TIMESTAMP').reset_index()
            
            df_PA_h_bd1['ESTACION'] = num_estacion
            
            # Guardar el archivo CSV depurado y corregido
            archivo_tiempo_rev_PA_h = f"{num_estacion}.{tiempo_inicial_PA_h.strftime('%Y%m%d-%H')}.{tiempo_final_PA_h.strftime('%Y%m%d-%H')}.PA.h.bd2.csv"
            df_PA_h_bd1.to_csv(os.path.join(ruta_analisis_PA, archivo_tiempo_rev_PA_h), index=False, na_rep='NA')
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"Se ha analizado exitosamente el archivo de la presión atmosférica horaria bd1 como: {archivo_tiempo_rev_PA_h}")
            print('')
            return True
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la presión atmosférica horaria bd1 para generar el archivo tipo bd2")
        return False  
Edita_tiempos_PA_h()
    
def Archivos_rev_tiempos_PA_h():
    if ruta_PA_h_db1:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_PA_h_bd1 = pd.read_csv(ruta_PA_h_db1)
            
            # Convierte los TIMESTAMPs a objetos datetime 
            df_PA_h_bd1['TIMESTAMP'] = pd.to_datetime(df_PA_h_bd1['TIMESTAMP'])
            
            #-------------------------------------------------- Obtener las fechas faltantes
            tiempo_inicial_PA_h = df_PA_h_bd1['TIMESTAMP'].min()
            tiempo_final_PA_h = df_PA_h_bd1['TIMESTAMP'].max()
            rango_deseado_PA_h = pd.date_range(start=tiempo_inicial_PA_h, end=tiempo_final_PA_h, freq='H')
            fechas_faltantes_PA_h = rango_deseado_PA_h.difference(df_PA_h_bd1['TIMESTAMP'])
            
            if fechas_faltantes_PA_h.empty:
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print("No faltan fechas en el archivo de la presión atmosférica horaria bd1.")
            else:
                # Guardar el archivo CSV con las fechas faltantes
                archivo_fechas_faltantes_PA_h = "Fechas_faltantes_PA_h.csv"
                archivo_timestamps_PA_h = pd.DataFrame({'TIMESTAMP': fechas_faltantes_PA_h})
                archivo_timestamps_PA_h.to_csv(os.path.join(ruta_pruebas_a, archivo_fechas_faltantes_PA_h), index=False)
                
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f"Se ha generado exitosamente el archivo de la presión atmosférica horaria: {archivo_fechas_faltantes_PA_h}.")
                print('')
            
            # Find duplicated timestamps
            timestamps_duplicados_PA_h = df_PA_h_bd1[df_PA_h_bd1['TIMESTAMP'].duplicated(keep=False)]['TIMESTAMP'].unique()
            
            # Initialize lists to store data
            timestamps_PA_h = []
            Test_deteccion_PA_h = []
            cantidad_PA_h = []
            fecha_reemplazo_PA_h = []
            
            for timestamp in timestamps_duplicados_PA_h:
                df_PA_h_bd1_timestamp = df_PA_h_bd1[df_PA_h_bd1['TIMESTAMP'] == timestamp]
                # Check if the timestamp is only repeated in timestamps
                if len(df_PA_h_bd1_timestamp.drop_duplicates()) == 1:
                    timestamps_PA_h.append(timestamp)
                    Test_deteccion_PA_h.append('fila_repetida')
                    cantidad_PA_h.append(len(df_PA_h_bd1_timestamp))
                    fecha_reemplazo_PA_h.append('fecha_eliminada')
                else:
                    timestamps_PA_h.extend([timestamp] * len(df_PA_h_bd1_timestamp))
                    Test_deteccion_PA_h.extend(['timestamp_repetido'] * len(df_PA_h_bd1_timestamp))
                    cantidad_PA_h.extend([len(df_PA_h_bd1_timestamp)] * len(df_PA_h_bd1_timestamp))
                    fecha_reemplazo_PA_h.extend(['fecha_sustituida'] * len(df_PA_h_bd1_timestamp))
            
            # Create DataFrame with the collected data
            fechas_repetidas_PA_h = pd.DataFrame({
                'TIMESTAMP': timestamps_PA_h,
                'Test_deteccion': Test_deteccion_PA_h,
                'Repeticiones': cantidad_PA_h,
                'Fecha_reemplazo': fecha_reemplazo_PA_h
            })
            
            # Drop duplicate rows
            fechas_repetidas_PA_h.drop_duplicates(inplace=True)
            
            if fechas_repetidas_PA_h.empty:
                print('')
            else:
                # Write the DataFrame to a CSV file only if there are duplicated timestamps
                archivo_fechas_repetidas_PA_h = 'Fechas_repetidas_PA_h.csv'
                fechas_repetidas_PA_h.to_csv(os.path.join(ruta_pruebas_a,  archivo_fechas_repetidas_PA_h), index=False)
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f'Se ha generado exitosamente el archivo de la presión atmosférica horario: {archivo_fechas_repetidas_PA_h}.')
        
            return True
        
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print('No se encontró el archivo de la presión atmosférica horaria bd1 para generar los archivos horarios de fechas faltantes y repetidas.')
Archivos_rev_tiempos_PA_h()




