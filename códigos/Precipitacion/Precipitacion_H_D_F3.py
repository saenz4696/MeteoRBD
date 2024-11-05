import pandas as pd
import os
import warnings

#-------------------------------Rutas generales

# Elimina UserWarnings de openpyxl
warnings.simplefilter('ignore', category=UserWarning)

datos_crudos = r'C:\\MeteoRBD.v1.0.0\\datos_rbd'

# Encuentra el archivo .xlsx en la datos_crudos que contiene 'Cuenca' y 'Estación' como columnas
ruta_archivo = next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Lluvia" in file and file.endswith(".xlsx")), None)

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
       
# Establece la ruta para los archivos de la lluvia según el número de estación obtenido del archivo Excel
ruta_analisis_Ll = f"C:\\MeteoRBD.v1.0.0\\revisión\\{num_estacion}-ema\\Precipitación"

# Combine the directory path and  define folder name
ruta_pruebas_a = os.path.join(ruta_analisis_Ll, "Pruebas_numericas_tiempo")

# Create the folder
os.makedirs(ruta_pruebas_a, exist_ok=True)

# Encuentra el archivo Ll.h.bd1.csv de la lluvia en la ruta de la estación
ruta_Ll_h_db1 = next((os.path.join(ruta_analisis_Ll, file) for file in os.listdir(ruta_analisis_Ll) if file.endswith(".csv") and 'Ll.h.bd1' in file), None)

# Encuentra el archivo Ll.d.bd1.csv de la lluvia en la ruta de la estación
ruta_Ll_d_db1 = next((os.path.join(ruta_analisis_Ll, file) for file in os.listdir(ruta_analisis_Ll) if file.endswith(".csv") and 'Ll.d.bd1' in file), None)

# Define una función para procesar datos de la lluvia
def Edita_tiempos_Ll_h():
    if ruta_Ll_h_db1:
        # Lee el archivo .csv y realiza operaciones de limpieza y corrección de timestamps
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_Ll_h_bd1 = pd.read_csv(ruta_Ll_h_db1)
            
            # Convertir TIMESTAMP a datetime objects
            df_Ll_h_bd1['TIMESTAMP'] = pd.to_datetime(df_Ll_h_bd1['TIMESTAMP'])
            
            # Eliminar filas completamente duplicadas en el DataFrame original
            df_Ll_h_bd1.drop_duplicates(inplace=True)
            
            # Identificar y reemplazar timestamps duplicados_Ll_h con una secuencia cronológica
            duplicados_Ll_h = df_Ll_h_bd1[df_Ll_h_bd1.duplicated(subset='TIMESTAMP', keep=False)]
            timestamps_unicos_Ll_h = duplicados_Ll_h['TIMESTAMP'].unique()
            
            # Corregir los timestamps duplicados_Ll_h
            for timestamp_Ll_h in timestamps_unicos_Ll_h:
                indices_Ll_h = duplicados_Ll_h[duplicados_Ll_h['TIMESTAMP'] == timestamp_Ll_h].index
                timestamps_nuevos_Ll_h = pd.date_range(start=timestamp_Ll_h, freq='H', periods=len(indices_Ll_h))
                df_Ll_h_bd1.loc[indices_Ll_h, 'TIMESTAMP'] = timestamps_nuevos_Ll_h
            
            # Ordenar el DataFrame por TIMESTAMP
            df_Ll_h_bd1 = df_Ll_h_bd1.sort_values('TIMESTAMP')
            
            # Rellenar o corregir los timestamps para tener un rango horario completo
            tiempo_inicial_Ll_h = df_Ll_h_bd1['TIMESTAMP'].min()
            tiempo_final_Ll_h = df_Ll_h_bd1['TIMESTAMP'].max()
            rango_deseado_Ll_h = pd.date_range(start=tiempo_inicial_Ll_h, end=tiempo_final_Ll_h, freq='H')

            df_Ll_h_bd1 = df_Ll_h_bd1.set_index('TIMESTAMP').reindex(rango_deseado_Ll_h).rename_axis('TIMESTAMP').reset_index()
            
            df_Ll_h_bd1['ESTACION'] = num_estacion
            
            # Guardar el archivo CSV depurado y corregido
            archivo_tiempo_rev_Ll_h = f"{num_estacion}.{tiempo_inicial_Ll_h.strftime('%Y%m%d-%H')}.{tiempo_final_Ll_h.strftime('%Y%m%d-%H')}.Ll.h.bd2.csv"
            df_Ll_h_bd1.to_csv(os.path.join(ruta_analisis_Ll, archivo_tiempo_rev_Ll_h), index=False, na_rep='NA')
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"Se ha analizado exitosamente el archivo de la lluvia horaria bd1 como: {archivo_tiempo_rev_Ll_h}")
            print('')
            return True
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la lluvia horaria bd1 para generar el archivo tipo bd2.")
        return False  
Edita_tiempos_Ll_h()
    
def Archivos_rev_tiempos_Ll_h():
    if ruta_Ll_h_db1:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_Ll_h_bd1 = pd.read_csv(ruta_Ll_h_db1)
            
            # Convierte los TIMESTAMPs a objetos datetime 
            df_Ll_h_bd1['TIMESTAMP'] = pd.to_datetime(df_Ll_h_bd1['TIMESTAMP'])
            
            #-------------------------------------------------- Obtener las fechas faltantes
            tiempo_inicial_Ll_h = df_Ll_h_bd1['TIMESTAMP'].min()
            tiempo_final_Ll_h = df_Ll_h_bd1['TIMESTAMP'].max()
            rango_deseado_Ll_h = pd.date_range(start=tiempo_inicial_Ll_h, end=tiempo_final_Ll_h, freq='H')
            fechas_faltantes_Ll_h = rango_deseado_Ll_h.difference(df_Ll_h_bd1['TIMESTAMP'])
            
            if fechas_faltantes_Ll_h.empty:
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print("No faltan fechas en el archivo de la lluvia horaria bd1.")
            else:
                # Guardar el archivo CSV con las fechas faltantes
                archivo_fechas_faltantes_Ll_h = "Fechas_faltantes_Ll_h.csv"
                archivo_timestamps_Ll_h = pd.DataFrame({'TIMESTAMP': fechas_faltantes_Ll_h})
                archivo_timestamps_Ll_h.to_csv(os.path.join(ruta_pruebas_a, archivo_fechas_faltantes_Ll_h), index=False)
                
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f"Se ha generado exitosamente el archivo de la lluvia horaria: {archivo_fechas_faltantes_Ll_h}.")
                print('')
            
            # Find duplicated timestamps
            timestamps_duplicados_Ll_h = df_Ll_h_bd1[df_Ll_h_bd1['TIMESTAMP'].duplicated(keep=False)]['TIMESTAMP'].unique()
            
            # Initialize lists to store data
            timestamps_Ll_h = []
            tesLl_deteccion_Ll_h = []
            cantidad_Ll_h = []
            fecha_reemplazo_Ll_h = []
            
            for timestamp in timestamps_duplicados_Ll_h:
                df_Ll_h_bd1_timestamp = df_Ll_h_bd1[df_Ll_h_bd1['TIMESTAMP'] == timestamp]
                # Check if the timestamp is only repeated in timestamps
                if len(df_Ll_h_bd1_timestamp.drop_duplicates()) == 1:
                    timestamps_Ll_h.append(timestamp)
                    tesLl_deteccion_Ll_h.append('fila_repetida')
                    cantidad_Ll_h.append(len(df_Ll_h_bd1_timestamp))
                    fecha_reemplazo_Ll_h.append('fecha_eliminada')
                else:
                    timestamps_Ll_h.extend([timestamp] * len(df_Ll_h_bd1_timestamp))
                    tesLl_deteccion_Ll_h.extend(['timestamp_repetido'] * len(df_Ll_h_bd1_timestamp))
                    cantidad_Ll_h.extend([len(df_Ll_h_bd1_timestamp)] * len(df_Ll_h_bd1_timestamp))
                    fecha_reemplazo_Ll_h.extend(['fecha_sustituida'] * len(df_Ll_h_bd1_timestamp))
            
            # Create DataFrame with the collected data
            fechas_repetidas_Ll_h = pd.DataFrame({
                'TIMESTAMP': timestamps_Ll_h,
                'TesLl_deteccion': tesLl_deteccion_Ll_h,
                'Repeticiones': cantidad_Ll_h,
                'Fecha_reemplazo': fecha_reemplazo_Ll_h
            })
            
            # Drop duplicate rows
            fechas_repetidas_Ll_h.drop_duplicates(inplace=True)
            
            if fechas_repetidas_Ll_h.empty:
                print('')
            else:
                # Write the DataFrame to a CSV file only if there are duplicated timestamps
                archivo_fechas_repetidas_Ll_h = 'Fechas_repetidas_Ll_h.csv'
                fechas_repetidas_Ll_h.to_csv(os.path.join(ruta_pruebas_a,  archivo_fechas_repetidas_Ll_h), index=False)
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f'Se ha generado exitosamente el archivo de la lluvia horario: {archivo_fechas_repetidas_Ll_h}.')
        
            return True
        
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print('No se encontró el archivo de la lluvia horaria bd1 para generar los archivos horarios de fechas faltantes y repetidas.')
Archivos_rev_tiempos_Ll_h()

def Edita_tiempos_Ll_d():
    if ruta_Ll_d_db1:
        # Lee el archivo .csv y realiza operaciones de limpieza y corrección de timestamps
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_Ll_d_db1 = pd.read_csv(ruta_Ll_d_db1)
            
            # Convertir TIMESTAMP a datetime objects
            df_Ll_d_db1['TIMESTAMP'] = pd.to_datetime(df_Ll_d_db1['TIMESTAMP'])
            
            # Eliminar filas completamente duplicadas en el DataFrame original
            df_Ll_d_db1.drop_duplicates(inplace=True)
            
            # Identificar y reemplazar timestamps duplicados_Ll_d con una secuencia cronológica
            duplicados_Ll_d = df_Ll_d_db1[df_Ll_d_db1.duplicated(subset='TIMESTAMP', keep=False)]
            timestamps_unicos_Ll_d = duplicados_Ll_d['TIMESTAMP'].unique()
            
            # Corregir los timestamps duplicados_Ll_d
            for timestamp_Ll_d in timestamps_unicos_Ll_d:
                indices_Ll_d = duplicados_Ll_d[duplicados_Ll_d['TIMESTAMP'] == timestamp_Ll_d].index
                timestamps_nuevos_Ll_d = pd.date_range(start=timestamp_Ll_d, freq='D', periods=len(indices_Ll_d))
                df_Ll_d_db1.loc[indices_Ll_d, 'TIMESTAMP'] = timestamps_nuevos_Ll_d
            
            # Ordenar el DataFrame por TIMESTAMP
            df_Ll_d_db1 = df_Ll_d_db1.sort_values('TIMESTAMP')
            
            # Rellenar o corregir los timestamps para tener un rango horario completo
            tiempo_inicial_Ll_d = df_Ll_d_db1['TIMESTAMP'].min()
            tiempo_final_Ll_d = df_Ll_d_db1['TIMESTAMP'].max()
            rango_deseado_Ll_d = pd.date_range(start=tiempo_inicial_Ll_d, end=tiempo_final_Ll_d, freq='D')

            df_Ll_d_db1 = df_Ll_d_db1.set_index('TIMESTAMP').reindex(rango_deseado_Ll_d).rename_axis('TIMESTAMP').reset_index()
            
            # Ajustar las horas de TIMESTAMP a las 07:00:00
            df_Ll_d_db1['TIMESTAMP'] = df_Ll_d_db1['TIMESTAMP'].dt.floor('D') + pd.DateOffset(hours=7)
        
            df_Ll_d_db1['ESTACION'] = num_estacion
            
            # Guardar el archivo CSV depurado y corregido
            archivo_tiempo_rev_Ll_d = f"{num_estacion}.{tiempo_inicial_Ll_d.strftime('%Y%m%d-%H')}.{tiempo_final_Ll_d.strftime('%Y%m%d-%H')}.Ll.d.bd2.csv"
            df_Ll_d_db1.to_csv(os.path.join(ruta_analisis_Ll,  archivo_tiempo_rev_Ll_d), index=False, na_rep='NA')
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"Se ha analizado exitosamente el archivo de la lluvia diara bd1 como: {archivo_tiempo_rev_Ll_d}")
            print('')
            return True
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la lluvia diaria bd1 para generar el archivo tipo bd2.")
        return False
Edita_tiempos_Ll_d()
    
def Archivos_rev_tiempos_Ll_d():
    if ruta_Ll_d_db1:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_Ll_d_bd1 = pd.read_csv(ruta_Ll_d_db1)
            
            # Convierte los TIMESTAMPs a objetos datetime 
            df_Ll_d_bd1['TIMESTAMP'] = pd.to_datetime(df_Ll_d_bd1['TIMESTAMP'])
            
            #-------------------------------------------------- Obtener las fechas faltantes
            fechas_faltantes_Ll_d = df_Ll_d_bd1['TIMESTAMP'].min()
            tiempo_final_Ll_d = df_Ll_d_bd1['TIMESTAMP'].max()
            rango_deseado_Ll_d = pd.date_range(start=fechas_faltantes_Ll_d, end=tiempo_final_Ll_d, freq='D')
            fechas_faltantes_Ll_d = rango_deseado_Ll_d.difference(df_Ll_d_bd1['TIMESTAMP'])
            # Ajustar las horas de TIMESTAMP a las 07:00:00
            df_Ll_d_bd1['TIMESTAMP'] = df_Ll_d_bd1['TIMESTAMP'].dt.floor('D') + pd.DateOffset(hours=7)
            
            if fechas_faltantes_Ll_d.empty:
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print("No faltan fechas en el archivo de la lluvia diaria bd1")
            else:
                # Guardar el archivo CSV con las fechas faltantes
                archivo_fechas_faltantes_Ll_d = "Fechas_faltantes_Ll_d.csv"
                archivo_timestamps_Ll_d = pd.DataFrame({'TIMESTAMP': fechas_faltantes_Ll_d})
                archivo_timestamps_Ll_d.to_csv(os.path.join(ruta_pruebas_a, archivo_fechas_faltantes_Ll_d), index=False)
                
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f"Se ha generado exitosamente el archivo de la lluvia horaria: {archivo_fechas_faltantes_Ll_d}.")
                print('')
            
            # Find duplicated timestamps
            timestamps_duplicados_Ll_d = df_Ll_d_bd1[df_Ll_d_bd1['TIMESTAMP'].duplicated(keep=False)]['TIMESTAMP'].unique()
            
            # Initialize lists to store data
            timestamps_Ll_d = []
            tesLl_deteccion_Ll_d = []
            cantidad_Ll_d = []
            fecha_reemplazo = []
            
            for timestamp in timestamps_duplicados_Ll_d:
                df_Ll_d_bd1_timestamp = df_Ll_d_bd1[df_Ll_d_bd1['TIMESTAMP'] == timestamp]
                # Check if the timestamp is only repeated in timestamps
                if len(df_Ll_d_bd1_timestamp.drop_duplicates()) == 1:
                    timestamps_Ll_d.append(timestamp)
                    tesLl_deteccion_Ll_d.append('fila_repetida')
                    cantidad_Ll_d.append(len(df_Ll_d_bd1_timestamp))
                    fecha_reemplazo.append('fecha_eliminada')
                else:
                    timestamps_Ll_d.extend([timestamp] * len(df_Ll_d_bd1_timestamp))
                    tesLl_deteccion_Ll_d.extend(['timestamp_repetido'] * len(df_Ll_d_bd1_timestamp))
                    cantidad_Ll_d.extend([len(df_Ll_d_bd1_timestamp)] * len(df_Ll_d_bd1_timestamp))
                    fecha_reemplazo.extend(['fecha_sustituida'] * len(df_Ll_d_bd1_timestamp))
            
            # Create DataFrame with the collected data
            fechas_repetidas_Ll_d = pd.DataFrame({
                'TIMESTAMP': timestamps_Ll_d,
                'TesLl_deteccion': tesLl_deteccion_Ll_d,
                'Repeticiones': cantidad_Ll_d,
                'Fecha_reemplazo': fecha_reemplazo
            })
            
            # Drop duplicate rows
            fechas_repetidas_Ll_d.drop_duplicates(inplace=True)
            
            if fechas_repetidas_Ll_d.empty:
                print('')
            else:
                # Write the DataFrame to a CSV file only if there are duplicated timestamps
                archivo_fechas_repetidas_Ll_d = 'Fechas_repetidas_Ll_d.csv'
                fechas_repetidas_Ll_d.to_csv(os.path.join(ruta_pruebas_a, archivo_fechas_repetidas_Ll_d), index=False)
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f'Se ha generado exitosamente el archivo de la lluvia horaria: {archivo_fechas_repetidas_Ll_d}.')
        
            return True
        
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la lluvia diaria bd1 para generar los archivos diarios de fechas faltante y repetidas.")
Archivos_rev_tiempos_Ll_d()



