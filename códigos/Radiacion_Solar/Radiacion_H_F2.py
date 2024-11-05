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

ruta_archivo = next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Radiación" in file and file.endswith(".xlsx")), None)

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
ruta_analisis_R = f"C:\\MeteoRBD.v1.0.0\\revisión\\{num_estacion}-ema\\Radiación Solar"

# Combine the directory path and  define folder name
ruta_pruebas_a = os.path.join(ruta_analisis_R, "Pruebas_numericas_tiempo")

# Create the folder
os.makedirs(ruta_pruebas_a, exist_ok=True)

# Encuentra el archivo .csv de la Radiación en la ruta de la estación con 'R.h.bd0' en el nombre
ruta_R_h_db0 = next((os.path.join(ruta_analisis_R, file) for file in os.listdir(ruta_analisis_R) if file.endswith(".csv") and 'R.h.bd0' in file), None)

#------------------------------------------------------------Para la radiación solar horaria

def Filtro_caracter_R_h():
    if ruta_R_h_db0:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_R_h_bd0 = pd.read_csv(ruta_R_h_db0)
            
         # Agrega condiciones para establecer valores como 'NA' en las columnas específicas
        df_R_h_bd0['Rad.MJ_m2.tot.1h.s1'] = pd.to_numeric(df_R_h_bd0['Rad.MJ_m2.tot.1h.s1'], errors='coerce')
        df_R_h_bd0.loc[(df_R_h_bd0['Rad.MJ_m2.tot.1h.s1'] > 5) | (df_R_h_bd0['Rad.MJ_m2.tot.1h.s1'] < 0), 'Rad.MJ_m2.tot.1h.s1'] = 'NA'

        df_R_h_bd0['Rad.kW_m2.max.1h.s1'] = pd.to_numeric(df_R_h_bd0['Rad.kW_m2.max.1h.s1'], errors='coerce')
        df_R_h_bd0.loc[(df_R_h_bd0['Rad.kW_m2.max.1h.s1'] > 3) | (df_R_h_bd0['Rad.kW_m2.max.1h.s1'] < 0), 'Rad.kW_m2.max.1h.s1'] = 'NA'
        
        # Agrega condiciones para establecer valores como 'NA' en las columnas específicas
        df_R_h_bd0['Rad.kW_m2.min.1h.s1'] = pd.to_numeric(df_R_h_bd0['Rad.kW_m2.min.1h.s1'], errors='coerce')
        df_R_h_bd0.loc[(df_R_h_bd0['Rad.kW_m2.min.1h.s1'] > 2) | (df_R_h_bd0['Rad.kW_m2.min.1h.s1'] < 0), 'Rad.kW_m2.min.1h.s1'] = 'NA'

        df_R_h_bd0['Rad-int_sol.min_hour.tot.1h.s1'] = pd.to_numeric(df_R_h_bd0['Rad-int_sol.min_hour.tot.1h.s1'], errors='coerce')
        df_R_h_bd0.loc[(df_R_h_bd0['Rad-int_sol.min_hour.tot.1h.s1'] > 60) | (df_R_h_bd0['Rad-int_sol.min_hour.tot.1h.s1'] < 0), 'Rad-int_sol.min_hour.tot.1h.s1'] = 'NA'
        
        # Filtra las filas sin valores numéricos al principio y al final en ciertas columnas
        indices_numericos_R_h = df_R_h_bd0[df_R_h_bd0[['Rad.MJ_m2.tot.1h.s1', 'Rad.kW_m2.max.1h.s1', 'Rad.kW_m2.min.1h.s1', 'Rad-int_sol.min_hour.tot.1h.s1']].apply(pd.to_numeric, errors='coerce').notnull().any(axis=1)].index
        
        # Reemplaza valores no numéricos con 'NA' en ciertas columnas y -9.0 con 'NA'
        reemplazo_columnas_R_h = ['Rad.MJ_m2.tot.1h.s1', 'Rad.kW_m2.max.1h.s1', 'Rad.kW_m2.min.1h.s1', 'Rad-int_sol.min_hour.tot.1h.s1']
        for col in reemplazo_columnas_R_h:
            df_R_h_bd0[col] = pd.to_numeric(df_R_h_bd0[col], errors='coerce')
            df_R_h_bd0[col] = df_R_h_bd0[col].where(df_R_h_bd0[col].notnull(), 'NA')
            df_R_h_bd0[col] = df_R_h_bd0[col].replace(-9.0, 'NA')

        if not indices_numericos_R_h.empty:
            primer_indice_numerico_R_h = indices_numericos_R_h[0]
            ultimo_indice_numerico_R_h = indices_numericos_R_h[-1]

            # Conserva las filas con valores numéricos
            df_R_h_bd0 = df_R_h_bd0.iloc[primer_indice_numerico_R_h:ultimo_indice_numerico_R_h + 1]

            # Rellena valores no numéricos con 'NA' en ciertas columnas y agrega el número de estación en la columna ESTACION
            rellena_caracteres_NA_R_h = ['Rad.MJ_m2.tot.1h.s1', 'Rad.kW_m2.max.1h.s1', 'Rad.kW_m2.min.1h.s1', 'Rad-int_sol.min_hour.tot.1h.s1']
            for col in rellena_caracteres_NA_R_h:
                df_R_h_bd0[col] = pd.to_numeric(df_R_h_bd0[col], errors='coerce').fillna('NA')

            df_R_h_bd0['ESTACION'] = num_estacion
            
            # Genera el nombre de archivo basado en marcas de tiempo inicial y final
            tiempo_inicial_R_h = pd.to_datetime(df_R_h_bd0.loc[primer_indice_numerico_R_h, 'TIMESTAMP'])
            tiempo_final_R_h = pd.to_datetime(df_R_h_bd0.loc[ultimo_indice_numerico_R_h, 'TIMESTAMP'])
            nombre_depurado_R_h = f"{num_estacion}.{tiempo_inicial_R_h.strftime('%Y%m%d-%H')}.{tiempo_final_R_h.strftime('%Y%m%d-%H')}.R.h.bd1.csv"
            
            # Guarda el archivo CSV
            df_R_h_bd0.to_csv(os.path.join(ruta_analisis_R, nombre_depurado_R_h), index=False)
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"Se ha depurado exitosamente el archivo de la radiación solar horaria bd0 como: {nombre_depurado_R_h}")
            print('')
        else:
            print("No hay datos numéricos en las columnas de la Radiación.")
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la radiación solar horaria bd0 para generar el archivo tipo bd1")

Filtro_caracter_R_h()

def Prueba_numerica_R_h():
    if ruta_R_h_db0:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_R_h_bd0 = pd.read_csv(ruta_R_h_db0, keep_default_na=False)
              
        # Obtiene las columnas relevantes excluyendo 'TIMESTAMP'
        col_rev_R_h = [col for col in df_R_h_bd0.columns if col not in ['TIMESTAMP']]
    
        df_no_numerico_R_h = []
    
        for col in col_rev_R_h:
            # Filtra las filas que no contienen valores numéricos o están vacías en la columna actual
            datos_no_numericos_R_h = df_R_h_bd0[
                (~df_R_h_bd0[col].astype(str).str.match(r'^-?\d*\.?\d*$')) | df_R_h_bd0[col].eq('')
            ].copy()
        
            if not datos_no_numericos_R_h.empty:
                # Agrega información sobre las columnas con valores no numéricos al DataFrame resultante
                datos_no_numericos_R_h['Elemento'] = col
                datos_no_numericos_R_h['Valor_original'] = datos_no_numericos_R_h[col].astype(str)
                
                if col == 'ESTACION':  # Verifica la columna 'ESTACION'
                    datos_no_numericos_R_h['Valor_reemplazo'] = num_estacion
                    datos_no_numericos_R_h['Procedimiento_adoptado'] = 'dato_sustituido'
                else:
                    datos_no_numericos_R_h['Valor_reemplazo'] = 'NA'
                    datos_no_numericos_R_h['Procedimiento_adoptado'] = 'dato_eliminado'
                
                datos_no_numericos_R_h['Test_deteccion'] = 'valor_no_numerico'
                
                df_no_numerico_R_h.append(datos_no_numericos_R_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])
            
            # Para identificar números no iguales en la columna 'ESTACION'
            rev_est_R_h = df_R_h_bd0[df_R_h_bd0['ESTACION'].apply(lambda x: (isinstance(x, str) and str(x).replace('.', '', 1).isdigit() and float(str(x).replace(',', '.', 1)) != num_estacion))]
            if not rev_est_R_h.empty:
                # Agrega información sobre las discrepancias en 'ESTACION' al DataFrame resultante
                rev_est_R_h.loc[:, 'Elemento'] = 'ESTACION'
                rev_est_R_h.loc[:, 'Valor_original'] = rev_est_R_h['ESTACION']
                rev_est_R_h.loc[:, 'Valor_reemplazo'] = num_estacion
                rev_est_R_h.loc[:, 'Test_deteccion'] = 'estacion_erronea'
                rev_est_R_h.loc[:, 'Procedimiento_adoptado'] = 'dato_sustituido'

                df_no_numerico_R_h.append(rev_est_R_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])
            
            # Verifica valores específicos (-9) en la columna actual
            # Convierte la columna al tipo numérico (float) ignorando los errores
            df_R_h_bd0[col] = pd.to_numeric(df_R_h_bd0[col], errors='coerce')
            datos_menos_9_R_h = df_R_h_bd0[df_R_h_bd0[col] == -9].copy()
            if not datos_menos_9_R_h.empty:
                # Agrega información sobre valores igual a -9 al DataFrame resultante
                datos_menos_9_R_h['Elemento'] = col
                datos_menos_9_R_h['Valor_original'] = -9
                datos_menos_9_R_h['Valor_reemplazo'] = 'NA'
                datos_menos_9_R_h['Test_deteccion'] = 'valor_igual_a_-9'
                datos_menos_9_R_h['Procedimiento_adoptado'] = 'dato_eliminado'
                
                df_no_numerico_R_h.append(datos_menos_9_R_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])
    
            if col == 'Rad.MJ_m2.tot.1h.s1':  # Aplica la variable para la Radiación del aire
                limite_inferior_Rtot_h = df_R_h_bd0[(df_R_h_bd0[col] < 0)].copy()
                if not limite_inferior_Rtot_h.empty:
                   limite_inferior_Rtot_h['Elemento'] = col
                   limite_inferior_Rtot_h['Valor_original'] = limite_inferior_Rtot_h[col]
                   limite_inferior_Rtot_h['Valor_reemplazo'] = 'NA'
                   limite_inferior_Rtot_h['Test_deteccion'] = 'valor_menor_a_0'
                   limite_inferior_Rtot_h['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_R_h.append(limite_inferior_Rtot_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])

                limite_superior_Rtot_h = df_R_h_bd0[(df_R_h_bd0[col] > 5)].copy()
                if not limite_superior_Rtot_h.empty:
                   limite_superior_Rtot_h['Elemento'] = col
                   limite_superior_Rtot_h['Valor_original'] = limite_superior_Rtot_h[col]
                   limite_superior_Rtot_h['Valor_reemplazo'] = 'NA'
                   limite_superior_Rtot_h['Test_deteccion'] = 'valor_mayor_a_5'
                   limite_superior_Rtot_h['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_R_h.append(limite_superior_Rtot_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])
                   
            if col == 'Rad.kW_m2.max.1h.s1':  # Aplica la condicion para la variable de la Radiación de rocio.
                limite_inferior_Rmax_h = df_R_h_bd0[(df_R_h_bd0[col] < 0)].copy()
                if not limite_inferior_Rmax_h.empty:
                   limite_inferior_Rmax_h['Elemento'] = col
                   limite_inferior_Rmax_h['Valor_original'] = limite_inferior_Rmax_h[col]
                   limite_inferior_Rmax_h['Valor_reemplazo'] = 'NA'
                   limite_inferior_Rmax_h['Test_deteccion'] = 'valor_menor_a_0'
                   limite_inferior_Rmax_h['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_R_h.append(limite_inferior_Rmax_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])

                limite_superior_Rmax_h = df_R_h_bd0[(df_R_h_bd0[col] > 3)].copy()
                if not limite_superior_Rmax_h.empty:
                   limite_superior_Rmax_h['Elemento'] = col
                   limite_superior_Rmax_h['Valor_original'] = limite_superior_Rmax_h[col]
                   limite_superior_Rmax_h['Valor_reemplazo'] = 'NA'
                   limite_superior_Rmax_h['Test_deteccion'] = 'valor_mayor_a_3'
                   limite_superior_Rmax_h['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_R_h.append(limite_superior_Rmax_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])
    
            if col == 'Rad.kW_m2.min.1h.s1':  # Aplica la condicion para la variable de la Radiación de rocio.
                limite_inferior_Rmin_h = df_R_h_bd0[(df_R_h_bd0[col] < 0)].copy()
                if not limite_inferior_Rmin_h.empty:
                   limite_inferior_Rmin_h['Elemento'] = col
                   limite_inferior_Rmin_h['Valor_original'] = limite_inferior_Rmin_h[col]
                   limite_inferior_Rmin_h['Valor_reemplazo'] = 'NA'
                   limite_inferior_Rmin_h['Test_deteccion'] = 'valor_menor_a_0'
                   limite_inferior_Rmin_h['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_R_h.append(limite_inferior_Rmin_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])

                limite_superior_Rmin_h = df_R_h_bd0[(df_R_h_bd0[col] > 2)].copy()
                if not limite_superior_Rmin_h.empty:
                   limite_superior_Rmin_h['Elemento'] = col
                   limite_superior_Rmin_h['Valor_original'] = limite_superior_Rmin_h[col]
                   limite_superior_Rmin_h['Valor_reemplazo'] = 'NA'
                   limite_superior_Rmin_h['Test_deteccion'] = 'valor_mayor_a_2'
                   limite_superior_Rmin_h['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_R_h.append(limite_superior_Rmin_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])
    
            if col == 'Rad-int_sol.min_hour.tot.1h.s1':  # Aplica la condicion para la variable de la Radiación de rocio.
                limite_inferior_Rint_h = df_R_h_bd0[(df_R_h_bd0[col] < 0)].copy()
                if not limite_inferior_Rint_h.empty:
                   limite_inferior_Rint_h['Elemento'] = col
                   limite_inferior_Rint_h['Valor_original'] = limite_inferior_Rint_h[col]
                   limite_inferior_Rint_h['Valor_reemplazo'] = 'NA'
                   limite_inferior_Rint_h['Test_deteccion'] = 'valor_menor_a_0'
                   limite_inferior_Rint_h['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_R_h.append(limite_inferior_Rint_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])

                limite_superior_Rint_h = df_R_h_bd0[(df_R_h_bd0[col] > 60)].copy()
                if not limite_superior_Rint_h.empty:
                   limite_superior_Rint_h['Elemento'] = col
                   limite_superior_Rint_h['Valor_original'] = limite_superior_Rint_h[col]
                   limite_superior_Rint_h['Valor_reemplazo'] = 'NA'
                   limite_superior_Rint_h['Test_deteccion'] = 'valor_mayor_a_60'
                   limite_superior_Rint_h['Procedimiento_adoptado'] = 'dato_eliminado'
                   df_no_numerico_R_h.append(limite_superior_Rint_h[['Elemento', 'TIMESTAMP', 'Valor_original', 'Valor_reemplazo', 'Test_deteccion', 'Procedimiento_adoptado']])
    
        if df_no_numerico_R_h:
            # Concatena los DataFrames con información sobre valores no numéricos
            carac_no_numerico_R_h = pd.concat(df_no_numerico_R_h, ignore_index=True)
            carac_no_numerico_R_h.rename(columns={'TIMESTAMP': 'Fecha'}, inplace=True)
        
            # Nombre del archivo para guardar los resultados
            nombre_Prueba_numerica_R_h = 'Prueba_numerica_R_h.csv'
           
            # Guarda los resultados en un archivo CSV
            carac_no_numerico_R_h.to_csv(os.path.join(ruta_pruebas_a, nombre_Prueba_numerica_R_h), index=False)
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"Se ha generado exitosamente el archivo de la radiación solar horaria: {nombre_Prueba_numerica_R_h}")
            print('')
        else:
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print("No se encontraron caracteres no numéricos o valores igual a -9 en los archivos bd0 de la radiación solar horaria.")
            print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la radiación solar horaria bd0 para generar el archivo de {nombre_Prueba_numerica_R_h}")
        
Prueba_numerica_R_h()
#------------------------------------------------------------


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
ruta_prueba_R_h = os.path.join(ruta_pruebas_a, "Prueba_numerica_R_h.csv")
elimina_fila_repetida_err(ruta_prueba_R_h)