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

#Donde se encuentran los archivos en analisis
ruta_analisis_Ll = f"C:\\MeteoRBD.v1.0.0\\revisión\\{num_estacion}-ema\\Precipitación"

# Combine the directory path and  define folder name
ruta_pruebas_a = os.path.join(ruta_analisis_Ll, "Pruebas_numericas_tiempo")

# Create the folder
os.makedirs(ruta_pruebas_a, exist_ok=True)

# Encuentra el archivo .csv de la Precipitación en la ruta de la estación con 'Ll.h.bd0' en el nombre
ruta_Ll_h_db0 = next((os.path.join(ruta_analisis_Ll, file) for file in os.listdir(ruta_analisis_Ll) if file.endswith(".csv") and 'Ll.h.bd0' in file), None)

# Encuentra el archivo .csv de la Precipitación en la ruta de la estación con 'Ll.d.bd0' en el nombre
ruta_Ll_d_db0 = next((os.path.join(ruta_analisis_Ll, file) for file in os.listdir(ruta_analisis_Ll) if file.endswith(".csv") and 'Ll.d.bd0' in file), None)

#------------------------------------------------------------Para la Precipitación horaria

def Filtro_caracter_Ll_h():
    if ruta_Ll_h_db0:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_Ll_h_bd0 = pd.read_csv(ruta_Ll_h_db0)
            
         # Agrega condiciones para establecer valores como 'NA' en las columnas específicas
        df_Ll_h_bd0['Precip.mm.tot.1h.s1'] = pd.to_numeric(df_Ll_h_bd0['Precip.mm.tot.1h.s1'], errors='coerce')
        df_Ll_h_bd0.loc[(df_Ll_h_bd0['Precip.mm.tot.1h.s1'] > 200) | (df_Ll_h_bd0['Precip.mm.tot.1h.s1'] < 0), 'Precip.mm.tot.1h.s1'] = 'NA'

        # Filtra las filas sin valores numéricos al principio y al final en ciertas columnas
        indices_numericos_Ll_h = df_Ll_h_bd0[df_Ll_h_bd0[['Precip.mm.tot.1h.s1']].apply(pd.to_numeric, errors='coerce').notnull().any(axis=1)].index
        
        # Reemplaza valores no numéricos con 'NA' en ciertas columnas y -9.0 con 'NA'
        reemplazo_columnas_Ll_h = ['Precip.mm.tot.1h.s1']
        for col in reemplazo_columnas_Ll_h:
            df_Ll_h_bd0[col] = pd.to_numeric(df_Ll_h_bd0[col], errors='coerce')
            df_Ll_h_bd0[col] = df_Ll_h_bd0[col].where(df_Ll_h_bd0[col].notnull(), 'NA')
            df_Ll_h_bd0[col] = df_Ll_h_bd0[col].replace(-9.0, 'NA')

        if not indices_numericos_Ll_h.empty:
            primer_indice_numerico_Ll_h = indices_numericos_Ll_h[0]
            ultimo_indice_numerico_Ll_h = indices_numericos_Ll_h[-1]

            # Conserva las filas con valores numéricos
            df_Ll_h_bd0 = df_Ll_h_bd0.iloc[primer_indice_numerico_Ll_h:ultimo_indice_numerico_Ll_h + 1]

            # Rellena valores no numéricos con 'NA' en ciertas columnas y agrega el número de estación en la columna ESTACION
            rellena_caracteres_NA_Ll_h = ['Precip.mm.tot.1h.s1']
            for col in rellena_caracteres_NA_Ll_h:
                df_Ll_h_bd0[col] = pd.to_numeric(df_Ll_h_bd0[col], errors='coerce').fillna('NA')

            df_Ll_h_bd0['ESTACION'] = num_estacion
            
            # Genera el nombre de archivo basado en marcas de tiempo inicial y final
            tiempo_inicial_Ll_h = pd.to_datetime(df_Ll_h_bd0.loc[primer_indice_numerico_Ll_h, 'TIMESTAMP'])
            tiempo_final_Ll_h = pd.to_datetime(df_Ll_h_bd0.loc[ultimo_indice_numerico_Ll_h, 'TIMESTAMP'])
            nombre_depurado_Ll_h = f"{num_estacion}.{tiempo_inicial_Ll_h.strftime('%Y%m%d-%H')}.{tiempo_final_Ll_h.strftime('%Y%m%d-%H')}.Ll.h.bd1.csv"
            
            # Guarda el archivo CSV
            df_Ll_h_bd0.to_csv(os.path.join(ruta_analisis_Ll, nombre_depurado_Ll_h), index=False)
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"Se ha depurado exitosamente el archivo de la lluvia horaria bd0 como: {nombre_depurado_Ll_h}")
            print('')
        else:
            print("No hay datos numéricos en las columnas de la lluvia.")
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la lluvia horaria bd0 para generar el archivo tipo bd1")

Filtro_caracter_Ll_h()

def Prueba_numerica_Ll_h():
    if ruta_Ll_h_db0:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_Ll_h_bd0 = pd.read_csv(ruta_Ll_h_db0, keep_default_na=False)
              
        # Obtiene las columnas relevantes excluyendo 'TIMESTAMP'
        col_rev_Ll_h = [col for col in df_Ll_h_bd0.columns if col not in ['TIMESTAMP']]
    
        df_no_numerico_Ll_h = []
    
        for col in col_rev_Ll_h:
            # Filtra las filas que no contienen valores numéricos o están vacías en la columna actual
            datos_no_numericos_Ll_h = df_Ll_h_bd0[
                (~df_Ll_h_bd0[col].astype(str).str.match(r'^-?\d*\.?\d*$')) | df_Ll_h_bd0[col].eq('')
            ].copy()
        
            if not datos_no_numericos_Ll_h.empty:
                # Agrega información sobre las columnas con valores no numéricos al DataFrame resultante
                datos_no_numericos_Ll_h['Elemento'] = col
                datos_no_numericos_Ll_h['Valor_original'] = datos_no_numericos_Ll_h[col].astype(str)
                
                if col == 'ESTACION':  # Verifica la columna 'ESTACION'
                    datos_no_numericos_Ll_h['Valor_reemplazo'] = num_estacion
                    datos_no_numericos_Ll_h['Procedimiento_adoptado'] = 'dato_sustituido'
                else:
                    datos_no_numericos_Ll_h['Valor_reemplazo'] = 'NA'
                    datos_no_numericos_Ll_h['Procedimiento_adoptado'] = 'dato_eliminado'
                
                datos_no_numericos_Ll_h['Test_deteccion'] = 'valor_no_numerico'
                
                df_no_numerico_Ll_h.append(datos_no_numericos_Ll_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])
            
            # Para identificar números no iguales en la columna 'ESTACION'
            rev_est_Ll_h = df_Ll_h_bd0[df_Ll_h_bd0['ESTACION'].apply(lambda x: (isinstance(x, str) and str(x).replace('.', '', 1).isdigit() and float(str(x).replace(',', '.', 1)) != num_estacion))]
            if not rev_est_Ll_h.empty:
                # Agrega información sobre las discrepancias en 'ESTACION' al DataFrame resultante
                rev_est_Ll_h.loc[:, 'Elemento'] = 'ESTACION'
                rev_est_Ll_h.loc[:, 'Valor_original'] = rev_est_Ll_h['ESTACION']
                rev_est_Ll_h.loc[:, 'Valor_reemplazo'] = num_estacion
                rev_est_Ll_h.loc[:, 'Test_deteccion'] = 'estacion_erronea'
                rev_est_Ll_h.loc[:, 'Procedimiento_adoptado'] = 'dato_sustituido'

                df_no_numerico_Ll_h.append(rev_est_Ll_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])
            
            # Verifica valores específicos (-9) en la columna actual
            # Convierte la columna al tipo numérico (float) ignorando los errores
            df_Ll_h_bd0[col] = pd.to_numeric(df_Ll_h_bd0[col], errors='coerce')
            datos_menos_9_Ll_h = df_Ll_h_bd0[df_Ll_h_bd0[col] == -9].copy()
            if not datos_menos_9_Ll_h.empty:
                # Agrega información sobre valores igual a -9 al DataFrame resultante
                datos_menos_9_Ll_h['Elemento'] = col
                datos_menos_9_Ll_h['Valor_original'] = -9
                datos_menos_9_Ll_h['Valor_reemplazo'] = 'NA'
                datos_menos_9_Ll_h['Test_deteccion'] = 'valor_igual_a_-9'
                datos_menos_9_Ll_h['Procedimiento_adoptado'] = 'dato_eliminado'
                
                df_no_numerico_Ll_h.append(datos_menos_9_Ll_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])
    
            if col == 'Precip.mm.tot.1h.s1':  # Aplica la variable para la Precipitación del aire
                limite_inferior_Ll_h = df_Ll_h_bd0[(df_Ll_h_bd0[col] < 0)].copy()
                if not limite_inferior_Ll_h.empty:
                   limite_inferior_Ll_h['Elemento'] = col
                   limite_inferior_Ll_h['Valor_original'] = limite_inferior_Ll_h[col]
                   limite_inferior_Ll_h['Valor_reemplazo'] = 'NA'
                   limite_inferior_Ll_h['Test_deteccion'] = 'valor_menor/igual_a_0'
                   limite_inferior_Ll_h['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_Ll_h.append(limite_inferior_Ll_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])

                limite_superior_Ll_h = df_Ll_h_bd0[(df_Ll_h_bd0[col] > 200)].copy()
                if not limite_superior_Ll_h.empty:
                   limite_superior_Ll_h['Elemento'] = col
                   limite_superior_Ll_h['Valor_original'] = limite_superior_Ll_h[col]
                   limite_superior_Ll_h['Valor_reemplazo'] = 'NA'
                   limite_superior_Ll_h['Test_deteccion'] = 'valor_mayor_a_100'
                   limite_superior_Ll_h['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_Ll_h.append(limite_superior_Ll_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])
                   
        if df_no_numerico_Ll_h:
            # Concatena los DataFrames con información sobre valores no numéricos
            carac_no_numerico_Ll_h = pd.concat(df_no_numerico_Ll_h, ignore_index=True)
            carac_no_numerico_Ll_h.rename(columns={'TIMESTAMP': 'Fecha'}, inplace=True)
        
            # Nombre del archivo para guardar los resultados
            nombre_Prueba_numerica_Ll_h = 'Prueba_numerica_Ll_h.csv'
           
            # Guarda los resultados en un archivo CSV
            carac_no_numerico_Ll_h.to_csv(os.path.join(ruta_pruebas_a, nombre_Prueba_numerica_Ll_h), index=False)
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"Se ha generado exitosamente el archivo de la lluvia horaria: {nombre_Prueba_numerica_Ll_h}")
            print('')
        else:
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print("No se encontraron caracteres no numéricos o valores igual a -9 en los archivos bd0 de la lluvia horaria.")
            print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la lluvia horaria bd0 para generar el archivo de {nombre_Prueba_numerica_Ll_h}")
        
Prueba_numerica_Ll_h()
#------------------------------------------------------------Para la Precipitación diaria

def Filtro_caracter_Ll_d():
    if ruta_Ll_d_db0:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_Ll_d_bd0 = pd.read_csv(ruta_Ll_d_db0)
            
         # Agrega condiciones para establecer valores como 'NA' en las columnas específicas
        df_Ll_d_bd0['Precip.mm.tot.dm.s1'] = pd.to_numeric(df_Ll_d_bd0['Precip.mm.tot.dm.s1'], errors='coerce')
        df_Ll_d_bd0.loc[(df_Ll_d_bd0['Precip.mm.tot.dm.s1'] > 200) | (df_Ll_d_bd0['Precip.mm.tot.dm.s1'] < 0), 'Precip.mm.tot.dm.s1'] = 'NA'

            
        # Encuentra los índices de filas con valores numéricos en al menos una de las columnas de la Precipitación
        indices_numericos_Ll_d = df_Ll_d_bd0[(pd.to_numeric(df_Ll_d_bd0['Precip.mm.tot.dm.s1'], errors='coerce').notnull())].index

        if not indices_numericos_Ll_d.empty:
            # Filtra las filas con valores numéricos en al menos una de las columnas de la Precipitación
            primer_indice_numerico_Ll_h = indices_numericos_Ll_d[0]
            ultimo_indice_numerico_Ll_h = indices_numericos_Ll_d[-1]

            # Conserva las filas con valores numéricos
            df_Ll_d_bd0 = df_Ll_d_bd0.iloc[primer_indice_numerico_Ll_h:ultimo_indice_numerico_Ll_h + 1]

            # Reemplaza valores no numéricos en las columnas de la Precipitación por 'NA'
            Ll_d_col = ['Precip.mm.tot.dm.s1', 'Precip-acum5.mm_h.max.dm.s1', 'Precip-acum10.mm_h.max.dm.s1', 'Precip-acum15.mm_h.max.dm.s1', 'Precip-acum30.mm_h.max.dm.s1']
            df_Ll_d_bd0[Ll_d_col] = df_Ll_d_bd0[Ll_d_col].apply(pd.to_numeric, errors='coerce').applymap(lambda x: 'NA' if pd.isna(x) else x)
            # Reemplaza -9.0 con 'NA'
            df_Ll_d_bd0[Ll_d_col] = df_Ll_d_bd0[Ll_d_col].replace(-9.0, 'NA')
            
            # Rellena valores no numéricos con el número de estación en la columna ESTACION
            df_Ll_d_bd0['ESTACION'] = num_estacion

            # Genera el nombre del archivo con bd1
            tiempo_inicial_Ll_d = pd.to_datetime(df_Ll_d_bd0.loc[primer_indice_numerico_Ll_h, 'TIMESTAMP'])
            tiempo_finall_Ll_d = pd.to_datetime(df_Ll_d_bd0.iloc[-1]['TIMESTAMP'])
            archivo_depurado_Ll_d = f"{num_estacion}.{tiempo_inicial_Ll_d.strftime('%Y%m%d-%H')}.{tiempo_finall_Ll_d.strftime('%Y%m%d-%H')}.Ll.d.bd1.csv"

            # Guarda los datos limpios en un nuevo archivo CSV
            df_Ll_d_bd0.to_csv(os.path.join(ruta_analisis_Ll, archivo_depurado_Ll_d), index=False)
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"Se ha depurado exitosamente el archivo de la lluvia diaria bd0 como: {archivo_depurado_Ll_d}.")
            print('')
        else:
            print("No hay datos numéricos en las columnas de la lluvia.")
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la lluvia diaria bd0 para generar el archivo tipo bd1")

# Ejecuta la función con la ruta de datos crudos
Filtro_caracter_Ll_d()

def Prueba_numerica_Ll_d():
    if ruta_Ll_d_db0:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_Ll_d_bd0 = pd.read_csv(ruta_Ll_d_db0, keep_default_na=False)
            
        # Obtiene las columnas relevantes excluyendo algunas y 'TIMESTAMP'
        col_rev_Ll_d = [col for col in df_Ll_d_bd0.columns if col not in ['TIMESTAMP']]
    
        df_no_numerico_Ll_d = []
    
        for col in col_rev_Ll_d:
            # Filtra las filas sin valores numéricos o vacías en la columna actual
            datos_no_numericos_Ll_d = df_Ll_d_bd0[
                (~df_Ll_d_bd0[col].astype(str).str.match(r'^-?\d*\.?\d*$')) | df_Ll_d_bd0[col].eq('')
            ].copy()
        
            if not datos_no_numericos_Ll_d.empty:
                # Agrega información sobre las columnas con valores no numéricos al DataFrame resultante
                datos_no_numericos_Ll_d['Elemento'] = col
                datos_no_numericos_Ll_d['Valor_original'] = datos_no_numericos_Ll_d[col].astype(str)
                
                if col == 'ESTACION':  
                    datos_no_numericos_Ll_d['Valor_reemplazo'] = num_estacion
                    datos_no_numericos_Ll_d['Procedimiento_adoptado'] = 'dato_sustituido'
                else:
                    datos_no_numericos_Ll_d['Valor_reemplazo'] = 'NA'
                    datos_no_numericos_Ll_d['Procedimiento_adoptado'] = 'dato_eliminado'
                
                datos_no_numericos_Ll_d['Test_deteccion'] = 'valor_no_numerico'
                
                df_no_numerico_Ll_d.append(datos_no_numericos_Ll_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])
    
                # Para identificar números no iguales en la columna 'ESTACION'
            rev_est_Ll_d = df_Ll_d_bd0[df_Ll_d_bd0['ESTACION'].apply(lambda x: (isinstance(x, str) and str(x).replace('.', '', 1).isdigit() and float(str(x).replace(',', '.', 1)) != num_estacion))]
            if not rev_est_Ll_d.empty:
                # Agrega información sobre discrepancias en 'ESTACION' al DataFrame resultante
                rev_est_Ll_d.loc[:, 'Elemento'] = 'ESTACION'
                rev_est_Ll_d.loc[:, 'Valor_original'] = rev_est_Ll_d['ESTACION']
                rev_est_Ll_d.loc[:, 'Valor_reemplazo'] = num_estacion
                rev_est_Ll_d.loc[:, 'Test_deteccion'] = 'estacion_erronea'
                rev_est_Ll_d.loc[:, 'Procedimiento_adoptado'] = 'dato_sustituido'

                df_no_numerico_Ll_d.append(rev_est_Ll_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])
    
        # Procesamiento de valores -9 fuera del bucle de las columnas
            df_Ll_d_bd0[col] = pd.to_numeric(df_Ll_d_bd0[col], errors='coerce')
            datos_menos_9_Ll_d = df_Ll_d_bd0[df_Ll_d_bd0[col] == -9].copy()
            if not datos_menos_9_Ll_d.empty:
                # Agrega información sobre valores igual a -9 al DataFrame resultante
                datos_menos_9_Ll_d['Elemento'] = col
                datos_menos_9_Ll_d['Valor_original'] = -9
                datos_menos_9_Ll_d['Valor_reemplazo'] = 'NA'
                datos_menos_9_Ll_d['Test_deteccion'] = 'valor_igual_a_-9'
                datos_menos_9_Ll_d['Procedimiento_adoptado'] = 'dato_eliminado'
                   
                df_no_numerico_Ll_d.append(datos_menos_9_Ll_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])
               
            if col == 'Precip.mm.tot.dm.s1':  # Aplica la condicion para la variable de la Precipitación del aire maxima.
                limite_inferior_Llmax_d = df_Ll_d_bd0[(df_Ll_d_bd0[col] < 0)].copy()
                if not limite_inferior_Llmax_d.empty:
                   limite_inferior_Llmax_d['Elemento'] = col
                   limite_inferior_Llmax_d['Valor_original'] = limite_inferior_Llmax_d[col]
                   limite_inferior_Llmax_d['Valor_reemplazo'] = 'NA'
                   limite_inferior_Llmax_d['Test_deteccion'] = 'valor_menor_a_0'
                   limite_inferior_Llmax_d['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_Ll_d.append(limite_inferior_Llmax_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])

                limite_superior_Llmax_d = df_Ll_d_bd0[(df_Ll_d_bd0[col] > 200)].copy()
                if not limite_superior_Llmax_d.empty:
                   limite_superior_Llmax_d['Elemento'] = col
                   limite_superior_Llmax_d['Valor_original'] = limite_superior_Llmax_d[col]
                   limite_superior_Llmax_d['Valor_reemplazo'] = 'NA'
                   limite_superior_Llmax_d['Test_deteccion'] = 'valor_mayor_a_200'
                   limite_superior_Llmax_d['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_Ll_d.append(limite_superior_Llmax_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])
    
            if col == 'Precip-acum5.mm_h.max.dm.s1':  # Aplica la condicion para la variable de la Precipitación del aire maxima.
                limite_inferior_5mm_d = df_Ll_d_bd0[(df_Ll_d_bd0[col] < 0)].copy()
                if not limite_inferior_5mm_d.empty:
                   limite_inferior_5mm_d['Elemento'] = col
                   limite_inferior_5mm_d['Valor_original'] = limite_inferior_5mm_d[col]
                   limite_inferior_5mm_d['Valor_reemplazo'] = 'NA'
                   limite_inferior_5mm_d['Test_deteccion'] = 'valor_menor_a_10'
                   limite_inferior_5mm_d['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_Ll_d.append(limite_inferior_5mm_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])

                limite_superior_5mm_d = df_Ll_d_bd0[(df_Ll_d_bd0[col] > 60)].copy()
                if not limite_superior_5mm_d.empty:
                   limite_superior_5mm_d['Elemento'] = col
                   limite_superior_5mm_d['Valor_original'] = limite_superior_5mm_d[col]
                   limite_superior_5mm_d['Valor_reemplazo'] = 'NA'
                   limite_superior_5mm_d['Test_deteccion'] = 'valor_mayor_a_60'
                   limite_superior_5mm_d['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_Ll_d.append(limite_superior_5mm_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])
                   
            if col == 'Precip-acum10.mm_h.max.dm.s1':  # Aplica la condicion para la variable de la Precipitación del aire maxima.
                limite_inferior_10mm_d = df_Ll_d_bd0[(df_Ll_d_bd0[col] < 0)].copy()
                if not limite_inferior_10mm_d.empty:
                   limite_inferior_10mm_d['Elemento'] = col
                   limite_inferior_10mm_d['Valor_original'] = limite_inferior_10mm_d[col]
                   limite_inferior_10mm_d['Valor_reemplazo'] = 'NA'
                   limite_inferior_10mm_d['Test_deteccion'] = 'valor_menor_a_10'
                   limite_inferior_10mm_d['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_Ll_d.append(limite_inferior_10mm_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])

                limite_superior_10mm_d = df_Ll_d_bd0[(df_Ll_d_bd0[col] > 90)].copy()
                if not limite_superior_10mm_d.empty:
                   limite_superior_10mm_d['Elemento'] = col
                   limite_superior_10mm_d['Valor_original'] = limite_superior_10mm_d[col]
                   limite_superior_10mm_d['Valor_reemplazo'] = 'NA'
                   limite_superior_10mm_d['Test_deteccion'] = 'valor_mayor_a_60'
                   limite_superior_10mm_d['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_Ll_d.append(limite_superior_10mm_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])
    
            if col == 'Precip-acum15.mm_h.max.dm.s1':  # Aplica la condicion para la variable de la Precipitación del aire maxima.
                limite_inferior_15mm_d = df_Ll_d_bd0[(df_Ll_d_bd0[col] < 0)].copy()
                if not limite_inferior_15mm_d.empty:
                   limite_inferior_15mm_d['Elemento'] = col
                   limite_inferior_15mm_d['Valor_original'] = limite_inferior_15mm_d[col]
                   limite_inferior_15mm_d['Valor_reemplazo'] = 'NA'
                   limite_inferior_15mm_d['Test_deteccion'] = 'valor_menor_a_10'
                   limite_inferior_15mm_d['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_Ll_d.append(limite_inferior_15mm_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])

                limite_superior_15mm_d = df_Ll_d_bd0[(df_Ll_d_bd0[col] > 120)].copy()
                if not limite_superior_15mm_d.empty:
                   limite_superior_15mm_d['Elemento'] = col
                   limite_superior_15mm_d['Valor_original'] = limite_superior_15mm_d[col]
                   limite_superior_15mm_d['Valor_reemplazo'] = 'NA'
                   limite_superior_15mm_d['Test_deteccion'] = 'valor_mayor_a_60'
                   limite_superior_15mm_d['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_Ll_d.append(limite_superior_15mm_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])
    
            if col == 'Precip-acum30.mm_h.max.dm.s1':  # Aplica la condicion para la variable de la Precipitación del aire maxima.
                limite_inferior_30mm_d = df_Ll_d_bd0[(df_Ll_d_bd0[col] < 0)].copy()
                if not limite_inferior_30mm_d.empty:
                   limite_inferior_30mm_d['Elemento'] = col
                   limite_inferior_30mm_d['Valor_original'] = limite_inferior_30mm_d[col]
                   limite_inferior_30mm_d['Valor_reemplazo'] = 'NA'
                   limite_inferior_30mm_d['Test_deteccion'] = 'valor_menor_a_10'
                   limite_inferior_30mm_d['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_Ll_d.append(limite_inferior_30mm_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])

                limite_superior_30mm_d = df_Ll_d_bd0[(df_Ll_d_bd0[col] > 150)].copy()
                if not limite_superior_30mm_d.empty:
                   limite_superior_30mm_d['Elemento'] = col
                   limite_superior_30mm_d['Valor_original'] = limite_superior_30mm_d[col]
                   limite_superior_30mm_d['Valor_reemplazo'] = 'NA'
                   limite_superior_30mm_d['Test_deteccion'] = 'valor_mayor_a_60'
                   limite_superior_30mm_d['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_Ll_d.append(limite_superior_30mm_d[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])
    
        if df_no_numerico_Ll_d:
            carac_no_numerico_Ll_d = pd.concat(df_no_numerico_Ll_d, ignore_index=True)
            carac_no_numerico_Ll_d.rename(columns={'TIMESTAMP': 'Fecha'}, inplace=True)
        
            nombre_Prueba_numerica_Ll_d = 'Prueba_numerica_Ll_d.csv'
        
            # Guarda los resultados en un archivo CSV
            carac_no_numerico_Ll_d.to_csv(os.path.join(ruta_pruebas_a, nombre_Prueba_numerica_Ll_d), index=False)
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"Se ha generado exitosamente el archivo de la lluvia diaria: {nombre_Prueba_numerica_Ll_d}")
            print('')
        else:
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print("No se encontraron caracteres no numéricos o valores igual a -9 en los archivos bd0 de la lluvia diaria.")
            print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la lluvia diaria bd0 para generar el archivo de {nombre_Prueba_numerica_Ll_d}")
        
Prueba_numerica_Ll_d()

def elimina_fila_repetida_err(ruta_archivo):
    if os.path.exists(ruta_archivo):
        # Lee el archivo
        df_prueba = pd.read_csv(ruta_archivo)
        
        # Keep track of the original order
        df_prueba['original_order'] = range(len(df_prueba))
        
        # Create a mask to identify rows with 'Test_deteccion' equal to 'valor_igual_a_-9'
        mask = df_prueba['Test_deteccion'] == 'valor_igual_a_-9'
        
        # Select rows with 'Test_deteccion' equal to 'valor_igual_a_-9' and the first occurrence of each group
        df_prueba = df_prueba[mask | ~df_prueba.duplicated(subset=['Elemento', 'Fecha', 'Valor_original'])]
        
        # Sort back to the original order
        df_prueba = df_prueba.sort_values(by='original_order').drop(columns=['original_order'])
        
        # Rellena la columna Valor_reemplazo con NA
        df_prueba['Valor_reemplazo'] = 'NA'
        
        # Guarda el archivo con el mismo nombre
        df_prueba.to_csv(ruta_archivo, index=False)

# Llama a la función para ejecutar el código con el archivo "Prueba_numerica_R_h.csv" si existe
ruta_prueba_Ll_h = os.path.join(ruta_pruebas_a, "Prueba_numerica_Ll_h.csv")
elimina_fila_repetida_err(ruta_prueba_Ll_h)

# Llama a la función para ejecutar el código con el archivo "Prueba_numerica_R_d.csv" si existe
ruta_prueba_Ll_d = os.path.join(ruta_pruebas_a, "Prueba_numerica_Ll_d.csv")
elimina_fila_repetida_err(ruta_prueba_Ll_d)