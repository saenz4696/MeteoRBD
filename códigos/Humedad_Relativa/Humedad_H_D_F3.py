import pandas as pd
import os
import warnings

#-------------------------------Rutas generales

# Elimina UserWarnings de openpyxl
warnings.simplefilter('ignore', category=UserWarning)

datos_crudos = r'C:\\MeteoRBD.v1.0.0\\datos_rbd'

# Encuentra el archivo .xlsx en la datos_crudos que contiene 'Cuenca' y 'Estación' como columnas
ruta_archivo = next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Humedad" in file and file.endswith(".xlsx")), None)

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
       
# Establece la ruta para los archivos de la humedad relativa según el número de estación obtenido del archivo Excel
ruta_analisis_HR = f"C:\\MeteoRBD.v1.0.0\\revisión\\{num_estacion}-ema\\Humedad relativa"

# Combine the directory path and  define folder name
ruta_pruebas_a = os.path.join(ruta_analisis_HR, "Pruebas_numericas_tiempo")

# Create the folder
os.makedirs(ruta_pruebas_a, exist_ok=True)

# Encuentra el archivo HR.h.bd1.csv de la humedad relativa en la ruta de la estación
ruta_HR_h_bd1 = next((os.path.join(ruta_analisis_HR, file) for file in os.listdir(ruta_analisis_HR) if file.endswith(".csv") and 'HR.h.bd1' in file), None)

# Encuentra el archivo HR.d.bd1.csv de la humedad relativa en la ruta de la estación
ruta_HR_d_bd1 = next((os.path.join(ruta_analisis_HR, file) for file in os.listdir(ruta_analisis_HR) if file.endswith(".csv") and 'HR.d.bd1' in file), None)

# Define una función para procesar datos de la humedad relativa
def Edita_tiempos_HR_h():
    if ruta_HR_h_bd1:
        # Lee el archivo .csv y realiza operaciones de limpieza y corrección de timestamps
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_HR_h_bd1 = pd.read_csv(ruta_HR_h_bd1)
            
            # Convertir TIMESTAMP a datetime objects
            df_HR_h_bd1['TIMESTAMP'] = pd.to_datetime(df_HR_h_bd1['TIMESTAMP'])
            
            # Eliminar filas completamente duplicadas en el DataFrame original
            df_HR_h_bd1.drop_duplicates(inplace=True)
            
            # Identificar y reemplazar timestamps duplicados_HR_h con una secuencia cronológica
            duplicados_HR_h = df_HR_h_bd1[df_HR_h_bd1.duplicated(subset='TIMESTAMP', keep=False)]
            timestamps_unicos_HR_h = duplicados_HR_h['TIMESTAMP'].unique()
            
            # Corregir los timestamps duplicados_HR_h
            for timestamp_HR_h in timestamps_unicos_HR_h:
                indices_HR_h = duplicados_HR_h[duplicados_HR_h['TIMESTAMP'] == timestamp_HR_h].index
                timestamps_nuevos_HR_h = pd.date_range(start=timestamp_HR_h, freq='H', periods=len(indices_HR_h))
                df_HR_h_bd1.loc[indices_HR_h, 'TIMESTAMP'] = timestamps_nuevos_HR_h
            
            # Ordenar el DataFrame por TIMESTAMP
            df_HR_h_bd1 = df_HR_h_bd1.sort_values('TIMESTAMP')
            
            # Rellenar o corregir los timestamps para tener un rango horario completo
            tiempo_inicial_HR_h = df_HR_h_bd1['TIMESTAMP'].min()
            tiempo_final_HR_h = df_HR_h_bd1['TIMESTAMP'].max()
            rango_deseado_HR_h = pd.date_range(start=tiempo_inicial_HR_h, end=tiempo_final_HR_h, freq='H')

            df_HR_h_bd1 = df_HR_h_bd1.set_index('TIMESTAMP').reindex(rango_deseado_HR_h).rename_axis('TIMESTAMP').reset_index()
            
            df_HR_h_bd1['ESTACION'] = num_estacion
            
            # Guardar el archivo CSV depurado y corregido
            archivo_tiempo_rev_HR_h = f"{num_estacion}.{tiempo_inicial_HR_h.strftime('%Y%m%d-%H')}.{tiempo_final_HR_h.strftime('%Y%m%d-%H')}.HR.h.bd2.csv"
            df_HR_h_bd1.to_csv(os.path.join(ruta_analisis_HR, archivo_tiempo_rev_HR_h), index=False, na_rep='NA')
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"Se ha analizado exitosamente el archivo de la humedad relativa horaria bd1 como: {archivo_tiempo_rev_HR_h}")
            print('')
            return True
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la humedad relativa horaria bd1 para generar el archivo tipo bd2")
        print('')
        return False  
Edita_tiempos_HR_h()
    
def Archivos_rev_tiempos_HR_h():
    if ruta_HR_h_bd1:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_HR_h_bd1 = pd.read_csv(ruta_HR_h_bd1)
            
            # Convierte los TIMESTAMPs a objetos datetime 
            df_HR_h_bd1['TIMESTAMP'] = pd.to_datetime(df_HR_h_bd1['TIMESTAMP'])
            
            #-------------------------------------------------- Obtener las fechas faltantes
            tiempo_inicial_HR_h = df_HR_h_bd1['TIMESTAMP'].min()
            tiempo_final_HR_h = df_HR_h_bd1['TIMESTAMP'].max()
            rango_deseado_HR_h = pd.date_range(start=tiempo_inicial_HR_h, end=tiempo_final_HR_h, freq='H')
            fechas_faltantes_HR_h = rango_deseado_HR_h.difference(df_HR_h_bd1['TIMESTAMP'])
            
            if fechas_faltantes_HR_h.empty:
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print("No faltan fechas en el archivo de la humedad relativa horaria bd1.")
                print('')
            else:
                # Guardar el archivo CSV con las fechas faltantes
                archivo_fechas_faltantes_HR_h = "Fechas_faltantes_HR_h.csv"
                archivo_timestamps_HR_h = pd.DataFrame({'TIMESTAMP': fechas_faltantes_HR_h})
                archivo_timestamps_HR_h.to_csv(os.path.join(ruta_pruebas_a, archivo_fechas_faltantes_HR_h), index=False)
                
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f"Se ha generado exitosamente el archivo de la humedad relativa horaria: {archivo_fechas_faltantes_HR_h}.")
                print('')
            
            # Find duplicated timestamps
            timestamps_duplicados_HR_h = df_HR_h_bd1[df_HR_h_bd1['TIMESTAMP'].duplicated(keep=False)]['TIMESTAMP'].unique()
            
            # Initialize lists to store data
            timestamps_HR_h = []
            tesHR_deteccion_HR_h = []
            cantidad_HR_h = []
            fecha_reemplazo_HR_h = []
            
            for timestamp in timestamps_duplicados_HR_h:
                df_HR_h_bd1_timestamp = df_HR_h_bd1[df_HR_h_bd1['TIMESTAMP'] == timestamp]
                # Check if the timestamp is only repeated in timestamps
                if len(df_HR_h_bd1_timestamp.drop_duplicates()) == 1:
                    timestamps_HR_h.append(timestamp)
                    tesHR_deteccion_HR_h.append('fila_repetida')
                    cantidad_HR_h.append(len(df_HR_h_bd1_timestamp))
                    fecha_reemplazo_HR_h.append('fecha_eliminada')
                else:
                    timestamps_HR_h.extend([timestamp] * len(df_HR_h_bd1_timestamp))
                    tesHR_deteccion_HR_h.extend(['timestamp_repetido'] * len(df_HR_h_bd1_timestamp))
                    cantidad_HR_h.extend([len(df_HR_h_bd1_timestamp)] * len(df_HR_h_bd1_timestamp))
                    fecha_reemplazo_HR_h.extend(['fecha_sustituida'] * len(df_HR_h_bd1_timestamp))
            
            # Create DataFrame with the collected data
            fechas_repetidas_HR_h = pd.DataFrame({
                'TIMESTAMP': timestamps_HR_h,
                'TesHR_deteccion': tesHR_deteccion_HR_h,
                'Repeticiones': cantidad_HR_h,
                'Fecha_reemplazo': fecha_reemplazo_HR_h
            })
            
            # Drop duplicate rows
            fechas_repetidas_HR_h.drop_duplicates(inplace=True)
            
            if fechas_repetidas_HR_h.empty:
                print('')
            else:
                # Write the DataFrame to a CSV file only if there are duplicated timestamps
                archivo_fechas_repetidas_HR_h = 'Fechas_repetidas_HR_h.csv'
                fechas_repetidas_HR_h.to_csv(os.path.join(ruta_pruebas_a,  archivo_fechas_repetidas_HR_h), index=False)
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f'Se ha generado exitosamente el archivo de la humedad relativa horario: {archivo_fechas_repetidas_HR_h}.')
                print('')
        
            return True
        
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print('No se encontró el archivo de la humedad relativa horaria bd1 para generar los archivos horarios de fechas faltantes y repetidas.')
        print('')
Archivos_rev_tiempos_HR_h()

def Edita_tiempos_HR_d():
    if ruta_HR_d_bd1:
        # Lee el archivo .csv y realiza operaciones de limpieza y corrección de timestamps
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_HR_d_bd1 = pd.read_csv(ruta_HR_d_bd1)
            
            # Convertir TIMESTAMP a datetime objects
            df_HR_d_bd1['TIMESTAMP'] = pd.to_datetime(df_HR_d_bd1['TIMESTAMP'])
            
            # Eliminar filas completamente duplicadas en el DataFrame original
            df_HR_d_bd1.drop_duplicates(inplace=True)
            
            # Identificar y reemplazar timestamps duplicados_HR_d con una secuencia cronológica
            duplicados_HR_d = df_HR_d_bd1[df_HR_d_bd1.duplicated(subset='TIMESTAMP', keep=False)]
            timestamps_unicos_HR_d = duplicados_HR_d['TIMESTAMP'].unique()
            
            # Corregir los timestamps duplicados_HR_d
            for timestamp_HR_d in timestamps_unicos_HR_d:
                indices_HR_d = duplicados_HR_d[duplicados_HR_d['TIMESTAMP'] == timestamp_HR_d].index
                timestamps_nuevos_HR_d = pd.date_range(start=timestamp_HR_d, freq='D', periods=len(indices_HR_d))
                df_HR_d_bd1.loc[indices_HR_d, 'TIMESTAMP'] = timestamps_nuevos_HR_d
            
            # Ordenar el DataFrame por TIMESTAMP
            df_HR_d_bd1 = df_HR_d_bd1.sort_values('TIMESTAMP')
            
            # Rellenar o corregir los timestamps para tener un rango horario completo
            tiempo_inicial_HR_d = df_HR_d_bd1['TIMESTAMP'].min()
            tiempo_final_HR_d = df_HR_d_bd1['TIMESTAMP'].max()
            rango_deseado_HR_d = pd.date_range(start=tiempo_inicial_HR_d, end=tiempo_final_HR_d, freq='D')

            df_HR_d_bd1 = df_HR_d_bd1.set_index('TIMESTAMP').reindex(rango_deseado_HR_d).rename_axis('TIMESTAMP').reset_index()
            
            # Ajustar las horas de TIMESTAMP a las 07:00:00
            df_HR_d_bd1['TIMESTAMP'] = df_HR_d_bd1['TIMESTAMP'].dt.floor('D') + pd.DateOffset(hours=7)
        
            df_HR_d_bd1['ESTACION'] = num_estacion
            
            # Guardar el archivo CSV depurado y corregido
            archivo_tiempo_rev_HR_d = f"{num_estacion}.{tiempo_inicial_HR_d.strftime('%Y%m%d-%H')}.{tiempo_final_HR_d.strftime('%Y%m%d-%H')}.HR.d.bd2.csv"
            df_HR_d_bd1.to_csv(os.path.join(ruta_analisis_HR,  archivo_tiempo_rev_HR_d), index=False, na_rep='NA')
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"Se ha analizado exitosamente el archivo de la humedad relativa diara bd1 como: {archivo_tiempo_rev_HR_d}")
            print('')
            return True
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la humedad relativa diaria bd1 para generar el archivo tipo bd2.")
        print('')
        return False
Edita_tiempos_HR_d()
    
def Archivos_rev_tiempos_HR_d():
    if ruta_HR_d_bd1:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_HR_d_bd1 = pd.read_csv(ruta_HR_d_bd1)
            
            # Convierte los TIMESTAMPs a objetos datetime 
            df_HR_d_bd1['TIMESTAMP'] = pd.to_datetime(df_HR_d_bd1['TIMESTAMP'])
            
            #-------------------------------------------------- Obtener las fechas faltantes
            fechas_faltantes_HR_d = df_HR_d_bd1['TIMESTAMP'].min()
            tiempo_final_HR_d = df_HR_d_bd1['TIMESTAMP'].max()
            rango_deseado_HR_d = pd.date_range(start=fechas_faltantes_HR_d, end=tiempo_final_HR_d, freq='D')
            fechas_faltantes_HR_d = rango_deseado_HR_d.difference(df_HR_d_bd1['TIMESTAMP'])
            # Ajustar las horas de TIMESTAMP a las 07:00:00
            df_HR_d_bd1['TIMESTAMP'] = df_HR_d_bd1['TIMESTAMP'].dt.floor('D') + pd.DateOffset(hours=7)
            
            if fechas_faltantes_HR_d.empty:
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print("No faltan fechas en el archivo de la humedad relativa diaria bd1")
                print('')
            else:
                # Guardar el archivo CSV con las fechas faltantes
                archivo_fechas_faltantes_HR_d = "Fechas_faltantes_HR_d.csv"
                archivo_timestamps_HR_d = pd.DataFrame({'TIMESTAMP': fechas_faltantes_HR_d})
                archivo_timestamps_HR_d.to_csv(os.path.join(ruta_pruebas_a, archivo_fechas_faltantes_HR_d), index=False)
                
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f"Se ha generado exitosamente el archivo de la humedad relativa horaria: {archivo_fechas_faltantes_HR_d}.")
                print('')
            
            # Find duplicated timestamps
            timestamps_duplicados_HR_d = df_HR_d_bd1[df_HR_d_bd1['TIMESTAMP'].duplicated(keep=False)]['TIMESTAMP'].unique()
            
            # Initialize lists to store data
            timestamps_HR_d = []
            tesHR_deteccion_HR_d = []
            cantidad_HR_d = []
            fecha_reemplazo = []
            
            for timestamp in timestamps_duplicados_HR_d:
                df_HR_d_bd1_timestamp = df_HR_d_bd1[df_HR_d_bd1['TIMESTAMP'] == timestamp]
                # Check if the timestamp is only repeated in timestamps
                if len(df_HR_d_bd1_timestamp.drop_duplicates()) == 1:
                    timestamps_HR_d.append(timestamp)
                    tesHR_deteccion_HR_d.append('fila_repetida')
                    cantidad_HR_d.append(len(df_HR_d_bd1_timestamp))
                    fecha_reemplazo.append('fecha_eliminada')
                else:
                    timestamps_HR_d.extend([timestamp] * len(df_HR_d_bd1_timestamp))
                    tesHR_deteccion_HR_d.extend(['timestamp_repetido'] * len(df_HR_d_bd1_timestamp))
                    cantidad_HR_d.extend([len(df_HR_d_bd1_timestamp)] * len(df_HR_d_bd1_timestamp))
                    fecha_reemplazo.extend(['fecha_sustituida'] * len(df_HR_d_bd1_timestamp))
            
            # Create DataFrame with the collected data
            fechas_repetidas_HR_d = pd.DataFrame({
                'TIMESTAMP': timestamps_HR_d,
                'TesHR_deteccion': tesHR_deteccion_HR_d,
                'Repeticiones': cantidad_HR_d,
                'Fecha_reemplazo': fecha_reemplazo
            })
            
            # Drop duplicate rows
            fechas_repetidas_HR_d.drop_duplicates(inplace=True)
            
            if fechas_repetidas_HR_d.empty:
                print('')
            else:
                # Write the DataFrame to a CSV file only if there are duplicated timestamps
                archivo_fechas_repetidas_HR_d = 'Fechas_repetidas_HR_d.csv'
                fechas_repetidas_HR_d.to_csv(os.path.join(ruta_pruebas_a, archivo_fechas_repetidas_HR_d), index=False)
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f'Se ha generado exitosamente el archivo de la humedad relativa horaria: {archivo_fechas_repetidas_HR_d}.')
                print('')
            return True
        
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la humedad relativa diaria bd1 para generar los archivos diarios de fechas faltante y repetidas.")
        print('')
Archivos_rev_tiempos_HR_d()

def registro_fechas_especificas_faltantes_HR_d(ruta_HR_d_bd1, ruta_destino):
    # Cargar el archivo CSV
    df = pd.read_csv(ruta_HR_d_bd1, na_values=['NA'], keep_default_na=False)

    # Filtrar filas con celdas en blanco en las columnas 'RH.CST.max.dm.s1' y 'RH.CST.min.dm.s1'
    df_fechas_faltantes = df[(df['RH.CST.max.dm.s1'] == '') | (df['RH.CST.min.dm.s1'] == '')]

    # Si se encuentran filas con celdas en blanco, proceder
    if not df_fechas_faltantes.empty:
        # Crear un DataFrame vacío para almacenar los resultados
        data = []

        # Iterar sobre las filas con celdas en blanco y agregarlas al DataFrame resultante
        for index, row in df_fechas_faltantes.iterrows():
            if row['RH.CST.max.dm.s1'] == '':
                data.append({'TIMESTAMP': row['TIMESTAMP'], 'Elemento': 'RH.CST.max.dm.s1'})
            if row['RH.CST.min.dm.s1'] == '':
                data.append({'TIMESTAMP': row['TIMESTAMP'], 'Elemento': 'RH.CST.min.dm.s1'})

        # Crear un DataFrame a partir de los datos recopilados
        df_resultado = pd.DataFrame(data)

        # Ordenar el DataFrame por timestamp y luego por la columna 'Elemento'
        df_resultado = df_resultado.sort_values(by=['Elemento', 'TIMESTAMP'])

        # Guardar el DataFrame resultante como un archivo CSV
        df_resultado.to_csv(os.path.join(ruta_destino, 'Fechas_especificas_faltantes_HR_d.csv'), index=False)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Se han encontrado celdas en blanco de los tiempos específicos en los archivos bd1 de la humedad relativa diaria.")
        print('')

registro_fechas_especificas_faltantes_HR_d(ruta_HR_d_bd1, ruta_pruebas_a)

# Encuentra el archivo HR.d.bd1.csv de la humedad relativa en la ruta de la estación
ruta_HR_d_bd2 = next((os.path.join(ruta_analisis_HR, file) for file in os.listdir(ruta_analisis_HR) if file.endswith(".csv") and 'HR.d.bd2' in file), None)


def fechas_especificas_faltantes_HR_d(ruta_HR_d_bd2):
    # Cargar el archivo CSV
    df = pd.read_csv(ruta_HR_d_bd2)

    # Reemplazar NA en Temp.CST.max.dm.s1 donde Temp.degC.max.dm.s1 es NA
    df.loc[df['RH.perc.max.dm.s1'].isna(), 'RH.CST.max.dm.s1'] = 'NA'
    #df.loc[df['RH.CST.max.dm.s1'].isna(), 'RH.perc.max.dm.s1'] = 'NA'
    # Reemplazar NA en Temp.CST.max.dm.s1 donde Temp.degC.max.dm.s1 es NA
    df['RH.perc.max.dm.s1'].fillna('NA', inplace=True)
    df['RH.CST.max.dm.s1'].fillna('NA', inplace=True)

    # Reemplazar NA en Temp.CST.min.dm.s1 donde Temp.degC.min.dm.s1 es NA
    df.loc[df['RH.perc.min.dm.s1'].isna(), 'RH.CST.min.dm.s1'] = 'NA'
    #df.loc[df['RH.CST.min.dm.s1'].isna(), 'RH.perc.min.dm.s1'] = 'NA'
    # Reemplazar NA en Temp.CST.min.dm.s1 donde Temp.degC.min.dm.s1 es NA
    df['RH.perc.min.dm.s1'].fillna('NA', inplace=True)
    df['RH.CST.min.dm.s1'].fillna('NA', inplace=True)

    # Guardar los cambios en el mismo archivo
    df.to_csv(ruta_HR_d_bd2, index=False)

fechas_especificas_faltantes_HR_d(ruta_HR_d_bd2)

