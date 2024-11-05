import pandas as pd
import os
import warnings
import shutil
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

# Eliminar UserWarnings de openpyxl
warnings.simplefilter('ignore', category=UserWarning)

datos_crudos = r'C:\\MeteoRBD.v1.0.0\\data_rbd'

# Encuentra el archivo .xlsx en los datos_crudos que contiene 'Cuenca' y 'Estación' como columnas
ruta_archivo = next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Humedad" in file and file.endswith(".xlsx")), None)

if ruta_archivo:
    archivo_excel = pd.read_excel(ruta_archivo)
    if all(col in archivo_excel.columns for col in ['Cuenca', 'Estación']):
        # Obtiene el número de estación a partir del archivo Excel
        cuenca = str(archivo_excel['Cuenca'].iloc[0])
        estacion = str(archivo_excel['Estación'].iloc[0])
        if len(estacion) == 2:
            estacion = '0' + estacion  # Add leading zero if 'Estación' has only two digits
        elif len(estacion) == 1:
            estacion = '00' + estacion
            
        num_estacion = cuenca + estacion
        num_estacion = int(num_estacion)

# Establece la ruta para los archivos de la humedad relativa según el número de estación obtenido del archivo Excel
ruta_analisis_HR = f"C:\\MeteoRBD.v1.0.0\\Data_Lake\\{num_estacion}-ema\\base_datos\\Humedad relativa\\análisis_datos"

# Crea las carpetas si no existen
for carpeta in ["", "Pruebas_estadisticas"]:
    ruta_pruebas_b = os.path.join(ruta_analisis_HR, carpeta)
    os.makedirs(ruta_pruebas_b, exist_ok=True)
    
# Encuentra el archivo HR.h.bd2.csv de la humedad relativa en la ruta de la estación
ruta_HR_h_bd2 = next((os.path.join(ruta_analisis_HR, archivo) for archivo in os.listdir(ruta_analisis_HR) if archivo.endswith(".csv") and 'HR.h.bd2' in archivo), None)

# Encuentra el archivo HR.d.bd2.csv de la humedad relativa en la ruta de la estación
ruta_HR_d_bd2 = next((os.path.join(ruta_analisis_HR, archivo) for archivo in os.listdir(ruta_analisis_HR) if archivo.endswith(".csv") and 'HR.d.bd2' in archivo), None)

# Define the function to generate final bd3 files
def genera_archivos_final_bd3():
    if ruta_HR_h_bd2:
        # Cambiar los nombres de los archivos a bd3
        archivo_final_rev_HR_h = ruta_HR_h_bd2.replace("HR.h.bd2", "HR.h.bd3")
        # Si el archivo bd3 ya existe, reemplazarlo
        if os.path.exists(archivo_final_rev_HR_h):
            os.remove(archivo_final_rev_HR_h)
        shutil.copy(ruta_HR_h_bd2, archivo_final_rev_HR_h)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Se ha replicado exitosamente el archivo de la humedad relativa horaria bd2 como: {os.path.basename(archivo_final_rev_HR_h)}.")
        print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la humedad relativa horaria bd2.")
        print('')

    if ruta_HR_d_bd2:
        # Cambiar los nombres de los archivos a bd3
        archivo_final_rev_HR_d = ruta_HR_d_bd2.replace("HR.d.bd2", "HR.d.bd3")
        # Si el archivo bd3 ya existe, reemplazarlo
        if os.path.exists(archivo_final_rev_HR_d):
            os.remove(archivo_final_rev_HR_d)
        shutil.copy(ruta_HR_d_bd2, archivo_final_rev_HR_d)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Se ha replicado exitosamente el archivo de la humedad relativa diaria bd2 como: {os.path.basename(archivo_final_rev_HR_d)}.")
        print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo humedad relativa diaria bd2.")
        print('')
        
def edita_mod_HR_h_db3():
    archivos_HR_h = os.path.join(ruta_analisis_HR, "Modif_Tec_HR_h.csv")
    
    if os.path.exists(archivos_HR_h):
        df_mod_HR_h = pd.read_csv(archivos_HR_h)
        
        if ruta_HR_h_bd3 and os.path.exists(ruta_HR_h_bd3):
            df_HR_h_bd3 = pd.read_csv(ruta_HR_h_bd3)  # Lee el archivo HR.h.bd3.csv una vez fuera del bucle
            
            for index, row in df_mod_HR_h.iterrows():
                Elemento = row['Elemento']
                Fecha = row['Fecha']
                valor_reemplazo = row['Valor_reemplazo']
                
                # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                if valor_reemplazo != 'NA':
                    # Realiza el reemplazo si coincide el Elemento y la Fecha
                    df_HR_h_bd3.loc[(df_HR_h_bd3['TIMESTAMP'] == Fecha), Elemento] = valor_reemplazo
            
            # Guarda el archivo HR.h.bd3.csv después de realizar todos los reemplazos
            df_HR_h_bd3.to_csv(ruta_HR_h_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos
            
            if len(df_mod_HR_h) >= 1:
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print("Se han incluido exitosamente los cambios generados en el archivo Modif_Tec_HR_h en el archivo de la humedad relativa horaria bd3.")
                print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo Modif_Tec_h.csv.")
        print('')

def edita_mod_HR_d_db3():
    archivos_HR_d = os.path.join(ruta_analisis_HR, "Modif_Tec_HR_d.csv")
    
    if os.path.exists(archivos_HR_d):
        if ruta_HR_d_bd3 and os.path.exists(ruta_HR_d_bd3):  # Verifica si el archivo HR.d.bd3.csv existe
            df_mod_HR_d = pd.read_csv(archivos_HR_d)
            df_HR_d_bd3 = pd.read_csv(ruta_HR_d_bd3)  # Lee el archivo HR.d.bd3.csv una vez fuera del bucle
            for index, row in df_mod_HR_d.iterrows():
                Elemento = row['Elemento']
                Fecha = row['Fecha']
                valor_reemplazo = row['Valor_reemplazo']
                # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                if valor_reemplazo != 'NA':
                    # Realiza el reemplazo si coincide el Elemento y la Fecha
                    df_HR_d_bd3.loc[(df_HR_d_bd3['TIMESTAMP'] == Fecha), Elemento] = valor_reemplazo
            # Guarda el archivo HR.d.bd3.csv después de realizar todos los reemplazos
            df_HR_d_bd3.to_csv(ruta_HR_d_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos
            if len(df_mod_HR_d) >= 1:
                print('-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print("Se han incluido exitosamente los cambios generados en el archivo Modif_Tec_HR_d en el archivo de la humedad relativa diaria bd3.")
                print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo Modif_Tec_d.csv.")
        print('')
        
def edita_HR_h_db3():
    if ruta_HR_h_bd3:
        for root, dirs, files in os.walk(ruta_pruebas_b):
            for file in files:
                if 'HR_h' in file and file.endswith('.csv'):
                    archivos_HR_h = os.path.join(root, file)
                    df_mes_HR_h = pd.read_csv(archivos_HR_h)
                    df_HR_h_bd3 = pd.read_csv(ruta_HR_h_bd3)  # Lee el archivo HR.h.bd3.csv una vez fuera del bucle
                    for index, row in df_mes_HR_h.iterrows():
                        Elemento = row['Elemento']
                        Fecha = row['Fecha']
                        valor_reemplazo = row['Valor_reemplazo']
                        # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                        if valor_reemplazo != 'NA':
                            # Realiza el reemplazo si coincide el Elemento y la Fecha
                            df_HR_h_bd3.loc[(df_HR_h_bd3['TIMESTAMP'] == Fecha), Elemento] = valor_reemplazo
                    # Guarda el archivo HR.h.bd3.csv después de realizar todos los reemplazos
                    df_HR_h_bd3.to_csv(ruta_HR_h_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Se han incluido exitosamente los cambios generados en los archivos mensuales en el archivo de la humedad relativa horaria bd3.")
        print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la humedad relativa horaria bd3.")
        print('')

def edita_HR_d_db3():
    if ruta_HR_d_bd3:
        for root, dirs, files in os.walk(ruta_pruebas_b):
            for file in files:
                if 'HR_d' in file and file.endswith('.csv'):
                    archivos_HR_d = os.path.join(root, file)
                    df_mes_HR_d = pd.read_csv(archivos_HR_d)
                    df_HR_d_bd3 = pd.read_csv(ruta_HR_d_bd3)  # Lee el archivo HR.d.bd3.csv una vez fuera del bucle
                    for index, row in df_mes_HR_d.iterrows():
                        Elemento = row['Elemento']
                        Fecha = row['Fecha']
                        valor_reemplazo = row['Valor_reemplazo']
                        # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                        if valor_reemplazo != 'NA':
                            # Realiza el reemplazo si coincide el Elemento y la Fecha
                            df_HR_d_bd3.loc[(df_HR_d_bd3['TIMESTAMP'] == Fecha), Elemento] = valor_reemplazo
                    # Guarda el archivo HR.d.bd3.csv después de realizar todos los reemplazos
                    df_HR_d_bd3.to_csv(ruta_HR_d_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Se han incluido exitosamente los cambios generados en los archivos mensuales en el archivo de la humedad relativa diaria bd3.")
        print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la humedad relativa diaria bd3.")
        print('')
        

genera_archivos_final_bd3()

# Encuentra el archivo HR.h.bd2.csv de la humedad relativa en la ruta de la estación
ruta_HR_h_bd3 = next((os.path.join(ruta_analisis_HR, archivo) for archivo in os.listdir(ruta_analisis_HR) if archivo.endswith(".csv") and 'HR.h.bd3' in archivo), None)

# Encuentra el archivo HR.d.bd2.csv de la humedad relativa en la ruta de la estación
ruta_HR_d_bd3 = next((os.path.join(ruta_analisis_HR, archivo) for archivo in os.listdir(ruta_analisis_HR) if archivo.endswith(".csv") and 'HR.d.bd3' in archivo), None)

edita_HR_h_db3()
edita_HR_d_db3()

edita_mod_HR_h_db3()
edita_mod_HR_d_db3()

def elimina_fila_anumerica_HR_h():
    if ruta_HR_h_bd3:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_HR_h_bd3 = pd.read_csv(ruta_HR_h_bd3, na_values=['NA'])
            
        # Rellena las celdas en blanco con 'NA' en todo el DataFrame
        #df_HR_h_bd3.fillna('NA', inplace=True)

        # Filtra las filas sin valores numéricos al principio y al final en ciertas columnas
        indices_numericos_HR_h = df_HR_h_bd3[df_HR_h_bd3[['RH.perc.avg.1h.s1']].apply(pd.to_numeric, errors='coerce').notnull().any(axis=1)].index
        
        if not indices_numericos_HR_h.empty:
            primer_indice_numerico_HR_h = indices_numericos_HR_h[0]
            ultimo_indice_numerico_HR_h = indices_numericos_HR_h[-1]

            # Conserva las filas con valores numéricos
            df_HR_h_bd3 = df_HR_h_bd3.iloc[primer_indice_numerico_HR_h:ultimo_indice_numerico_HR_h + 1]

            # Rellena valores no numéricos con 'NA' en ciertas columnas y agrega el número de estación en la columna ESTACION
            rellena_caracteres_NA_HR_h = ['RH.perc.avg.1h.s1']
            for col in rellena_caracteres_NA_HR_h:
                df_HR_h_bd3[col] = pd.to_numeric(df_HR_h_bd3[col], errors='coerce').fillna('NA')

            # Guarda el archivo CSV
            df_HR_h_bd3.to_csv(ruta_HR_h_bd3, index=False, na_rep='NA')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la humedad relativa horaria bd3")

elimina_fila_anumerica_HR_h()

def elimina_fila_anumerica_HR_d():
    if ruta_HR_d_bd3:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_HR_d_bd3 = pd.read_csv(ruta_HR_d_bd3, na_values=['NA'])
            
        # Rellena las celdas en blanco con 'NA' en todo el DataFrame
        #df_HR_d_bd3.fillna('NA', inplace=True)

        # Filtra las filas sin valores numéricos al principio y al final en ciertas columnas
        indices_numericos_HR_d = df_HR_d_bd3[df_HR_d_bd3[['RH.perc.max.dm.s1', 'RH.perc.min.dm.s1']].apply(pd.to_numeric, errors='coerce').notnull().any(axis=1)].index
        
        if not indices_numericos_HR_d.empty:
            primer_indice_numerico_HR_d = indices_numericos_HR_d[0]
            ultimo_indice_numerico_HR_d = indices_numericos_HR_d[-1]

            # Conserva las filas con valores numéricos
            df_HR_d_bd3 = df_HR_d_bd3.iloc[primer_indice_numerico_HR_d:ultimo_indice_numerico_HR_d + 1]

            # Rellena valores no numéricos con 'NA' en ciertas columnas y agrega el número de estación en la columna ESTACION
            rellena_caracteres_NA_HR_d = ['RH.perc.max.dm.s1', 'RH.perc.min.dm.s1']
            for col in rellena_caracteres_NA_HR_d:
                df_HR_d_bd3[col] = pd.to_numeric(df_HR_d_bd3[col], errors='coerce').fillna('NA')
                
            # Guarda el archivo CSV
            df_HR_d_bd3.to_csv(ruta_HR_d_bd3, index=False, na_rep='NA')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la humedad relativa horaria bd3")

elimina_fila_anumerica_HR_d()

def renombra_HR_h(ruta_HR_h_bd3, num_estacion, ruta_analisis_HR):
    if ruta_HR_h_bd3:
        df_HR_h_bd3 = pd.read_csv(ruta_HR_h_bd3)
        df_HR_h_bd3['TIMESTAMP'] = pd.to_datetime(df_HR_h_bd3['TIMESTAMP'])
        tiempo_inicial_HR_h = df_HR_h_bd3['TIMESTAMP'].min()
        tiempo_final_HR_h = df_HR_h_bd3['TIMESTAMP'].max()
        nuevo_nombre_HR_h_bd3 = f"{num_estacion}.{tiempo_inicial_HR_h.strftime('%Y%m%d-%H')}.{tiempo_final_HR_h.strftime('%Y%m%d-%H')}.HR.h.bd3.csv"
        nueva_ruta_HR_h_bd3 = os.path.join(ruta_analisis_HR, nuevo_nombre_HR_h_bd3)
        os.rename(ruta_HR_h_bd3, nueva_ruta_HR_h_bd3)

renombra_HR_h(ruta_HR_h_bd3, num_estacion, ruta_analisis_HR)

def renombra_HR_d(ruta_HR_d_bd3, num_estacion, ruta_analisis_HR):
    if ruta_HR_d_bd3:
        df_HR_d_bd3 = pd.read_csv(ruta_HR_d_bd3)
        df_HR_d_bd3['TIMESTAMP'] = pd.to_datetime(df_HR_d_bd3['TIMESTAMP'])
        tiempo_inicial_HR_d = df_HR_d_bd3['TIMESTAMP'].min()
        tiempo_final_HR_d = df_HR_d_bd3['TIMESTAMP'].max()
        nuevo_nombre_HR_d_bd3 = f"{num_estacion}.{tiempo_inicial_HR_d.strftime('%Y%m%d-%H')}.{tiempo_final_HR_d.strftime('%Y%m%d-%H')}.HR.d.bd3.csv"
        nueva_ruta_HR_d_bd3 = os.path.join(ruta_analisis_HR, nuevo_nombre_HR_d_bd3)
        os.rename(ruta_HR_d_bd3, nueva_ruta_HR_d_bd3)

renombra_HR_d(ruta_HR_d_bd3, num_estacion, ruta_analisis_HR)


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

# Encuentra el archivo HR.h.bd2.csv de la humedad relativa en la ruta de la estación
ruta_HR_h_bd3 = next((os.path.join(ruta_analisis_HR, archivo) for archivo in os.listdir(ruta_analisis_HR) if archivo.endswith(".csv") and 'HR.h.bd3' in archivo), None)

# Encuentra el archivo HR.d.bd2.csv de la humedad relativa en la ruta de la estación
ruta_HR_d_bd3 = next((os.path.join(ruta_analisis_HR, archivo) for archivo in os.listdir(ruta_analisis_HR) if archivo.endswith(".csv") and 'HR.d.bd3' in archivo), None)

#-----------------------------------------------------------------------------------------------------------------
unidad = '%'

# Variables para HR.h
Variables_HR_h = ['RH.perc.avg.1h.s1']
# Variables para HR.d
Variables_HR_d = ['RH.perc.max.dm.s1', 'RH.perc.min.dm.s1']

# Definir los nombres de los meses en español
nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

#-----------------------------------------------------------------------------------------------------------------

if ruta_HR_h_bd3 or ruta_HR_d_bd3:
    # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if ruta_HR_h_bd3:
            df_HR_h_bd3 = pd.read_csv(ruta_HR_h_bd3, na_values=['NA'])
            df_HR_h_bd3['TIMESTAMP'] = pd.to_datetime(df_HR_h_bd3['TIMESTAMP'])  # Convertir a tipo de dato de fecha y hora

        if ruta_HR_d_bd3:
            df_HR_d_bd3 = pd.read_csv(ruta_HR_d_bd3, na_values=['NA'])
            df_HR_d_bd3['TIMESTAMP'] = pd.to_datetime(df_HR_d_bd3['TIMESTAMP'])

def Estadisticos_HR_h_d(ruta_pruebas_b, num_estacion):

    # Inicializar diccionarios para almacenar estadísticas de HR_h y HR_d
    estadisticos_HR_h_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_HR_h + Variables_HR_d}

    # Iterar sobre cada mes en los datos de HR_h y HR_d
    for mes in range(1, 13):
        # Filtrar datos por mes para HR_h y HR_d
        df_mes_HR_h = df_HR_h_bd3[df_HR_h_bd3['TIMESTAMP'].dt.month == mes]
        df_mes_HR_d = df_HR_d_bd3[df_HR_d_bd3['TIMESTAMP'].dt.month == mes]

        # Iterar sobre cada variable en Variables_HR_h y Variables_HR_d
        for variable in Variables_HR_h + Variables_HR_d:
            # Seleccionar el dataframe correspondiente
            df_mes = df_mes_HR_h if variable in Variables_HR_h else df_mes_HR_d

            # Calcular estadísticas si hay valores que no son NaN
            if not df_mes[variable].empty:
                # Calcular máximo, mínimo, media y desviación estándar
                max_val = df_mes[variable].max()
                min_val = df_mes[variable].min()
                mean_val = df_mes[variable].mean()
                std_val = df_mes[variable].std()

                # Almacenar estadísticas en el diccionario
                estadisticos_HR_h_d[variable][nombres_meses[mes - 1]] = [max_val, min_val, mean_val, std_val]

    # Guardar estadísticas para HR_h y HR_d en un archivo de texto
    with open(os.path.join(ruta_pruebas_b, "Estadisticos_HR_E1.txt"), "w") as file:
        for variable in Variables_HR_h + Variables_HR_d:
            file.write(f"\nEstación: {num_estacion} - Variable: {variable}\n")
            file.write("{:<12} {:<8} {:<8} {:<17} {:<17}\n".format("Mes", "Máximo", "Mínimo", "Media aritmética", "Desviación estándar"))
            for mes in range(1, 13):
                max_val, min_val, mean_val, std_val = estadisticos_HR_h_d[variable][nombres_meses[mes - 1]]
                file.write("{:<12} {:<8.2f} {:<8.2f} {:<17.2f} {:<17.2f}\n".format(nombres_meses[mes - 1], max_val, min_val, mean_val, std_val))

# Llamada a la función
Estadisticos_HR_h_d(ruta_pruebas_b, num_estacion)

#-----------------------------------------------------------------------------------------------------------------

#Genera diagramas de caja totales y mensuales para cada variable.
def Diagrama_caja_total_HR(unidades):

    if ruta_HR_h_bd3 or ruta_HR_d_bd3:
        # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            if ruta_HR_h_bd3:
                df_HR_h_bd3 = pd.read_csv(ruta_HR_h_bd3, na_values=['NA'])
                df_HR_h_bd3['TIMESTAMP'] = pd.to_datetime(df_HR_h_bd3['TIMESTAMP'])  # Convertir a tipo de dato de Fecha y hora
                
            if ruta_HR_d_bd3:
                df_HR_d_bd3 = pd.read_csv(ruta_HR_d_bd3, na_values=['NA'])
                df_HR_d_bd3['TIMESTAMP'] = pd.to_datetime(df_HR_d_bd3['TIMESTAMP'])

            # Genera una figura con cuatro subtramas (3 filas, 2 columnas)
            fig, axes = plt.subplots(3, 2, figsize=(16, 25), dpi=300)
            
            intervalo = 2

            # Boxplots para HR.h
            if ruta_HR_h_bd3:
                for i, variable_HR_h in enumerate(Variables_HR_h):
                    # Boxplot de la serie total (orientación vertical)
                    sns.boxplot(y=df_HR_h_bd3[variable_HR_h], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i, 0])
                    
                    axes[i, 0].set_title(f'Diagrama de caja serie total -{variable_HR_h}- Estación: {num_estacion}')
                    axes[i, 0].set_ylabel('')
                    axes[i, 0].set_ylim(np.floor(df_HR_h_bd3[variable_HR_h].min()), np.ceil(df_HR_h_bd3[variable_HR_h].max()))
                    axes[i, 0].set_yticks(np.arange(np.floor(df_HR_h_bd3[variable_HR_h].min()), np.ceil(df_HR_h_bd3[variable_HR_h].max()), 2))
                    #axes[i, 0].set_yticks(range(0, 100 + 1, intervalo))
                    axes[i, 0].tick_params(axis='y', rotation=0)
                    axes[i, 0].grid(True, axis='y')

                    # Boxplots mensuales
                    sns.boxplot(x=df_HR_h_bd3['TIMESTAMP'].dt.month, y=df_HR_h_bd3[variable_HR_h], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i, 1])
                    
                    axes[i, 1].set_title(f'Diagrama de cajas mensuales - {variable_HR_h} - Estación: {num_estacion}')
                    axes[i, 1].set_xlabel('Mes')
                    axes[i, 1].set_ylabel('')
                    axes[i, 1].set_xticks(range(0, 13))  # 13 meses
                    axes[i, 1].set_ylim(np.floor(df_HR_h_bd3[variable_HR_h].min()), np.ceil(df_HR_h_bd3[variable_HR_h].max()))
                    axes[i, 1].set_yticks(np.arange(np.floor(df_HR_h_bd3[variable_HR_h].min()), np.ceil(df_HR_h_bd3[variable_HR_h].max()), 2))
                    #axes[i, 0].set_yticks(range(0, 100 + 1, intervalo))
                    axes[i, 1].tick_params(axis='x', rotation=45)
                    axes[i, 1].grid(True, axis='y')

            # Boxplots para HR.d
            if ruta_HR_d_bd3:
                for i, variable_HR_d in enumerate(Variables_HR_d):
                    # Boxplot de la serie total (orientación vertical)
                    sns.boxplot(y=df_HR_d_bd3[variable_HR_d], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i+1, 0])
                    
                    axes[i+1, 0].set_title(f'Diagrama de caja serie total -{variable_HR_d}- Estación: {num_estacion}')
                    axes[i+1, 0].set_ylabel('')
                    #axes[i+1, 0].set_yticks(range(0, 100 + 1, intervalo))
                    axes[i+1, 0].set_ylim(np.floor(df_HR_d_bd3[variable_HR_d].min()), np.ceil(df_HR_d_bd3[variable_HR_d].max()))
                    axes[i+1, 0].set_yticks(np.arange(np.floor(df_HR_d_bd3[variable_HR_d].min()), np.ceil(df_HR_d_bd3[variable_HR_d].max()), 2))
                    axes[i+1, 0].tick_params(axis='y', rotation=0)
                    axes[i+1, 0].grid(True, axis='y')

                    # Boxplots mensuales
                    sns.boxplot(x=df_HR_d_bd3['TIMESTAMP'].dt.month, y=df_HR_d_bd3[variable_HR_d], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i+1, 1])
                    
                    axes[i+1, 1].set_title(f'Diagrama de cajas mensuales - {variable_HR_d} - Estación: {num_estacion}')
                    axes[i+1, 1].set_xlabel('Mes')
                    axes[i+1, 1].set_ylabel('')
                    axes[i+1, 1].set_xticks(range(0, 13))  # 13 meses
                    
                    #axes[i+1, 0].set_yticks(range(0, 100 + 1, intervalo))
                    axes[i+1, 1].set_ylim(np.floor(df_HR_d_bd3[variable_HR_d].min()), np.ceil(df_HR_d_bd3[variable_HR_d].max()))
                    axes[i+1, 1].set_yticks(np.arange(np.floor(df_HR_d_bd3[variable_HR_d].min()), np.ceil(df_HR_d_bd3[variable_HR_d].max()), 2))
                    axes[i+1, 1].tick_params(axis='x', rotation=45)
                    axes[i+1, 1].grid(True, axis='y')

            # Ajusta la disposición general y muestra el gráfico
            plt.tight_layout()
            plt.subplots_adjust(top=0.95)
            # Agrega un título a la figura
            fig.suptitle(f'Diagramas de cajas de la serie total - Estación: {num_estacion}', fontsize=16)
            nombre_diag_caja_HR = 'DC_HR_Total_E1.png'
            plt.savefig(os.path.join(ruta_pruebas_b, 'DC_HR_Total_E1.png'))
            plt.close()
            print('-----------------------------------------------------------------------------------------------------------')
            print(f'Se ha generado exitosamente el diagrama de cajas de la serie total de la etapa 1 para la humedad relativa como: {nombre_diag_caja_HR}.')
            print('')
            return True
    else:
        print("No se encontraron archivos HR.h.bd3 y/o HR.d.bd3 en la ruta especificada.")
        return False
    
#-----------------------------------------------------------------------------------------------------------------

def Diagrama_caja_mensual_T(unidades):
    
    # Leer archivos .csv y realizar operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        df_HR_h_bd3 = None
        df_HR_d_bd3 = None

        if ruta_HR_h_bd3:
            df_HR_h_bd3 = pd.read_csv(ruta_HR_h_bd3, na_values=['NA'])
            df_HR_h_bd3['TIMESTAMP'] = pd.to_datetime(df_HR_h_bd3['TIMESTAMP']) 

        if ruta_HR_d_bd3:
            df_HR_d_bd3 = pd.read_csv(ruta_HR_d_bd3, na_values=['NA'])
            df_HR_d_bd3['TIMESTAMP'] = pd.to_datetime(df_HR_d_bd3['TIMESTAMP'])

    # Lista de nombres de los meses en español
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    # Iterar a través de cada mes
    for month in range(1, 13):
        # Nombre del mes en español
        nombre_mes_carpeta = f"{month:02d}.{meses[month - 1]}"
        nombre_mes = meses[month - 1]
        ruta_meses = os.path.join(ruta_pruebas_b, nombre_mes_carpeta)
        os.makedirs(ruta_meses, exist_ok=True)

        # Genera una figura con cuatro subtramas (4 filas, 2 columnas)
        fig, axes = plt.subplots(3, 1, figsize=(10, 20), dpi=300)

        # Diagramas de caja para HR.h si df_HR_h_bd3 no es None
        if df_HR_h_bd3 is not None:
            for i, variable_HR_h in enumerate(Variables_HR_h):
                data = df_HR_h_bd3[variable_HR_h][df_HR_h_bd3['TIMESTAMP'].dt.month == month]
                
                # Calcular estadísticas
                Media_aritmética_HR_h = data.mean()
                Desviación_estándar_HR_h = data.std()
                P25_HR_h = data.quantile(0.25)
                P50_HR_h = data.quantile(0.50)  # Median
                P75_HR_h = data.quantile(0.75)
                IQR_HR_h = P75_HR_h - P25_HR_h
                BI_HR_h = P25_HR_h - 1.5 * IQR_HR_h
                BS_HR_h = P75_HR_h + 1.5 * IQR_HR_h
                Min_HR_h = data.min()
                Max_HR_h = data.max()
                MinZ_HR_h = (Min_HR_h - Media_aritmética_HR_h) / Desviación_estándar_HR_h
                MaxZ_HR_h = (Max_HR_h - Media_aritmética_HR_h) / Desviación_estándar_HR_h
                lim_inf_HR_h = np.fix(MinZ_HR_h)*Desviación_estándar_HR_h + Media_aritmética_HR_h
                lim_sup_HR_h = np.fix(MaxZ_HR_h)*Desviación_estándar_HR_h + Media_aritmética_HR_h
                
                sns.boxplot(y=data, color="blue", linewidth=1.5,
                            boxprops=dict(facecolor='blue', edgecolor='black'),
                            flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'),
                            ax=axes[i])
                axes[i].set_title(f'{variable_HR_h} - {nombre_mes}')
                axes[i].set_xlabel('')
                axes[i].set_ylabel(f'Humedad relativa ({unidad})')
                # Set the y-axis limits
                axes[i].set_ylim(np.floor(data.min()), np.ceil(data.max()))
                # Automatically adjust the number of y-ticks based on the data range
                axes[i].yaxis.set_major_locator(ticker.MaxNLocator(15, integer=True))
                #axes[i].set_yticks(range(0, 100 + 1, 2))
                axes[i].tick_params(axis='y', rotation=00)
                axes[i].grid(True, axis='y')

                # Agregar información estadística en la esquina superior derecha de cada subplot
                axes[i].text(0.95, 0.95, f'Media aritmética = {Media_aritmética_HR_h:.2f}{unidad}\nDesviación estándar = {Desviación_estándar_HR_h:.2f}{unidad}\nLím.Vec.inferior = {lim_inf_HR_h:.2f}{unidad}\nBigote inferior = {BI_HR_h:.2f}{unidad}',
                                      transform=axes[i].transAxes,
                                      fontsize=8, verticalalignment='top', horizontalalignment='right', backgroundcolor='white')

        # Diagramas de caja para HR.d si df_HR_d_bd3 no es None
        if df_HR_d_bd3 is not None:
            for i, variable_HR_d in enumerate(Variables_HR_d):
                data = df_HR_d_bd3[variable_HR_d][df_HR_d_bd3['TIMESTAMP'].dt.month == month]
                
                # Calcular estadísticas
                Media_aritmética_HR_d = data.mean()
                Desviación_estándar_HR_d = data.std()
                P25_HR_d = data.quantile(0.25)
                P50_HR_d = data.quantile(0.50)  # Median
                P75_HR_d = data.quantile(0.75)
                IQR_HR_d = P75_HR_d - P25_HR_d
                BI_HR_d = P25_HR_d - 1.5 * IQR_HR_d
                BS_HR_d = P75_HR_d + 1.5 * IQR_HR_d
                Min_HR_d = data.min()
                Max_HR_d = data.max()
                MinZ_HR_d = (Min_HR_d - Media_aritmética_HR_d) / Desviación_estándar_HR_d
                MaxZ_HR_d = (Max_HR_d - Media_aritmética_HR_d) / Desviación_estándar_HR_d
                lim_inf_HR_d = np.fix(MinZ_HR_d)*Desviación_estándar_HR_d + Media_aritmética_HR_d
                lim_sup_HR_d = np.fix(MaxZ_HR_d)*Desviación_estándar_HR_d + Media_aritmética_HR_d
                
                sns.boxplot(y=data, color="blue", linewidth=1.5,
                            boxprops=dict(facecolor='blue', edgecolor='black'),
                            flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'),
                            ax=axes[i+1])
                axes[i+1].set_title(f'{variable_HR_d} - {nombre_mes}')
                axes[i+1].set_xlabel('')
                axes[i+1].set_ylabel(f'Humedad relativa ({unidad})')
                #axes[i+1].set_yticks(range(0, 100 + 1, 2))
                
                # Set the y-axis limits
                axes[i+1].set_ylim(np.floor(data.min()), np.ceil(data.max()))
                # Automatically adjust the number of y-ticks based on the data range
                axes[i+1].yaxis.set_major_locator(ticker.MaxNLocator(15, integer=True))
                
                axes[i+1].tick_params(axis='y', rotation=0)
                axes[i+1].grid(True, axis='y')

                if variable_HR_d == 'RH.perc.min.dm.s1':
                    axes[i+1].text(0.95, 0.95, f'Media aritmética = {Media_aritmética_HR_d:.2f}{unidad}\nDesviación estándar = {Desviación_estándar_HR_d:.2f}{unidad}\nLím.Vec.superior = {lim_sup_HR_d:.2f}{unidad}\nLím.Vec. inferior = {lim_inf_HR_d:.2f}{unidad}\nBigote superior = {BS_HR_d:.2f}{unidad}\nBigote inferior = {BI_HR_d:.2f}{unidad}',
                                                 transform=axes[i+1].transAxes,
                                                 fontsize=8, verticalalignment='top', horizontalalignment='right', backgroundcolor='white')
                    
                else:
                    axes[i+1].text(0.95, 0.95, f'Media aritmética = {Media_aritmética_HR_d:.2f}{unidad}\nDesviación estándar = {Desviación_estándar_HR_d:.2f}{unidad}\nLím.Vec. inferior = {lim_inf_HR_d:.2f}{unidad}\nBigote inferior = {BI_HR_d:.2f}{unidad}',
                                                 transform=axes[i+1].transAxes,
                                                 fontsize=8, verticalalignment='top', horizontalalignment='right', backgroundcolor='white')
    # Ajustar el diseño
        plt.tight_layout()

    # Guardar el gráfico
        plt.savefig(os.path.join(ruta_meses, f'{nombre_mes}_DC_E1.png'))
        plt.close()

    print('-----------------------------------------------------------------------------------------------------------')
    print('Se han generado exitosamente los diagramas de cajas mensuales de la etapa 1 para la humedad relativa.')
    print('')
    return True if (df_HR_h_bd3 is not None or df_HR_d_bd3 is not None) else False

#-----------------------------------------------------------------------------------------------------------------
#Llama funciones:

Diagrama_caja_total_HR(['%', '%'])

Diagrama_caja_mensual_T("")

def generar_archivo_txt_HR_h():
    # Si existe el archivo ruta_HR_h_bd3, procesar y crear el archivo de texto
    if ruta_HR_h_bd3:
        # Leer el archivo CSV y reemplazar los NA por -9
        df_HR_h_bd3 = pd.read_csv(ruta_HR_h_bd3)
        df_HR_h_bd3.fillna(-9, inplace=True)

        # Crear una copia del DataFrame con los nombres de columnas cambiados
        df_HR_h_bd3_copy = df_HR_h_bd3.rename(columns={
            'RH.perc.avg.1h.s1': 'RH_Avg'
        })

        # Crear el nombre del archivo de texto
        Fecha_inicial = pd.to_datetime(df_HR_h_bd3['TIMESTAMP']).min().strftime('%Y%m%d')
        Fecha_final = pd.to_datetime(df_HR_h_bd3['TIMESTAMP']).max().strftime('%Y%m%d')
        nombre_archivo_txt_HR_h = f"H-{num_estacion}-{Fecha_inicial}-{Fecha_final}.txt"

        # Guardar el archivo de texto con las celdas separadas por coma
        ruta_archivo_texto = os.path.join(ruta_analisis_HR, nombre_archivo_txt_HR_h)
        menos_nueve_entero(df_HR_h_bd3_copy, ruta_archivo_texto)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Se ha generado exitosamente el archivo de texto de la humedad relativa horaria como: {nombre_archivo_txt_HR_h}.")
        print('')
    else:
        print("Error: No se pudo generar el archivo de texto puesto que no se encontró el archivo de la humedad relativa horaria bd3")

# Llamada a la función
generar_archivo_txt_HR_h()

def generar_archivo_txt_HR_d():
    # Si existe el archivo ruta_HR_d_bd3, procesar y crear el archivo de texto
    if ruta_HR_d_bd3:
        # Leer el archivo CSV y reemplazar los NA por -9
        df_HR_d_bd3 = pd.read_csv(ruta_HR_d_bd3)
        df_HR_d_bd3.fillna(int(-9), inplace=True)
        
        # Crear una copia del DataFrame con los nombres de columnas cambiados
        df_HR_d_bd3_copy = df_HR_d_bd3.rename(columns={
            'RH.perc.max.dm.s1': 'RH_Max',
            'RH.CST.max.dm.s1': 'RH_TMx',
            'RH.perc.min.dm.s1': 'RH_Min',
            'RH.CST.min.dm.s1': 'RH_TMn'
        })

        # Crear el nombre del archivo de texto
        Fecha_inicial = pd.to_datetime(df_HR_d_bd3['TIMESTAMP']).min().strftime('%Y%m%d')
        Fecha_final = pd.to_datetime(df_HR_d_bd3['TIMESTAMP']).max().strftime('%Y%m%d')
        nombre_arcihvotxt_HR_d = f"D-{num_estacion}-{Fecha_inicial}-{Fecha_final}.txt"

        # Guardar el archivo de texto con las celdas separadas por coma
        ruta_archivo_texto = os.path.join(ruta_analisis_HR, nombre_arcihvotxt_HR_d)
        menos_nueve_entero(df_HR_d_bd3_copy, ruta_archivo_texto)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Se ha generado exitosamente el archivo de texto de la humedad relativa diaria como: {nombre_arcihvotxt_HR_d}.")
        print('')
    else:
        print("Error:No se pudo generar el archivo de texto puesto que no se encontró el archivo de la humedad relativa diarai bd3")
        
generar_archivo_txt_HR_d()

def fechas_especificas_faltantes_HR_d(ruta_HR_d_bd3):
    # Cargar el archivo CSV
    df = pd.read_csv(ruta_HR_d_bd3)

    # Reemplazar NA en Temp.CST.max.dm.s1 donde Temp.degC.max.dm.s1 es NA
    df.loc[df['RH.perc.max.dm.s1'].isna(), 'RH.CST.max.dm.s1'] = 'NA'
    df.loc[df['RH.CST.max.dm.s1'].isna(), 'RH.perc.max.dm.s1'] = 'NA'
    # Reemplazar NA en Temp.CST.max.dm.s1 donde Temp.degC.max.dm.s1 es NA
    df['RH.perc.max.dm.s1'].fillna('NA', inplace=True)
    df['RH.CST.max.dm.s1'].fillna('NA', inplace=True)

    # Reemplazar NA en Temp.CST.min.dm.s1 donde Temp.degC.min.dm.s1 es NA
    df.loc[df['RH.perc.min.dm.s1'].isna(), 'RH.CST.min.dm.s1'] = 'NA'
    df.loc[df['RH.CST.min.dm.s1'].isna(), 'RH.perc.min.dm.s1'] = 'NA'
    # Reemplazar NA en Temp.CST.min.dm.s1 donde Temp.degC.min.dm.s1 es NA
    df['RH.perc.min.dm.s1'].fillna('NA', inplace=True)
    df['RH.CST.min.dm.s1'].fillna('NA', inplace=True)

    # Guardar los cambios en el mismo archivo
    df.to_csv(ruta_HR_d_bd3, index=False)

fechas_especificas_faltantes_HR_d(ruta_HR_d_bd3)