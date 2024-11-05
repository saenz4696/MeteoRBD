import pandas as pd
import os
import warnings
import shutil
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import matplotlib.dates as mdates

# Eliminar UserWarnings de openpyxl
warnings.simplefilter('ignore', category=UserWarning)

datos_crudos = r'C:\\MeteoRBD.v1.0.0\\datos_rbd'

# Encuentra el archivo .xlsx en los datos_crudos que contiene 'Cuenca' y 'Estación' como columnas
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

# Crea las carpetas si no existen
for carpeta in ["", "Pruebas_estadisticas"]:
    ruta_pruebas_b = os.path.join(ruta_analisis_Ll, carpeta)
    os.makedirs(ruta_pruebas_b, exist_ok=True)
    
# Encuentra el archivo Ll.h.bd2.csv de la lluvia en la ruta de la estación
ruta_Ll_h_bd2 = next((os.path.join(ruta_analisis_Ll, archivo) for archivo in os.listdir(ruta_analisis_Ll) if archivo.endswith(".csv") and 'Ll.h.bd2' in archivo), None)

# Encuentra el archivo Ll.d.bd2.csv de la lluvia en la ruta de la estación
ruta_Ll_d_bd2 = next((os.path.join(ruta_analisis_Ll, archivo) for archivo in os.listdir(ruta_analisis_Ll) if archivo.endswith(".csv") and 'Ll.d.bd2' in archivo), None)

# Define the function to generate final bd3 files
def genera_archivos_final_bd3():
    # Check if h.bd3 file exists and replace it
    ruta_h_bd3 = next((os.path.join(ruta_analisis_Ll, archivo) for archivo in os.listdir(ruta_analisis_Ll) if "h.bd3" in archivo), None)
    if ruta_h_bd3:
        os.remove(ruta_h_bd3)
        shutil.copy(ruta_Ll_h_bd2, os.path.join(ruta_analisis_Ll, os.path.basename(ruta_Ll_h_bd2).replace("bd2", "bd3")))
    else:
        # If bd3 file doesn't exist, create a copy of bd2 with bd3 extension
        shutil.copy(ruta_Ll_h_bd2, os.path.join(ruta_analisis_Ll, os.path.basename(ruta_Ll_h_bd2).replace("bd2", "bd3")))

    # Check if d.bd3 file exists and replace it
    ruta_d_bd3 = next((os.path.join(ruta_analisis_Ll, archivo) for archivo in os.listdir(ruta_analisis_Ll) if "d.bd3" in archivo), None)
    if ruta_d_bd3:
        os.remove(ruta_d_bd3)
        shutil.copy(ruta_Ll_d_bd2, os.path.join(ruta_analisis_Ll, os.path.basename(ruta_Ll_d_bd2).replace("bd2", "bd3")))
    else:
        shutil.copy(ruta_Ll_d_bd2, os.path.join(ruta_analisis_Ll, os.path.basename(ruta_Ll_d_bd2).replace("bd2", "bd3")))

genera_archivos_final_bd3()

# Encuentra el archivo Ll.h.bd2.csv de la temperatura en la ruta de la estación
ruta_Ll_h_bd3 = next((os.path.join(ruta_analisis_Ll, archivo) for archivo in os.listdir(ruta_analisis_Ll) if archivo.endswith(".csv") and 'Ll.h.bd3' in archivo), None)

# Encuentra el archivo Ll.d.bd2.csv de la temperatura en la ruta de la estación
ruta_Ll_d_bd3 = next((os.path.join(ruta_analisis_Ll, archivo) for archivo in os.listdir(ruta_analisis_Ll) if archivo.endswith(".csv") and 'Ll.d.bd3' in archivo), None)

def edita_mod_Ll_h_db3():
    archivos_Ll_h = os.path.join(ruta_analisis_Ll, "Modif_Tec_Ll_h.csv")
    
    if os.path.exists(archivos_Ll_h):
        df_mod_Ll_h = pd.read_csv(archivos_Ll_h)
        
        if ruta_Ll_h_bd3 and os.path.exists(ruta_Ll_h_bd3):
            df_Ll_h_bd3 = pd.read_csv(ruta_Ll_h_bd3)  # Lee el archivo Ll.h.bd3.csv una vez fuera del bucle
            
            for index, row in df_mod_Ll_h.iterrows():
                Elemento = row['Elemento']
                Fecha = row['Fecha']
                valor_reemplazo = row['Valor_reemplazo']
                
                # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                if valor_reemplazo != 'NA':
                    # Realiza el reemplazo si coincide el Elemento y la Fecha
                    df_Ll_h_bd3.loc[(df_Ll_h_bd3['TIMESTAMP'] == Fecha), Elemento] = valor_reemplazo
            
            # Guarda el archivo Ll.h.bd3.csv después de realizar todos los reemplazos
            df_Ll_h_bd3.to_csv(ruta_Ll_h_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos
            
            if len(df_mod_Ll_h) >= 1:
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print("Se han incluido exitosamente los cambios generados en el archivo Modif_Tec_Ll_h en el archivo de la lluvia horaria bd3.")
                print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo Modif_Tec_h.csv.")
        print('')

def edita_mod_Ll_d_db3():
    archivos_Ll_d = os.path.join(ruta_analisis_Ll, "Modif_Tec_Ll_d.csv")
    
    if os.path.exists(archivos_Ll_d):
        if ruta_Ll_d_bd3 and os.path.exists(ruta_Ll_d_bd3):  # Verifica si el archivo Ll.d.bd3.csv existe
            df_mod_Ll_d = pd.read_csv(archivos_Ll_d)
            df_Ll_d_bd3 = pd.read_csv(ruta_Ll_d_bd3)  # Lee el archivo Ll.d.bd3.csv una vez fuera del bucle
            for index, row in df_mod_Ll_d.iterrows():
                Elemento = row['Elemento']
                Fecha = row['Fecha']
                valor_reemplazo = row['Valor_reemplazo']
                # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                if valor_reemplazo != 'NA':
                    # Realiza el reemplazo si coincide el Elemento y la Fecha
                    df_Ll_d_bd3.loc[(df_Ll_d_bd3['TIMESTAMP'] == Fecha), Elemento] = valor_reemplazo
            # Guarda el archivo Ll.d.bd3.csv después de realizar todos los reemplazos
            df_Ll_d_bd3.to_csv(ruta_Ll_d_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos
            if len(df_mod_Ll_d) >= 1:
                print('-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print("Se han incluido exitosamente los cambios generados en el archivo Modif_Tec_Ll_d en el archivo de la lluvia diaria bd3.")
                print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo Modif_Tec_d.csv.")
        print('')
        
def edita_Ll_h_db3():
    if ruta_Ll_h_bd3:
        for root, dirs, files in os.walk(ruta_pruebas_b):
            for file in files:
                if 'Ll_h' in file and file.endswith('.csv'):
                    archivos_Ll_h = os.path.join(root, file)
                    df_mes_Ll_h = pd.read_csv(archivos_Ll_h)
                    df_Ll_h_bd3 = pd.read_csv(ruta_Ll_h_bd3)  # Lee el archivo Ll.h.bd3.csv una vez fuera del bucle
                    for index, row in df_mes_Ll_h.iterrows():
                        Elemento = row['Elemento']
                        Fecha = row['Fecha']
                        valor_reemplazo = row['Valor_reemplazo']
                        # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                        if valor_reemplazo != 'NA':
                            # Realiza el reemplazo si coincide el Elemento y la Fecha
                            df_Ll_h_bd3.loc[(df_Ll_h_bd3['TIMESTAMP'] == Fecha), Elemento] = valor_reemplazo
                    # Guarda el archivo Ll.h.bd3.csv después de realizar todos los reemplazos
                    df_Ll_h_bd3.to_csv(ruta_Ll_h_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Se han incluido exitosamente los cambios generados en los archivos mensuales en el archivo de la lluvia horaria bd3.")
        print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la lluvia horaria bd3.")
        print('')

def edita_Ll_d_db3():
    if ruta_Ll_d_bd3:
        for root, dirs, files in os.walk(ruta_pruebas_b):
            for file in files:
                if 'Ll_d' in file and file.endswith('.csv'):
                    archivos_Ll_d = os.path.join(root, file)
                    df_mes_Ll_d = pd.read_csv(archivos_Ll_d)
                    df_Ll_d_bd3 = pd.read_csv(ruta_Ll_d_bd3)  # Lee el archivo Ll.d.bd3.csv una vez fuera del bucle
                    for index, row in df_mes_Ll_d.iterrows():
                        Elemento = row['Elemento']
                        Fecha = row['Fecha']
                        valor_reemplazo = row['Valor_reemplazo']
                        # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                        if valor_reemplazo != 'NA':
                            # Realiza el reemplazo si coincide el Elemento y la Fecha
                            df_Ll_d_bd3.loc[(df_Ll_d_bd3['TIMESTAMP'] == Fecha), Elemento] = valor_reemplazo
                    # Guarda el archivo Ll.d.bd3.csv después de realizar todos los reemplazos
                    df_Ll_d_bd3.to_csv(ruta_Ll_d_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Se han incluido exitosamente los cambios generados en los archivos mensuales en el archivo de la lluvia diaria bd3.")
        print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la lluvia diaria bd3.")
        print('')
        

genera_archivos_final_bd3()

edita_Ll_h_db3()
edita_Ll_d_db3()

edita_mod_Ll_h_db3()
edita_mod_Ll_d_db3()

def elimina_fila_anumerica_Ll_h():
    if ruta_Ll_h_bd3:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_Ll_h_bd3 = pd.read_csv(ruta_Ll_h_bd3, na_values=['NA'])
            
        # Rellena las celdas en blanco con 'NA' en todo el DataFrame
        #df_Ll_h_bd3.fillna('NA', inplace=True)

        # Filtra las filas sin valores numéricos al principio y al final en ciertas columnas
        indices_numericos_Ll_h = df_Ll_h_bd3[df_Ll_h_bd3[['Precip.mm.tot.1h.s1']].apply(pd.to_numeric, errors='coerce').notnull().any(axis=1)].index
        
        if not indices_numericos_Ll_h.empty:
            primer_indice_numerico_Ll_h = indices_numericos_Ll_h[0]
            ultimo_indice_numerico_Ll_h = indices_numericos_Ll_h[-1]

            # Conserva las filas con valores numéricos
            df_Ll_h_bd3 = df_Ll_h_bd3.iloc[primer_indice_numerico_Ll_h:ultimo_indice_numerico_Ll_h + 1]

            # Rellena valores no numéricos con 'NA' en ciertas columnas y agrega el número de estación en la columna ESTACION
            rellena_caracteres_NA_Ll_h = ['Precip.mm.tot.1h.s1']
            for col in rellena_caracteres_NA_Ll_h:
                df_Ll_h_bd3[col] = pd.to_numeric(df_Ll_h_bd3[col], errors='coerce').fillna('NA')

            # Guarda el archivo CSV
            df_Ll_h_bd3.to_csv(ruta_Ll_h_bd3, index=False, na_rep='NA')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la lluvia horaria bd3")

elimina_fila_anumerica_Ll_h()

def elimina_fila_anumerica_Ll_d():
    if ruta_Ll_d_bd3:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_Ll_d_bd3 = pd.read_csv(ruta_Ll_d_bd3, na_values=['NA'])
            
        # Rellena las celdas en blanco con 'NA' en todo el DataFrame
        #df_Ll_d_bd3.fillna('NA', inplace=True)

        # Filtra las filas sin valores numéricos al principio y al final en ciertas columnas
        indices_numericos_Ll_d = df_Ll_d_bd3[df_Ll_d_bd3[['Precip.mm.tot.dm.s1', 'Precip-acum5.mm_h.max.dm.s1', 'Precip-acum10.mm_h.max.dm.s1', 'Precip-acum15.mm_h.max.dm.s1', 'Precip-acum30.mm_h.max.dm.s1']].apply(pd.to_numeric, errors='coerce').notnull().any(axis=1)].index
        
        if not indices_numericos_Ll_d.empty:
            primer_indice_numerico_Ll_d = indices_numericos_Ll_d[0]
            ultimo_indice_numerico_Ll_d = indices_numericos_Ll_d[-1]

            # Conserva las filas con valores numéricos
            df_Ll_d_bd3 = df_Ll_d_bd3.iloc[primer_indice_numerico_Ll_d:ultimo_indice_numerico_Ll_d + 1]

            # Rellena valores no numéricos con 'NA' en ciertas columnas y agrega el número de estación en la columna ESTACION
            rellena_caracteres_NA_Ll_d = ['Precip.mm.tot.dm.s1', 'Precip-acum5.mm_h.max.dm.s1', 'Precip-acum10.mm_h.max.dm.s1', 'Precip-acum15.mm_h.max.dm.s1', 'Precip-acum30.mm_h.max.dm.s1']
            for col in rellena_caracteres_NA_Ll_d:
                df_Ll_d_bd3[col] = pd.to_numeric(df_Ll_d_bd3[col], errors='coerce').fillna('NA')
                
            # Guarda el archivo CSV
            df_Ll_d_bd3.to_csv(ruta_Ll_d_bd3, index=False, na_rep='NA')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la lluvia horaria bd3")

elimina_fila_anumerica_Ll_d()

def renombra_Ll_h(ruta_Ll_h_bd3, num_estacion, ruta_analisis_Ll):
    if ruta_Ll_h_bd3:
        df_Ll_h_bd3 = pd.read_csv(ruta_Ll_h_bd3)
        df_Ll_h_bd3['TIMESTAMP'] = pd.to_datetime(df_Ll_h_bd3['TIMESTAMP'])
        tiempo_inicial_Ll_h = df_Ll_h_bd3['TIMESTAMP'].min()
        tiempo_final_Ll_h = df_Ll_h_bd3['TIMESTAMP'].max()
        nuevo_nombre_Ll_h_bd3 = f"{num_estacion}.{tiempo_inicial_Ll_h.strftime('%Y%m%d-%H')}.{tiempo_final_Ll_h.strftime('%Y%m%d-%H')}.Ll.h.bd3.csv"
        nueva_ruta_Ll_h_bd3 = os.path.join(ruta_analisis_Ll, nuevo_nombre_Ll_h_bd3)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Se ha generado exitosamente el archivo de la lluvia horaria bd3 como: {nuevo_nombre_Ll_h_bd3}")
        print('')
        # Mover y renombrar el archivo, sobrescribiendo si es necesario
        shutil.move(ruta_Ll_h_bd3, nueva_ruta_Ll_h_bd3)

def renombra_Ll_d(ruta_Ll_d_bd3, num_estacion, ruta_analisis_Ll):
    if ruta_Ll_d_bd3:
        df_Ll_d_bd3 = pd.read_csv(ruta_Ll_d_bd3)
        df_Ll_d_bd3['TIMESTAMP'] = pd.to_datetime(df_Ll_d_bd3['TIMESTAMP'])
        tiempo_inicial_Ll_d = df_Ll_d_bd3['TIMESTAMP'].min()
        tiempo_final_Ll_d = df_Ll_d_bd3['TIMESTAMP'].max()
        nuevo_nombre_Ll_d_bd3 = f"{num_estacion}.{tiempo_inicial_Ll_d.strftime('%Y%m%d-%H')}.{tiempo_final_Ll_d.strftime('%Y%m%d-%H')}.Ll.d.bd3.csv"
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Se ha generado exitosamente el archivo de la lluvia diaria bd3 como: {nuevo_nombre_Ll_d_bd3}")
        print('')
        nueva_ruta_Ll_d_bd3 = os.path.join(ruta_analisis_Ll, nuevo_nombre_Ll_d_bd3)
        
        # Mover y renombrar el archivo, sobrescribiendo si es necesario
        shutil.move(ruta_Ll_d_bd3, nueva_ruta_Ll_d_bd3)
        
# Ejemplo de llamada a las funciones (asegúrate de definir las rutas adecuadas antes de llamarlas)
renombra_Ll_h(ruta_Ll_h_bd3, num_estacion, ruta_analisis_Ll)
renombra_Ll_d(ruta_Ll_d_bd3, num_estacion, ruta_analisis_Ll)


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

# Encuentra el archivo Ll.h.bd2.csv de la lluvia en la ruta de la estación
ruta_Ll_h_bd3 = next((os.path.join(ruta_analisis_Ll, archivo) for archivo in os.listdir(ruta_analisis_Ll) if archivo.endswith(".csv") and 'Ll.h.bd3' in archivo), None)

# Encuentra el archivo Ll.d.bd2.csv de la lluvia en la ruta de la estación
ruta_Ll_d_bd3 = next((os.path.join(ruta_analisis_Ll, archivo) for archivo in os.listdir(ruta_analisis_Ll) if archivo.endswith(".csv") and 'Ll.d.bd3' in archivo), None)

unidad = 'mm'

# Variables para Ll.h
Variables_Ll_h = ['Precip.mm.tot.1h.s1']
# Variables para Ll.d
Variables_Ll_d = ['Precip.mm.tot.dm.s1']


#-----------------------------------------------------------------------------------------------------------------
#Estadisticas chebyshev
if ruta_Ll_h_bd3 or ruta_Ll_d_bd3:
    # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if ruta_Ll_h_bd3:
            df_Ll_h_bd3 = pd.read_csv(ruta_Ll_h_bd3, na_values=['NA'])
            df_Ll_h_bd3['TIMESTAMP'] = pd.to_datetime(df_Ll_h_bd3['TIMESTAMP'])  # Convertir a tipo de dato de Fecha y hora
            
        if ruta_Ll_d_bd3:
            df_Ll_d_bd3 = pd.read_csv(ruta_Ll_d_bd3, na_values=['NA'])
            df_Ll_d_bd3['TIMESTAMP'] = pd.to_datetime(df_Ll_d_bd3['TIMESTAMP'])
            
# Definir los nombres de los meses en español
nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

def Estadisticos_Ll_h_d(ruta_pruebas_b, num_estacion):

    # Inicializar diccionarios para almacenar estadísticas de Ll_h y Ll_d
    estadisticos_Ll_h_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_Ll_h + Variables_Ll_d}

    # Iterar sobre cada mes en los datos de Ll_h y Ll_d
    for mes in range(1, 13):
        # Filtrar datos por mes para Ll_h y Ll_d
        df_mes_Ll_h = df_Ll_h_bd3[df_Ll_h_bd3['TIMESTAMP'].dt.month == mes]
        df_mes_Ll_d = df_Ll_d_bd3[df_Ll_d_bd3['TIMESTAMP'].dt.month == mes]

        # Iterar sobre cada variable en Variables_Ll_h y Variables_Ll_d
        for variable in Variables_Ll_h + Variables_Ll_d:
            # Seleccionar el dataframe correspondiente
            df_mes = df_mes_Ll_h if variable in Variables_Ll_h else df_mes_Ll_d

            # Calcular estadísticas si hay valores que no son NaN
            if not df_mes[variable].empty:
                # Calcular máximo, mínimo, media y desviación estándar
                max_val = df_mes[variable].max()
                min_val = df_mes[variable].min()
                mean_val = df_mes[variable].mean()
                std_val = df_mes[variable].std()

                # Almacenar estadísticas en el diccionario
                estadisticos_Ll_h_d[variable][nombres_meses[mes - 1]] = [max_val, min_val, mean_val, std_val]

    # Guardar estadísticas para Ll_h y Ll_d en un archivo de texto
    with open(os.path.join(ruta_pruebas_b, "Estadisticos_Ll_E1.txt"), "w") as file:
        for variable in Variables_Ll_h + Variables_Ll_d:
            file.write(f"\nEstación: {num_estacion} - Variable: {variable}\n")
            file.write("{:<12} {:<8} {:<8} {:<17} {:<17}\n".format("Mes", "Máximo", "Mínimo", "Media aritmética", "Desviación estándar"))
            for mes in range(1, 13):
                max_val, min_val, mean_val, std_val = estadisticos_Ll_h_d[variable][nombres_meses[mes - 1]]
                file.write("{:<12} {:<8.2f} {:<8.2f} {:<17.2f} {:<17.2f}\n".format(nombres_meses[mes - 1], max_val, min_val, mean_val, std_val))

# Llamada a la función
Estadisticos_Ll_h_d(ruta_pruebas_b, num_estacion)


#-----------------------------------------------------------------------------------------------------------------

#Genera diagramas de caja totales y mensuales para cada variable.
def Diagrama_caja_total_Ll(unidades):

    if ruta_Ll_h_bd3 or ruta_Ll_d_bd3:
        # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            if ruta_Ll_h_bd3:
                df_Ll_h_bd3 = pd.read_csv(ruta_Ll_h_bd3, na_values=['NA'])
                df_Ll_h_bd3['TIMESTAMP'] = pd.to_datetime(df_Ll_h_bd3['TIMESTAMP'])  # Convertir a tipo de dato de Fecha y hora

            if ruta_Ll_d_bd3:
                df_Ll_d_bd3 = pd.read_csv(ruta_Ll_d_bd3, na_values=['NA'])
                df_Ll_d_bd3['TIMESTAMP'] = pd.to_datetime(df_Ll_d_bd3['TIMESTAMP'])

            # Genera una figura con cuatro subtramas (3 filas, 2 columnas)
            fig, axes = plt.subplots(2, 2, figsize=(16, 25), dpi=300)
            
            # Boxplots para Ll.h
            if ruta_Ll_h_bd3:
                for i, variable_Ll_h in enumerate(Variables_Ll_h):
                    # Boxplot de la serie total (orientación vertical)
                    sns.boxplot(y=df_Ll_h_bd3[variable_Ll_h], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i, 0])
                    
                    axes[i, 0].set_title(f'{num_estacion} -{variable_Ll_h}- Total')
                    axes[i, 0].set_ylabel('Lluvia (mm)')
                    axes[i, 0].set_ylim(np.floor(df_Ll_h_bd3[variable_Ll_h].min()), np.ceil(df_Ll_h_bd3[variable_Ll_h].max()))
                    axes[i, 0].set_yticks(np.arange(np.floor(df_Ll_h_bd3[variable_Ll_h].min()), np.ceil(df_Ll_h_bd3[variable_Ll_h].max()), 5))
                    axes[i, 0].tick_params(axis='y', rotation=0)
                    axes[i, 0].grid(True, axis='y')

                    # Boxplots mensuales
                    sns.boxplot(x=df_Ll_h_bd3['TIMESTAMP'].dt.month, y=df_Ll_h_bd3[variable_Ll_h], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i, 1])
                    
                    axes[i, 1].set_title(f'{num_estacion} -{variable_Ll_h}- Mensual')
                    axes[i, 1].set_xlabel('Mes')
                    axes[i, 1].set_ylabel('Lluvia (mm)')
                    axes[i, 1].set_xticks(range(0, 13))  # 13 meses
                    axes[i, 1].set_ylim(np.floor(df_Ll_h_bd3[variable_Ll_h].min()), np.ceil(df_Ll_h_bd3[variable_Ll_h].max()))
                    axes[i, 1].set_yticks(np.arange(np.floor(df_Ll_h_bd3[variable_Ll_h].min()), np.ceil(df_Ll_h_bd3[variable_Ll_h].max()), 5))
                    axes[i, 1].tick_params(axis='x', rotation=45)
                    axes[i, 1].grid(True, axis='y')

            # Boxplots para Ll.d
            if ruta_Ll_d_bd3:
                for i, variable_Ll_d in enumerate(Variables_Ll_d):
                    # Boxplot de la serie total (orientación vertical)
                    sns.boxplot(y=df_Ll_d_bd3[variable_Ll_d], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i+1, 0])
                    
                    axes[i+1, 0].set_title(f'{num_estacion} -{variable_Ll_d}- Total')
                    axes[i+1, 0].set_ylabel('Lluvia (mm)')
                    axes[i+1, 0].set_ylim(np.floor(df_Ll_d_bd3[variable_Ll_d].min()), np.ceil(df_Ll_d_bd3[variable_Ll_d].max()))
                    axes[i+1, 0].set_yticks(np.arange(np.floor(df_Ll_d_bd3[variable_Ll_d].min()), np.ceil(df_Ll_d_bd3[variable_Ll_d].max()), 5))
                    axes[i+1, 0].tick_params(axis='y', rotation=0)
                    axes[i+1, 0].grid(True, axis='y')

                    # Boxplots mensuales
                    sns.boxplot(x=df_Ll_d_bd3['TIMESTAMP'].dt.month, y=df_Ll_d_bd3[variable_Ll_d], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i+1, 1])
                    
                    axes[i+1, 1].set_title(f'{num_estacion} -{variable_Ll_d}- Mensual')
                    axes[i+1, 1].set_xlabel('Mes')
                    axes[i+1, 1].set_ylabel('Lluvia (mm)')
                    axes[i+1, 1].set_xticks(range(0, 13))  # 13 meses
                    axes[i+1, 1].set_ylim(np.floor(df_Ll_d_bd3[variable_Ll_d].min()), np.ceil(df_Ll_d_bd3[variable_Ll_d].max()))
                    axes[i+1, 1].set_yticks(np.arange(np.floor(df_Ll_d_bd3[variable_Ll_d].min()), np.ceil(df_Ll_d_bd3[variable_Ll_d].max()), 5))
                    axes[i+1, 1].tick_params(axis='x', rotation=45)
                    axes[i+1, 1].grid(True, axis='y')

            # Ajusta la disposición general y muestra el gráfico
            plt.tight_layout()
            plt.subplots_adjust(top=0.95)
            # Agrega un título a la figura
            fig.suptitle(f'Diagramas de cajas - Estación: {num_estacion}', fontsize=16)
            nombre_diag_caja_Ll = 'DC_Ll_Total_E1.png'
            plt.savefig(os.path.join(ruta_pruebas_b, 'DC_Ll_Total_E1.png'))
            plt.close()
            print('-----------------------------------------------------------------------------------------------------------')
            print(f'Se ha generado exitosamente el diagrama de cajas de la serie total de la etapa 1 para la lluvia como: {nombre_diag_caja_Ll}.')
            print('')
            return True
    else:
        print("No se encontraron archivos Ll.h.bd3 y/o Ll.d.bd3 en la ruta especificada.")
        return False
    
#-----------------------------------------------------------------------------------------------------------------

def plot_time_series(df_Ll_h_bd3, df_Ll_d_bd3, var1, var2, title=None, xlabel="Tiempo", ylabel="Lluvia (mm)"):
    if title is None:
        title = f"Serie de tiempo - Estación: {num_estacion}"
    
    plt.figure(figsize=(60, 8), dpi=300)

    # Resample data to monthly frequency and calculate max
    df_Ll_h_bd3_monthly_max = df_Ll_h_bd3.resample('M', on='TIMESTAMP')[var1].max()
    df_Ll_d_bd3_monthly_max = df_Ll_d_bd3.resample('M', on='TIMESTAMP')[var2].max()
    
    # Reindex to the same date range
    date_range = pd.date_range(start=min(df_Ll_h_bd3_monthly_max.index.min(), df_Ll_d_bd3_monthly_max.index.min()), 
                               end=max(df_Ll_h_bd3_monthly_max.index.max(), df_Ll_d_bd3_monthly_max.index.max()), 
                               freq='M')
    df_Ll_h_bd3_monthly_max = df_Ll_h_bd3_monthly_max.reindex(date_range)
    df_Ll_d_bd3_monthly_max = df_Ll_d_bd3_monthly_max.reindex(date_range)
    
    # Create a combined dataframe for seaborn
    combined_df = pd.DataFrame({
        'Date': date_range,
        f'Max {var1}': df_Ll_h_bd3_monthly_max.values,
        f'Max {var2}': df_Ll_d_bd3_monthly_max.values,
    }).melt('Date', var_name='Variable', value_name='Value')
    
    # Plot using seaborn
    sns.lineplot(data=combined_df, x='Date', y='Value', hue='Variable', palette=['blue', 'red'], markers=True)
    
    # Add markers to the maximum points
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
    plt.gca().xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], bymonthday=-1))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%m'))
    
    # Rotate and align x-axis labels
    plt.xticks(rotation=90, ha='center')
    
    # Set y-axis major and minor tick locators and formatting
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(3))
    plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(3))
    plt.gca().yaxis.set_major_formatter('{:.0f}'.format)
    
    # Ensure ticks and labels appear on both sides of y-axis
    plt.gca().tick_params(axis='y', which='both', direction='inout', left=False, right=False)
    
    # Set y-axis limits to start from 0
    plt.ylim(bottom=0)
    
    # Disable the y-axis labels for the primary y-axis
    plt.gca().yaxis.set_ticks([])
    
    # Get the current y-axis limits
    y_limits = plt.gca().get_ylim()
    
    # Create a twin axis for y
    ax2 = plt.gca().twinx()
    ax2.set_ylim(y_limits)
    
    # Synchronize y-axis tick locators for the twin axis
    ax2.yaxis.set_major_locator(plt.MultipleLocator(3))
    ax2.yaxis.set_minor_locator(plt.MultipleLocator(3))
    ax2.yaxis.set_major_formatter('{:.0f}'.format)
    ax2.tick_params(axis='y', which='both', direction='inout', left=False, right=False)
    
    ax2.set_ylabel(ylabel)
    
    # Disable the y-axis labels for the secondary y-axis
    ax2.yaxis.set_ticks([])
    
    # Add horizontal gridlines for each tick
    plt.gca().yaxis.grid(True, which='both')
    
    # Add additional y-axis labels on top of each year
    unique_years = combined_df['Date'].dt.year.unique()
    for year in unique_years:
        year_date = pd.Timestamp(year=year, month=1, day=1)
        for y_value in range(int(y_limits[0]), int(y_limits[1])+1, 3):
            plt.text(year_date, y_value, f'{y_value}', ha='center', va='bottom', color='gray', fontsize=10)
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(os.path.join(ruta_pruebas_b, 'ST_Extremos_Ll_E1.png'))
    plt.show()
    
    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print('Se ha generado exitosamente la serie de tiempo de los extremos mensuales de la serie total para la lluvia de la etapa 1 como: ST_Extremos_Ll_E1.png.')
    print('')

def Diagrama_caja_mensual_T(unidades):
    
    # Leer archivos .csv y realizar operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        df_Ll_h_bd3 = None
        df_Ll_d_bd3 = None

        if ruta_Ll_h_bd3:
            df_Ll_h_bd3 = pd.read_csv(ruta_Ll_h_bd3, na_values=['NA'])
            df_Ll_h_bd3['TIMESTAMP'] = pd.to_datetime(df_Ll_h_bd3['TIMESTAMP']) 
            
        if ruta_Ll_d_bd3:
            df_Ll_d_bd3 = pd.read_csv(ruta_Ll_d_bd3, na_values=['NA'])
            df_Ll_d_bd3['TIMESTAMP'] = pd.to_datetime(df_Ll_d_bd3['TIMESTAMP'])

    # Lista de nombres de los meses en español
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    # Iterar a través de cada mes
    for month in range(1, 13):
        # Nombre del mes en español
        nombre_mes_carpeta = f"{month:02d}.{meses[month - 1]}"
        nombre_mes = meses[month - 1]
        ruta_meses = os.path.join(ruta_pruebas_b, nombre_mes_carpeta)
        os.makedirs(ruta_meses, exist_ok=True)

        # Genera una figura con (2 filas, 1 columna)
        fig, axes = plt.subplots(2, 1, figsize=(10, 20), dpi=300)

        # Diagramas de caja para Ll.h si df_Ll_h_bd3 no es None
        if df_Ll_h_bd3 is not None:
            for i, variable_Ll_h in enumerate(Variables_Ll_h):
                data = df_Ll_h_bd3[variable_Ll_h][df_Ll_h_bd3['TIMESTAMP'].dt.month == month]
                
                # Calcular estadísticas
                Media_aritmética_Ll_h = data.mean()
                Desviación_estándar_Ll_h = data.std()
                P25_Ll_h = data.quantile(0.25)
                P50_Ll_h = data.quantile(0.50)  # Median
                P75_Ll_h = data.quantile(0.75)
                IQR_Ll_h = P75_Ll_h - P25_Ll_h
                BI_Ll_h = P25_Ll_h - 1.5 * IQR_Ll_h
                BS_Ll_h = P75_Ll_h + 1.5 * IQR_Ll_h
                Min_Ll_h = data.min()
                Max_Ll_h = data.max()
                MinZ_Ll_h = (Min_Ll_h - Media_aritmética_Ll_h) / Desviación_estándar_Ll_h
                MaxZ_Ll_h = (Max_Ll_h - Media_aritmética_Ll_h) / Desviación_estándar_Ll_h
                lim_inf_Ll_h = np.fix(MinZ_Ll_h)*Desviación_estándar_Ll_h + Media_aritmética_Ll_h
                lim_sup_Ll_h = np.fix(MaxZ_Ll_h)*Desviación_estándar_Ll_h + Media_aritmética_Ll_h
                
                sns.boxplot(y=data, color="blue", linewidth=1.5,
                            boxprops=dict(facecolor='blue', edgecolor='black'),
                            flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'),
                            ax=axes[i])
                axes[i].set_title(f'{num_estacion} - {variable_Ll_h} - {nombre_mes}')
                axes[i].set_xlabel('')
                axes[i].set_ylabel(f'Lluvia ({unidad})')
                
                # Set the y-axis limits
                axes[i].set_ylim(np.floor(data.min()), np.ceil(data.max()))
                # Automatically adjust the number of y-ticks based on the data range
                axes[i].yaxis.set_major_locator(ticker.MaxNLocator(15))
                
                #axes[i].set_ylim(np.floor(data.min()), np.ceil(data.max()))
                #axes[i].set_yticks(range(int(data.min()), int(data.max()) + 1))
                axes[i].tick_params(axis='y', rotation=00)

                # Agregar información estadística en la esquina superior derecha de cada subplot
                axes[i].text(0.95, 0.95, f'Media aritmética = {Media_aritmética_Ll_h:.2f}{unidad}\nDesviación estándar = {Desviación_estándar_Ll_h:.2f}{unidad}\nLím.Vec. superior = {lim_sup_Ll_h:.2f}{unidad}\nBigote superior = {BS_Ll_h:.2f}{unidad}',
                                      transform=axes[i].transAxes,
                                      fontsize=8, verticalalignment='top', horizontalalignment='right', backgroundcolor='white')

        # Diagramas de caja para Ll.d si df_Ll_d_bd3 no es None
        if df_Ll_d_bd3 is not None:
            for i, variable_Ll_d in enumerate(Variables_Ll_d):
                data = df_Ll_d_bd3[variable_Ll_d][df_Ll_d_bd3['TIMESTAMP'].dt.month == month]
                
                # Calcular estadísticas
                Media_aritmética_Ll_d = data.mean()
                Desviación_estándar_Ll_d = data.std()
                P25_Ll_d = data.quantile(0.25)
                P50_Ll_d = data.quantile(0.50)  # Median
                P75_Ll_d = data.quantile(0.75)
                IQR_Ll_d = P75_Ll_d - P25_Ll_d
                BI_Ll_d = P25_Ll_d - 1.5 * IQR_Ll_d
                BS_Ll_d = P75_Ll_d + 1.5 * IQR_Ll_d
                Min_Ll_d = data.min()
                Max_Ll_d = data.max()
                MinZ_Ll_d = (Min_Ll_d - Media_aritmética_Ll_d) / Desviación_estándar_Ll_d
                MaxZ_Ll_d = (Max_Ll_d - Media_aritmética_Ll_d) / Desviación_estándar_Ll_d
                lim_inf_Ll_d = np.fix(MinZ_Ll_d)*Desviación_estándar_Ll_d + Media_aritmética_Ll_d
                lim_sup_Ll_d = np.fix(MaxZ_Ll_d)*Desviación_estándar_Ll_d + Media_aritmética_Ll_d
                
                sns.boxplot(y=data, color="blue", linewidth=1.5,
                            boxprops=dict(facecolor='blue', edgecolor='black'),
                            flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'),
                            ax=axes[i+1])
                axes[i+1].set_title(f'{num_estacion} - {variable_Ll_d} - {nombre_mes}')
                axes[i+1].set_xlabel('')
                axes[i+1].set_ylabel(f'Lluvia ({unidad})')
                
                # Set the y-axis limits
                axes[i+1].set_ylim(np.floor(data.min()), np.ceil(data.max()))
                # Automatically adjust the number of y-ticks based on the data range
                axes[i+1].yaxis.set_major_locator(ticker.MaxNLocator(15))
                
                #axes[i+1].set_ylim(np.floor(data.min()), np.ceil(data.max()))
                #axes[i+1].set_yticks(range(int(data.min()), int(data.max()) + 1))
                axes[i+1].tick_params(axis='y', rotation=0)

                # Agregar información estadística en la esquina superior derecha de cada subplot
                axes[i+1].text(0.95, 0.95, f'Media aritmética = {Media_aritmética_Ll_d:.2f}{unidad}\nDesviación estándar = {Desviación_estándar_Ll_d:.2f}{unidad}\nLím.Vec.superior = {lim_sup_Ll_d:.2f}{unidad}\nBigote superior = {BS_Ll_d:.2f}{unidad}',
                                             transform=axes[i+1].transAxes,
                                             fontsize=8, verticalalignment='top', horizontalalignment='right', backgroundcolor='white')
    # Ajustar el diseño
        plt.tight_layout()

    # Guardar el gráfico
        plt.savefig(os.path.join(ruta_meses, f'DC_Ll_{nombre_mes}_E1.png'))
        plt.close()

    print('-----------------------------------------------------------------------------------------------------------')
    print('Se han generado exitosamente los diagramas de cajas mensuales de la etapa 1 para la lluvia.')
    print('')
    return True if (df_Ll_h_bd3 is not None or df_Ll_d_bd3 is not None) else False

#-----------------------------------------------------------------------------------------------------------------
#Llama funciones:

Diagrama_caja_total_Ll(['%', '%'])

# Example call to the function (adjust variables and dataframes as per your dataset)
plot_time_series(df_Ll_h_bd3, df_Ll_d_bd3, 'Precip.mm.tot.1h.s1', 'Precip.mm.tot.dm.s1')

Diagrama_caja_mensual_T("")

def generar_archivo_txt_Ll_h():
    # Si existe el archivo ruta_Ll_h_bd3, procesar y crear el archivo de texto
    if ruta_Ll_h_bd3:
        # Leer el archivo CSV y reemplazar los NA por -9
        df_Ll_h_bd3 = pd.read_csv(ruta_Ll_h_bd3)
        df_Ll_h_bd3.fillna(-9, inplace=True)

        # Crear una copia del DataFrame con los nombres de columnas cambiados
        df_Ll_h_bd3_copy = df_Ll_h_bd3.rename(columns={
            'Precip.mm.tot.1h.s1': 'LLUV_mm_Tot'
        })

        # Crear el nombre del archivo de texto
        Fecha_inicial = pd.to_datetime(df_Ll_h_bd3['TIMESTAMP']).min().strftime('%Y%m%d')
        Fecha_final = pd.to_datetime(df_Ll_h_bd3['TIMESTAMP']).max().strftime('%Y%m%d')
        nombre_archivo_txt_Ll_h = f"H-{num_estacion}-{Fecha_inicial}-{Fecha_final}.txt"

        # Guardar el archivo de texto con las celdas separadas por coma
        ruta_archivo_texto = os.path.join(ruta_analisis_Ll, nombre_archivo_txt_Ll_h)
        for file_name in os.listdir(ruta_analisis_Ll):
            if file_name.startswith('H-'):
                os.remove(os.path.join(ruta_analisis_Ll, file_name)) 
                
        menos_nueve_entero(df_Ll_h_bd3_copy, ruta_archivo_texto)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Se ha generado exitosamente el archivo de texto de la lluvia horaria como: {nombre_archivo_txt_Ll_h}.")
        print('')
    else:
        print("Error: No se pudo generar el archivo de texto puesto que no se encontró el archivo de la lluvia horaria bd3")

# Llamada a la función
generar_archivo_txt_Ll_h()

def generar_archivo_txt_Ll_d():
    # Si existe el archivo ruta_Ll_d_bd3, procesar y crear el archivo de texto
    if ruta_Ll_d_bd3:
        # Leer el archivo CSV y reemplazar los NA por -9
        df_Ll_d_bd3 = pd.read_csv(ruta_Ll_d_bd3)
        df_Ll_d_bd3.fillna(int(-9), inplace=True)
        
        # Crear una copia del DataFrame con los nombres de columnas cambiados
        df_Ll_d_bd3_copy = df_Ll_d_bd3.rename(columns={
            'Precip.mm.tot.dm.s1': 'LLUV_mm_Tot',
            'Precip-acum5.mm_h.max.dm.s1': 'Acum5_Max',
            'Precip-acum10.mm_h.max.dm.s1': 'Acum10_Max',
            'Precip-acum15.mm_h.max.dm.s1': 'Acum15_Max',
            'Precip-acum30.mm_h.max.dm.s1': 'Acum30_Max'
        })

        # Crear el nombre del archivo de texto
        Fecha_inicial = pd.to_datetime(df_Ll_d_bd3['TIMESTAMP']).min().strftime('%Y%m%d')
        Fecha_final = pd.to_datetime(df_Ll_d_bd3['TIMESTAMP']).max().strftime('%Y%m%d')
        nombre_arcihvotxt_Ll_d = f"D-{num_estacion}-{Fecha_inicial}-{Fecha_final}.txt"

        # Guardar el archivo de texto con las celdas separadas por coma
        ruta_archivo_texto = os.path.join(ruta_analisis_Ll, nombre_arcihvotxt_Ll_d)
        # Verificar si existe un archivo que comience con "D-" y eliminarlo
        for file_name in os.listdir(ruta_analisis_Ll):
            if file_name.startswith('D-'):
                os.remove(os.path.join(ruta_analisis_Ll, file_name))
                
        menos_nueve_entero(df_Ll_d_bd3_copy, ruta_archivo_texto)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Se ha generado exitosamente el archivo de texto de la lluvia diaria como: {nombre_arcihvotxt_Ll_d}.")
        print('')
    else:
        print("Error:No se pudo generar el archivo de texto puesto que no se encontró el archivo de la lluvia diaria bd3")
        
generar_archivo_txt_Ll_d()