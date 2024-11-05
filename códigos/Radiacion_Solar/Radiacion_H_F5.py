import pandas as pd
import os
import warnings
import shutil
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
from matplotlib.ticker import MaxNLocator
import matplotlib.dates as mdates

# Eliminar UserWarnings de openpyxl
warnings.simplefilter('ignore', category=UserWarning)

datos_crudos = r'C:\\MeteoRBD.v1.0.0\\datos_rbd'

# Encuentra el archivo .xlsx en los datos_crudos que contiene 'Cuenca' y 'Estación' como columnas
ruta_archivo = next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Radiación" in file and file.endswith(".xlsx")), None)

if ruta_archivo:
    archivo_excel = pd.read_excel(ruta_archivo)
    if all(col in archivo_excel.columns for col in ['Cuenca', 'Estación']):
        # Obtiene el número de estación a Rrtir del archivo Excel
        cuenca = str(archivo_excel['Cuenca'].iloc[0])
        estacion = str(archivo_excel['Estación'].iloc[0])

        # Asegúrate de que la cuenca tenga tres dígitos
        cuenca = cuenca.zfill(3)

        # Asegúrate de que la estación tenga tres dígitos
        estacion = estacion.zfill(3)

        # Concatenar cuenca y estación
        num_estacion = cuenca + estacion

# Establece la ruta para los archivos de la radiación solar horaria según el número de estación obtenido del archivo Excel
ruta_analisis_R = f"C:\\MeteoRBD.v1.0.0\\revisión\\{num_estacion}-ema\\Radiación Solar"

# Crea las carpetas si no existen
for carpeta in ["", "Pruebas_estadisticas"]:
    ruta_pruebas_b = os.path.join(ruta_analisis_R, carpeta)
    os.makedirs(ruta_pruebas_b, exist_ok=True)
    
# Encuentra el archivo R.h.bd2.csv de la radiación solar horaria en la ruta de la estación
ruta_R_h_bd2 = next((os.path.join(ruta_analisis_R, archivo) for archivo in os.listdir(ruta_analisis_R) if archivo.endswith(".csv") and 'R.h.bd2' in archivo), None)

# Define the function to generate final bd3 files
def genera_archivos_final_bd3():
    ruta_h_bd3 = next((os.path.join(ruta_analisis_R, archivo) for archivo in os.listdir(ruta_analisis_R) if "h.bd3" in archivo), None)
    if ruta_h_bd3:
        os.remove(ruta_h_bd3)
        shutil.copy(ruta_R_h_bd2, os.path.join(ruta_analisis_R, os.path.basename(ruta_R_h_bd2).replace("bd2", "bd3")))
    else:
        # If bd3 file doesn't exist, create a copy of bd2 with bd3 extension
        shutil.copy(ruta_R_h_bd2, os.path.join(ruta_analisis_R, os.path.basename(ruta_R_h_bd2).replace("bd2", "bd3")))

genera_archivos_final_bd3()

# Encuentra el archivo R.h.bd2.csv de la presión atmosférica en la ruta de la estación
ruta_R_h_bd3 = next((os.path.join(ruta_analisis_R, archivo) for archivo in os.listdir(ruta_analisis_R) if archivo.endswith(".csv") and 'R.h.bd3' in archivo), None)
        
def edita_mod_R_h_db3():
    archivos_R_h = os.path.join(ruta_analisis_R, "Modif_Tec_R_h.csv")
    
    if os.path.exists(archivos_R_h):
        df_mod_R_h = pd.read_csv(archivos_R_h)
        
        if ruta_R_h_bd3 and os.path.exists(ruta_R_h_bd3):
            df_R_h_bd3 = pd.read_csv(ruta_R_h_bd3)  # Lee el archivo R.h.bd3.csv una vez fuera del bucle
            
            for index, row in df_mod_R_h.iterrows():
                elemento = row['ELEMENTO']
                fecha = row['FECHA']
                valor_reemplazo = row['Valor_reemplazo']
                
                # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                if valor_reemplazo != 'NA':
                    # Realiza el reemplazo si coincide el elemento y la fecha
                    df_R_h_bd3.loc[(df_R_h_bd3['TIMESTAMP'] == fecha), elemento] = valor_reemplazo
            
            # Guarda el archivo R.h.bd3.csv después de realizar todos los reemplazos
            df_R_h_bd3.to_csv(ruta_R_h_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos
            
            if len(df_mod_R_h) >= 1:
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print("Se han incluido exitosamente los cambios generados en el archivo Modif_Tec_R_h en el archivo de la radiación solar horaria horaria bd3.")
                print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo Modif_Tec_h.csv.")
        print('')
        
def edita_R_h_db3():
    if ruta_R_h_bd3:
        for root, dirs, files in os.walk(ruta_pruebas_b):
            for file in files:
                if 'R_h' in file and file.endswith('.csv'):
                    archivos_R_h = os.path.join(root, file)
                    df_mes_R_h = pd.read_csv(archivos_R_h)
                    df_R_h_bd3 = pd.read_csv(ruta_R_h_bd3)  # Lee el archivo R.h.bd3.csv una vez fuera del bucle
                    for index, row in df_mes_R_h.iterrows():
                        elemento = row['ELEMENTO']
                        fecha = row['FECHA']
                        valor_reemplazo = row['Valor_reemplazo']
                        # Verifica si el valor de Valor_reemplazo es NA, en cuyo caso no se realiza ningún reemplazo
                        if valor_reemplazo != 'NA':
                            # Realiza el reemplazo si coincide el elemento y la fecha
                            df_R_h_bd3.loc[(df_R_h_bd3['TIMESTAMP'] == fecha), elemento] = valor_reemplazo
                    # Guarda el archivo R.h.bd3.csv después de realizar todos los reemplazos
                    df_R_h_bd3.to_csv(ruta_R_h_bd3, index=False, na_rep='NA')  # Utiliza na_rep='NA' para mantener los valores NA intactos
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Se han incluido exitosamente los cambios generados en los archivos mensuales en el archivo de la radiación solar horaria horaria bd3.")
        print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la radiación solar horaria horaria bd3.")
        print('')

edita_R_h_db3()

edita_mod_R_h_db3()


def elimina_fila_anumerica_R_h():
    if ruta_R_h_bd3:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Lee el archivo CSV
            df_R_h_bd3 = pd.read_csv(ruta_R_h_bd3, na_values=['NA'])
            
        # Rellena las celdas en blanco con 'NA' en todo el DataFrame
        #df_R_h_bd3.fillna('NA', inplace=True)

        # Filtra las filas sin valores numéricos al principio y al final en ciertas columnas
        indices_numericos_R_h = df_R_h_bd3[df_R_h_bd3[['Rad.MJ_m2.tot.1h.s1', 'Rad.kW_m2.max.1h.s1', 'Rad.kW_m2.min.1h.s1', 'Rad-int_sol.min_hour.tot.1h.s1']].apply(pd.to_numeric, errors='coerce').notnull().any(axis=1)].index
        
        if not indices_numericos_R_h.empty:
            primer_indice_numerico_R_h = indices_numericos_R_h[0]
            ultimo_indice_numerico_R_h = indices_numericos_R_h[-1]

            # Conserva las filas con valores numéricos
            df_R_h_bd3 = df_R_h_bd3.iloc[primer_indice_numerico_R_h:ultimo_indice_numerico_R_h + 1]

            # Rellena valores no numéricos con 'NA' en ciertas columnas y agrega el número de estación en la columna ESTACION
            rellena_caracteres_NA_R_h = ['Rad.MJ_m2.tot.1h.s1', 'Rad.kW_m2.max.1h.s1', 'Rad.kW_m2.min.1h.s1', 'Rad-int_sol.min_hour.tot.1h.s1']
            for col in rellena_caracteres_NA_R_h:
                df_R_h_bd3[col] = pd.to_numeric(df_R_h_bd3[col], errors='coerce').fillna('NA')

            # Guarda el archivo CSV
            df_R_h_bd3.to_csv(ruta_R_h_bd3, index=False, na_rep='NA')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se encontró el archivo de la radiación solar horaria horaria bd3")

elimina_fila_anumerica_R_h()


def renombra_R_h(ruta_R_h_bd3, num_estacion, ruta_analisis_R):
    if ruta_R_h_bd3:
        df_R_h_bd3 = pd.read_csv(ruta_R_h_bd3)
        df_R_h_bd3['TIMESTAMP'] = pd.to_datetime(df_R_h_bd3['TIMESTAMP'])
        tiempo_inicial_R_h = df_R_h_bd3['TIMESTAMP'].min()
        tiempo_final_R_h = df_R_h_bd3['TIMESTAMP'].max()
        nuevo_nombre_R_h_bd3 = f"{num_estacion}.{tiempo_inicial_R_h.strftime('%Y%m%d-%H')}.{tiempo_final_R_h.strftime('%Y%m%d-%H')}.R.h.bd3.csv"
        nueva_ruta_R_h_bd3 = os.path.join(ruta_analisis_R, nuevo_nombre_R_h_bd3)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Se ha generado exitosamente el archivo de la radiación solar horaria bd3 como: {nuevo_nombre_R_h_bd3}")
        print('')
        # Mover y renombrar el archivo, sobrescribiendo si es necesario
        shutil.move(ruta_R_h_bd3, nueva_ruta_R_h_bd3)

renombra_R_h(ruta_R_h_bd3, num_estacion, ruta_analisis_R)

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

# Encuentra el archivo R.h.bd2.csv de la radiación solar horaria en la ruta de la estación
ruta_R_h_bd3 = next((os.path.join(ruta_analisis_R, archivo) for archivo in os.listdir(ruta_analisis_R) if archivo.endswith(".csv") and 'R.h.bd3' in archivo), None)

unidades = ['$MJ/m^2$', 'kW/m$^2$', 'kW/m$^2$']

# Variables para T.h
Variables_R_h = ['Rad.MJ_m2.tot.1h.s1', 'Rad.kW_m2.max.1h.s1', 'Rad.kW_m2.min.1h.s1']

Variable_nombre = ['Radiación solar total','Radiación solar máxima','Radiación solar mínima']

#-----------------------------------------------------------------------------------------------------------------

if ruta_R_h_bd3:
    # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if ruta_R_h_bd3:
            df_R_h_bd3 = pd.read_csv(ruta_R_h_bd3, na_values=['NA'])
            df_R_h_bd3['TIMESTAMP'] = pd.to_datetime(df_R_h_bd3['TIMESTAMP'])  # Convertir a tipo de dato de fecha y hora

# Definir los nombres de los meses en español
nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

def Estadisticos_R_h_d(ruta_pruebas_b, num_estacion):

    # Inicializar diccionarios para almacenar estadísticas de R_h y R_d
    estadisticos_R_h_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_R_h}

    # Iterar sobre cada mes en los datos de R_h y R_d
    for mes in range(1, 13):
        # Filtrar datos por mes para R_h y R_d
        df_mes_R_h = df_R_h_bd3[df_R_h_bd3['TIMESTAMP'].dt.month == mes]

        # Iterar sobre cada variable en Variables_R_h y Variables_R_d
        for variable in Variables_R_h:
            # Seleccionar el dataframe correspondiente
            df_mes = df_mes_R_h 

            # Calcular estadísticas si hay valores que no son NaN
            if not df_mes[variable].empty:
                # Calcular máximo, mínimo, media y desviación estándar
                max_val = df_mes[variable].max()
                min_val = df_mes[variable].min()
                mean_val = df_mes[variable].mean()
                std_val = df_mes[variable].std()

                # Almacenar estadísticas en el diccionario
                estadisticos_R_h_d[variable][nombres_meses[mes - 1]] = [max_val, min_val, mean_val, std_val]

    # Guardar estadísticas para R_h y R_d en un archivo de texto
    with open(os.path.join(ruta_pruebas_b, "Estadisticos_R_E1.txt"), "w") as file:
        for variable in Variables_R_h:
            file.write(f"\nEstación: {num_estacion} - Variable: {variable}\n")
            file.write("{:<12} {:<8} {:<8} {:<17} {:<17}\n".format("Mes", "Máximo", "Mínimo", "Media aritmética", "Desviación estándar"))
            for mes in range(1, 13):
                max_val, min_val, mean_val, std_val = estadisticos_R_h_d[variable][nombres_meses[mes - 1]]
                file.write("{:<12} {:<8.2f} {:<8.2f} {:<17.2f} {:<17.2f}\n".format(nombres_meses[mes - 1], max_val, min_val, mean_val, std_val))

# Ramada a la función
Estadisticos_R_h_d(ruta_pruebas_b, num_estacion)

#Genera diagramas de caja totales y mensuales para cada variable.
def Diagrama_caja_total_R(unidades):

    if ruta_R_h_bd3:
        # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            if ruta_R_h_bd3:
                df_R_h_bd3 = pd.read_csv(ruta_R_h_bd3, na_values=['NA'])
                df_R_h_bd3['TIMESTAMP'] = pd.to_datetime(df_R_h_bd3['TIMESTAMP'])  # Convertir a tipo de dato de fecha y hora

            # Genera una figura con cuatro subtramas (4 filas, 2 columnas)
            fig, axes = plt.subplots(3, 2, figsize=(16, 25), dpi=300)

            # Boxplots para T.h
            if ruta_R_h_bd3:
                for i, variable_R_h in enumerate(Variables_R_h):
                    unidad = unidades[i]
                    # Boxplot de la serie total (orientación vertical)
                    sns.boxplot(y=df_R_h_bd3[variable_R_h], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i, 0])
                    
                    axes[i, 0].set_title(f'{num_estacion} - {variable_R_h}- Total')
                    axes[i, 0].set_ylabel(unidad)
                    axes[i, 0].set_ylim(np.floor(df_R_h_bd3[variable_R_h].min()), np.ceil(df_R_h_bd3[variable_R_h].max()))
                    locator = MaxNLocator(prune='both')
                    axes[i, 0].yaxis.set_major_locator(locator)
                    
                    # Force the figure to update the y-ticks
                    fig.canvas.draw_idle()
                    axes[i, 0].tick_params(axis='y', rotation=0)

                    # Boxplots mensuales
                    sns.boxplot(x=df_R_h_bd3['TIMESTAMP'].dt.month, y=df_R_h_bd3[variable_R_h], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i, 1])
                    
                    axes[i, 1].set_title(f'{num_estacion} - {variable_R_h}- Mensual')
                    axes[i, 1].set_xlabel('Mes')
                    axes[i, 1].set_ylabel(unidad)
                    axes[i, 1].set_xticks(range(0, 13))  # 13 meses
                    axes[i, 1].set_ylim(np.floor(df_R_h_bd3[variable_R_h].min()), np.ceil(df_R_h_bd3[variable_R_h].max()))
                    locator = MaxNLocator(prune='both')
                    axes[i, 1].yaxis.set_major_locator(locator)
                    
                    # Force the figure to update the y-ticks
                    fig.canvas.draw_idle()
                    axes[i, 1].tick_params(axis='x', rotation=45)

            # Ajusta la disposición general y muestra el gráfico
            plt.tight_layout()
            plt.subplots_adjust(top=0.95)
            # Agrega un título a la figura
            fig.suptitle(f'Diagramas de cajas - Estación: {num_estacion}', fontsize=16)
            nombre_diag_caja_T = 'DC_R_Total_E1.png'
            plt.savefig(os.path.join(ruta_pruebas_b, 'DC_R_Total_E1.png'))
            plt.close()
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f'Se ha generado exitosamente el diagrama de cajas de la serie total para la etapa 1 de la radiación solar horaria como: {nombre_diag_caja_T}.')
            print('')
            return True
    else:
        print("No se encontro el archivo R.h.bd2 en la ruta especificada.")
        return False

Diagrama_caja_total_R(unidades)


def plot_time_series(df_R_h_bd3, var1, var2, var3, title=f"Serie de tiempo - Estación: {num_estacion}", xlabel="Tiempo", ylabel= "Radiación Solar"):
    
    plt.figure(figsize=(60, 8), dpi=300)  # Adjusted figure size and DPI as per your requirement

    # Resample data to monthly frequency and calculate max and min
    df_R_h_bd3_monthly_max = df_R_h_bd3.resample('M', on='TIMESTAMP')[var1].max()
    df_R_h_bd3_monthly_max_Rmax = df_R_h_bd3.resample('M', on='TIMESTAMP')[var2].max()
    df_R_h_bd3_monthly_max_Rmin = df_R_h_bd3.resample('M', on='TIMESTAMP')[var3].max()
    #df_R_h_bd3_monthly_min = df_R_h_bd3.resample('M', on='TIMESTAMP')[var1].min()

    
    # Create a combined dataframe for seaborn
    combined_df = pd.DataFrame({
        'Date': df_R_h_bd3_monthly_max.index,
        f'Max {var1}': df_R_h_bd3_monthly_max.values,
        f'Max {var2}': df_R_h_bd3_monthly_max_Rmax.values,
        f'Max {var3}': df_R_h_bd3_monthly_max_Rmin.values,
    }).melt('Date', var_name='Variable', value_name='Value')
    
    # Plot using seaborn
    sns.lineplot(data=combined_df, x='Date', y='Value', hue='Variable', palette=['black', 'blue', 'red'], markers=True)
    
    # Add markers to the maximum and minimum points
    sns.scatterplot(data=combined_df, x='Date', y='Value', hue='Variable', palette=['black', 'blue', 'red'], s=30, legend=False)
    
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
    plt.savefig(os.path.join(ruta_pruebas_b, 'ST_Extremos_R_E1.png'))
    
    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print('Se ha generado exitosamente la serie de tiempo de los extremos mensuales de la serie total para la radiación solar como: ST_Extremos_R_E1.png.')
    print('')

plot_time_series(df_R_h_bd3, 'Rad.MJ_m2.tot.1h.s1', 'Rad.kW_m2.max.1h.s1', 'Rad.kW_m2.min.1h.s1')

#-----------------------------------------------------------------------------------------------------------------

def Diagrama_caja_mensual_R(unidades):
    
    # Leer archivos .csv y realizar operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        df_R_h_bd3 = None

        if ruta_R_h_bd3:
            df_R_h_bd3 = pd.read_csv(ruta_R_h_bd3, na_values=['NA'])
            df_R_h_bd3['TIMESTAMP'] = pd.to_datetime(df_R_h_bd3['TIMESTAMP']) 

    # Lista de nombres de los meses en español
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    # Iterar a través de cada mes
    for month in range(1, 13):
        # Nombre del mes en español
        nombre_mes_carpeta = f"{month:02d}.{meses[month - 1]}"
        nombre_mes = meses[month - 1]
        ruta_meses = os.path.join(ruta_pruebas_b, nombre_mes_carpeta)
        os.makedirs(ruta_meses, exist_ok=True)

        # Genera una figura con cuatro subtramas (3 filas, 1 columnas)
        fig, axes = plt.subplots(3, 1, figsize=(8, 15), dpi=300)

        # Diagramas de caja para T.h si df_R_h_bd3 no es None
        if df_R_h_bd3 is not None:
            for i, (variable_R_h, nombre_variable, unidades_variable) in enumerate(zip(Variables_R_h, Variable_nombre, unidades)):
                data = df_R_h_bd3[variable_R_h][df_R_h_bd3['TIMESTAMP'].dt.month == month]
                
                # Calcular estadísticas
                Media_aritmética_R_h = data.mean()
                Desviación_estándar_R_h = data.std()
                P25_R_h = data.quantile(0.25)
                P50_R_h = data.quantile(0.50)  # Median
                P75_R_h = data.quantile(0.75)
                IQR_R_h = P75_R_h - P25_R_h
                BI_R_h = P25_R_h - 1.5 * IQR_R_h
                BS_R_h = P75_R_h + 1.5 * IQR_R_h
                Min_R_h = data.min()
                Max_R_h = data.max()
                MinZ_R_h = (Min_R_h - Media_aritmética_R_h) / Desviación_estándar_R_h
                MaxZ_R_h = (Max_R_h - Media_aritmética_R_h) / Desviación_estándar_R_h
                lim_inf_R_h = np.fix(MinZ_R_h)*Desviación_estándar_R_h + Media_aritmética_R_h
                lim_sup_R_h = np.fix(MaxZ_R_h)*Desviación_estándar_R_h + Media_aritmética_R_h
                
                sns.boxplot(y=data, color="blue", linewidth=1.5,
                            boxprops=dict(facecolor='blue', edgecolor='black'),
                            flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'),
                            ax=axes[i])
                axes[i].set_title(f'{num_estacion} - {variable_R_h} - {nombre_mes}')
                axes[i].set_xlabel('')
                axes[i].set_ylabel(f'{nombre_variable} ({unidades_variable})')
                axes[i].set_ylim(np.floor(data.min()), np.ceil(data.max()))
                locator = MaxNLocator(prune='both')
                axes[i].yaxis.set_major_locator(locator)
                
                # Force the figure to update the y-ticks
                fig.canvas.draw_idle()
                axes[i].tick_params(axis='y', rotation=0)
                axes[i].grid(True, axis='y')

                # Agregar información estadística en la esquina superior derecha de cada subplot
                axes[i].text(0.95, 0.95, f'Media aritmética = {Media_aritmética_R_h:.2f} {unidades_variable}\nDesviación estándar = {Desviación_estándar_R_h:.2f} {unidades_variable}\nLím.Vec. superior = {lim_sup_R_h:.2f}{unidades_variable}\nBigote superior = {BS_R_h:.2f}{unidades_variable}',
                                      transform=axes[i].transAxes,
                                      fontsize=8, verticalalignment='top', horizontalalignment='right', backgroundcolor='white')

    # Ajustar el diseño
        plt.tight_layout()

    # Guardar el gráfico
        plt.savefig(os.path.join(ruta_meses, f'{nombre_mes}_DC_E1.png'))
        plt.close()

    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print('Se han generado exitosamente los diagramas de cajas mensuales de la etapa 1 para la radiación solar horaria.')
    print('')
    return True if (df_R_h_bd3 is not None) else False

Diagrama_caja_mensual_R("")

#-----------------------------------------------------------------------------------------------------------------


def generar_archivo_txt_R_h():
    # Si existe el archivo ruta_R_h_bd3, procesar y crear el archivo de texto
    if ruta_R_h_bd3:
        # Leer el archivo CSV y reemplazar los NA por -9
        df_R_h_bd3 = pd.read_csv(ruta_R_h_bd3)
        df_R_h_bd3.fillna(-9, inplace=True)

        # Crear una copia del DataFrame con los nombres de columnas cambiados
        df_R_h_bd3_copy = df_R_h_bd3.rename(columns={
            'Rad.MJ_m2.tot.1h.s1': 'RAD_MJ_m2_Tot',
            'Rad.kW_m2.max.1h.s1': 'RAD_KW_m2_Max',
            'Rad.kW_m2.min.1h.s1': 'RAD_KW_m2_Min',
            'Rad-int_sol.min_hour.tot.1h.s1': 'INT_sol'
        })

        # Crear el nombre del archivo de texto
        fecha_inicial = pd.to_datetime(df_R_h_bd3['TIMESTAMP']).min().strftime('%Y%m%d')
        fecha_final = pd.to_datetime(df_R_h_bd3['TIMESTAMP']).max().strftime('%Y%m%d')
        nombre_archivo_txt_R_h = f"H-{num_estacion}-{fecha_inicial}-{fecha_final}.txt"

        # Guardar el archivo de texto con las celdas separadas por coma
        ruta_archivo_texto = os.path.join(ruta_analisis_R, nombre_archivo_txt_R_h)
        # Verificar si existe un archivo que comience con "D-" y eliminarlo
        for file_name in os.listdir(ruta_analisis_R):
            if file_name.startswith('H-'):
                os.remove(os.path.join(ruta_analisis_R, file_name))
                
        menos_nueve_entero(df_R_h_bd3_copy, ruta_archivo_texto)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Se ha generado exitosamente el archivo de texto de la radiación solar horaria horaria como: {nombre_archivo_txt_R_h}.")
        print('')
    else:
        print("Error: No se pudo generar el archivo de texto puesto que no se encontró el archivo de la radiación solar horaria horaria bd3")

# Llamada a la función
generar_archivo_txt_R_h()

