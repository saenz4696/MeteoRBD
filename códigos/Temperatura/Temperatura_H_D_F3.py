import pandas as pd
import os
import warnings

#-------------------------------Rutas generales

# Elimina UserWarnings de openpyxl
warnings.simplefilter('ignore', category=UserWarning)

datos_crudos = r'C:\\MeteoRBD.v1.0.0\\datos_rbd'

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
       
# Establece la ruta para los archivos de la temperatura según el número de estación obtenido del archivo Excel
ruta_analisis_T = f"C:\\MeteoRBD.v1.0.0\\revisión\\{num_estacion}-ema\\Temperatura"

# Combine the directory path and  define folder name
ruta_pruebas_a = os.path.join(ruta_analisis_T, "Pruebas_numericas_tiempo")

# Create the folder
os.makedirs(ruta_pruebas_a, exist_ok=True)

# Encuentra el archivo T.h.bd1.csv de la temperatura en la ruta de la estación
ruta_T_h_bd1 = next((os.path.join(ruta_analisis_T, file) for file in os.listdir(ruta_analisis_T) if file.endswith(".csv") and 'T.h.bd1' in file), None)

# Encuentra el archivo T.d.bd1.csv de la temperatura en la ruta de la estación
ruta_T_d_bd1 = next((os.path.join(ruta_analisis_T, file) for file in os.listdir(ruta_analisis_T) if file.endswith(".csv") and 'T.d.bd1' in file), None)

# Define una función para procesar datos de la temperatura
def Edita_tiempos_T_h():
    if ruta_T_h_bd1:
        # Lee el archivo .csv y realiza operaciones de limpieza y corrección de timestamps
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_T_h_bd1 = pd.read_csv(ruta_T_h_bd1)
            
            # Convertir TIMESTAMP a datetime objects
            df_T_h_bd1['TIMESTAMP'] = pd.to_datetime(df_T_h_bd1['TIMESTAMP'])
            
            # Eliminar filas completamente duplicadas en el DataFrame original
            df_T_h_bd1.drop_duplicates(inplace=True)
            
            # Identificar y reemplazar timestamps duplicados_T_h con una secuencia cronológica
            duplicados_T_h = df_T_h_bd1[df_T_h_bd1.duplicated(subset='TIMESTAMP', keep=False)]
            timestamps_unicos_T_h = duplicados_T_h['TIMESTAMP'].unique()
            
            # Corregir los timestamps duplicados_T_h
            for timestamp_T_h in timestamps_unicos_T_h:
                indices_T_h = duplicados_T_h[duplicados_T_h['TIMESTAMP'] == timestamp_T_h].index
                timestamps_nuevos_T_h = pd.date_range(start=timestamp_T_h, freq='H', periods=len(indices_T_h))
                df_T_h_bd1.loc[indices_T_h, 'TIMESTAMP'] = timestamps_nuevos_T_h
            
            # Ordenar el DataFrame por TIMESTAMP
            df_T_h_bd1 = df_T_h_bd1.sort_values('TIMESTAMP')
            
            # Rellenar o corregir los timestamps para tener un rango horario completo
            tiempo_inicial_T_h = df_T_h_bd1['TIMESTAMP'].min()
            tiempo_final_T_h = df_T_h_bd1['TIMESTAMP'].max()
            rango_deseado_T_h = pd.date_range(start=tiempo_inicial_T_h, end=tiempo_final_T_h, freq='H')

            df_T_h_bd1 = df_T_h_bd1.set_index('TIMESTAMP').reindex(rango_deseado_T_h).rename_axis('TIMESTAMP').reset_index()
            
            df_T_h_bd1['ESTACION'] = num_estacion
            
            # Guardar el archivo CSV depurado y corregido
            archivo_tiempo_rev_T_h = f"{num_estacion}.{tiempo_inicial_T_h.strftime('%Y%m%d-%H')}.{tiempo_final_T_h.strftime('%Y%m%d-%H')}.T.h.bd2.csv"
            df_T_h_bd1.to_csv(os.path.join(ruta_analisis_T, archivo_tiempo_rev_T_h), index=False, na_rep='NA')
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"Se ha analizado exitosamente el archivo de la temperatura horaria bd1 como: {archivo_tiempo_rev_T_h}.")
            print('')
            return True
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la temperatura horaria bd1 para generar el archivo tipo bd2.")
        print('')
        return False  
Edita_tiempos_T_h()
    
def Archivos_rev_tiempos_T_h():
    if ruta_T_h_bd1:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_T_h_bd1 = pd.read_csv(ruta_T_h_bd1)
            
            # Convierte los TIMESTAMPs a objetos datetime 
            df_T_h_bd1['TIMESTAMP'] = pd.to_datetime(df_T_h_bd1['TIMESTAMP'])
            
            #-------------------------------------------------- Obtener las fechas faltantes
            tiempo_inicial_T_h = df_T_h_bd1['TIMESTAMP'].min()
            tiempo_final_T_h = df_T_h_bd1['TIMESTAMP'].max()
            rango_deseado_T_h = pd.date_range(start=tiempo_inicial_T_h, end=tiempo_final_T_h, freq='H')
            fechas_faltantes_T_h = rango_deseado_T_h.difference(df_T_h_bd1['TIMESTAMP'])
            
            if fechas_faltantes_T_h.empty:
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print("No faltan fechas en el archivo de la temperatura horaria bd1.")
                print('')
            else:
                # Guardar el archivo CSV con las fechas faltantes
                archivo_fechas_faltantes_T_h = "Fechas_faltantes_T_h.csv"
                archivo_timestamps_T_h = pd.DataFrame({'TIMESTAMP': fechas_faltantes_T_h})
                archivo_timestamps_T_h.to_csv(os.path.join(ruta_pruebas_a, archivo_fechas_faltantes_T_h), index=False)
                
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f"Se ha generado exitosamente el archivo de la temperatura horaria: {archivo_fechas_faltantes_T_h}.")
                print('')
            
            # Find duplicated timestamps
            timestamps_duplicados_T_h = df_T_h_bd1[df_T_h_bd1['TIMESTAMP'].duplicated(keep=False)]['TIMESTAMP'].unique()
            
            # Initialize lists to store data
            timestamps_T_h = []
            test_deteccion_T_h = []
            cantidad_T_h = []
            fecha_reemplazo_T_h = []
            
            for timestamp in timestamps_duplicados_T_h:
                df_T_h_bd1_timestamp = df_T_h_bd1[df_T_h_bd1['TIMESTAMP'] == timestamp]
                # Check if the timestamp is only repeated in timestamps
                if len(df_T_h_bd1_timestamp.drop_duplicates()) == 1:
                    timestamps_T_h.append(timestamp)
                    test_deteccion_T_h.append('fila_repetida')
                    cantidad_T_h.append(len(df_T_h_bd1_timestamp))
                    fecha_reemplazo_T_h.append('fecha_eliminada')
                else:
                    timestamps_T_h.extend([timestamp] * len(df_T_h_bd1_timestamp))
                    test_deteccion_T_h.extend(['timestamp_repetido'] * len(df_T_h_bd1_timestamp))
                    cantidad_T_h.extend([len(df_T_h_bd1_timestamp)] * len(df_T_h_bd1_timestamp))
                    fecha_reemplazo_T_h.extend(['fecha_sustituida'] * len(df_T_h_bd1_timestamp))
            
            # Create DataFrame with the collected data
            fechas_repetidas_T_h = pd.DataFrame({
                'TIMESTAMP': timestamps_T_h,
                'Test_deteccion': test_deteccion_T_h,
                'Repeticiones': cantidad_T_h,
                'Fecha_reemplazo': fecha_reemplazo_T_h
            })
            
            # Drop duplicate rows
            fechas_repetidas_T_h.drop_duplicates(inplace=True)
            
            if fechas_repetidas_T_h.empty:
                print('')
            else:
                # Write the DataFrame to a CSV file only if there are duplicated timestamps
                archivo_fechas_repetidas_T_h = 'Fechas_repetidas_T_h.csv'
                fechas_repetidas_T_h.to_csv(os.path.join(ruta_pruebas_a,  archivo_fechas_repetidas_T_h), index=False)
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f'Se ha generado exitosamente el archivo de la temperatura horario: {archivo_fechas_repetidas_T_h}.')
                print('')
        
            return True
        
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print('No se encontró el archivo de la temperatura horaria bd1 para generar los archivos horarios de fechas faltantes y repetidas.')
        print('')
Archivos_rev_tiempos_T_h()

def Edita_tiempos_T_d():
    if ruta_T_d_bd1:
        # Lee el archivo .csv y realiza operaciones de limpieza y corrección de timestamps
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_T_d_bd1 = pd.read_csv(ruta_T_d_bd1)
            
            # Convertir TIMESTAMP a datetime objects
            df_T_d_bd1['TIMESTAMP'] = pd.to_datetime(df_T_d_bd1['TIMESTAMP'])
            
            # Eliminar filas completamente duplicadas en el DataFrame original
            df_T_d_bd1.drop_duplicates(inplace=True)
            
            # Identificar y reemplazar timestamps duplicados_T_d con una secuencia cronológica
            duplicados_T_d = df_T_d_bd1[df_T_d_bd1.duplicated(subset='TIMESTAMP', keep=False)]
            timestamps_unicos_T_d = duplicados_T_d['TIMESTAMP'].unique()
            
            # Corregir los timestamps duplicados_T_d
            for timestamp_T_d in timestamps_unicos_T_d:
                indices_T_d = duplicados_T_d[duplicados_T_d['TIMESTAMP'] == timestamp_T_d].index
                timestamps_nuevos_T_d = pd.date_range(start=timestamp_T_d, freq='D', periods=len(indices_T_d))
                df_T_d_bd1.loc[indices_T_d, 'TIMESTAMP'] = timestamps_nuevos_T_d
            
            # Ordenar el DataFrame por TIMESTAMP
            df_T_d_bd1 = df_T_d_bd1.sort_values('TIMESTAMP')
            
            # Rellenar o corregir los timestamps para tener un rango horario completo
            tiempo_inicial_T_d = df_T_d_bd1['TIMESTAMP'].min()
            tiempo_final_T_d = df_T_d_bd1['TIMESTAMP'].max()
            rango_deseado_T_d = pd.date_range(start=tiempo_inicial_T_d, end=tiempo_final_T_d, freq='D')

            df_T_d_bd1 = df_T_d_bd1.set_index('TIMESTAMP').reindex(rango_deseado_T_d).rename_axis('TIMESTAMP').reset_index()
            
            # Ajustar las horas de TIMESTAMP a las 07:00:00
            df_T_d_bd1['TIMESTAMP'] = df_T_d_bd1['TIMESTAMP'].dt.floor('D') + pd.DateOffset(hours=7)
        
            df_T_d_bd1['ESTACION'] = num_estacion
            
            # Guardar el archivo CSV depurado y corregido
            archivo_tiempo_rev_T_d = f"{num_estacion}.{tiempo_inicial_T_d.strftime('%Y%m%d-%H')}.{tiempo_final_T_d.strftime('%Y%m%d-%H')}.T.d.bd2.csv"
            df_T_d_bd1.to_csv(os.path.join(ruta_analisis_T,  archivo_tiempo_rev_T_d), index=False, na_rep='NA')
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"Se ha analizado exitosamente el archivo de la temperatura diara bd1 como: {archivo_tiempo_rev_T_d}")
            print('')
            return True
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la temperatura diaria bd1 para generar el archivo tipo bd2.")
        print('')
        return False
Edita_tiempos_T_d()
    
def Archivos_rev_tiempos_T_d():
    if ruta_T_d_bd1:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_T_d_bd1 = pd.read_csv(ruta_T_d_bd1)
            
            # Convierte los TIMESTAMPs a objetos datetime 
            df_T_d_bd1['TIMESTAMP'] = pd.to_datetime(df_T_d_bd1['TIMESTAMP'])
            
            #-------------------------------------------------- Obtener las fechas faltantes
            fechas_faltantes_T_d = df_T_d_bd1['TIMESTAMP'].min()
            tiempo_final_T_d = df_T_d_bd1['TIMESTAMP'].max()
            rango_deseado_T_d = pd.date_range(start=fechas_faltantes_T_d, end=tiempo_final_T_d, freq='D')
            fechas_faltantes_T_d = rango_deseado_T_d.difference(df_T_d_bd1['TIMESTAMP'])
            # Ajustar las horas de TIMESTAMP a las 07:00:00
            df_T_d_bd1['TIMESTAMP'] = df_T_d_bd1['TIMESTAMP'].dt.floor('D') + pd.DateOffset(hours=7)
            
            if fechas_faltantes_T_d.empty:
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print("No faltan fechas en el archivo de la temperatura diaria bd1")
                print('')
            else:
                # Guardar el archivo CSV con las fechas faltantes
                archivo_fechas_faltantes_T_d = "Fechas_faltantes_T_d.csv"
                archivo_timestamps_T_d = pd.DataFrame({'TIMESTAMP': fechas_faltantes_T_d})
                archivo_timestamps_T_d.to_csv(os.path.join(ruta_pruebas_a, archivo_fechas_faltantes_T_d), index=False)
                
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f"Se ha generado exitosamente el archivo de la temperatura horaria: {archivo_fechas_faltantes_T_d}.")
                print('')
            
            # Find duplicated timestamps
            timestamps_duplicados_T_d = df_T_d_bd1[df_T_d_bd1['TIMESTAMP'].duplicated(keep=False)]['TIMESTAMP'].unique()
            
            # Initialize lists to store data
            timestamps_T_d = []
            test_deteccion_T_d = []
            cantidad_T_d = []
            fecha_reemplazo = []
            
            for timestamp in timestamps_duplicados_T_d:
                df_T_d_bd1_timestamp = df_T_d_bd1[df_T_d_bd1['TIMESTAMP'] == timestamp]
                # Check if the timestamp is only repeated in timestamps
                if len(df_T_d_bd1_timestamp.drop_duplicates()) == 1:
                    timestamps_T_d.append(timestamp)
                    test_deteccion_T_d.append('fila_repetida')
                    cantidad_T_d.append(len(df_T_d_bd1_timestamp))
                    fecha_reemplazo.append('fecha_eliminada')
                else:
                    timestamps_T_d.extend([timestamp] * len(df_T_d_bd1_timestamp))
                    test_deteccion_T_d.extend(['timestamp_repetido'] * len(df_T_d_bd1_timestamp))
                    cantidad_T_d.extend([len(df_T_d_bd1_timestamp)] * len(df_T_d_bd1_timestamp))
                    fecha_reemplazo.extend(['fecha_sustituida'] * len(df_T_d_bd1_timestamp))
            
            # Create DataFrame with the collected data
            fechas_repetidas_T_d = pd.DataFrame({
                'TIMESTAMP': timestamps_T_d,
                'Test_deteccion': test_deteccion_T_d,
                'Repeticiones': cantidad_T_d,
                'Fecha_reemplazo': fecha_reemplazo
            })
            
            # Drop duplicate rows
            fechas_repetidas_T_d.drop_duplicates(inplace=True)
            
            if fechas_repetidas_T_d.empty:
                print('')
            else:
                # Write the DataFrame to a CSV file only if there are duplicated timestamps
                archivo_fechas_repetidas_T_d = 'Fechas_repetidas_T_d.csv'
                fechas_repetidas_T_d.to_csv(os.path.join(ruta_pruebas_a, archivo_fechas_repetidas_T_d), index=False)
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f'Se ha generado exitosamente el archivo de la temperatura horaria: {archivo_fechas_repetidas_T_d}.')
                print('')
            return True
        
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la temperatura diaria bd1 para generar los archivos diarios de fechas faltante y repetidas.")
        print('')
Archivos_rev_tiempos_T_d()

def registro_fechas_especificas_faltantes_T_d(ruta_T_d_bd1, ruta_destino):
    # Cargar el archivo CSV
    df = pd.read_csv(ruta_T_d_bd1, na_values=['NA'], keep_default_na=False)

    # Filtrar filas con celdas en blanco en las columnas 'Temp.CST.max.dm.s1' y 'Temp.CST.min.dm.s1'
    df_fechas_faltantes = df[(df['Temp.CST.max.dm.s1'] == '') | (df['Temp.CST.min.dm.s1'] == '')]

    # Si se encuentran filas con celdas en blanco, proceder
    if not df_fechas_faltantes.empty:
        # Crear un DataFrame vacío para almacenar los resultados
        data = []

        # Iterar sobre las filas con celdas en blanco y agregarlas al DataFrame resultante
        for index, row in df_fechas_faltantes.iterrows():
            if row['Temp.CST.max.dm.s1'] == '':
                data.append({'TIMESTAMP': row['TIMESTAMP'], 'Elemento': 'Temp.CST.max.dm.s1'})
            if row['Temp.CST.min.dm.s1'] == '':
                data.append({'TIMESTAMP': row['TIMESTAMP'], 'Elemento': 'Temp.CST.min.dm.s1'})

        # Crear un DataFrame a partir de los datos recopilados
        df_resultado = pd.DataFrame(data)

        # Ordenar el DataFrame por timestamp y luego por la columna 'Elemento'
        df_resultado = df_resultado.sort_values(by=['Elemento', 'TIMESTAMP'])

        # Guardar el DataFrame resultante como un archivo CSV
        df_resultado.to_csv(os.path.join(ruta_destino, 'Fechas_especificas_faltantes_T_d.csv'), index=False)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Se han encontrado celdas en blanco de los tiempos específicos en los archivos bd1 de la temperatura diaria.")
        print('')
registro_fechas_especificas_faltantes_T_d(ruta_T_d_bd1, ruta_pruebas_a)

# Encuentra el archivo .csv de la temperatura en la ruta de la estación con 'T.d.bd1' en el nombre
ruta_T_d_bd2 = next((os.path.join(ruta_analisis_T, file) for file in os.listdir(ruta_analisis_T) if file.endswith(".csv") and 'T.d.bd2' in file), None)

def fechas_especificas_faltantes_T_d(ruta_T_d_bd2):
    # Cargar el archivo CSV
    df = pd.read_csv(ruta_T_d_bd2)

    # Reemplazar NA en Temp.CST.max.dm.s1 donde Temp.CST.max.dm.s1 es NA
    df.loc[df['Temp.degC.max.dm.s1'].isna(), 'Temp.CST.max.dm.s1'] = 'NA'
    
    # Reemplazar NA en Temp.degC.max.dm.s1 donde Temp.CST.max.dm.s1 es NA
    #df.loc[df['Temp.CST.max.dm.s1'].isna(), 'Temp.degC.max.dm.s1'] = 'NA'

    df['Temp.degC.max.dm.s1'].fillna('NA', inplace=True)
    df['Temp.CST.max.dm.s1'].fillna('NA', inplace=True)

    # Reemplazar NA en Temp.CST.min.dm.s1 donde Temp.degC.min.dm.s1 es NA
    df.loc[df['Temp.degC.min.dm.s1'].isna(), 'Temp.CST.min.dm.s1'] = 'NA'
    
    # Reemplazar NA en Temp.degC.min.dm.s1 donde Temp.CST.min.dm.s1 es NA
    #df.loc[df['Temp.CST.min.dm.s1'].isna(), 'Temp.degC.min.dm.s1'] = 'NA'

    df['Temp.degC.min.dm.s1'].fillna('NA', inplace=True)
    df['Temp.CST.min.dm.s1'].fillna('NA', inplace=True)

    # Guardar los cambios en el mismo archivo
    df.to_csv(ruta_T_d_bd2, index=False)

fechas_especificas_faltantes_T_d(ruta_T_d_bd2)
