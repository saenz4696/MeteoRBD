import pandas as pd
import os
import warnings
import shutil
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates


# Eliminar UserWarnings de openpyxl
warnings.simplefilter('ignore', category=UserWarning)

datos_crudos = r'C:\\MeteoRBD.v1.0.0\\datos_rbd'

# Encuentra el archivo .xlsx en los datos_crudos que contiene 'Cuenca' y 'Estación' como columnas
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

# Establece la ruta para los archivos de el viento según el número de estación obtenido del archivo Excel
ruta_analisis_V = f"C:\\MeteoRBD.v1.0.0\\revisión\\{num_estacion}-ema\\Viento"

# Crea las carpetas si no existen
for carpeta in ["", "Pruebas_estadisticas"]:
    ruta_pruebas_b = os.path.join(ruta_analisis_V, carpeta)
    os.makedirs(ruta_pruebas_b, exist_ok=True)
    
# Encuentra el archivo V.h.bd2.csv de el viento en la ruta de la estación
ruta_V_h_bd2 = next((os.path.join(ruta_analisis_V, archivo) for archivo in os.listdir(ruta_analisis_V) if archivo.endswith(".csv") and 'V.h.bd2' in archivo), None)

# Encuentra el archivo V.d.bd2.csv de el viento en la ruta de la estación
ruta_V_d_bd2 = next((os.path.join(ruta_analisis_V, archivo) for archivo in os.listdir(ruta_analisis_V) if archivo.endswith(".csv") and 'V.d.bd2' in archivo), None)

# Define the function to generate final bd3 files
def genera_archivos_final_bd3():
    # Check if h.bd3 file exists and replace it
    ruta_h_bd3 = next((os.path.join(ruta_analisis_V, archivo) for archivo in os.listdir(ruta_analisis_V) if "h.bd3" in archivo), None)
    if ruta_h_bd3:
        os.remove(ruta_h_bd3)
        shutil.copy(ruta_V_h_bd2, os.path.join(ruta_analisis_V, os.path.basename(ruta_V_h_bd2).replace("bd2", "bd3")))
    else:
        # If bd3 file doesn't exist, create a copy of bd2 with bd3 extension
        shutil.copy(ruta_V_h_bd2, os.path.join(ruta_analisis_V, os.path.basename(ruta_V_h_bd2).replace("bd2", "bd3")))

    # Check if d.bd3 file exists and replace it
    ruta_d_bd3 = next((os.path.join(ruta_analisis_V, archivo) for archivo in os.listdir(ruta_analisis_V) if "d.bd3" in archivo), None)
    if ruta_d_bd3:
        os.remove(ruta_d_bd3)
        shutil.copy(ruta_V_d_bd2, os.path.join(ruta_analisis_V, os.path.basename(ruta_V_d_bd2).replace("bd2", "bd3")))
    else:
        shutil.copy(ruta_V_d_bd2, os.path.join(ruta_analisis_V, os.path.basename(ruta_V_d_bd2).replace("bd2", "bd3")))

genera_archivos_final_bd3()

# Encuentra el archivo V.h.bd2.csv de el viento en la ruta de la estación
ruta_V_h_bd3 = next((os.path.join(ruta_analisis_V, archivo) for archivo in os.listdir(ruta_analisis_V) if archivo.endswith(".csv") and 'V.h.bd3' in archivo), None)

# Encuentra el archivo V.d.bd2.csv de el viento en la ruta de la estación
ruta_V_d_bd3 = next((os.path.join(ruta_analisis_V, archivo) for archivo in os.listdir(ruta_analisis_V) if archivo.endswith(".csv") and 'V.d.bd3' in archivo), None)

        
def edita_mod_V_h_db3():
    archivos_V_h = os.path.join(ruta_analisis_V, "Modif_Tec_V_h.csv")
    
    if os.path.exists(archivos_V_h):
        df_mod_V_h = pd.read_csv(archivos_V_h)
        
        if ruta_V_h_bd3 and os.path.exists(ruta_V_h_bd3):
            df_V_h_bd3 = pd.read_csv(ruta_V_h_bd3)  # Lee el archivo V.h.bd3.csv una vez fuera del bucle
            
            for index, row in df_mod_V_h.iterrows():
                Elemento = row['Elemento']
                Fecha = row['Fecha']
                valor_reemplazo = row['Valor_reemplazo']
                
                # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                if valor_reemplazo != 'NA':
                    # Realiza el reemplazo si coincide el Elemento y la Fecha
                    df_V_h_bd3.loc[(df_V_h_bd3['TIMESTAMP'] == Fecha), Elemento] = valor_reemplazo
            
            # Guarda el archivo V.h.bd3.csv después de realizar todos los reemplazos
            df_V_h_bd3.to_csv(ruta_V_h_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos
            
            if len(df_mod_V_h) >= 1:
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print("Se han incluido exitosamente los cambios generados en el archivo Modif_Tec_V_h en el archivo de el viento horaria bd3.")
                print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo Modif_Tec_h.csv.")
        print('')

def edita_mod_V_d_db3():
    archivos_V_d = os.path.join(ruta_analisis_V, "Modif_Tec_V_d.csv")
    
    if os.path.exists(archivos_V_d):
        if ruta_V_d_bd3 and os.path.exists(ruta_V_d_bd3):  # Verifica si el archivo V.d.bd3.csv existe
            df_mod_V_d = pd.read_csv(archivos_V_d)
            df_V_d_bd3 = pd.read_csv(ruta_V_d_bd3)  # Lee el archivo V.d.bd3.csv una vez fuera del bucle
            for index, row in df_mod_V_d.iterrows():
                Elemento = row['Elemento']
                Fecha = row['Fecha']
                valor_reemplazo = row['Valor_reemplazo']
                # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                if valor_reemplazo != 'NA':
                    # Realiza el reemplazo si coincide el Elemento y la Fecha
                    df_V_d_bd3.loc[(df_V_d_bd3['TIMESTAMP'] == Fecha), Elemento] = valor_reemplazo
            # Guarda el archivo V.d.bd3.csv después de realizar todos los reemplazos
            df_V_d_bd3.to_csv(ruta_V_d_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos
            if len(df_mod_V_d) >= 1:
                print('-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print("Se han incluido exitosamente los cambios generados en el archivo Modif_Tec_V_d en el archivo de el viento diaria bd3.")
                print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo Modif_Tec_d.csv.")
        print('')
        
def edita_V_h_db3():
    if ruta_V_h_bd3:
        for root, dirs, files in os.walk(ruta_pruebas_b):
            for file in files:
                if 'V_h' in file and file.endswith('.csv'):
                    archivos_V_h = os.path.join(root, file)
                    df_mes_V_h = pd.read_csv(archivos_V_h)
                    df_V_h_bd3 = pd.read_csv(ruta_V_h_bd3)  # Lee el archivo V.h.bd3.csv una vez fuera del bucle
                    for index, row in df_mes_V_h.iterrows():
                        Elemento = row['Elemento']
                        Fecha = row['Fecha']
                        valor_reemplazo = row['Valor_reemplazo']
                        # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                        if valor_reemplazo != 'NA':
                            # Realiza el reemplazo si coincide el Elemento y la Fecha
                            df_V_h_bd3.loc[(df_V_h_bd3['TIMESTAMP'] == Fecha), Elemento] = valor_reemplazo
                    # Guarda el archivo V.h.bd3.csv después de realizar todos los reemplazos
                    df_V_h_bd3.to_csv(ruta_V_h_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Se han incluido exitosamente los cambios generados en los archivos mensuales en el archivo de el viento horaria bd3.")
        print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de el viento horaria bd3.")
        print('')

def edita_V_d_db3():
    if ruta_V_d_bd3:
        for root, dirs, files in os.walk(ruta_pruebas_b):
            for file in files:
                if 'V_d' in file and file.endswith('.csv'):
                    archivos_V_d = os.path.join(root, file)
                    df_mes_V_d = pd.read_csv(archivos_V_d)
                    df_V_d_bd3 = pd.read_csv(ruta_V_d_bd3)  # Lee el archivo V.d.bd3.csv una vez fuera del bucle
                    for index, row in df_mes_V_d.iterrows():
                        Elemento = row['Elemento']
                        Fecha = row['Fecha']
                        valor_reemplazo = row['Valor_reemplazo']
                        # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                        if valor_reemplazo != 'NA':
                            # Realiza el reemplazo si coincide el Elemento y la Fecha
                            df_V_d_bd3.loc[(df_V_d_bd3['TIMESTAMP'] == Fecha), Elemento] = valor_reemplazo
                    # Guarda el archivo V.d.bd3.csv después de realizar todos los reemplazos
                    df_V_d_bd3.to_csv(ruta_V_d_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Se han incluido exitosamente los cambios generados en los archivos mensuales en el archivo de el viento diaria bd3.")
        print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de el viento diaria bd3.")
        print('')
        
edita_V_h_db3()
edita_V_d_db3()

edita_mod_V_h_db3()
edita_mod_V_d_db3()

def elimina_fila_anumerica_V_h():
    if ruta_V_h_bd3:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_V_h_bd3 = pd.read_csv(ruta_V_h_bd3, na_values=['NA'])
            
        # Rellena las celdas en blanco con 'NA' en todo el DataFrame
        #df_V_h_bd3.fillna('NA', inplace=True)

        # Filtra las filas sin valores numéricos al principio y al final en ciertas columnas
        indices_numericos_V_h = df_V_h_bd3[df_V_h_bd3[['Wind-dir_pred', 'Wind-freq.fs.tot.1h.s1', 'Wind-scalar.m_s.avg.1h.s1', 'Wind-vector.m_s.wvc.1h.s1', 'Wind-dir.deg.wvc.1h.s1', 'Wind-dir.sd.deg.std.1h.s1']].apply(pd.to_numeric, errors='coerce').notnull().any(axis=1)].index
        
        if not indices_numericos_V_h.empty:
            primer_indice_numerico_V_h = indices_numericos_V_h[0]
            ultimo_indice_numerico_V_h = indices_numericos_V_h[-1]

            # Conserva las filas con valores numéricos
            df_V_h_bd3 = df_V_h_bd3.iloc[primer_indice_numerico_V_h:ultimo_indice_numerico_V_h + 1]

            # Rellena valores no numéricos con 'NA' en ciertas columnas y agrega el número de estación en la columna ESTACION
            rellena_caracteres_NA_V_h = ['Wind-dir_pred','Wind-freq.fs.tot.1h.s1', 'Wind-scalar.m_s.avg.1h.s1', 'Wind-vector.m_s.wvc.1h.s1', 'Wind-dir.deg.wvc.1h.s1', 'Wind-dir.sd.deg.std.1h.s1']
            for col in rellena_caracteres_NA_V_h:
                df_V_h_bd3[col] = pd.to_numeric(df_V_h_bd3[col], errors='coerce').fillna('NA')

            # Guarda el archivo CSV
            df_V_h_bd3.to_csv(ruta_V_h_bd3, index=False, na_rep='NA')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de el viento horario bd3")

elimina_fila_anumerica_V_h()

def elimina_fila_anumerica_V_d():
    if ruta_V_d_bd3:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_V_d_bd3 = pd.read_csv(ruta_V_d_bd3, na_values=['NA'])
            
        # Rellena las celdas en blanco con 'NA' en todo el DataFrame
        #df_V_d_bd3.fillna('NA', inplace=True)

        # Filtra las filas sin valores numéricos al principio y al final en ciertas columnas
        indices_numericos_V_d = df_V_d_bd3[df_V_d_bd3[['Wind.m_s.max.dm.s1']].apply(pd.to_numeric, errors='coerce').notnull().any(axis=1)].index
        
        if not indices_numericos_V_d.empty:
            primer_indice_numerico_V_d = indices_numericos_V_d[0]
            ultimo_indice_numerico_V_d = indices_numericos_V_d[-1]

            # Conserva las filas con valores numéricos
            df_V_d_bd3 = df_V_d_bd3.iloc[primer_indice_numerico_V_d:ultimo_indice_numerico_V_d + 1]

            # Rellena valores no numéricos con 'NA' en ciertas columnas y agrega el número de estación en la columna ESTACION
            rellena_caracteres_NA_V_d = ['Wind.m_s.max.dm.s1']
            for col in rellena_caracteres_NA_V_d:
                df_V_d_bd3[col] = pd.to_numeric(df_V_d_bd3[col], errors='coerce').fillna('NA')
                
            # Guarda el archivo CSV
            df_V_d_bd3.to_csv(ruta_V_d_bd3, index=False, na_rep='NA')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de el viento horario bd3")

elimina_fila_anumerica_V_d()

def renombra_V_h(ruta_V_h_bd3, num_estacion, ruta_analisis_V):
    if ruta_V_h_bd3:
        df_V_h_bd3 = pd.read_csv(ruta_V_h_bd3)
        df_V_h_bd3['TIMESTAMP'] = pd.to_datetime(df_V_h_bd3['TIMESTAMP'])
        tiempo_inicial_V_h = df_V_h_bd3['TIMESTAMP'].min()
        tiempo_final_V_h = df_V_h_bd3['TIMESTAMP'].max()
        nuevo_nombre_V_h_bd3 = f"{num_estacion}.{tiempo_inicial_V_h.strftime('%Y%m%d-%H')}.{tiempo_final_V_h.strftime('%Y%m%d-%H')}.V.h.bd3.csv"
        nueva_ruta_V_h_bd3 = os.path.join(ruta_analisis_V, nuevo_nombre_V_h_bd3)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Se ha generado exitosamente el archivo del viento horario bd3 como: {nuevo_nombre_V_h_bd3}")
        print('')
        shutil.move(ruta_V_h_bd3, nueva_ruta_V_h_bd3)

renombra_V_h(ruta_V_h_bd3, num_estacion, ruta_analisis_V)

def renombra_V_d(ruta_V_d_bd3, num_estacion, ruta_analisis_V):
    if ruta_V_d_bd3:
        df_V_d_bd3 = pd.read_csv(ruta_V_d_bd3)
        df_V_d_bd3['TIMESTAMP'] = pd.to_datetime(df_V_d_bd3['TIMESTAMP'])
        tiempo_inicial_V_d = df_V_d_bd3['TIMESTAMP'].min()
        tiempo_final_V_d = df_V_d_bd3['TIMESTAMP'].max()
        nuevo_nombre_V_d_bd3 = f"{num_estacion}.{tiempo_inicial_V_d.strftime('%Y%m%d-%H')}.{tiempo_final_V_d.strftime('%Y%m%d-%H')}.V.d.bd3.csv"
        nueva_ruta_V_d_bd3 = os.path.join(ruta_analisis_V, nuevo_nombre_V_d_bd3)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Se ha generado exitosamente el archivo del viento diario bd3 como: {nuevo_nombre_V_d_bd3}")
        print('')
        shutil.move(ruta_V_d_bd3, nueva_ruta_V_d_bd3)

renombra_V_d(ruta_V_d_bd3, num_estacion, ruta_analisis_V)

def menos_nueve_entero(df, ruta_archivo):
    with open(ruta_archivo, 'w') as f:
        # Escribir encabezado
        f.write(','.join(df.columns) + '\n')

        # Escribir datos fila por fila
        for index, row in df.iterrows():
            row_values = []
            for value in row:
                # Personalizar el formato para -9.0
                if isinstance(value, float) and value == -9.0:
                    row_values.append('-9')
                else:
                    row_values.append(str(value))
            f.write(','.join(row_values) + '\n')

# Encuentra el archivo V.h.bd2.csv de el viento en la ruta de la estación
ruta_V_h_bd3 = next((os.path.join(ruta_analisis_V, archivo) for archivo in os.listdir(ruta_analisis_V) if archivo.endswith(".csv") and 'V.h.bd3' in archivo), None)

# Encuentra el archivo V.d.bd2.csv de el viento en la ruta de la estación
ruta_V_d_bd3 = next((os.path.join(ruta_analisis_V, archivo) for archivo in os.listdir(ruta_analisis_V) if archivo.endswith(".csv") and 'V.d.bd3' in archivo), None)

unidad = '(m/s)'

# Variables para V.h
Variables_V_h = ['Wind-scalar.m_s.avg.1h.s1']
# Variables para V.d
Variables_V_d = ['Wind.m_s.max.dm.s1']
Variables_V_d_Vime = ['Wind.CST.max.dm.s1']

# Definir los nombres de los meses en español
nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

#-----------------------------------------------------------------------------------------------------------------
#Estadisticas chebyshev
if ruta_V_h_bd3 or ruta_V_d_bd3:
    # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if ruta_V_h_bd3:
            df_V_h_bd3 = pd.read_csv(ruta_V_h_bd3, na_values=['NA'])
            df_V_h_bd3['TIMESTAMP'] = pd.to_datetime(df_V_h_bd3['TIMESTAMP'])  # Convertir a tipo de dato de Fecha y hora

        if ruta_V_d_bd3:
            df_V_d_bd3 = pd.read_csv(ruta_V_d_bd3, na_values=['NA'])
            df_V_d_bd3['TIMESTAMP'] = pd.to_datetime(df_V_d_bd3['TIMESTAMP'])

#-----------------------------------------------------------------------------------------------------------------

def Estadisticos_V_h_d(ruta_pruebas_b, num_estacion):

    # Inicializar diccionarios para almacenar estadísticas de V_h y V_d
    estadisticos_V_h_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_V_h + Variables_V_d}

    # Iterar sobre cada mes en los datos de V_h y V_d
    for mes in range(1, 13):
        # Filtrar datos por mes para V_h y V_d
        df_mes_V_h = df_V_h_bd3[df_V_h_bd3['TIMESTAMP'].dt.month == mes]
        df_mes_V_d = df_V_d_bd3[df_V_d_bd3['TIMESTAMP'].dt.month == mes]

        # Iterar sobre cada variable en Variables_V_h y Variables_V_d
        for variable in Variables_V_h + Variables_V_d:
            # Seleccionar el dataframe correspondiente
            df_mes = df_mes_V_h if variable in Variables_V_h else df_mes_V_d

            # Calcular estadísticas si hay valores que no son NaN
            if not df_mes[variable].dropna().empty:
                # Calcular máximo, mínimo, media y desviación estándar
                max_val = df_mes[variable].max()
                min_val = df_mes[variable].min()
                mean_val = df_mes[variable].mean()
                std_val = df_mes[variable].std()

                # Almacenar estadísticas en el diccionario
                estadisticos_V_h_d[variable][nombres_meses[mes - 1]] = [max_val, min_val, mean_val, std_val]

    # Guardar estadísticas para V_h y V_d en un archivo de texto
    with open(os.path.join(ruta_pruebas_b, "Estadisticos_V_E1.txt"), "w") as file:
        for variable in Variables_V_h + Variables_V_d:
            file.write(f"\nEstación: {num_estacion} - Variable: {variable}\n")
            file.write("{:<12} {:<8} {:<8} {:<17} {:<17}\n".format("Mes", "Máximo", "Mínimo", "Media aritmética", "Desviación estándar"))
            for mes in range(1, 13):
                max_val, min_val, mean_val, std_val = estadisticos_V_h_d[variable][nombres_meses[mes - 1]]
                file.write("{:<12} {:<8.2f} {:<8.2f} {:<17.2f} {:<17.2f}\n".format(nombres_meses[mes - 1], max_val, min_val, mean_val, std_val))

# Llamada a la función
Estadisticos_V_h_d(ruta_pruebas_b, num_estacion)

#-----------------------------------------------------------------------------------------------------------------

#Genera diagramas de caja totales y mensuales para cada variable.
def Diagrama_caja_Total_V(unidades):

    if ruta_V_h_bd3 or ruta_V_d_bd3:
        # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            if ruta_V_h_bd3:
                df_V_h_bd3 = pd.read_csv(ruta_V_h_bd3, na_values=['NA'])
                df_V_h_bd3['TIMESTAMP'] = pd.to_datetime(df_V_h_bd3['TIMESTAMP'])  # Convertir a tipo de dato de Fecha y hora

            if ruta_V_d_bd3:
                df_V_d_bd3 = pd.read_csv(ruta_V_d_bd3, na_values=['NA'])
                df_V_d_bd3['TIMESTAMP'] = pd.to_datetime(df_V_d_bd3['TIMESTAMP'])

            # Genera una figura con cuatro subtramas (4 filas, 2 columnas)
            fig, axes = plt.subplots(2, 2, figsize=(16, 25), dpi=300)

            # Boxplots para V.h
            if ruta_V_h_bd3:
                for i, variable_V_h in enumerate(Variables_V_h):
                    # Boxplot de la serie total (orientación vertical)
                    sns.boxplot(y=df_V_h_bd3[variable_V_h].dropna(), color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i, 0])
                    
                    axes[i, 0].set_title(f'{num_estacion} - {variable_V_h}- Total')
                    axes[i, 0].set_ylabel('Viento escalar (m/s)')
                    axes[i, 0].set_yticks(range(int(df_V_h_bd3[variable_V_h].min()), int(df_V_h_bd3[variable_V_h].max()) + 1))
                    axes[i, 0].tick_params(axis='y', rotation=0)
                    axes[i, 0].grid(True, axis='y')

                    # Boxplots mensuales
                    sns.boxplot(x=df_V_h_bd3['TIMESTAMP'].dt.month, y=df_V_h_bd3[variable_V_h], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i, 1])
                    
                    axes[i, 1].set_title(f'{num_estacion} - {variable_V_h}- Mensual')
                    axes[i, 1].set_xlabel('Mes')
                    axes[i, 1].set_ylabel('Viento escalar (m/s)')
                    axes[i, 1].set_xticks(range(0, 13))  # 13 meses
                    axes[i, 1].set_yticks(range(int(df_V_h_bd3[variable_V_h].min()), int(df_V_h_bd3[variable_V_h].max()) + 1))
                    axes[i, 1].tick_params(axis='x', rotation=45)
                    axes[i, 1].grid(True, axis='y')

            # Boxplots para V.d
            if ruta_V_d_bd3:
                for i, variable_V_d in enumerate(Variables_V_d):
                    # Boxplot de la serie total (orientación vertical)
                    sns.boxplot(y=df_V_d_bd3[variable_V_d].dropna(), color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i+1, 0])
                    
                    axes[i+1, 0].set_title(f'{num_estacion} - {variable_V_d}- Total')
                    axes[i+1, 0].set_ylabel('Viento máximo (m/s)')
                    axes[i+1, 0].set_yticks(range(int(df_V_d_bd3[variable_V_d].min()), int(df_V_d_bd3[variable_V_d].max()) + 1))
                    axes[i+1, 0].tick_params(axis='y', rotation=0)
                    axes[i+1, 0].grid(True, axis='y')

                    # Boxplots mensuales
                    sns.boxplot(x=df_V_d_bd3['TIMESTAMP'].dt.month, y=df_V_d_bd3[variable_V_d], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i+1, 1])
                    
                    axes[i+1, 1].set_title(f'{num_estacion} - {variable_V_d}- Mensual')
                    axes[i+1, 1].set_xlabel('Mes')
                    axes[i+1, 1].set_ylabel('Viento máximo (m/s)')
                    axes[i+1, 1].set_xticks(range(0, 13))  # 13 meses
                    axes[i+1, 1].set_yticks(range(int(df_V_d_bd3[variable_V_d].min()), int(df_V_d_bd3[variable_V_d].max()) + 1))
                    axes[i+1, 1].tick_params(axis='x', rotation=45)
                    axes[i+1, 1].grid(True, axis='y')

            # Ajusta la disposición general y muestra el gráfico
            plt.tight_layout()
            plt.subplots_adjust(top=0.95)
            # Agrega un título a la figura
            fig.suptitle(f'Diagramas de cajas - Estación: {num_estacion}', fontsize=16)
            nombre_diag_caja_V = 'DC_V_Total_E1.png'
            plt.savefig(os.path.join(ruta_pruebas_b, 'DC_V_Total_E1.png'))
            plt.close()
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f'Se ha generado exitosamente el diagrama de cajas de la serie total de la etapa 1 para el viento como: {nombre_diag_caja_V}.')
            print('')
            return True
    else:
        print("No se encontraron archivos V.h.bd3 y/o V.d.bd3 en la ruta especificada.")
        return False

Diagrama_caja_Total_V(['',''])
#-----------------------------------------------------------------------------------------------------------------

def plot_time_series(df_V_h_bd3, df_V_d_bd3, var1, var2, title=f"Serie de tiempo - Estación: {num_estacion}", xlabel="Tiempo", ylabel="Viento (m/s)"):
    plt.figure(figsize=(60, 8), dpi=300)  # Adjusted figure size and DPI as per your requirement

    # Resample data to monthly frequency and calculate max and min
    df_V_h_bd3_monthly_max = df_V_h_bd3.resample('M', on='TIMESTAMP')[var1].max()
    df_V_d_bd3_monthly_max = df_V_d_bd3.resample('M', on='TIMESTAMP')[var2].max()

     # Reindex to ensure both series cover the same time range
    df_V_d_bd3_monthly_max = df_V_d_bd3_monthly_max.reindex(df_V_h_bd3_monthly_max.index)
    

    # Create a combined dataframe for seaborn
    combined_df = pd.DataFrame({
        'Date': df_V_h_bd3_monthly_max.index,
        f'Max {var1}': df_V_h_bd3_monthly_max.values,
        f'Max {var2}': df_V_d_bd3_monthly_max.values,
    }).melt('Date', var_name='Variable', value_name='Value')
    
    # Plot using seaborn
    sns.lineplot(data=combined_df, x='Date', y='Value', hue='Variable', palette=['blue', 'red'], markers=True)
    
    # Add markers to the maximum and minimum points
    sns.scatterplot(data=combined_df, x='Date', y='Value', hue='Variable', palette=['blue', 'red'], s=30, legend=False)
    
    # Formatting the plot
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    # Add the first legend in the default location
    legend_default = plt.legend(loc='best')
    
    # Add the second legend in the top left corner
    legend_top_left = plt.legend(loc='upper left', bbox_to_anchor=(0, 1))
    
    # Add the first legend back
    plt.gca().add_artist(legend_default)
    
    plt.grid(True, which='both', axis='x')
    
    # Set major ticks format
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    plt.gca().xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], bymonthday=-1))  # Set minor ticks at the end of each month
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%m'))  # Use '%m' for month number
    
    # Rotate and align x-axis labels
    plt.xticks(rotation=90, ha='center')
    
    # Set y-axis major and minor tick locators and formatting
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(1))  # Set major ticks every 1 unit
    plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(0.5))  # Set minor ticks every 0.5 units
    plt.gca().yaxis.set_major_formatter('{:.0f}'.format)  # Format major ticks as whole numbers

    # Ensure ticks and labels appear on both sides of y-axis
    plt.gca().tick_params(axis='y', which='both', direction='inout', left=False, right=False)  # Disable outer y-axis ticks

    # Disable the y-axis labels for the primary y-axis
    plt.gca().yaxis.set_ticks([])

    # Get the current y-axis limits
    y_limits = plt.gca().get_ylim()

    # Create a twin axis for y
    ax2 = plt.gca().twinx()
    ax2.set_ylim(y_limits)  # Set the same y-axis limits as the original axis

    # Synchronize y-axis tick locators for the twin axis
    ax2.yaxis.set_major_locator(plt.MultipleLocator(1))  # Set major ticks every 1 unit
    ax2.yaxis.set_minor_locator(plt.MultipleLocator(0.5))  # Set minor ticks every 0.5 units
    ax2.yaxis.set_major_formatter('{:.0f}'.format)  # Format major ticks as whole numbers
    ax2.tick_params(axis='y', which='both', direction='inout', left=False, right=False)  # Disable outer y-axis ticks
    
    ax2.set_ylabel(ylabel)

    # Disable the y-axis labels for the secondary y-axis
    ax2.yaxis.set_ticks([])

    # Add horizontal gridlines for each tick
    plt.gca().yaxis.grid(True, which='both')

    # Add additional y-axis labels on top of each year
    unique_years = combined_df['Date'].dt.year.unique()
    for year in unique_years:
        year_date = pd.Timestamp(year=year, month=1, day=1)
        for y_value in range(int(y_limits[0]), int(y_limits[1])+1):
            plt.text(year_date, y_value, f'{y_value}', ha='center', va='bottom', color='gray', fontsize=10)

    plt.tight_layout()
    
    # Save the plot (assuming ruta_guardado is defined in your environment)
    plt.savefig(os.path.join(ruta_pruebas_b, 'ST_Extremos_V_E1.png'))
    plt.show()
    
    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print('Se ha generado exitosamente la serie de tiempo de los extremos mensuales de la serie total para el viento de la etapa 1 como: ST_Extremos_V_E1.png.')
    print('')

# Example call to the function (adjust variables and dataframes as per your dataset)
plot_time_series(df_V_h_bd3, df_V_d_bd3, 'Wind-scalar.m_s.avg.1h.s1', 'Wind.m_s.max.dm.s1')

def Diagrama_caja_mensual_V(unidades):
    
    # Leer archivos .csv y realizar operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        df_V_h_bd3 = None
        df_V_d_bd3 = None

        if ruta_V_h_bd3:
            df_V_h_bd3 = pd.read_csv(ruta_V_h_bd3, na_values=['NA'])
            df_V_h_bd3['TIMESTAMP'] = pd.to_datetime(df_V_h_bd3['TIMESTAMP']) 

        if ruta_V_d_bd3:
            df_V_d_bd3 = pd.read_csv(ruta_V_d_bd3, na_values=['NA'])
            df_V_d_bd3['TIMESTAMP'] = pd.to_datetime(df_V_d_bd3['TIMESTAMP'])

    # Lista de nombres de los meses en español
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    # Iterar a través de cada mes
    for month in range(1, 13):
        # Nombre del mes en español
        nombre_mes_carpeta = f"{month:02d}.{meses[month - 1]}"
        nombre_mes = meses[month - 1]
        ruta_meses = os.path.join(ruta_pruebas_b, nombre_mes_carpeta)
        os.makedirs(ruta_meses, exist_ok=True)

        # Genera una figura con cuatro subtramas (2 filas, 1 columna)
        fig, axes = plt.subplots(2, 1, figsize=(10, 20), dpi=300)

        # Diagramas de caja para V.h si df_V_h_bd3 no es None
        if df_V_h_bd3 is not None:
            for i, variable_V_h in enumerate(Variables_V_h):
                data = df_V_h_bd3[variable_V_h][df_V_h_bd3['TIMESTAMP'].dt.month == month].dropna()
                
                # Calcular estadísticas
                Media_aritmética_V_h = data.mean()
                Desviación_estándar_V_h = data.std()
                P25_V_h = data.quantile(0.25)
                P50_V_h = data.quantile(0.50)  # Median
                P75_V_h = data.quantile(0.75)
                IQR_V_h = P75_V_h - P25_V_h
                BI_V_h = P25_V_h - 1.5 * IQR_V_h
                BS_V_h = P75_V_h + 1.5 * IQR_V_h
                Min_V_h = data.min()
                Max_V_h = data.max()
                MinZ_V_h = (Min_V_h - Media_aritmética_V_h) / Desviación_estándar_V_h
                MaxZ_V_h = (Max_V_h - Media_aritmética_V_h) / Desviación_estándar_V_h
                lim_inf_V_h = np.fix(MinZ_V_h)*Desviación_estándar_V_h + Media_aritmética_V_h
                lim_sup_V_h = np.fix(MaxZ_V_h)*Desviación_estándar_V_h + Media_aritmética_V_h
                
                sns.boxplot(y=data, color="blue", linewidth=1.5,
                            boxprops=dict(facecolor='blue', edgecolor='black'),
                            flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'),
                            ax=axes[i])
                axes[i].set_title(f'{num_estacion} - {variable_V_h} - {nombre_mes}')
                axes[i].set_xlabel('')
                axes[i].set_ylabel('Viento escalar (m/s)')
                axes[i].set_yticks(range(int(data.min()), int(data.max()) + 1))
                axes[i].tick_params(axis='y', rotation=0)
                axes[i].grid(True, axis='y')
                
                # Agregar información estadística en la esquina superior derecha de cada subplot
                axes[i].text(0.95, 0.95, f'Media aritmética = {Media_aritmética_V_h:.2f}{unidad}\nDesviación estándar = {Desviación_estándar_V_h:.2f}{unidad}\nLím.Tec. superior = {lim_sup_V_h:.2f}{unidad}\nBigote superior = {BS_V_h:.2f}{unidad}',
                                      transform=axes[i].transAxes,
                                      fontsize=8, verticalalignment='top', horizontalalignment='right', backgroundcolor='white')

        # Diagramas de caja para V.d si df_V_d_bd3 no es None
        if df_V_d_bd3 is not None:
            for i, variable_V_d in enumerate(Variables_V_d):
                data = df_V_d_bd3[variable_V_d][df_V_d_bd3['TIMESTAMP'].dt.month == month].dropna()
                
                # Calcular estadísticas
                Media_aritmética_V_d = data.mean()
                Desviación_estándar_V_d = data.std()
                P25_V_d = data.quantile(0.25)
                P50_V_d = data.quantile(0.50)  # Median
                P75_V_d = data.quantile(0.75)
                IQR_V_d = P75_V_d - P25_V_d
                BI_V_d = P25_V_d - 1.5 * IQR_V_d
                BS_V_d = P75_V_d + 1.5 * IQR_V_d
                Min_V_d = data.min()
                Max_V_d = data.max()
                MinZ_V_d = (Min_V_d - Media_aritmética_V_d) / Desviación_estándar_V_d
                MaxZ_V_d = (Max_V_d - Media_aritmética_V_d) / Desviación_estándar_V_d
                lim_inf_V_d = np.fix(MinZ_V_d)*Desviación_estándar_V_d + Media_aritmética_V_d
                lim_sup_V_d = np.fix(MaxZ_V_d)*Desviación_estándar_V_d + Media_aritmética_V_d
                
                sns.boxplot(y=data, color="blue", linewidth=1.5,
                            boxprops=dict(facecolor='blue', edgecolor='black'),
                            flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'),
                            ax=axes[i+1])
                axes[i+1].set_title(f'{num_estacion} - {variable_V_d} - {nombre_mes}')
                axes[i+1].set_xlabel('')
                axes[i+1].set_ylabel('Viento máximo (m/s)')
                axes[i+1].set_yticks(range(int(data.min()), int(data.max()) + 1))
                axes[i+1].tick_params(axis='y', rotation=0)
                axes[i+1].grid(True, axis='y')

                # Agregar información estadística en la esquina superior derecha de cada subplot
                axes[i+1].text(0.95, 0.95, f'Media aritmética = {Media_aritmética_V_d:.2f}{unidad}\nDesviación estándar = {Desviación_estándar_V_d:.2f}{unidad}\nLím.Tec.superior = {lim_sup_V_d:.2f}{unidad}\nLím.Tec. inferior = {lim_inf_V_d:.2f}{unidad}\nBigote superior = {BS_V_d:.2f}{unidad}\nBigote inferior = {BI_V_d:.2f}{unidad}',
                                             transform=axes[i+1].transAxes,
                                             fontsize=8, verticalalignment='top', horizontalalignment='right', backgroundcolor='white')
    # Ajustar el diseño
        plt.tight_layout()

    # Guardar el gráfico
        plt.savefig(os.path.join(ruta_meses, f'{nombre_mes}_DC_E1.png'))
        plt.close()

    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print('Se han generado exitosamente los diagramas de cajas mensuales de la etapa 1 para el viento.')
    print('')
    return True if (df_V_h_bd3 is not None or df_V_d_bd3 is not None) else False

#-----------------------------------------------------------------------------------------------------------------

Diagrama_caja_mensual_V("")

def fechas_especificas_faltantes_V_d(ruta_V_d_bd3):
    # Cargar el archivo CSV
    df = pd.read_csv(ruta_V_d_bd3)

    # Reemplazar NA en Wind.CST.max.dm.s1 donde Wind.m_s.max.dm.s1 es NA
    df.loc[df['Wind.m_s.max.dm.s1'].isna(), 'Wind.CST.max.dm.s1'] = 'NA'
    
    #df.loc[df['Wind.CST.max.dm.s1'].isna(), 'Wind.m_s.max.dm.s1'] = 'NA'
    # Reemplazar NA en Wind.CST.max.dm.s1 donde Wind.m_s.max.dm.s1 es NA
    df['Wind.m_s.max.dm.s1'].fillna('NA', inplace=True)
    df['Wind.CST.max.dm.s1'].fillna('NA', inplace=True)

    # Guardar los cambios en el mismo archivo
    df.to_csv(ruta_V_d_bd2, index=False)

fechas_especificas_faltantes_V_d(ruta_V_d_bd2)

def generar_archivo_txt_V_h():
    # Si existe el archivo ruta_V_h_bd3, procesar y crear el archivo de texto
    if ruta_V_h_bd3:
        # Leer el archivo CSV y reemplazar los NA por -9
        df_V_h_bd3 = pd.read_csv(ruta_V_h_bd3)
        df_V_h_bd3.fillna(-9, inplace=True)

        # Crear una copia del DataFrame con los nombres de columnas cambiados
        df_V_h_bd3_copy = df_V_h_bd3.rename(columns={
            'Wind-dir_pred': 'DIR_PRED',
            'Wind-freq.fs.tot.1h.s1': 'FREC_VIEN',
            'Wind-scalar.m_s.avg.1h.s1': 'VIENT_m_s_escalar',
            'Wind-vector.m_s.wvc.1h.s1': 'VIENT_m_s_S_WVT',
            'Wind-dir.deg.wvc.1h.s1': 'DIR_vient_SD1_WVT',
            'Wind-dir.sd.deg.std.1h.s1': 'DIR_vient_SD1_WVT'
        })

        # Crear el nombre del archivo de texto
        Fecha_inicial = pd.to_datetime(df_V_h_bd3['TIMESTAMP']).min().strftime('%Y%m%d')
        Fecha_final = pd.to_datetime(df_V_h_bd3['TIMESTAMP']).max().strftime('%Y%m%d')
        nombre_archivo_txt_V_h = f"H-{num_estacion}-{Fecha_inicial}-{Fecha_final}.txt"

        # Ruta completa del archivo de texto
        ruta_archivo_texto = os.path.join(ruta_analisis_V, nombre_archivo_txt_V_h)
        
        # Verificar si existe un archivo que comience con "H-" y eliminarlo
        for file_name in os.listdir(ruta_analisis_V):
            if file_name.startswith('H-'):
                os.remove(os.path.join(ruta_analisis_V, file_name))

        # Guardar el archivo de texto con las celdas separadas por coma
        menos_nueve_entero(df_V_h_bd3_copy, ruta_archivo_texto)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Se ha generado exitosamente el archivo de texto del viento horario como: {nombre_archivo_txt_V_h}.")
        print('')
    else:
        print("Error: No se pudo generar el archivo de texto puesto que no se encontró el archivo del viento horario bd3")

# Llamada a la función
generar_archivo_txt_V_h()

def generar_archivo_txt_V_d():
    # Si existe el archivo ruta_V_d_bd3, procesar y crear el archivo de texto
    if ruta_V_d_bd3:
        # Leer el archivo CSV y reemplazar los NA por -9
        df_V_d_bd3 = pd.read_csv(ruta_V_d_bd3)
        df_V_d_bd3.fillna(int(-9), inplace=True)
        
        # Reemplazar "NA" por "NULL" en las columnas específicas
        df_V_d_bd3['Wind.CST.max.dm.s1'] = df_V_d_bd3['Wind.CST.max.dm.s1'].replace(int(-9), "NULL")
        
        # Crear una copia del DataFrame con los nombres de columnas cambiados
        df_V_d_bd3_copy = df_V_d_bd3.rename(columns={
            'Wind.m_s.max.dm.s1': 'VCORR_m_s_Max',
            'Wind.CST.max.dm.s1': 'VCORR_m_s_TMx',
        })

        # Crear el nombre del archivo de texto
        Fecha_inicial = pd.to_datetime(df_V_d_bd3['TIMESTAMP']).min().strftime('%Y%m%d')
        Fecha_final = pd.to_datetime(df_V_d_bd3['TIMESTAMP']).max().strftime('%Y%m%d')
        nombre_archivotxt_V_d = f"D-{num_estacion}-{Fecha_inicial}-{Fecha_final}.txt"

        # Ruta completa del archivo de texto
        ruta_archivo_texto = os.path.join(ruta_analisis_V, nombre_archivotxt_V_d)
        
        # Verificar si existe un archivo que comience con "D-" y eliminarlo
        for file_name in os.listdir(ruta_analisis_V):
            if file_name.startswith('D-'):
                os.remove(os.path.join(ruta_analisis_V, file_name))

        # Guardar el archivo de texto con las celdas separadas por coma
        menos_nueve_entero(df_V_d_bd3_copy, ruta_archivo_texto)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Se ha generado exitosamente el archivo de texto del viento diario como: {nombre_archivotxt_V_d}.")
        print('')
    else:
        print("Error: No se pudo generar el archivo de texto puesto que no se encontró el archivo del viento diario bd3")

# Llamada a la función
generar_archivo_txt_V_d()