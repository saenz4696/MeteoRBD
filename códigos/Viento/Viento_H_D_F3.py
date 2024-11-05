import pandas as pd
import os
import warnings

#-------------------------------Rutas generales

# Elimina UserWarnings de openpyxl
warnings.simplefilter('ignore', category=UserWarning)

datos_crudos = r'C:\\MeteoRBD.v1.0.0\\datos_rbd'

# Encuentra el archivo .xlsx en la datos_crudos que contiene 'Cuenca' y 'Estación' como columnas
ruta_archivo = next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Viento" in file and file.endswith(".xlsx")), None)

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
       
# Establece la ruta para los archivos del viento según el número de estación obtenido del archivo Excel
ruta_analisis_V = f"C:\\MeteoRBD.v1.0.0\\revisión\\{num_estacion}-ema\\Viento"

# Combine the directory path and  define folder name
ruta_pruebas_a = os.path.join(ruta_analisis_V, "Pruebas_numericas_tiempo")

# Create the folder
os.makedirs(ruta_pruebas_a, exist_ok=True)

# Encuentra el archivo V.h.bd1.csv del viento en la ruta de la estación
ruta_V_h_bd1 = next((os.path.join(ruta_analisis_V, file) for file in os.listdir(ruta_analisis_V) if file.endswith(".csv") and 'V.h.bd1' in file), None)

# Encuentra el archivo V.d.bd1.csv del viento en la ruta de la estación
ruta_V_d_bd1 = next((os.path.join(ruta_analisis_V, file) for file in os.listdir(ruta_analisis_V) if file.endswith(".csv") and 'V.d.bd1' in file), None)

# Define una función para procesar datos del viento
def Edita_tiempos_V_h():
    if ruta_V_h_bd1:
        # Lee el archivo .csv y realiza operaciones de limpieza y corrección de timestamps
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_V_h_bd1 = pd.read_csv(ruta_V_h_bd1)
            
            # Convertir TIMESTAMP a datetime objects
            df_V_h_bd1['TIMESTAMP'] = pd.to_datetime(df_V_h_bd1['TIMESTAMP'])
            
            # Eliminar filas completamente duplicadas en el DataFrame original
            df_V_h_bd1.drop_duplicates(inplace=True)
            
            # Identificar y reemplazar timestamps duplicados_V_h con una secuencia cronológica
            duplicados_V_h = df_V_h_bd1[df_V_h_bd1.duplicated(subset='TIMESTAMP', keep=False)]
            timestamps_unicos_V_h = duplicados_V_h['TIMESTAMP'].unique()
            
            # Corregir los timestamps duplicados_V_h
            for timestamp_V_h in timestamps_unicos_V_h:
                indices_V_h = duplicados_V_h[duplicados_V_h['TIMESTAMP'] == timestamp_V_h].index
                timestamps_nuevos_V_h = pd.date_range(start=timestamp_V_h, freq='H', periods=len(indices_V_h))
                df_V_h_bd1.loc[indices_V_h, 'TIMESTAMP'] = timestamps_nuevos_V_h
            
            # Ordenar el DataFrame por TIMESTAMP
            df_V_h_bd1 = df_V_h_bd1.sort_values('TIMESTAMP')
            
            # Rellenar o corregir los timestamps para tener un rango horario completo
            tiempo_inicial_V_h = df_V_h_bd1['TIMESTAMP'].min()
            tiempo_final_V_h = df_V_h_bd1['TIMESTAMP'].max()
            rango_deseado_V_h = pd.date_range(start=tiempo_inicial_V_h, end=tiempo_final_V_h, freq='H')

            df_V_h_bd1 = df_V_h_bd1.set_index('TIMESTAMP').reindex(rango_deseado_V_h).rename_axis('TIMESTAMP').reset_index()
            
            df_V_h_bd1['ESTACION'] = num_estacion
            
            # Guardar el archivo CSV depurado y corregido
            archivo_tiempo_rev_V_h = f"{num_estacion}.{tiempo_inicial_V_h.strftime('%Y%m%d-%H')}.{tiempo_final_V_h.strftime('%Y%m%d-%H')}.V.h.bd2.csv"
            df_V_h_bd1.to_csv(os.path.join(ruta_analisis_V, archivo_tiempo_rev_V_h), index=False, na_rep='NA')
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"Se ha analizado exitosamente el archivo del viento horario bd1 como: {archivo_tiempo_rev_V_h}")
            print('')
            return True
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo del viento horario bd1 para generar el archivo tipo bd2")
        return False  
Edita_tiempos_V_h()
    
def Archivos_rev_tiempos_V_h():
    if ruta_V_h_bd1:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_V_h_bd1 = pd.read_csv(ruta_V_h_bd1)
            
            # Convierte los TIMESTAMPs a objetos datetime 
            df_V_h_bd1['TIMESTAMP'] = pd.to_datetime(df_V_h_bd1['TIMESTAMP'])
            
            #-------------------------------------------------- Obtener las fechas faltantes
            tiempo_inicial_V_h = df_V_h_bd1['TIMESTAMP'].min()
            tiempo_final_V_h = df_V_h_bd1['TIMESTAMP'].max()
            rango_deseado_V_h = pd.date_range(start=tiempo_inicial_V_h, end=tiempo_final_V_h, freq='H')
            fechas_faltantes_V_h = rango_deseado_V_h.difference(df_V_h_bd1['TIMESTAMP'])
            
            if fechas_faltantes_V_h.empty:
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print("No faltan fechas en el archivo del viento horario bd1.")
            else:
                # Guardar el archivo CSV con las fechas faltantes
                archivo_fechas_faltantes_V_h = "Fechas_faltantes_V_h.csv"
                archivo_timestamps_V_h = pd.DataFrame({'TIMESTAMP': fechas_faltantes_V_h})
                archivo_timestamps_V_h.to_csv(os.path.join(ruta_pruebas_a, archivo_fechas_faltantes_V_h), index=False)
                
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f"Se ha generado exitosamente el archivo del viento horario: {archivo_fechas_faltantes_V_h}.")
                print('')
            
            # Find duplicated timestamps
            timestamps_duplicados_V_h = df_V_h_bd1[df_V_h_bd1['TIMESTAMP'].duplicated(keep=False)]['TIMESTAMP'].unique()
            
            # Initialize lists to store data
            timestamps_V_h = []
            Test_deteccion_V_h = []
            cantidad_V_h = []
            fecha_reemplazo_V_h = []
            
            for timestamp in timestamps_duplicados_V_h:
                df_V_h_bd1_timestamp = df_V_h_bd1[df_V_h_bd1['TIMESTAMP'] == timestamp]
                # Check if the timestamp is only repeated in timestamps
                if len(df_V_h_bd1_timestamp.drop_duplicates()) == 1:
                    timestamps_V_h.append(timestamp)
                    Test_deteccion_V_h.append('fila_repetida')
                    cantidad_V_h.append(len(df_V_h_bd1_timestamp))
                    fecha_reemplazo_V_h.append('fecha_eliminada')
                else:
                    timestamps_V_h.extend([timestamp] * len(df_V_h_bd1_timestamp))
                    Test_deteccion_V_h.extend(['timestamp_repetido'] * len(df_V_h_bd1_timestamp))
                    cantidad_V_h.extend([len(df_V_h_bd1_timestamp)] * len(df_V_h_bd1_timestamp))
                    fecha_reemplazo_V_h.extend(['fecha_sustituida'] * len(df_V_h_bd1_timestamp))
            
            # Create DataFrame with the collected data
            fechas_repetidas_V_h = pd.DataFrame({
                'TIMESTAMP': timestamps_V_h,
                'Test_deteccion': Test_deteccion_V_h,
                'Repeticiones': cantidad_V_h,
                'Fecha_reemplazo': fecha_reemplazo_V_h
            })
            
            # Drop duplicate rows
            fechas_repetidas_V_h.drop_duplicates(inplace=True)
            
            if fechas_repetidas_V_h.empty:
                print("")
            else:
                # Write the DataFrame to a CSV file only if there are duplicated timestamps
                archivo_fechas_repetidas_V_h = 'Fechas_repetidas_V_h.csv'
                fechas_repetidas_V_h.to_csv(os.path.join(ruta_pruebas_a,  archivo_fechas_repetidas_V_h), index=False)
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f'Se ha generado exitosamente el archivo del viento horario: {archivo_fechas_repetidas_V_h}.')
        
            return True
        
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print('No se encontró el archivo del viento horario bd1 para generar los archivos horarios de fechas faltantes y repetidas.')
Archivos_rev_tiempos_V_h()

def Edita_tiempos_V_d():
    if ruta_V_d_bd1:
        # Lee el archivo .csv y realiza operaciones de limpieza y corrección de timestamps
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_V_d_bd1 = pd.read_csv(ruta_V_d_bd1)
            
            # Convertir TIMESTAMP a datetime objects
            df_V_d_bd1['TIMESTAMP'] = pd.to_datetime(df_V_d_bd1['TIMESTAMP'])
            
            # Eliminar filas completamente duplicadas en el DataFrame original
            df_V_d_bd1.drop_duplicates(inplace=True)
            
            # Identificar y reemplazar timestamps duplicados_V_d con una secuencia cronológica
            duplicados_V_d = df_V_d_bd1[df_V_d_bd1.duplicated(subset='TIMESTAMP', keep=False)]
            timestamps_unicos_V_d = duplicados_V_d['TIMESTAMP'].unique()
            
            # Corregir los timestamps duplicados_V_d
            for timestamp_V_d in timestamps_unicos_V_d:
                indices_V_d = duplicados_V_d[duplicados_V_d['TIMESTAMP'] == timestamp_V_d].index
                timestamps_nuevos_V_d = pd.date_range(start=timestamp_V_d, freq='D', periods=len(indices_V_d))
                df_V_d_bd1.loc[indices_V_d, 'TIMESTAMP'] = timestamps_nuevos_V_d
            
            # Ordenar el DataFrame por TIMESTAMP
            df_V_d_bd1 = df_V_d_bd1.sort_values('TIMESTAMP')
            
            # Rellenar o corregir los timestamps para tener un rango horario completo
            tiempo_inicial_V_d = df_V_d_bd1['TIMESTAMP'].min()
            tiempo_final_V_d = df_V_d_bd1['TIMESTAMP'].max()
            rango_deseado_V_d = pd.date_range(start=tiempo_inicial_V_d, end=tiempo_final_V_d, freq='D')

            df_V_d_bd1 = df_V_d_bd1.set_index('TIMESTAMP').reindex(rango_deseado_V_d).rename_axis('TIMESTAMP').reset_index()
            
            # Ajustar las horas de TIMESTAMP a las 07:00:00
            df_V_d_bd1['TIMESTAMP'] = df_V_d_bd1['TIMESTAMP'].dt.floor('D') + pd.DateOffset(hours=7)
        
            df_V_d_bd1['ESTACION'] = num_estacion
            
            # Guardar el archivo CSV depurado y corregido
            archivo_tiempo_rev_V_d = f"{num_estacion}.{tiempo_inicial_V_d.strftime('%Y%m%d-%H')}.{tiempo_final_V_d.strftime('%Y%m%d-%H')}.V.d.bd2.csv"
            df_V_d_bd1.to_csv(os.path.join(ruta_analisis_V,  archivo_tiempo_rev_V_d), index=False, na_rep='NA')
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"Se ha analizado exitosamente el archivo del viento diario bd1 como: {archivo_tiempo_rev_V_d}")
            print('')
            return True
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo del viento diario bd1 para generar el archivo tipo bd2.")
        return False
Edita_tiempos_V_d()
    
def Archivos_rev_tiempos_V_d():
    if ruta_V_d_bd1:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_V_d_bd1 = pd.read_csv(ruta_V_d_bd1)
            
            # Convierte los TIMESTAMPs a objetos datetime 
            df_V_d_bd1['TIMESTAMP'] = pd.to_datetime(df_V_d_bd1['TIMESTAMP'])
            
            #-------------------------------------------------- Obtener las fechas faltantes
            fechas_faltantes_V_d = df_V_d_bd1['TIMESTAMP'].min()
            tiempo_final_V_d = df_V_d_bd1['TIMESTAMP'].max()
            rango_deseado_V_d = pd.date_range(start=fechas_faltantes_V_d, end=tiempo_final_V_d, freq='D')
            fechas_faltantes_V_d = rango_deseado_V_d.difference(df_V_d_bd1['TIMESTAMP'])
            # Ajustar las horas de TIMESTAMP a las 07:00:00
            df_V_d_bd1['TIMESTAMP'] = df_V_d_bd1['TIMESTAMP'].dt.floor('D') + pd.DateOffset(hours=7)
            
            if fechas_faltantes_V_d.empty:
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print("No faltan fechas en el archivo del viento diario bd1")
            else:
                # Guardar el archivo CSV con las fechas faltantes
                archivo_fechas_faltantes_V_d = "Fechas_faltantes_V_d.csv"
                archivo_timestamps_V_d = pd.DataFrame({'TIMESTAMP': fechas_faltantes_V_d})
                archivo_timestamps_V_d.to_csv(os.path.join(ruta_pruebas_a, archivo_fechas_faltantes_V_d), index=False)
                
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f"Se ha generado exitosamente el archivo del viento horario: {archivo_fechas_faltantes_V_d}.")
                print('')
            
            # Find duplicated timestamps
            timestamps_duplicados_V_d = df_V_d_bd1[df_V_d_bd1['TIMESTAMP'].duplicated(keep=False)]['TIMESTAMP'].unique()
            
            # Initialize lists to store data
            timestamps_V_d = []
            Test_deteccion_V_d = []
            cantidad_V_d = []
            fecha_reemplazo = []
            
            for timestamp in timestamps_duplicados_V_d:
                df_V_d_bd1_timestamp = df_V_d_bd1[df_V_d_bd1['TIMESTAMP'] == timestamp]
                # Check if the timestamp is only repeated in timestamps
                if len(df_V_d_bd1_timestamp.drop_duplicates()) == 1:
                    timestamps_V_d.append(timestamp)
                    Test_deteccion_V_d.append('fila_repetida')
                    cantidad_V_d.append(len(df_V_d_bd1_timestamp))
                    fecha_reemplazo.append('fecha_eliminada')
                else:
                    timestamps_V_d.extend([timestamp] * len(df_V_d_bd1_timestamp))
                    Test_deteccion_V_d.extend(['timestamp_repetido'] * len(df_V_d_bd1_timestamp))
                    cantidad_V_d.extend([len(df_V_d_bd1_timestamp)] * len(df_V_d_bd1_timestamp))
                    fecha_reemplazo.extend(['fecha_sustituida'] * len(df_V_d_bd1_timestamp))
            
            # Create DataFrame with the collected data
            fechas_repetidas_V_d = pd.DataFrame({
                'TIMESTAMP': timestamps_V_d,
                'Test_deteccion': Test_deteccion_V_d,
                'Repeticiones': cantidad_V_d,
                'Fecha_reemplazo': fecha_reemplazo
            })
            
            # Drop duplicate rows
            fechas_repetidas_V_d.drop_duplicates(inplace=True)
            
            if fechas_repetidas_V_d.empty:
                print('')
            else:
                # Write the DataFrame to a CSV file only if there are duplicated timestamps
                archivo_fechas_repetidas_V_d = 'Fechas_repetidas_V_d.csv'
                fechas_repetidas_V_d.to_csv(os.path.join(ruta_pruebas_a, archivo_fechas_repetidas_V_d), index=False)
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f'Se ha generado exitosamente el archivo del viento horario: {archivo_fechas_repetidas_V_d}.')
        
            return True
        
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo del viento diario bd1 para generar los archivos diarios de fechas faltante y repetidas.")
Archivos_rev_tiempos_V_d()

def registro_fechas_especificas_faltantes_V_d(ruta_V_d_bd1, ruta_destino):
    # Cargar el archivo CSV
    df = pd.read_csv(ruta_V_d_bd1, na_values=['NA'], keep_default_na=False)

    # Filtrar filas con celdas en blanco en las columnas 'Wind.CST.max.dm.s1' y 'Temp.CSV.min.dm.s1'
    df_fechas_faltantes = df[(df['Wind.CST.max.dm.s1'] == '')]

    # Si se encuentran filas con celdas en blanco, proceder
    if not df_fechas_faltantes.empty:
        # Crear un DataFrame vacío para almacenar los resultados
        data = []

        # Iterar sobre las filas con celdas en blanco y agregarlas al DataFrame resultante
        for index, row in df_fechas_faltantes.iterrows():
            if row['Wind.CST.max.dm.s1'] == '':
                data.append({'TIMESTAMP': row['TIMESTAMP'], 'Elemento': 'Wind.CST.max.dm.s1'})
                
        # Crear un DataFrame a partir de los datos recopilados
        df_resultado = pd.DataFrame(data)

        # Ordenar el DataFrame por timestamp y luego por la columna 'Elemento'
        df_resultado = df_resultado.sort_values(by=['Elemento', 'TIMESTAMP'])

        # Guardar el DataFrame resultante como un archivo CSV
        df_resultado.to_csv(os.path.join(ruta_destino, 'Fechas_especificas_faltantes_V_d.csv'), index=False)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Se han encontrado celdas en blanco de los tiempos específicos en los archivos bd1 del viento diario.")
        print('')
registro_fechas_especificas_faltantes_V_d(ruta_V_d_bd1, ruta_pruebas_a)

# Encuentra el archivo .csv de la temperatura en la ruta de la estación con 'V.d.bd1' en el nombre
ruta_V_d_bd2 = next((os.path.join(ruta_analisis_V, file) for file in os.listdir(ruta_analisis_V) if file.endswith(".csv") and 'V.d.bd2' in file), None)

def fechas_especificas_faltantes_V_d(ruta_V_d_bd2):
    # Cargar el archivo CSV
    df = pd.read_csv(ruta_V_d_bd2)

    # Reemplazar NA en Wind.CST.max.dm.s1 donde Wind.m_s.max.dm.s1 es NA
    df.loc[df['Wind.m_s.max.dm.s1'].isna(), 'Wind.CST.max.dm.s1'] = 'NA'
    
    #df.loc[df['Wind.CST.max.dm.s1'].isna(), 'Wind.m_s.max.dm.s1'] = 'NA'
    # Reemplazar NA en Wind.CST.max.dm.s1 donde Wind.m_s.max.dm.s1 es NA
    df['Wind.m_s.max.dm.s1'].fillna('NA', inplace=True)
    df['Wind.CST.max.dm.s1'].fillna('NA', inplace=True)

    # Guardar los cambios en el mismo archivo
    df.to_csv(ruta_V_d_bd2, index=False)

fechas_especificas_faltantes_V_d(ruta_V_d_bd2)