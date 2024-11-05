import pandas as pd
import os
import warnings

#-------------------------------Rutas generales

# Elimina UserWarnings de openpyxl
warnings.simplefilter('ignore', category=UserWarning)

# Suppress FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

# Suppress SettingWithCopyWarning
warnings.simplefilter(action='ignore', category=pd.core.generic.SettingWithCopyWarning)

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

#Donde se encuentran los archivos en analisis
ruta_analisis_T = f"C:\\MeteoRBD.v1.0.0\\revisión\\{num_estacion}-ema\\Temperatura"

# Combine the directory path and  define folder name
ruta_pruebas_a = os.path.join(ruta_analisis_T, "Pruebas_numericas_tiempo")

# Create the folder
os.makedirs(ruta_pruebas_a, exist_ok=True)

# Encuentra el archivo .csv de la temperatura en la ruta de la estación con 'T.h.bd0' en el nombre
ruta_T_h_bd0 = next((os.path.join(ruta_analisis_T, file) for file in os.listdir(ruta_analisis_T) if file.endswith(".csv") and 'T.h.bd0' in file), None)

# Encuentra el archivo .csv de la temperatura en la ruta de la estación con 'T.d.bd0' en el nombre
ruta_T_d_bd0 = next((os.path.join(ruta_analisis_T, file) for file in os.listdir(ruta_analisis_T) if file.endswith(".csv") and 'T.d.bd0' in file), None)

#------------------------------------------------------------Para la temperatura horaria

def Filtro_caracter_T_h():
    if ruta_T_h_bd0:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_T_h_bd0 = pd.read_csv(ruta_T_h_bd0)
            
         # Agrega condiciones para establecer valores como 'NA' en las columnas específicas
        df_T_h_bd0['Temp.degC.avg.1h.s1'] = pd.to_numeric(df_T_h_bd0['Temp.degC.avg.1h.s1'], errors='coerce')
        df_T_h_bd0.loc[(df_T_h_bd0['Temp.degC.avg.1h.s1'] > 45) | (df_T_h_bd0['Temp.degC.avg.1h.s1'] < -10), 'Temp.degC.avg.1h.s1'] = 'NA'

        #df_T_h_bd0['Td.degC.avg.1h.c1'] = pd.to_numeric(df_T_h_bd0['Td.degC.avg.1h.c1'], errors='coerce')
        #df_T_h_bd0.loc[(df_T_h_bd0['Td.degC.avg.1h.c1'] > 40) | (df_T_h_bd0['Td.degC.avg.1h.c1'] < -20), 'Td.degC.avg.1h.c1'] = 'NA'
        
        # Filtra las filas sin valores numéricos al principio y al final en ciertas columnas
        indices_numericos_T_h = df_T_h_bd0[df_T_h_bd0[['Temp.degC.avg.1h.s1']].apply(pd.to_numeric, errors='coerce').notnull().any(axis=1)].index
        
        # Reemplaza valores no numéricos con 'NA' en ciertas columnas y -9.0 con 'NA'
        reemplazo_columnas_T_h = ['Temp.degC.avg.1h.s1']
        for col in reemplazo_columnas_T_h:
            df_T_h_bd0[col] = pd.to_numeric(df_T_h_bd0[col], errors='coerce')
            df_T_h_bd0[col] = df_T_h_bd0[col].where(df_T_h_bd0[col].notnull(), 'NA')
            df_T_h_bd0[col] = df_T_h_bd0[col].replace(-9.0, 'NA')

        if not indices_numericos_T_h.empty:
            primer_indice_numerico_T_h = indices_numericos_T_h[0]
            ultimo_indice_numerico_T_h = indices_numericos_T_h[-1]

            # Conserva las filas con valores numéricos
            df_T_h_bd0 = df_T_h_bd0.iloc[primer_indice_numerico_T_h:ultimo_indice_numerico_T_h + 1]

            # Rellena valores no numéricos con 'NA' en ciertas columnas y agrega el número de estación en la columna ESTACION
            rellena_caracteres_NA_T_h = ['Temp.degC.avg.1h.s1']
            for col in rellena_caracteres_NA_T_h:
                df_T_h_bd0[col] = pd.to_numeric(df_T_h_bd0[col], errors='coerce').fillna('NA')

            df_T_h_bd0['ESTACION'] = num_estacion
            
            # Genera el nombre de archivo basado en marcas de tiempo inicial y final
            tiempo_inicial_T_h = pd.to_datetime(df_T_h_bd0.loc[primer_indice_numerico_T_h, 'TIMESTAMP'])
            tiempo_final_T_h = pd.to_datetime(df_T_h_bd0.loc[ultimo_indice_numerico_T_h, 'TIMESTAMP'])
            nombre_depurado_T_h = f"{num_estacion}.{tiempo_inicial_T_h.strftime('%Y%m%d-%H')}.{tiempo_final_T_h.strftime('%Y%m%d-%H')}.T.h.bd1.csv"
            
            # Guarda el archivo CSV
            df_T_h_bd0.to_csv(os.path.join(ruta_analisis_T, nombre_depurado_T_h), index=False)
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"Se ha depurado exitosamente el archivo de la temperatura horaria bd0 como: {nombre_depurado_T_h}")
            print('')
        else:
            print("No hay datos numéricos en las columnas de la temperatura.")
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la temperatura horaria bd0 para generar el archivo tipo bd1")

Filtro_caracter_T_h()

def Prueba_numerica_T_h():
    if ruta_T_h_bd0:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_T_h_bd0 = pd.read_csv(ruta_T_h_bd0, keep_default_na=False)
              
        # Obtiene las columnas relevantes excluyendo 'TIMESTAMP'
        col_rev_T_h = [col for col in df_T_h_bd0.columns if col not in ['TIMESTAMP', 'Td.degC.avg.1h.c1']]
    
        df_no_numerico_T_h = []
    
        for col in col_rev_T_h:
            # Filtra las filas que no contienen valores numéricos o están vacías en la columna actual
            datos_no_numericos_T_h = df_T_h_bd0[
                (~df_T_h_bd0[col].astype(str).str.match(r'^-?\d*\.?\d*$')) | df_T_h_bd0[col].eq('')
            ].copy()
        
            if not datos_no_numericos_T_h.empty:
                # Agrega información sobre las columnas con valores no numéricos al DataFrame resultante
                datos_no_numericos_T_h['Elemento'] = col
                datos_no_numericos_T_h['Valor_original'] = datos_no_numericos_T_h[col].astype(str)
                
                if col == 'ESTACION':  # Verifica la columna 'ESTACION'
                    datos_no_numericos_T_h['Valor_reemplazo'] = num_estacion
                    datos_no_numericos_T_h['Procedimiento_adoptado'] = 'dato_sustituido'
                else:
                    datos_no_numericos_T_h['Valor_reemplazo'] = 'NA'
                    datos_no_numericos_T_h['Procedimiento_adoptado'] = 'dato_eliminado'
                
                datos_no_numericos_T_h['Prueba_deteccion'] = 'valor_no_numerico'
                
                df_no_numerico_T_h.append(datos_no_numericos_T_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Prueba_deteccion', 'Procedimiento_adoptado']])
            
            # Para identificar números no iguales en la columna 'ESTACION'
            rev_est_T_h = df_T_h_bd0[df_T_h_bd0['ESTACION'].apply(lambda x: (isinstance(x, str) and str(x).replace('.', '', 1).isdigit() and float(str(x).replace(',', '.', 1)) != num_estacion))]
            if not rev_est_T_h.empty:
                # Agrega información sobre las discrepancias en 'ESTACION' al DataFrame resultante
                rev_est_T_h.loc[:, 'Elemento'] = 'ESTACION'
                rev_est_T_h.loc[:, 'Valor_original'] = rev_est_T_h['ESTACION']
                rev_est_T_h.loc[:, 'Valor_reemplazo'] = num_estacion
                rev_est_T_h.loc[:, 'Prueba_deteccion'] = 'estacion_erronea'
                rev_est_T_h.loc[:, 'Procedimiento_adoptado'] = 'dato_sustituido'

                df_no_numerico_T_h.append(rev_est_T_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Prueba_deteccion', 'Procedimiento_adoptado']])
            
            # Verifica valores específicos (-9) en la columna actual
            # Convierte la columna al tipo numérico (float) ignorando los errores
            df_T_h_bd0[col] = pd.to_numeric(df_T_h_bd0[col], errors='coerce')
            datos_menos_9_T_h = df_T_h_bd0[df_T_h_bd0[col] == -9].copy()
            if not datos_menos_9_T_h.empty:
                # Agrega información sobre valores igual a -9 al DataFrame resultante
                datos_menos_9_T_h['Elemento'] = col
                datos_menos_9_T_h['Valor_original'] = -9
                datos_menos_9_T_h['Valor_reemplazo'] = 'NA'
                datos_menos_9_T_h['Prueba_deteccion'] = 'valor_igual_a_-9'
                datos_menos_9_T_h['Procedimiento_adoptado'] = 'dato_eliminado'
                
                df_no_numerico_T_h.append(datos_menos_9_T_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Prueba_deteccion', 'Procedimiento_adoptado']])
    
            if col == 'Temp.degC.avg.1h.s1':  # Aplica la variable para la temperatura del aire
                limite_inferior_T_h = df_T_h_bd0[(df_T_h_bd0[col] < -10)].copy()
                if not limite_inferior_T_h.empty:
                   limite_inferior_T_h['Elemento'] = col
                   limite_inferior_T_h['Valor_original'] = limite_inferior_T_h[col]
                   limite_inferior_T_h['Valor_reemplazo'] = 'NA'
                   limite_inferior_T_h['Prueba_deteccion'] = 'valor_menor_a_-10'
                   limite_inferior_T_h['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_T_h.append(limite_inferior_T_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Prueba_deteccion', 'Procedimiento_adoptado']])

                limite_superior_T_h = df_T_h_bd0[(df_T_h_bd0[col] > 45)].copy()
                if not limite_superior_T_h.empty:
                   limite_superior_T_h['Elemento'] = col
                   limite_superior_T_h['Valor_original'] = limite_superior_T_h[col]
                   limite_superior_T_h['Valor_reemplazo'] = 'NA'
                   limite_superior_T_h['Prueba_deteccion'] = 'valor_mayor_a_45'
                   limite_superior_T_h['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_T_h.append(limite_superior_T_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Prueba_deteccion', 'Procedimiento_adoptado']])
                   
            #if col == 'Td.degC.avg.1h.c1':  # Aplica la condicion para la variable de la temperatura de rocio.
                #limite_inferior_Td_h = df_T_h_bd0[(df_T_h_bd0[col] < -20)].copy()
                #if not limite_inferior_T_h.empty:
                   #limite_inferior_Td_h['Elemento'] = col
                   #limite_inferior_Td_h['Valor_original'] = limite_inferior_Td_h[col]
                   #limite_inferior_Td_h['Valor_reemplazo'] = 'NA'
                   #limite_inferior_Td_h['Prueba_deteccion'] = 'valor_menor_a_-20'
                   #limite_inferior_Td_h['Procedimiento_adoptado'] = 'dato_eliminado'
                   #df_no_numerico_T_h.append(limite_inferior_Td_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Prueba_deteccion', 'Procedimiento_adoptado']])

                #limite_superior_Td_h = df_T_h_bd0[(df_T_h_bd0[col] > 40)].copy()
                #if not limite_superior_T_h.empty:
                   #limite_superior_Td_h['Elemento'] = col
                   #limite_superior_Td_h['Valor_original'] = limite_superior_Td_h[col]
                   #limite_superior_Td_h['Valor_reemplazo'] = 'NA'
                   #limite_superior_Td_h['Prueba_deteccion'] = 'valor_mayor_a_40'
                   #limite_superior_Td_h['Procedimiento_adoptado'] = 'dato_eliminado'
                   #df_no_numerico_T_h.append(limite_superior_Td_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Prueba_deteccion', 'Procedimiento_adoptado']])
    
        if df_no_numerico_T_h:
            # Concatena los DataFrames con información sobre valores no numéricos
            carac_no_numerico_T_h = pd.concat(df_no_numerico_T_h, ignore_index=True)
            carac_no_numerico_T_h.rename(columns={'TIMESTAMP': 'Fecha'}, inplace=True)
        
            # Nombre del archivo para guardar los resultados
            nombre_Prueba_numerica_T_h = 'Prueba_numerica_T_h.csv'
           
            # Guarda los resultados en un archivo CSV
            carac_no_numerico_T_h.to_csv(os.path.join(ruta_pruebas_a, nombre_Prueba_numerica_T_h), index=False)
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"Se ha generado exitosamente el archivo de la temperatura horaria: {nombre_Prueba_numerica_T_h}")
            print('')
        else:
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print("No se encontraron caracteres no numéricos o valores igual a -9 en los archivos bd0 de la temperatura horaria.")
            print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la temperatura horaria bd0 para generar el archivo de {nombre_Prueba_numerica_T_h}")
        
Prueba_numerica_T_h()
#------------------------------------------------------------Para la temperatura diaria

def Filtro_caracter_T_d():
    if ruta_T_d_bd0:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_T_d_bd0 = pd.read_csv(ruta_T_d_bd0)
            
         # Agrega condiciones para establecer valores como 'NA' en las columnas específicas
        df_T_d_bd0['Temp.degC.max.dm.s1'] = pd.to_numeric(df_T_d_bd0['Temp.degC.max.dm.s1'], errors='coerce')
        df_T_d_bd0.loc[(df_T_d_bd0['Temp.degC.max.dm.s1'] > 45) | (df_T_d_bd0['Temp.degC.max.dm.s1'] < -5), 'Temp.degC.max.dm.s1'] = 'NA'

        df_T_d_bd0['Temp.degC.min.dm.s1'] = pd.to_numeric(df_T_d_bd0['Temp.degC.min.dm.s1'], errors='coerce')
        df_T_d_bd0.loc[(df_T_d_bd0['Temp.degC.min.dm.s1'] > 40) | (df_T_d_bd0['Temp.degC.min.dm.s1'] < -10), 'Temp.degC.min.dm.s1'] = 'NA'
            
        # Encuentra los índices de filas con valores numéricos en al menos una de las columnas de la temperatura
        indices_numericos_T_d = df_T_d_bd0[(pd.to_numeric(df_T_d_bd0['Temp.degC.max.dm.s1'], errors='coerce').notnull()) | (pd.to_numeric(df_T_d_bd0['Temp.degC.min.dm.s1'], errors='coerce').notnull())].index

        if not indices_numericos_T_d.empty:
            # Filtra las filas con valores numéricos en al menos una de las columnas de la temperatura
            primer_indice_numerico_T_h = indices_numericos_T_d[0]
            ultimo_indice_numerico_T_h = indices_numericos_T_d[-1]

            # Conserva las filas con valores numéricos
            df_T_d_bd0 = df_T_d_bd0.iloc[primer_indice_numerico_T_h:ultimo_indice_numerico_T_h + 1]

            # Conserva los tiempos en formato internacional en las columnas Temp.CST.max.dm.s1 y Temp.CST.min.dm.s1
            col_tiempo = ['Temp.CST.max.dm.s1', 'Temp.CST.min.dm.s1']
            for col in col_tiempo:
                df_T_d_bd0[col] = pd.to_datetime(df_T_d_bd0[col], errors='coerce')

            # Reemplaza valores no numéricos en las columnas de la temperatura por 'NA'
            T_d_col = ['Temp.degC.max.dm.s1', 'Temp.degC.min.dm.s1']
            df_T_d_bd0[T_d_col] = df_T_d_bd0[T_d_col].apply(pd.to_numeric, errors='coerce').applymap(lambda x: 'NA' if pd.isna(x) else x)
            # Reemplaza -9.0 con 'NA'
            df_T_d_bd0[T_d_col] = df_T_d_bd0[T_d_col].replace(-9.0, 'NA')
            
            # Rellena valores no numéricos con el número de estación en la columna ESTACION
            df_T_d_bd0['ESTACION'] = num_estacion

            # Genera el nombre del archivo con bd1
            tiempo_inicial_T_d = pd.to_datetime(df_T_d_bd0.loc[primer_indice_numerico_T_h, 'TIMESTAMP'])
            tiempo_finall_T_d = pd.to_datetime(df_T_d_bd0.iloc[-1]['TIMESTAMP'])
            archivo_depurado_T_d = f"{num_estacion}.{tiempo_inicial_T_d.strftime('%Y%m%d-%H')}.{tiempo_finall_T_d.strftime('%Y%m%d-%H')}.T.d.bd1.csv"

            # Guarda los datos limpios en un nuevo archivo CSV
            df_T_d_bd0.to_csv(os.path.join(ruta_analisis_T, archivo_depurado_T_d), index=False)
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"Se ha depurado exitosamente el archivo de la temperatura diaria bd0 como: {archivo_depurado_T_d}.")
            print('')
        else:
            print("No hay datos numéricos en las columnas de la temperatura.")
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la temperatura diaria bd0 para generar el archivo tipo bd1")

# Ejecuta la función con la ruta de datos crudos
Filtro_caracter_T_d()

def Prueba_numerica_T_d():
    if ruta_T_d_bd0:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_T_d_bd0 = pd.read_csv(ruta_T_d_bd0, keep_default_na=False)
            
        # Obtiene las columnas relevantes excluyendo algunas y 'TIMESTAMP'
        col_rev_T_d = [col for col in df_T_d_bd0.columns if col not in ['Temp.CST.max.dm.s1', 'Temp.CST.min.dm.s1', 'TIMESTAMP']]
    
        df_no_numerico_T_d = []
    
        for col in col_rev_T_d:
            # Filtra las filas sin valores numéricos o vacías en la columna actual
            datos_no_numericos_T_d = df_T_d_bd0[
                (~df_T_d_bd0[col].astype(str).str.match(r'^-?\d*\.?\d*$')) | df_T_d_bd0[col].eq('')
            ].copy()
        
            if not datos_no_numericos_T_d.empty:
                # Agrega información sobre las columnas con valores no numéricos al DataFrame resultante
                datos_no_numericos_T_d['Elemento'] = col
                datos_no_numericos_T_d['Valor_original'] = datos_no_numericos_T_d[col].astype(str)
                
                if col == 'ESTACION':  
                    datos_no_numericos_T_d['Valor_reemplazo'] = num_estacion
                    datos_no_numericos_T_d['Procedimiento_adoptado'] = 'dato_sustituido'
                else:
                    datos_no_numericos_T_d['Valor_reemplazo'] = 'NA'
                    datos_no_numericos_T_d['Procedimiento_adoptado'] = 'dato_eliminado'
                
                datos_no_numericos_T_d['Prueba_deteccion'] = 'valor_no_numerico'
                
                df_no_numerico_T_d.append(datos_no_numericos_T_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Prueba_deteccion', 'Procedimiento_adoptado']])
    
                # Para identificar números no iguales en la columna 'ESTACION'
            rev_est_T_d = df_T_d_bd0[df_T_d_bd0['ESTACION'].apply(lambda x: (isinstance(x, str) and str(x).replace('.', '', 1).isdigit() and float(str(x).replace(',', '.', 1)) != num_estacion))]
            if not rev_est_T_d.empty:
                # Agrega información sobre discrepancias en 'ESTACION' al DataFrame resultante
                rev_est_T_d.loc[:, 'Elemento'] = 'ESTACION'
                rev_est_T_d.loc[:, 'Valor_original'] = rev_est_T_d['ESTACION']
                rev_est_T_d.loc[:, 'Valor_reemplazo'] = num_estacion
                rev_est_T_d.loc[:, 'Prueba_deteccion'] = 'estacion_erronea'
                rev_est_T_d.loc[:, 'Procedimiento_adoptado'] = 'dato_sustituido'

                df_no_numerico_T_d.append(rev_est_T_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Prueba_deteccion', 'Procedimiento_adoptado']])
    
        # Procesamiento de valores -9 fuera del bucle de las columnas
            df_T_d_bd0[col] = pd.to_numeric(df_T_d_bd0[col], errors='coerce')
            datos_menos_9_T_d = df_T_d_bd0[df_T_d_bd0[col] == -9].copy()
            if not datos_menos_9_T_d.empty:
                # Agrega información sobre valores igual a -9 al DataFrame resultante
                datos_menos_9_T_d['Elemento'] = col
                datos_menos_9_T_d['Valor_original'] = -9
                datos_menos_9_T_d['Valor_reemplazo'] = 'NA'
                datos_menos_9_T_d['Prueba_deteccion'] = 'valor_igual_a_-9'
                datos_menos_9_T_d['Procedimiento_adoptado'] = 'dato_eliminado'
                   
                df_no_numerico_T_d.append(datos_menos_9_T_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Prueba_deteccion', 'Procedimiento_adoptado']])
    
            if col == 'Temp.degC.min.dm.s1':  # Aplica la variable para la temperatura del aire minima.
                limite_inferior_Tmin_d = df_T_d_bd0[(df_T_d_bd0[col] < -10)].copy()
                if not limite_inferior_Tmin_d.empty:
                   limite_inferior_Tmin_d['Elemento'] = col
                   limite_inferior_Tmin_d['Valor_original'] = limite_inferior_Tmin_d[col]
                   limite_inferior_Tmin_d['Valor_reemplazo'] = 'NA'
                   limite_inferior_Tmin_d['Prueba_deteccion'] = 'valor_menor_a_-10'
                   limite_inferior_Tmin_d['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_T_d.append(limite_inferior_Tmin_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Prueba_deteccion', 'Procedimiento_adoptado']])

                limite_superior_Tmin_d = df_T_d_bd0[(df_T_d_bd0[col] > 40)].copy()
                if not limite_superior_Tmin_d.empty:
                   limite_superior_Tmin_d['Elemento'] = col
                   limite_superior_Tmin_d['Valor_original'] = limite_superior_Tmin_d[col]
                   limite_superior_Tmin_d['Valor_reemplazo'] = 'NA'
                   limite_superior_Tmin_d['Prueba_deteccion'] = 'valor_mayor_a_40'
                   limite_superior_Tmin_d['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_T_d.append(limite_superior_Tmin_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Prueba_deteccion', 'Procedimiento_adoptado']])
                   
            if col == 'Temp.degC.max.dm.s1':  # Aplica la condicion para la variable de la temperatura del aire maxima.
                limite_inferior_Tmax_d = df_T_d_bd0[(df_T_d_bd0[col] < -5)].copy()
                if not limite_inferior_Tmax_d.empty:
                   limite_inferior_Tmax_d['Elemento'] = col
                   limite_inferior_Tmax_d['Valor_original'] = limite_inferior_Tmax_d[col]
                   limite_inferior_Tmax_d['Valor_reemplazo'] = 'NA'
                   limite_inferior_Tmax_d['Prueba_deteccion'] = 'valor_menor_a_-5'
                   limite_inferior_Tmax_d['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_T_d.append(limite_inferior_Tmax_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Prueba_deteccion', 'Procedimiento_adoptado']])

                limite_superior_Tmax_d = df_T_d_bd0[(df_T_d_bd0[col] > 45)].copy()
                if not limite_superior_Tmax_d.empty:
                   limite_superior_Tmax_d['Elemento'] = col
                   limite_superior_Tmax_d['Valor_original'] = limite_superior_Tmax_d[col]
                   limite_superior_Tmax_d['Valor_reemplazo'] = 'NA'
                   limite_superior_Tmax_d['Prueba_deteccion'] = 'valor_mayor_a_50'
                   limite_superior_Tmax_d['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_T_d.append(limite_superior_Tmax_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Prueba_deteccion', 'Procedimiento_adoptado']])
    
        if df_no_numerico_T_d:
            carac_no_numerico_T_d = pd.concat(df_no_numerico_T_d, ignore_index=True)
            carac_no_numerico_T_d.rename(columns={'TIMESTAMP': 'Fecha'}, inplace=True)
        
            nombre_Prueba_numerica_T_d = 'Prueba_numerica_T_d.csv'
        
            # Guarda los resultados en un archivo CSV
            carac_no_numerico_T_d.to_csv(os.path.join(ruta_pruebas_a, nombre_Prueba_numerica_T_d), index=False)
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"Se ha generado exitosamente el archivo de la temperatura diaria: {nombre_Prueba_numerica_T_d}")
            print('')
        else:
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print("No se encontraron caracteres no numéricos o valores igual a -9 en los archivos bd0 de la temperatura diaria.")
            print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la temperatura diaria bd0 para generar el archivo de {nombre_Prueba_numerica_T_d}")
        
Prueba_numerica_T_d()

def elimina_fila_repetida_err(ruta_archivo):
    if os.path.exists(ruta_archivo):
        # Lee el archivo
        df_prueba = pd.read_csv(ruta_archivo)
        
        # Keep track of the original order
        df_prueba['original_order'] = range(len(df_prueba))
        
        # Create a mask to identify rows with 'Prueba_deteccion' equal to 'valor_igual_a_-9'
        mask = df_prueba['Prueba_deteccion'] == 'valor_igual_a_-9'
        
        # Select rows with 'Prueba_deteccion' equal to 'valor_igual_a_-9' and the first occurrence of each group
        df_prueba = df_prueba[mask | ~df_prueba.duplicated(subset=['Elemento', 'Fecha', 'Valor_original'])]
        
        # Sort back to the original order
        df_prueba = df_prueba.sort_values(by='original_order').drop(columns=['original_order'])
        
        # Rellena la columna Valor_reemplazo con NA
        df_prueba['Valor_reemplazo'] = 'NA'
        
        # Guarda el archivo con el mismo nombre
        df_prueba.to_csv(ruta_archivo, index=False)

# Llama a la función para ejecutar el código con el archivo "Prueba_numerica_R_h.csv" si existe
ruta_prueba_T_h = os.path.join(ruta_pruebas_a, "Prueba_numerica_T_h.csv")
elimina_fila_repetida_err(ruta_prueba_T_h)

# Llama a la función para ejecutar el código con el archivo "Prueba_numerica_R_d.csv" si existe
ruta_prueba_T_d = os.path.join(ruta_pruebas_a, "Prueba_numerica_T_d.csv")
elimina_fila_repetida_err(ruta_prueba_T_d)

# Encuentra el archivo T.d.bd1.csv de la temperatura en la ruta de la estación
ruta_T_d_bd1 = next((os.path.join(ruta_analisis_T, file) for file in os.listdir(ruta_analisis_T) if file.endswith(".csv") and 'T.d.bd1' in file), None)

def fechas_especificas_faltantes_T_d(ruta_T_d_bd1):
    # Cargar el archivo CSV
    df = pd.read_csv(ruta_T_d_bd1)

    df.loc[df['Temp.degC.max.dm.s1'].isna(), 'Temp.CST.max.dm.s1'] = 'NA'
    df['Temp.degC.max.dm.s1'].fillna('NA', inplace=True)


    df.loc[df['Temp.degC.min.dm.s1'].isna(), 'Temp.CST.min.dm.s1'] = 'NA'
    df['Temp.degC.min.dm.s1'].fillna('NA', inplace=True)

    # Guardar los cambios en el mismo archivo
    df.to_csv(ruta_T_d_bd1, index=False)

#fechas_especificas_faltantes_T_d(ruta_T_d_bd1)
