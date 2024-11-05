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

# Crea las carpetas si no existen
for carpeta in ["", "Pruebas_estadisticas"]:
    ruta_pruebas_b = os.path.join(ruta_analisis_T, carpeta)
    os.makedirs(ruta_pruebas_b, exist_ok=True)
    
# Encuentra el archivo T.h.bd2.csv de la temperatura en la ruta de la estación
ruta_T_h_bd2 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.h.bd2' in archivo), None)

# Encuentra el archivo T.d.bd2.csv de la temperatura en la ruta de la estación
ruta_T_d_bd2 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.d.bd2' in archivo), None)

# Define the function to generate final bd3 files
def genera_archivos_final_bd3():
    # Check if h.bd3 file exists and replace it
    ruta_h_bd3 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if "h.bd3" in archivo), None)
    if ruta_h_bd3:
        os.remove(ruta_h_bd3)
        shutil.copy(ruta_T_h_bd2, os.path.join(ruta_analisis_T, os.path.basename(ruta_T_h_bd2).replace("bd2", "bd3")))
    else:
        # If bd3 file doesn't exist, create a copy of bd2 with bd3 extension
        shutil.copy(ruta_T_h_bd2, os.path.join(ruta_analisis_T, os.path.basename(ruta_T_h_bd2).replace("bd2", "bd3")))

    # Check if d.bd3 file exists and replace it
    ruta_d_bd3 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if "d.bd3" in archivo), None)
    if ruta_d_bd3:
        os.remove(ruta_d_bd3)
        shutil.copy(ruta_T_d_bd2, os.path.join(ruta_analisis_T, os.path.basename(ruta_T_d_bd2).replace("bd2", "bd3")))
    else:
        shutil.copy(ruta_T_d_bd2, os.path.join(ruta_analisis_T, os.path.basename(ruta_T_d_bd2).replace("bd2", "bd3")))

genera_archivos_final_bd3()

# Encuentra el archivo T.h.bd2.csv de la temperatura en la ruta de la estación
ruta_T_h_bd3 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.h.bd3' in archivo), None)

# Encuentra el archivo T.d.bd2.csv de la temperatura en la ruta de la estación
ruta_T_d_bd3 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.d.bd3' in archivo), None)

        
def edita_mod_T_h_db3():
    archivos_T_h = os.path.join(ruta_analisis_T, "Modif_Tec_T_h.csv")
    
    if os.path.exists(archivos_T_h):
        df_mod_T_h = pd.read_csv(archivos_T_h)
        
        if ruta_T_h_bd3 and os.path.exists(ruta_T_h_bd3):
            df_T_h_bd3 = pd.read_csv(ruta_T_h_bd3)  # Lee el archivo T.h.bd3.csv una vez fuera del bucle
            
            for index, row in df_mod_T_h.iterrows():
                Elemento = row['Elemento']
                Fecha = row['Fecha']
                valor_reemplazo = row['Valor_reemplazo']
                
                # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                if valor_reemplazo != 'NA':
                    # Realiza el reemplazo si coincide el Elemento y la Fecha
                    df_T_h_bd3.loc[(df_T_h_bd3['TIMESTAMP'] == Fecha), Elemento] = valor_reemplazo
            
            # Guarda el archivo T.h.bd3.csv después de realizar todos los reemplazos
            df_T_h_bd3.to_csv(ruta_T_h_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos
            
            if len(df_mod_T_h) >= 1:
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print("Se han incluido exitosamente los cambios generados en el archivo Modif_Tec_T_h en el archivo de la temperatura horaria bd3.")
                print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo Modif_Tec_h.csv.")
        print('')

def edita_mod_T_d_db3():
    archivos_T_d = os.path.join(ruta_analisis_T, "Modif_Tec_T_d.csv")
    
    if os.path.exists(archivos_T_d):
        if ruta_T_d_bd3 and os.path.exists(ruta_T_d_bd3):  # Verifica si el archivo T.d.bd3.csv existe
            df_mod_T_d = pd.read_csv(archivos_T_d)
            df_T_d_bd3 = pd.read_csv(ruta_T_d_bd3)  # Lee el archivo T.d.bd3.csv una vez fuera del bucle
            for index, row in df_mod_T_d.iterrows():
                Elemento = row['Elemento']
                Fecha = row['Fecha']
                valor_reemplazo = row['Valor_reemplazo']
                # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                if valor_reemplazo != 'NA':
                    # Realiza el reemplazo si coincide el Elemento y la Fecha
                    df_T_d_bd3.loc[(df_T_d_bd3['TIMESTAMP'] == Fecha), Elemento] = valor_reemplazo
            # Guarda el archivo T.d.bd3.csv después de realizar todos los reemplazos
            df_T_d_bd3.to_csv(ruta_T_d_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos
            if len(df_mod_T_d) >= 1:
                print('-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print("Se han incluido exitosamente los cambios generados en el archivo Modif_Tec_T_d en el archivo de la temperatura diaria bd3.")
                print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo Modif_Tec_d.csv.")
        print('')
        
def edita_T_h_db3():
    if ruta_T_h_bd3:
        for root, dirs, files in os.walk(ruta_pruebas_b):
            for file in files:
                if 'T_h' in file and file.endswith('.csv'):
                    archivos_T_h = os.path.join(root, file)
                    df_mes_T_h = pd.read_csv(archivos_T_h)
                    df_T_h_bd3 = pd.read_csv(ruta_T_h_bd3)  # Lee el archivo T.h.bd3.csv una vez fuera del bucle
                    for index, row in df_mes_T_h.iterrows():
                        Elemento = row['Elemento']
                        Fecha = row['Fecha']
                        valor_reemplazo = row['Valor_reemplazo']
                        # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                        if valor_reemplazo != 'NA':
                            # Realiza el reemplazo si coincide el Elemento y la Fecha
                            df_T_h_bd3.loc[(df_T_h_bd3['TIMESTAMP'] == Fecha), Elemento] = valor_reemplazo
                    # Guarda el archivo T.h.bd3.csv después de realizar todos los reemplazos
                    df_T_h_bd3.to_csv(ruta_T_h_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Se han incluido exitosamente los cambios generados en los archivos mensuales en el archivo de la temperatura horaria bd3.")
        print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la temperatura horaria bd3.")
        print('')

def edita_T_d_db3():
    if ruta_T_d_bd3:
        for root, dirs, files in os.walk(ruta_pruebas_b):
            for file in files:
                if 'T_d' in file and file.endswith('.csv'):
                    archivos_T_d = os.path.join(root, file)
                    df_mes_T_d = pd.read_csv(archivos_T_d)
                    df_T_d_bd3 = pd.read_csv(ruta_T_d_bd3)  # Lee el archivo T.d.bd3.csv una vez fuera del bucle
                    for index, row in df_mes_T_d.iterrows():
                        Elemento = row['Elemento']
                        Fecha = row['Fecha']
                        valor_reemplazo = row['Valor_reemplazo']
                        # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                        if valor_reemplazo != 'NA':
                            # Realiza el reemplazo si coincide el Elemento y la Fecha
                            df_T_d_bd3.loc[(df_T_d_bd3['TIMESTAMP'] == Fecha), Elemento] = valor_reemplazo
                    # Guarda el archivo T.d.bd3.csv después de realizar todos los reemplazos
                    df_T_d_bd3.to_csv(ruta_T_d_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Se han incluido exitosamente los cambios generados en los archivos mensuales en el archivo de la temperatura diaria bd3.")
        print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la temperatura diaria bd3.")
        print('')
        
        
edita_T_h_db3()
edita_T_d_db3()

edita_mod_T_h_db3()
edita_mod_T_d_db3()

#Aqui iba el removedor de filas iniciales y finales NA.

def convierte_variables_a_numericas_T_h():
    if ruta_T_h_bd3:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_T_h_bd3 = pd.read_csv(ruta_T_h_bd3, na_values=['NA'])
            
        # Convierte a valores numéricos y rellena NaN con 'NA' en las columnas especificadas
        rellena_caracteres_NA_T_h = ['Temp.degC.avg.1h.s1']
        for col in rellena_caracteres_NA_T_h:
            df_T_h_bd3[col] = pd.to_numeric(df_T_h_bd3[col], errors='coerce').fillna('NA')

        # Guarda el archivo CSV
        df_T_h_bd3.to_csv(ruta_T_h_bd3, index=False, na_rep='NA')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la temperatura horaria bd3")

convierte_variables_a_numericas_T_h()

def convierte_variables_a_numericas_T_d():
    if ruta_T_d_bd3:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_T_d_bd3 = pd.read_csv(ruta_T_d_bd3, na_values=['NA'])
            
        # Convierte a valores numéricos y rellena NaN con 'NA' en las columnas especificadas
        rellena_caracteres_NA_T_d = ['Temp.degC.max.dm.s1', 'Temp.degC.min.dm.s1']
        for col in rellena_caracteres_NA_T_d:
            df_T_d_bd3[col] = pd.to_numeric(df_T_d_bd3[col], errors='coerce').fillna('NA')

        # Guarda el archivo CSV
        df_T_d_bd3.to_csv(ruta_T_d_bd3, index=False, na_rep='NA')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la temperatura diaria bd3")

convierte_variables_a_numericas_T_d()

def renombra_T_h(ruta_T_h_bd3, num_estacion, ruta_analisis_T):
    if ruta_T_h_bd3:
        df_T_h_bd3 = pd.read_csv(ruta_T_h_bd3)
        df_T_h_bd3['TIMESTAMP'] = pd.to_datetime(df_T_h_bd3['TIMESTAMP'])
        tiempo_inicial_T_h = df_T_h_bd3['TIMESTAMP'].min()
        tiempo_final_T_h = df_T_h_bd3['TIMESTAMP'].max()
        nuevo_nombre_T_h_bd3 = f"{num_estacion}.{tiempo_inicial_T_h.strftime('%Y%m%d-%H')}.{tiempo_final_T_h.strftime('%Y%m%d-%H')}.T.h.bd3.csv"
        nueva_ruta_T_h_bd3 = os.path.join(ruta_analisis_T, nuevo_nombre_T_h_bd3)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Se ha generado exitosamente el archivo de la temperatura horaria bd3 como: {nuevo_nombre_T_h_bd3}")
        print('')
        # Mover y renombrar el archivo, sobrescribiendo si es necesario
        shutil.move(ruta_T_h_bd3, nueva_ruta_T_h_bd3)

def renombra_T_d(ruta_T_d_bd3, num_estacion, ruta_analisis_T):
    if ruta_T_d_bd3:
        df_T_d_bd3 = pd.read_csv(ruta_T_d_bd3)
        df_T_d_bd3['TIMESTAMP'] = pd.to_datetime(df_T_d_bd3['TIMESTAMP'])
        tiempo_inicial_T_d = df_T_d_bd3['TIMESTAMP'].min()
        tiempo_final_T_d = df_T_d_bd3['TIMESTAMP'].max()
        nuevo_nombre_T_d_bd3 = f"{num_estacion}.{tiempo_inicial_T_d.strftime('%Y%m%d-%H')}.{tiempo_final_T_d.strftime('%Y%m%d-%H')}.T.d.bd3.csv"
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Se ha generado exitosamente el archivo de la temperatura diaria bd3 como: {nuevo_nombre_T_d_bd3}")
        print('')
        nueva_ruta_T_d_bd3 = os.path.join(ruta_analisis_T, nuevo_nombre_T_d_bd3)
        
        # Mover y renombrar el archivo, sobrescribiendo si es necesario
        shutil.move(ruta_T_d_bd3, nueva_ruta_T_d_bd3)

# Ejemplo de llamada a las funciones (asegúrate de definir las rutas adecuadas antes de llamarlas)
renombra_T_h(ruta_T_h_bd3, num_estacion, ruta_analisis_T)
renombra_T_d(ruta_T_d_bd3, num_estacion, ruta_analisis_T)

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

# Encuentra el archivo T.h.bd2.csv de la temperatura en la ruta de la estación
ruta_T_h_bd3 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.h.bd3' in archivo), None)

# Encuentra el archivo T.d.bd2.csv de la temperatura en la ruta de la estación
ruta_T_d_bd3 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.d.bd3' in archivo), None)

#Genera graficas finales
# Variables para T.h
Variables_T_h = ['Temp.degC.avg.1h.s1']
# Variables para T.d
Variables_T_d = ['Temp.degC.max.dm.s1', 'Temp.degC.min.dm.s1']

unidad = '°C'

# Definir los nombres de los meses en español
nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

#-----------------------------------------------------------------------------------------------------------------
#Estadisticas chebyshev
if ruta_T_h_bd3 or ruta_T_d_bd3:
    # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if ruta_T_h_bd3:
            df_T_h_bd3 = pd.read_csv(ruta_T_h_bd3, na_values=['NA'])
            df_T_h_bd3['TIMESTAMP'] = pd.to_datetime(df_T_h_bd3['TIMESTAMP'])  # Convertir a tipo de dato de Fecha y hora

        if ruta_T_d_bd3:
            df_T_d_bd3 = pd.read_csv(ruta_T_d_bd3, na_values=['NA'])
            df_T_d_bd3['TIMESTAMP'] = pd.to_datetime(df_T_d_bd3['TIMESTAMP'])

#-----------------------------------------------------------------------------------------------------------------

def Estadisticos_T_h_d(ruta_pruebas_b, num_estacion):

    # Inicializar diccionarios para almacenar estadísticas de T_h y T_d
    estadisticos_T_h_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_h + Variables_T_d}
    
    # Iterar sobre cada mes
    for mes in range(1, 13):
        # Filtrar datos por mes para T_h y T_d
        df_mes_T_h = df_T_h_bd3[df_T_h_bd3['TIMESTAMP'].dt.month == mes]
        df_mes_T_d = df_T_d_bd3[df_T_d_bd3['TIMESTAMP'].dt.month == mes]

        # Iterar sobre cada variable en Variables_T_h y Variables_T_d
        for variable in Variables_T_h + Variables_T_d:
            # Seleccionar el dataframe correspondiente
            df_mes = df_mes_T_h if variable in Variables_T_h else df_mes_T_d

            # Calcular estadísticas si hay valores que no son NaN
            if not df_mes[variable].empty:
                # Calcular máximo, mínimo, media y desviación estándar
                max_val = df_mes[variable].max()
                min_val = df_mes[variable].min()
                mean_val = df_mes[variable].mean()
                std_val = df_mes[variable].std()

                # Almacenar estadísticas en el diccionario
                estadisticos_T_h_d[variable][nombres_meses[mes - 1]] = [max_val, min_val, mean_val, std_val]
            else:
                # Si el DataFrame está vacío, almacenar valores 'NA'
                estadisticos_T_h_d[variable][nombres_meses[mes - 1]] = ['NA'] * 4

    # Guardar estadísticas para T_h y T_d en un archivo de texto
    with open(os.path.join(ruta_pruebas_b, "Estadisticos_T_E1.txt"), "w") as file:
        for variable in Variables_T_h + Variables_T_d:
            file.write(f"\nEstación: {num_estacion} - Variable: {variable}\n")
            file.write("{:<12} {:<8} {:<8} {:<17} {:<17}\n".format("Mes", "Máximo", "Mínimo", "Media aritmética", "Desviación estándar"))
            for mes in range(1, 13):
                valores = estadisticos_T_h_d[variable][nombres_meses[mes - 1]]
                max_val, min_val, mean_val, std_val = valores

                # Escribir en el archivo manejando 'NA'
                if max_val == 'NA':
                    file.write("{:<12} {:<8} {:<8} {:<17} {:<17}\n".format(nombres_meses[mes - 1], 'NA', 'NA', 'NA', 'NA'))
                else:
                    file.write("{:<12} {:<8.2f} {:<8.2f} {:<17.2f} {:<17.2f}\n".format(nombres_meses[mes - 1], max_val, min_val, mean_val, std_val))

# Llamada a la función
Estadisticos_T_h_d(ruta_pruebas_b, num_estacion)

#-----------------------------------------------------------------------------------------------------------------

#Genera diagramas de caja totales y mensuales para cada variable.
def Diagrama_caja_total_T(unidades):

    if ruta_T_h_bd3 or ruta_T_d_bd3:
        # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            if ruta_T_h_bd3:
                df_T_h_bd3 = pd.read_csv(ruta_T_h_bd3, na_values=['NA'])
                df_T_h_bd3['TIMESTAMP'] = pd.to_datetime(df_T_h_bd3['TIMESTAMP'])  # Convertir a tipo de dato de Fecha y hora

            if ruta_T_d_bd3:
                df_T_d_bd3 = pd.read_csv(ruta_T_d_bd3, na_values=['NA'])
                df_T_d_bd3['TIMESTAMP'] = pd.to_datetime(df_T_d_bd3['TIMESTAMP'])
                
            # Genera una figura con 3 subtramas (3 filas, 2 columnas)
            fig, axes = plt.subplots(3, 2, figsize=(16, 25), dpi=300)

            # Boxplots para T.h
            if ruta_T_h_bd3:
                for i, variable_T_h in enumerate(Variables_T_h):
                    # Boxplot de la serie total (orientación vertical)
                    sns.boxplot(y=df_T_h_bd3[variable_T_h], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i, 0])
                    
                    axes[i, 0].set_title(f'{num_estacion} - {variable_T_h} - Total')
                    axes[i, 0].set_ylabel('Temperatura (°C)')
                    axes[i, 0].set_yticks(range(int(df_T_h_bd3[variable_T_h].min()), int(df_T_h_bd3[variable_T_h].max()) + 1, 2))
                    axes[i, 0].tick_params(axis='y', rotation=0)
                    axes[i, 0].grid(True, axis='y')

                    # Boxplots mensuales
                    sns.boxplot(x=df_T_h_bd3['TIMESTAMP'].dt.month, y=df_T_h_bd3[variable_T_h], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i, 1])
                    
                    axes[i, 1].set_title(f'{num_estacion} - {variable_T_h} - Mensual')
                    axes[i, 1].set_xlabel('Mes')
                    axes[i, 1].set_ylabel('Temperatura (°C)')
                    axes[i, 1].set_xticks(range(0, 13))  # 13 meses
                    axes[i, 1].set_yticks(range(int(df_T_h_bd3[variable_T_h].min()), int(df_T_h_bd3[variable_T_h].max()) + 1, 2))
                    axes[i, 1].tick_params(axis='x', rotation=45)
                    axes[i, 1].grid(True, axis='y')

            # Boxplots para T.d
            if ruta_T_d_bd3:
                for i, variable_T_d in enumerate(Variables_T_d):
                    # Boxplot de la serie total (orientación vertical)
                    sns.boxplot(y=df_T_d_bd3[variable_T_d], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i+1, 0])
                    
                    axes[i+1, 0].set_title(f'{num_estacion} - {variable_T_d}- Total')
                    axes[i+1, 0].set_ylabel('Temperatura (°C)')
                    axes[i+1, 0].set_yticks(range(int(df_T_d_bd3[variable_T_d].min()), int(df_T_d_bd3[variable_T_d].max()) + 1))
                    axes[i+1, 0].tick_params(axis='y', rotation=0)
                    axes[i+1, 0].grid(True, axis='y')

                    # Boxplots mensuales
                    sns.boxplot(x=df_T_d_bd3['TIMESTAMP'].dt.month, y=df_T_d_bd3[variable_T_d], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i+1, 1])
                    
                    axes[i+1, 1].set_title(f'{num_estacion} - {variable_T_d}- Mensual')
                    axes[i+1, 1].set_xlabel('Mes')
                    axes[i+1, 1].set_ylabel('Temperatura (°C)')
                    axes[i+1, 1].set_xticks(range(0, 13))  # 13 meses
                    axes[i+1, 1].set_yticks(range(int(df_T_d_bd3[variable_T_d].min()), int(df_T_d_bd3[variable_T_d].max()) + 1))
                    axes[i+1, 1].tick_params(axis='x', rotation=45)
                    axes[i+1, 1].grid(True, axis='y')

            # Ajusta la disposición general y muestra el gráfico
            plt.tight_layout()
            plt.subplots_adjust(top=0.95)
            # Agrega un título a la figura
            fig.suptitle(f'Diagramas de cajas - Estación: {num_estacion}', fontsize=16)
            nombre_diag_caja_T = 'DC_T_Total_E1.png'
            plt.savefig(os.path.join(ruta_pruebas_b, 'DC_T_Total_E1.png'))
            plt.close()
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f'Se ha generado exitosamente el diagrama de cajas de la serie total de la etapa 1 para la temperatura como: {nombre_diag_caja_T}.')
            print('')
            return True
    else:
        print("No se encontraron archivos T.h.bd3 y/o T.d.bd3 en la ruta especificada.")
        return False
    

Diagrama_caja_total_T(['°C'])


def plot_time_series(df_T_h_bd3, df_T_d_bd3, var1, var2, var3, title=f"Serie de tiempo - Estación: {num_estacion}", xlabel="Tiempo", ylabel="Temperatura (°C)"):
    plt.figure(figsize=(60, 8), dpi=300)  # Adjusted figure size and DPI as per your requirement

    # Resample data to monthly frequency and calculate max and min
    df_T_h_bd3_monthly_max = df_T_h_bd3.resample('M', on='TIMESTAMP')[var1].max()
    df_T_h_bd3_monthly_min = df_T_h_bd3.resample('M', on='TIMESTAMP')[var1].min()
    df_T_d_bd3_monthly_max = df_T_d_bd3.resample('M', on='TIMESTAMP')[var2].max()
    df_T_d_bd3_monthly_min = df_T_d_bd3.resample('M', on='TIMESTAMP')[var3].min()

# Align the indices to ensure all arrays have the same length
    combined_index = df_T_h_bd3_monthly_max.index.union(df_T_h_bd3_monthly_min.index).union(df_T_d_bd3_monthly_max.index).union(df_T_d_bd3_monthly_min.index)
    df_T_h_bd3_monthly_max = df_T_h_bd3_monthly_max.reindex(combined_index)
    df_T_h_bd3_monthly_min = df_T_h_bd3_monthly_min.reindex(combined_index)
    df_T_d_bd3_monthly_max = df_T_d_bd3_monthly_max.reindex(combined_index)
    df_T_d_bd3_monthly_min = df_T_d_bd3_monthly_min.reindex(combined_index)
    
    # Create a combined dataframe for seaborn
    combined_df = pd.DataFrame({
        'Date': df_T_h_bd3_monthly_max.index,
        f'Max {var1}': df_T_h_bd3_monthly_max.values,
        f'Min {var1}': df_T_h_bd3_monthly_min.values,
        f'Max {var2}': df_T_d_bd3_monthly_max.values,
        f'Min {var3}': df_T_d_bd3_monthly_min.values
    }).melt('Date', var_name='Variable', value_name='Value')
    
    # Plot using seaborn
    sns.lineplot(data=combined_df, x='Date', y='Value', hue='Variable', palette=['orange', 'green', 'red', 'blue'], markers=True)
    
    # Add markers to the maximum and minimum points
    sns.scatterplot(data=combined_df, x='Date', y='Value', hue='Variable', palette=['orange', 'green', 'red', 'blue'], s=30, legend=False)
    
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
    
    # Remove the first y-axis tick
    ax = plt.gca()
    y_ticks = ax.get_yticks()
    if len(y_ticks) > 0:
        ax.set_yticks(y_ticks[1:-1])  # Remove the first tick by slicing the list

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
        for y_value in range(int(y_limits[0])+1, int(y_limits[1])+1):
            plt.text(year_date, y_value, f'{y_value}', ha='center', va='bottom', color='gray', fontsize=10)

    plt.tight_layout()
    
    # Save the plot (assuming ruta_guardado is defined in your environment)
    plt.savefig(os.path.join(ruta_pruebas_b, 'ST_Extremos_T_E1.png'))
    
    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print('Se ha generado exitosamente la serie de tiempo de los extremos mensuales de la serie total para la temperatura de la etapa 1 como: ST_Extremos_T_E1.png.')
    print('')

# Example call to the function (adjust variables and dataframes as per your dataset)
plot_time_series(df_T_h_bd3, df_T_d_bd3, 'Temp.degC.avg.1h.s1', 'Temp.degC.max.dm.s1', 'Temp.degC.min.dm.s1')

#-----------------------------------------------------------------------------------------------------------------

def Diagrama_caja_mensual_T(unidades):
    
    # Leer archivos .csv y realizar operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        df_T_h_bd3 = None
        df_T_d_bd3 = None

        if ruta_T_h_bd3:
            df_T_h_bd3 = pd.read_csv(ruta_T_h_bd3, na_values=['NA'])
            df_T_h_bd3['TIMESTAMP'] = pd.to_datetime(df_T_h_bd3['TIMESTAMP']) 

        if ruta_T_d_bd3:
            df_T_d_bd3 = pd.read_csv(ruta_T_d_bd3, na_values=['NA'])
            df_T_d_bd3['TIMESTAMP'] = pd.to_datetime(df_T_d_bd3['TIMESTAMP'])

    # Lista de nombres de los meses en español
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    # Iterar a través de cada mes
    for month in range(1, 13):
        # Nombre del mes en español
        nombre_mes_carpeta = f"{month:02d}.{meses[month - 1]}"
        nombre_mes = meses[month - 1]
        ruta_meses = os.path.join(ruta_pruebas_b, nombre_mes_carpeta)
        os.makedirs(ruta_meses, exist_ok=True)

        # Genera una figura con 3 subtramas (3 filas, 1 columna)
        fig, axes = plt.subplots(3, 1, figsize=(10, 20), dpi=300)

        # Diagramas de caja para T.h si df_T_h_bd3 no es None
        if df_T_h_bd3 is not None:
            for i, variable_T_h in enumerate(Variables_T_h):
                data = df_T_h_bd3[variable_T_h][df_T_h_bd3['TIMESTAMP'].dt.month == month]
                
                if not data.empty:
                    # Calcular estadísticas
                    Media_aritmética_T_h = data.mean()
                    Desviación_estándar_T_h = data.std()
                    P25_T_h = data.quantile(0.25)
                    P50_T_h = data.quantile(0.50)  # Median
                    P75_T_h = data.quantile(0.75)
                    IQR_T_h = P75_T_h - P25_T_h
                    BI_T_h = P25_T_h - 1.5 * IQR_T_h
                    BS_T_h = P75_T_h + 1.5 * IQR_T_h
                    Min_T_h = data.min()
                    Max_T_h = data.max()
                    MinZ_T_h = (Min_T_h - Media_aritmética_T_h) / Desviación_estándar_T_h
                    MaxZ_T_h = (Max_T_h - Media_aritmética_T_h) / Desviación_estándar_T_h
                    lim_inf_T_h = np.fix(MinZ_T_h) * Desviación_estándar_T_h + Media_aritmética_T_h
                    lim_sup_T_h = np.fix(MaxZ_T_h) * Desviación_estándar_T_h + Media_aritmética_T_h
                    
                    # Verificar si los valores mínimos y máximos no son NaN
                    min_data = int(data.min()) if not pd.isna(data.min()) else 0
                    max_data = int(data.max()) if not pd.isna(data.max()) else 1

                    sns.boxplot(y=data, color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'),
                                ax=axes[i])
                    axes[i].set_title(f'{num_estacion} - {variable_T_h} - {nombre_mes}')
                    axes[i].set_xlabel('')
                    axes[i].set_ylabel('Temperatura (°C)')
                    axes[i].set_yticks(range(min_data, max_data + 1, 2))
                    axes[i].tick_params(axis='y', rotation=0)
                    axes[i].grid(True, axis='y')
                    
                    # Agregar información estadística en la esquina superior derecha de cada subplot
                    axes[i].text(0.95, 0.95, f'Media aritmética = {Media_aritmética_T_h:.2f}{unidad}\nDesviación estándar = {Desviación_estándar_T_h:.2f}{unidad}\nLím.Vec. superior = {lim_sup_T_h:.2f}{unidad}\nLím.Vec.inferior = {lim_inf_T_h:.2f}{unidad}\nBigote superior = {BS_T_h:.2f}{unidad}\nBigote inferior = {BI_T_h:.2f}{unidad}',
                                  transform=axes[i].transAxes,
                                  fontsize=8, verticalalignment='top', horizontalalignment='right', backgroundcolor='white')

        # Diagramas de caja para T.d si df_T_d_bd3 no es None
        if df_T_d_bd3 is not None:
            for i, variable_T_d in enumerate(Variables_T_d):
                data = df_T_d_bd3[variable_T_d][df_T_d_bd3['TIMESTAMP'].dt.month == month]
                
                if not data.empty:
                    # Calcular estadísticas
                    Media_aritmética_T_d = data.mean()
                    Desviación_estándar_T_d = data.std()
                    P25_T_d = data.quantile(0.25)
                    P50_T_d = data.quantile(0.50)  # Median
                    P75_T_d = data.quantile(0.75)
                    IQR_T_d = P75_T_d - P25_T_d
                    BI_T_d = P25_T_d - 1.5 * IQR_T_d
                    BS_T_d = P75_T_d + 1.5 * IQR_T_d
                    Min_T_d = data.min()
                    Max_T_d = data.max()
                    MinZ_T_d = (Min_T_d - Media_aritmética_T_d) / Desviación_estándar_T_d
                    MaxZ_T_d = (Max_T_d - Media_aritmética_T_d) / Desviación_estándar_T_d
                    lim_inf_T_d = np.fix(MinZ_T_d) * Desviación_estándar_T_d + Media_aritmética_T_d
                    lim_sup_T_d = np.fix(MaxZ_T_d) * Desviación_estándar_T_d + Media_aritmética_T_d
                    
                    # Verificar si los valores mínimos y máximos no son NaN
                    min_data = int(data.min()) if not pd.isna(data.min()) else 0
                    max_data = int(data.max()) if not pd.isna(data.max()) else 1

                    sns.boxplot(y=data, color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'),
                                ax=axes[i+1])
                    axes[i+1].set_title(f'{num_estacion} - {variable_T_d} - {nombre_mes}')
                    axes[i+1].set_xlabel('')
                    axes[i+1].set_ylabel('Temperatura (°C)')
                    axes[i+1].set_yticks(range(min_data, max_data + 1))
                    axes[i+1].tick_params(axis='y', rotation=0)
                    axes[i+1].grid(True, axis='y')

                    # Agregar información estadística en la esquina superior derecha de cada subplot
                    axes[i+1].text(0.95, 0.95, f'Media aritmética = {Media_aritmética_T_d:.2f}{unidad}\nDesviación estándar = {Desviación_estándar_T_d:.2f}{unidad}\nLím.Vec.superior = {lim_sup_T_d:.2f}{unidad}\nLím.Vec. inferior = {lim_inf_T_d:.2f}{unidad}\nBigote superior = {BS_T_d:.2f}{unidad}\nBigote inferior = {BI_T_d:.2f}{unidad}',
                                     transform=axes[i+1].transAxes,
                                     fontsize=8, verticalalignment='top', horizontalalignment='right', backgroundcolor='white')

        # Ajustar el diseño
        plt.tight_layout()

        # Guardar el gráfico
        plt.savefig(os.path.join(ruta_meses, f'DC_T_{nombre_mes}_E1.png'))
        plt.close()

    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print('Se han generado exitosamente los diagramas de cajas mensuales de la etapa 1 para la temperatura.')
    print('')
    return True if (df_T_h_bd3 is not None or df_T_d_bd3 is not None) else False

#-----------------------------------------------------------------------------------------------------------------

Diagrama_caja_mensual_T("")

def fechas_especificas_faltantes_T_d(ruta_T_d_bd3):
    # Cargar el archivo CSV
    df = pd.read_csv(ruta_T_d_bd3)

    # Reemplazar NA en Temp.CST.max.dm.s1 donde Temp.degC.max.dm.s1 es NA
    df.loc[df['Temp.degC.max.dm.s1'].isna(), 'Temp.CST.max.dm.s1'] = 'NA'
    #df.loc[df['Temp.CST.max.dm.s1'].isna(), 'Temp.degC.max.dm.s1'] = 'NA'
    # Reemplazar NA en Temp.CST.max.dm.s1 donde Temp.degC.max.dm.s1 es NA
    df['Temp.degC.max.dm.s1'].fillna('NA', inplace=True)
    df['Temp.CST.max.dm.s1'].fillna('NA', inplace=True)

    # Reemplazar NA en Temp.CST.max.dm.s1 donde Temp.degC.max.dm.s1 es NA
    df.loc[df['Temp.degC.min.dm.s1'].isna(), 'Temp.CST.min.dm.s1'] = 'NA'
    #df.loc[df['Temp.CST.min.dm.s1'].isna(), 'Temp.degC.min.dm.s1'] = 'NA'
    # Reemplazar NA en Temp.CST.max.dm.s1 donde Temp.degC.max.dm.s1 es NA
    df['Temp.degC.min.dm.s1'].fillna('NA', inplace=True)
    df['Temp.CST.min.dm.s1'].fillna('NA', inplace=True)

    # Guardar los cambios en el mismo archivo
    df.to_csv(ruta_T_d_bd3, index=False)

fechas_especificas_faltantes_T_d(ruta_T_d_bd3)

def generar_archivo_txt_T_h():
    # Si existe el archivo ruta_T_h_bd3, procesar y crear el archivo de texto
    if ruta_T_h_bd3:
        # Leer el archivo CSV y reemplazar los NA por -9
        df_T_h_bd3 = pd.read_csv(ruta_T_h_bd3)
        df_T_h_bd3.fillna(-9, inplace=True)

        # Crear una copia del DataFrame con los nombres de columnas cambiados
        df_T_h_bd3_copy = df_T_h_bd3.rename(columns={
            'Temp.degC.avg.1h.s1': 'TEMP_C_Avg'})
        
        # Eliminar la columna 'Td'
        df_T_h_bd3_copy.drop(columns=['Td.degC.avg.1h.c1'], inplace=True)

        # Crear el nombre del archivo de texto
        Fecha_inicial = pd.to_datetime(df_T_h_bd3['TIMESTAMP']).min().strftime('%Y%m%d')
        Fecha_final = pd.to_datetime(df_T_h_bd3['TIMESTAMP']).max().strftime('%Y%m%d')
        nombre_archivo_txt_T_h = f"H-{num_estacion}-{Fecha_inicial}-{Fecha_final}.txt"

        # Guardar el archivo de texto con las celdas separadas por coma
        ruta_archivo_texto = os.path.join(ruta_analisis_T, nombre_archivo_txt_T_h)
        for file_name in os.listdir(ruta_analisis_T):
            if file_name.startswith('H-'):
                os.remove(os.path.join(ruta_analisis_T, file_name))
        
        menos_nueve_entero(df_T_h_bd3_copy, ruta_archivo_texto)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Se ha generado exitosamente el archivo de texto de la temperatura horaria como: {nombre_archivo_txt_T_h}.")
        print('')
    else:
        print("Error: No se pudo generar el archivo de texto puesto que no se encontró el archivo de la temperatura horaria bd3")

# Llamada a la función
generar_archivo_txt_T_h()

def generar_archivo_txt_T_d():
    # Si existe el archivo ruta_T_d_bd3, procesar y crear el archivo de texto
    if ruta_T_d_bd3:
        # Leer el archivo CSV y reemplazar los NA por -9
        df_T_d_bd3 = pd.read_csv(ruta_T_d_bd3)
        df_T_d_bd3.fillna(int(-9), inplace=True)
        
        # Reemplazar "NA" por "NULL" en las columnas específicas
        df_T_d_bd3['Temp.CST.max.dm.s1'] = df_T_d_bd3['Temp.CST.max.dm.s1'].replace(int(-9), "NULL")
        df_T_d_bd3['Temp.CST.min.dm.s1'] = df_T_d_bd3['Temp.CST.min.dm.s1'].replace(int(-9), "NULL")

        
        # Crear una copia del DataFrame con los nombres de columnas cambiados
        df_T_d_bd3_copy = df_T_d_bd3.rename(columns={
            'Temp.degC.max.dm.s1': 'TEMP_C_Max',
            'Temp.CST.max.dm.s1': 'TEMP_C_TMx',
            'Temp.degC.min.dm.s1': 'TEMP_C_Min',
            'Temp.CST.min.dm.s1': 'TEMP_C_TMn'
        })

        # Crear el nombre del archivo de texto
        Fecha_inicial = pd.to_datetime(df_T_d_bd3['TIMESTAMP']).min().strftime('%Y%m%d')
        Fecha_final = pd.to_datetime(df_T_d_bd3['TIMESTAMP']).max().strftime('%Y%m%d')
        nombre_arcihvotxt_T_d = f"D-{num_estacion}-{Fecha_inicial}-{Fecha_final}.txt"

        # Guardar el archivo de texto con las celdas separadas por coma
        ruta_archivo_texto = os.path.join(ruta_analisis_T, nombre_arcihvotxt_T_d)
        # Verificar si existe un archivo que comience con "D-" y eliminarlo
        for file_name in os.listdir(ruta_analisis_T):
            if file_name.startswith('D-'):
                os.remove(os.path.join(ruta_analisis_T, file_name))
        
        menos_nueve_entero(df_T_d_bd3_copy, ruta_archivo_texto)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Se ha generado exitosamente el archivo de texto de la temperatura diaria como: {nombre_arcihvotxt_T_d}.")
        print('')
    else:
        print("Error:No se pudo generar el archivo de texto puesto que no se encontró el archivo de la temperatura diaria bd3")
        
generar_archivo_txt_T_d()
