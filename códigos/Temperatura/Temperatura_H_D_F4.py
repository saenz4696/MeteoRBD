import pandas as pd
import os
import warnings
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
from distfit import distfit
import scipy.stats as stats
import numpy as np
from scipy.stats import skew, kurtosis
import matplotlib.dates as mdates

sns.set_style("whitegrid")
matplotlib.use('Agg')

# -------------------------------Rutas generales

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
    
# Ruta donde se guardarán los archivos CSV
ruta_guardado = os.path.join(ruta_analisis_T, "Pruebas_estadisticas")
    
# Encuentra el archivo T.h.bd2.csv de la temperatura en la ruta de la estación
ruta_T_h_bd2 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.h.bd2' in archivo), None)

# Encuentra el archivo T.d.bd2.csv de la temperatura en la ruta de la estación
ruta_T_d_bd2 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.d.bd2' in archivo), None)
    
unidad = '°C'

# Variables para T.h
Variables_T_h = ['Temp.degC.avg.1h.s1']
# Variables para T.d
Variables_T_d = ['Temp.degC.max.dm.s1', 'Temp.degC.min.dm.s1']
Variables_T_d_Time = ['Temp.CST.max.dm.s1','Temp.CST.min.dm.s1']

#-----------------------------------------------------------------------------------------------------------------
#Estadisticas chebyshev
if ruta_T_h_bd2 or ruta_T_d_bd2:
    # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if ruta_T_h_bd2:
            df_T_h_bd2 = pd.read_csv(ruta_T_h_bd2, na_values=['NA'])
            df_T_h_bd2['TIMESTAMP'] = pd.to_datetime(df_T_h_bd2['TIMESTAMP'])  # Convertir a tipo de dato de Fecha y hora

        if ruta_T_d_bd2:
            df_T_d_bd2 = pd.read_csv(ruta_T_d_bd2, na_values=['NA'])
            df_T_d_bd2['TIMESTAMP'] = pd.to_datetime(df_T_d_bd2['TIMESTAMP'])

#-----------------------------------------------------------------------------------------------------------------
# Definir los nombres de los meses en español
nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

def Estadisticos_T_h_d(ruta_pruebas_b, num_estacion):
    
    # Inicializar diccionarios para almacenar estadísticas de T_h y T_d
    estadisticos_T_h_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_T_h + Variables_T_d}

    # Leer archivos .csv y realizar operaciones de limpieza y corrección de TIMESTAMPs
    df_T_h_bd2 = pd.read_csv(ruta_T_h_bd2, na_values=['NA'])
    df_T_h_bd2['TIMESTAMP'] = pd.to_datetime(df_T_h_bd2['TIMESTAMP']) 
    
    df_T_d_bd2 = pd.read_csv(ruta_T_d_bd2, na_values=['NA'])
    df_T_d_bd2['TIMESTAMP'] = pd.to_datetime(df_T_d_bd2['TIMESTAMP'])

    # Iterar sobre cada mes
    for mes in range(1, 13):
        # Filtrar datos por mes para T_h y T_d
        df_mes_T_h = df_T_h_bd2[df_T_h_bd2['TIMESTAMP'].dt.month == mes]
        df_mes_T_d = df_T_d_bd2[df_T_d_bd2['TIMESTAMP'].dt.month == mes]

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
    with open(os.path.join(ruta_pruebas_b, "Estadisticos_T.txt"), "w") as file:
        for variable in Variables_T_h + Variables_T_d:
            file.write(f"\nEstación: {num_estacion} - Variable: {variable}\n")
            file.write("{:<12} {:<8} {:<8} {:<17} {:<17}\n".format("Mes", "Máximo", "Mínimo", "Media aritmética", "Desviación estándar"))
            for mes in range(1, 13):
                valores = estadisticos_T_h_d[variable][nombres_meses[mes - 1]]
                max_val, min_val, mean_val, std_val = valores
                
                if max_val == 'NA':
                    file.write("{:<12} {:<8} {:<8} {:<17} {:<17}\n".format(nombres_meses[mes - 1], 'NA', 'NA', 'NA', 'NA'))
                else:
                    file.write("{:<12} {:<8.2f} {:<8.2f} {:<17.2f} {:<17.2f}\n".format(nombres_meses[mes - 1], max_val, min_val, mean_val, std_val))

# Llamada a la función
Estadisticos_T_h_d(ruta_pruebas_b, num_estacion)

#-----------------------------------------------------------------------------------------------------------------

#Genera diagramas de caja totales y mensuales para cada variable.
def Diagrama_caja_total_T(unidades):

    if ruta_T_h_bd2 or ruta_T_d_bd2:
        # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            if ruta_T_h_bd2:
                df_T_h_bd2 = pd.read_csv(ruta_T_h_bd2, na_values=['NA'])
                df_T_h_bd2['TIMESTAMP'] = pd.to_datetime(df_T_h_bd2['TIMESTAMP'])  # Convertir a tipo de dato de Fecha y hora

            if ruta_T_d_bd2:
                df_T_d_bd2 = pd.read_csv(ruta_T_d_bd2, na_values=['NA'])
                df_T_d_bd2['TIMESTAMP'] = pd.to_datetime(df_T_d_bd2['TIMESTAMP'])
                
            # Genera una figura con 3 subtramas (3 filas, 2 columnas)
            fig, axes = plt.subplots(3, 2, figsize=(16, 25), dpi=300)

            # Boxplots para T.h
            if ruta_T_h_bd2:
                for i, variable_T_h in enumerate(Variables_T_h):
                    # Boxplot de la serie total (orientación vertical)
                    sns.boxplot(y=df_T_h_bd2[variable_T_h], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i, 0])
                    
                    axes[i, 0].set_title(f'{num_estacion} - {variable_T_h}- Total')
                    axes[i, 0].set_ylabel('Temperatura (°C)')
                    axes[i, 0].set_yticks(range(int(df_T_h_bd2[variable_T_h].min()), int(df_T_h_bd2[variable_T_h].max()) + 1, 2))
                    axes[i, 0].tick_params(axis='y', rotation=0)
                    axes[i, 0].grid(True, axis='y')

                    # Boxplots mensuales
                    sns.boxplot(x=df_T_h_bd2['TIMESTAMP'].dt.month, y=df_T_h_bd2[variable_T_h], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i, 1])
                    
                    axes[i, 1].set_title(f'{num_estacion} - {variable_T_h}- Mensual')
                    axes[i, 1].set_xlabel('Mes')
                    axes[i, 1].set_ylabel('Temperatura (°C)')
                    axes[i, 1].set_xticks(range(0, 13))  # 13 meses
                    axes[i, 1].set_yticks(range(int(df_T_h_bd2[variable_T_h].min()), int(df_T_h_bd2[variable_T_h].max()) + 1, 2))
                    axes[i, 1].tick_params(axis='x', rotation=45)
                    axes[i, 1].grid(True, axis='y')

            # Boxplots para T.d
            if ruta_T_d_bd2:
                for i, variable_T_d in enumerate(Variables_T_d):
                    # Boxplot de la serie total (orientación vertical)
                    sns.boxplot(y=df_T_d_bd2[variable_T_d], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i+1, 0])
                    
                    axes[i+1, 0].set_title(f'{num_estacion} - {variable_T_d}- Total')
                    axes[i+1, 0].set_ylabel('Temperatura (°C)')
                    axes[i+1, 0].set_yticks(range(int(df_T_d_bd2[variable_T_d].min()), int(df_T_d_bd2[variable_T_d].max()) + 1))
                    axes[i+1, 0].tick_params(axis='y', rotation=0)
                    axes[i+1, 0].grid(True, axis='y')

                    # Boxplots mensuales
                    sns.boxplot(x=df_T_d_bd2['TIMESTAMP'].dt.month, y=df_T_d_bd2[variable_T_d], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i+1, 1])
                    
                    axes[i+1, 1].set_title(f'{num_estacion} - {variable_T_d}- Mensual')
                    axes[i+1, 1].set_xlabel('Mes')
                    axes[i+1, 1].set_ylabel('Temperatura (°C)')
                    axes[i+1, 1].set_xticks(range(0, 13))  # 13 meses
                    axes[i+1, 1].set_yticks(range(int(df_T_d_bd2[variable_T_d].min()), int(df_T_d_bd2[variable_T_d].max()) + 1))
                    axes[i+1, 1].tick_params(axis='x', rotation=45)
                    axes[i+1, 1].grid(True, axis='y')

            # Ajusta la disposición general y muestra el gráfico
            plt.tight_layout()
            plt.subplots_adjust(top=0.95)
            # Agrega un título a la figura
            fig.suptitle(f'Diagramas de cajas - Estación: {num_estacion}', fontsize=16)
            nombre_diag_caja_T = 'DC_T_Total.png'
            plt.savefig(os.path.join(ruta_pruebas_b, 'DC_T_Total.png'))
            plt.close()
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f'Se ha generado exitosamente el diagrama de cajas de la serie total para la temperatura como: {nombre_diag_caja_T}.')
            print('')
            return True
    else:
        print("No se encontraron archivos T.h.bd2 y/o T.d.bd2 en la ruta especificada.")
        return False
    
Diagrama_caja_total_T(['°C'])
#-----------------------------------------------------------------------------------------------------------------

def plot_time_series(df_T_h_bd2, df_T_d_bd2, var1, var2, var3, title=f"Serie de tiempo - Estación: {num_estacion}", xlabel="Tiempo", ylabel="Temperatura (°C)"):
    plt.figure(figsize=(60, 8), dpi=300)  # Adjusted figure size and DPI as per your requirement

    # Resample data to monthly frequency and calculate max and min
    df_T_h_bd2_monthly_max = df_T_h_bd2.resample('M', on='TIMESTAMP')[var1].max()
    df_T_h_bd2_monthly_min = df_T_h_bd2.resample('M', on='TIMESTAMP')[var1].min()
    df_T_d_bd2_monthly_max = df_T_d_bd2.resample('M', on='TIMESTAMP')[var2].max()
    df_T_d_bd2_monthly_min = df_T_d_bd2.resample('M', on='TIMESTAMP')[var3].min()
    
    # Align the indices to ensure all arrays have the same length
    combined_index = df_T_h_bd2_monthly_max.index.union(df_T_h_bd2_monthly_min.index).union(df_T_d_bd2_monthly_max.index).union(df_T_d_bd2_monthly_min.index)
    df_T_h_bd2_monthly_max = df_T_h_bd2_monthly_max.reindex(combined_index)
    df_T_h_bd2_monthly_min = df_T_h_bd2_monthly_min.reindex(combined_index)
    df_T_d_bd2_monthly_max = df_T_d_bd2_monthly_max.reindex(combined_index)
    df_T_d_bd2_monthly_min = df_T_d_bd2_monthly_min.reindex(combined_index)
    
    # Create a combined dataframe for seaborn
    combined_df = pd.DataFrame({
        'Date': df_T_h_bd2_monthly_max.index,
        f'Max {var1}': df_T_h_bd2_monthly_max.values,
        f'Min {var1}': df_T_h_bd2_monthly_min.values,
        f'Max {var2}': df_T_d_bd2_monthly_max.values,
        f'Min {var3}': df_T_d_bd2_monthly_min.values
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
    plt.savefig(os.path.join(ruta_guardado, 'ST_Extremos_T.png'))
    
    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print('Se ha generado exitosamente la serie de tiempo de los extremos mensuales de la serie total para la temperatura como: ST_Extremos_T.png.')
    print('')

# Example call to the function (adjust variables and dataframes as per your dataset)
plot_time_series(df_T_h_bd2, df_T_d_bd2, 'Temp.degC.avg.1h.s1', 'Temp.degC.max.dm.s1', 'Temp.degC.min.dm.s1')

# Define una función para ajustar la mejor distribucion posible a las variables analizadas.

def Dist_prob_T_h_d():

    # Variables para verificar si se encontraron ambos archivos
    encontrado_T_h_bd2 = ruta_T_h_bd2 is not None
    encontrado_T_d_bd2 = ruta_T_d_bd2 is not None
    
    #Establece el nivel de ocnfianza
    niv_conf = 0.9995

    if encontrado_T_h_bd2 or encontrado_T_d_bd2:
        # Crea una figura con cuatro subfiguras en tres filas y dos columnas
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 15), dpi=300)

        # Procesa T.h.bd2 si está presente
        if encontrado_T_h_bd2:
            # Lee el archivo .csv y realiza operaciones de limpieza y corrección de timestamps para T.h.bd2
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df_T_h_bd2 = pd.read_csv(ruta_T_h_bd2, na_values=['NA'], keep_default_na=False)

                           
            # Selecciona las columnas de interés para temperatura del aire y temperatura de rocío
            columnas_interes_T_h = ['Temp.degC.avg.1h.s1', 'TIMESTAMP']

            # Filtra solo las columnas que contienen las variables de la temperatura hoaria y 'TIMESTAMP'
            df_filtrado_T_h = df_T_h_bd2[columnas_interes_T_h].dropna()

            # Asigna las columnas a las variables de interés
            timestamps_T_h = df_filtrado_T_h['TIMESTAMP']

            # Selecciona las columnas de interés para temperatura del aire y temperatura de rocío
            col_temp_T_h = df_filtrado_T_h['Temp.degC.avg.1h.s1']

            # Inicializa el objeto distfit para la temperatura del aire
            dist_T_h = distfit()
            dist_T_h.fit_transform(col_temp_T_h, verbose=0)

            # Obtiene la mejor distribución y sus parámetros para la temperatura del aire
            Dist_Ajust_T_h = dist_T_h.model['name']
            Dist_Ajust_Param_T_h = dist_T_h.model['params']
            Dist_Ajust_Stats_T_h = getattr(stats, Dist_Ajust_T_h)
            Dist_Ajust_rvs_T_h =Dist_Ajust_Stats_T_h.rvs(*Dist_Ajust_Param_T_h, size=len(col_temp_T_h))
            Ajusta_datos_T_h = Dist_Ajust_rvs_T_h

            # Calcula los intervalos de confianza para la mejor distribución de la temperatura del aire
            lim_inf_T_h, lim_sup_T_h =Dist_Ajust_Stats_T_h.interval(niv_conf, *Dist_Ajust_Param_T_h)
            
            #Calculo de parametros estadisticos.
            μ_T_h = col_temp_T_h.mean()
            std_dev_T_h = col_temp_T_h.std()
            Asimetría_T_h = skew(col_temp_T_h)
            kurtosis_T_h = kurtosis(col_temp_T_h)

            # Grafica la distribución ajustada junto con el histograma de los datos originales para la temperatura del aire
            sns.histplot(col_temp_T_h, kde=True, color='blue', label=f'Datos originales\nKurtosis = {kurtosis_T_h:.2f} - Asimetría = {Asimetría_T_h:.2f}\nMedia aritmética: = {μ_T_h:.2f}°C\nDesviación estándar = {std_dev_T_h:.2f}°C', ax=ax1)
            sns.histplot(Ajusta_datos_T_h, kde=True, color='red', label=f'Distribución ajustada ({Dist_Ajust_T_h})\nIC: ({lim_inf_T_h:.2f} °C - {lim_sup_T_h:.2f} °C) - NC: {niv_conf*100:.2f}%', ax=ax1)

            # Ajusta los límites del eje X para mostrar cada unidad
            ax1.set_xticks(np.arange(int(col_temp_T_h.min()), int(col_temp_T_h.max()) + 1, 1))
            ax1.set_xticklabels(ax1.get_xticks(), rotation='vertical')

            # Ajusta los límites del eje X para mostrar una unidad de
            ax1.grid(True, linestyle='--', alpha=0.7, color='black')

            ax1.set_title(f'{num_estacion} - {columnas_interes_T_h[0]}')
            ax1.set_xlabel('Temperatura (°C)')
            ax1.set_ylabel('Frecuencia')
            ax1.legend()
            
        # Procesa T.d.bd2 si está presente
        if encontrado_T_d_bd2:
            # Lee el archivo .csv y realiza operaciones de limpieza y corrección de timestamps para T.d.bd2
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df_T_d_bd2 = pd.read_csv(ruta_T_d_bd2, na_values=['NA'], keep_default_na=False)
                
            # Selecciona las columnas de interés para temperatura del aire y temperatura de rocío
            columnas_interes_T_d = ['Temp.degC.max.dm.s1', 'Temp.degC.min.dm.s1', 'TIMESTAMP']

            # Filtra solo las filas que contienen ambos 'Temp.degC.avg.1h.s1' y 'TIMESTAMP'
            df_filtrado_T_d = df_T_d_bd2[columnas_interes_T_d].dropna()

            # Asigna las columnas a las variables de interés
            timestamps_T_d = df_filtrado_T_d['TIMESTAMP']

            # Selecciona las columnas de interés para temperatura del aire y temperatura de rocío
            col_Tmax_T_d = df_filtrado_T_d['Temp.degC.max.dm.s1']
            col_Tmin_T_d = df_filtrado_T_d['Temp.degC.min.dm.s1']

            # Inicializa el objeto distfit para T.d.bd2 - Temp. Máxima
            dist_Tmax_d = distfit()
            dist_Tmax_d.fit_transform(col_Tmax_T_d, verbose=0)

            # Obtiene la mejor distribución y sus parámetros para T.d.bd2 - Temp. Máxima
            Dist_Ajust_Tmax_d = dist_Tmax_d.model['name']
            Dist_Ajust_Param_Tmax_d = dist_Tmax_d.model['params']
            Dist_Ajust_Stats_Tmax_d = getattr(stats, Dist_Ajust_Tmax_d)
            Dist_Ajust_rvs_Tmax_d =Dist_Ajust_Stats_Tmax_d.rvs(*Dist_Ajust_Param_Tmax_d, size=len(col_Tmax_T_d))
            Ajusta_datos_Tmax_d = Dist_Ajust_rvs_Tmax_d

            # Calcula los intervalos de confianza para la mejor distribución de T.d.bd2 - Temp. Máxima
            lim_inf_Tmax_d, lim_sup_Tmax_d =Dist_Ajust_Stats_Tmax_d.interval(niv_conf, *Dist_Ajust_Param_Tmax_d)

            # Inicializa el objeto distfit para T.d.bd2 - Temp. Mínima
            dist_Tmin_d = distfit()
            dist_Tmin_d.fit_transform(col_Tmin_T_d, verbose=0)

            # Obtiene la mejor distribución y sus parámetros para T.d.bd2 - Temp. Mínima
            Dist_Ajust_Tmin_d = dist_Tmin_d.model['name']
            Dist_Ajust_Param_Tmin_d = dist_Tmin_d.model['params']
            Dist_Ajust_Stats_Tmin_d = getattr(stats, Dist_Ajust_Tmin_d)
            Dist_Ajust_rvs_Tmin_d =Dist_Ajust_Stats_Tmin_d.rvs(*Dist_Ajust_Param_Tmin_d, size=len(col_Tmin_T_d))
            Ajusta_datos_Tmin_d = Dist_Ajust_rvs_Tmin_d

            # Calcula los intervalos de confianza para la mejor distribución de T.d.bd2 - Temp. Mínima
            lim_inf_Tmin_d, lim_sup_Tmin_d =Dist_Ajust_Stats_Tmin_d.interval(niv_conf, *Dist_Ajust_Param_Tmin_d)
            
            μ_Tmax_d= col_Tmax_T_d.mean()
            std_dev_Tmax_d = col_Tmax_T_d.std()
            Asimetría_Tmax_d = skew(col_Tmax_T_d)
            kurtosis_Tmax_d = kurtosis(col_Tmax_T_d)

            # Grafica la distribución ajustada junto con el histograma de los datos originales para T.d.bd2 - Temp. Máxima
            sns.histplot(col_Tmax_T_d, kde=True, color='blue', label=f'Datos originales\nKurtosis = {kurtosis_Tmax_d:.2f} - Asimetría = {Asimetría_Tmax_d:.2f}\nMedia aritmética = {μ_Tmax_d:.2f}°C\nDesviación estándar = {std_dev_Tmax_d:.2f}°C', ax=ax2)
            sns.histplot(Ajusta_datos_Tmax_d, kde=True, color='red', label=f'Distribución ajustada ({Dist_Ajust_Tmax_d})\nIC: ({lim_inf_Tmax_d:.2f} °C - {lim_sup_Tmax_d:.2f} °C) - NC: {niv_conf*100:.2f}%', ax=ax2)

            # Ajusta los límites del eje X para mostrar cada unidad
            ax2.set_xticks(np.arange(int(col_Tmax_T_d.min()), int(col_Tmax_T_d.max()) + 1, 1))
            ax2.set_xticklabels(ax2.get_xticks(), rotation='vertical')

            # Ajusta los límites del eje X para mostrar una unidad de
            ax2.grid(True, linestyle='--', alpha=0.7, color='black')

            ax2.set_title(f'{num_estacion} - {columnas_interes_T_d[0]}')
            ax2.set_xlabel('Temperatura (°C)')
            ax2.set_ylabel('Frecuencia')
            ax2.legend()
            
            μ_Tmin_d = col_Tmin_T_d.mean()
            std_dev_Tmin_d = col_Tmin_T_d.std()
            Asimetría_Tmin_d = skew(col_Tmin_T_d)
            kurtosis_Tmin_d = kurtosis(col_Tmin_T_d)

            # Grafica la distribución ajustada junto con el histograma de los datos originales para T.d.bd2 - Temp. Mínima
            sns.histplot(col_Tmin_T_d, kde=True, color='blue', label=f'Datos originales\nKurtosis = {kurtosis_Tmin_d:.2f} - Asimetría = {Asimetría_Tmin_d:.2f}\nMedia aritmética = {μ_Tmin_d:.2f}°C\nDesviación estándar = {std_dev_Tmin_d:.2f}°C', ax=ax3)
            sns.histplot(Ajusta_datos_Tmin_d, kde=True, color='red', label=f'Distribución ajustada ({Dist_Ajust_Tmin_d})\nIC: ({lim_inf_Tmin_d:.2f} °C - {lim_sup_Tmin_d:.2f} °C) - NC: {niv_conf*100:.2f}%', ax=ax3)

            # Ajusta los límites del eje X para mostrar cada unidad
            ax3.set_xticks(np.arange(int(col_Tmin_T_d.min()), int(col_Tmin_T_d.max()) + 1, 1))
            ax3.set_xticklabels(ax3.get_xticks(), rotation='vertical')

            # Ajusta los límites del eje X para mostrar una unidad de
            ax3.grid(True, linestyle='--', alpha=0.7, color='black')

            ax3.set_title(f'{num_estacion} - {columnas_interes_T_d[1]}')
            ax3.set_xlabel('Temperatura (°C)')
            ax3.set_ylabel('Frecuencia')
            ax3.legend()
            
        # Ajusta la disposición de las subfiguras
        plt.tight_layout()
        
        # Agrega un título a la imagen general con ajuste de posición vertical
        plt.suptitle(f'Distribuciones de la temperatura - Estación: {num_estacion}', fontsize=16, y=0.95)
        
        # Ajusta la posición de la figura para dejar espacio para el título
        plt.subplots_adjust(top=0.9, bottom=0.1)

        # Guarda la imagen con ambas subfiguras
        plt.savefig(os.path.join(ruta_pruebas_b, 'H_T_Total.png'))
        plt.show()
        
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print('Se ha generado exitosamente el histograma de la serie total para la temperatura como: H_T_Total.png.')
        
Dist_prob_T_h_d()
#-----------------------------------------------------------------------------------------------------------------
#Funcion para generar boxplots mensuales de todas las variables.

def Diagrama_caja_mensual_T(unidades):
    # Leer archivos .csv y realizar operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        df_T_h_bd2 = None
        df_T_d_bd2 = None

        if ruta_T_h_bd2:
            df_T_h_bd2 = pd.read_csv(ruta_T_h_bd2, na_values=['NA'])
            df_T_h_bd2['TIMESTAMP'] = pd.to_datetime(df_T_h_bd2['TIMESTAMP'])

        if ruta_T_d_bd2:
            df_T_d_bd2 = pd.read_csv(ruta_T_d_bd2, na_values=['NA'])
            df_T_d_bd2['TIMESTAMP'] = pd.to_datetime(df_T_d_bd2['TIMESTAMP'])

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

        # Diagramas de caja para T.h si df_T_h_bd2 no es None
        if df_T_h_bd2 is not None:
            for i, variable_T_h in enumerate(Variables_T_h):
                data = df_T_h_bd2[variable_T_h][df_T_h_bd2['TIMESTAMP'].dt.month == month]

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

        # Diagramas de caja para T.d si df_T_d_bd2 no es None
        if df_T_d_bd2 is not None:
            for i, variable_T_d in enumerate(Variables_T_d):
                data = df_T_d_bd2[variable_T_d][df_T_d_bd2['TIMESTAMP'].dt.month == month]

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
        plt.savefig(os.path.join(ruta_meses, f'DC_T_{nombre_mes}.png'))
        plt.close()

    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print('Se han generado exitosamente los diagramas de cajas mensuales para la temperatura.')
    print('')
    return True if (df_T_h_bd2 is not None or df_T_d_bd2 is not None) else False


Diagrama_caja_mensual_T("")

#-----------------------------------------------------------------------------------------------------------------

# Inicializar el DataFrame fuera del bucle para acumular datos de todos los meses
valores_fuera_total = pd.DataFrame(columns=['TIMESTAMP', 'Valor_Original', 'Limite', 'Elemento'])

# Iterar sobre cada mes en tus datos
# Iterar sobre cada mes en tus datos
def rubextremes_T_h(df_T_h_bd2, Variables_T_h, nombres_meses, ruta_guardado):
    for mes in range(1, 13):
        # Filtrar datos por mes si df_T_h_bd2 está definido
        if 'df_T_h_bd2' in locals():
            df_mes = df_T_h_bd2[df_T_h_bd2['TIMESTAMP'].dt.month == mes]

            # Inicializar el DataFrame para cada mes
            valores_fuera_mes = pd.DataFrame(columns=['Elemento','TIMESTAMP', 'Valor_Original', 'Valor_reemplazo', 'Limite', 'Procedimiento_adoptado','Comentario'])

            # Iterar sobre cada variable en Variables_T_h
            for variable in Variables_T_h:
                # Calcular Media_aritmética_T_h  y desviación estándar si hay datos
                if not df_mes.empty:
                    Media_aritmética_T_h  = df_mes[variable].mean()
                    Desviación_estándar_T_h = df_mes[variable].std()
                    P25_T_h = df_mes[variable].quantile(0.25)
                    P50_T_h = df_mes[variable].quantile(0.50)  # Median
                    P75_T_h = df_mes[variable].quantile(0.75)
                    IQR_T_h = P75_T_h - P25_T_h
                    BI_T_h = P25_T_h - 1.5 * IQR_T_h
                    BS_T_h = P75_T_h + 1.5 * IQR_T_h
                    Min_T_h = df_mes[variable].min()
                    Max_T_h = df_mes[variable].max()
                    MinZ_T_h = (Min_T_h - Media_aritmética_T_h) / Desviación_estándar_T_h
                    MaxZ_T_h = (Max_T_h - Media_aritmética_T_h) / Desviación_estándar_T_h
                    lim_inf_T_h = np.fix(MinZ_T_h) * Desviación_estándar_T_h + Media_aritmética_T_h
                    lim_sup_T_h = np.fix(MaxZ_T_h) * Desviación_estándar_T_h + Media_aritmética_T_h

                    # Inicializar los DataFrames para valores menores y mayores
                    valores_menores = pd.DataFrame(columns=['TIMESTAMP', variable, 'Limite'])
                    valores_mayores = pd.DataFrame(columns=['TIMESTAMP', variable, 'Limite'])

                    # Definir condiciones para valores menores al límite inferior
                    cond1_T_h = (lim_inf_T_h <= BI_T_h) or (MinZ_T_h <= -3)
                    cond1b_T_h = Min_T_h < BI_T_h
                    if cond1_T_h:
                        # Check if the minimum value is less than the lower whisker
                        valores_menores = df_mes.loc[(df_mes[variable] < lim_inf_T_h), ['TIMESTAMP', variable]]
                        valores_menores['Limite'] = f"Menor_a_{lim_inf_T_h:.2f}"
                    elif cond1b_T_h:
                        # Register the minimum value
                        valores_menores = df_mes.loc[df_mes[variable] == Min_T_h, ['TIMESTAMP', variable]]
                        valores_menores['Limite'] = f"Menor_a_{BI_T_h:.2f}"

                    # Definir condiciones para valores mayores al límite superior
                    cond2_T_h = (lim_sup_T_h >= BS_T_h) or (MaxZ_T_h >= 3)
                    cond2b_T_h = Max_T_h > BS_T_h
                    if cond2_T_h:
                        # Check if the maximum value is greater than the upper whisker
                        valores_mayores = df_mes.loc[(df_mes[variable] > lim_sup_T_h), ['TIMESTAMP', variable]]
                        valores_mayores['Limite'] = f"Mayor_a_{lim_sup_T_h:.2f}"
                    elif cond2b_T_h:
                        # Register the maximum value
                        valores_mayores = df_mes.loc[df_mes[variable] == Max_T_h, ['TIMESTAMP', variable]]
                        valores_mayores['Limite'] = f"Mayor_a_{BS_T_h:.2f}"

                    # Concatenar los dos DataFrames de valores filtrados
                    valores_fuera = pd.concat([valores_menores, valores_mayores])

                    # Agregar el nombre de la variable a la columna 'Elemento'
                    valores_fuera['Elemento'] = variable

                    # Renombrar la columna de valores originales
                    valores_fuera = valores_fuera.rename(columns={variable: 'Valor_Original'})

                    # Agregar la columna 'valor_reemplazo' con la misma información que 'Valor_Original'
                    valores_fuera = valores_fuera.assign(Valor_reemplazo=valores_fuera['Valor_Original'])

                    # Agregar la columna 'Procedimiento_adoptado' con el valor 'dato_sospechoso'
                    valores_fuera['Procedimiento_adoptado'] = 'dato_sospechoso'

                    valores_fuera['Comentario'] = ''

                    # Verificar si hay datos filtrados
                    if not valores_fuera.empty:
                        # Agregar los valores fuera de los límites al DataFrame total
                        if not valores_fuera_mes.empty:
                            valores_fuera_mes = pd.concat([valores_fuera_mes, valores_fuera])
                        else:
                            valores_fuera_mes = valores_fuera

            if not valores_fuera_mes.empty:
                # Obtener el nombre del mes en español
                nombre_mes_espanol = nombres_meses[mes - 1]

                # Nombre del archivo CSV con el nombre del mes en español
                nombre_archivo = f"{nombre_mes_espanol}_T_h.csv"

                # Save the DataFrame to a CSV file in the folder containing the Spanish month name
                for root, dirs, files in os.walk(ruta_guardado):
                    for dir in dirs:
                        if nombre_mes_espanol.lower() in dir.lower():
                            ruta_archivo = os.path.join(root, dir, nombre_archivo)

                            # Reorder columns to match the specified order
                            valores_fuera_mes = valores_fuera_mes[['Elemento','TIMESTAMP', 'Valor_Original', 'Valor_reemplazo', 'Limite', 'Procedimiento_adoptado','Comentario']]

                            # Cambiar el nombre de la columna 'TIMESTAMP' a 'Fecha'
                            valores_fuera_mes.rename(columns={'TIMESTAMP': 'Fecha'}, inplace=True)

                            valores_fuera_mes.to_csv(ruta_archivo, index=False)
                            break

    # Print statement placed outside the loop
    if 'df_T_h_bd2' in locals():
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Se han generado exitosamente las pruebas de valores atipicos mensuales extremos para la temperatura horaria a partir de los archivos bd2.")
        print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se realizaron pruebas de valores atípicos mensuales extemos para la temperatura diaria porque no se encontro el archivo diario tipo bd2.")
        print('')

rubextremes_T_h(df_T_h_bd2, Variables_T_h, nombres_meses, ruta_guardado)
    
# Iterar sobre cada mes en tus datos
def rubextremes_T_d(df_T_d_bd2, Variables_T_d, Variables_T_d_Time, nombres_meses, ruta_guardado):
    for mes in range(1, 13):
        # Filtrar datos por mes si df_T_d_bd2 está definido
        if 'df_T_d_bd2' in locals():
            df_mes = df_T_d_bd2[df_T_d_bd2['TIMESTAMP'].dt.month == mes]

            # Inicializar el DataFrame para cada mes
            valores_fuera_mes = pd.DataFrame(columns=['Elemento','TIMESTAMP', 'Fecha_Especifica', 'Valor_Original', 'Valor_reemplazo', 'Limite', 'Procedimiento_adoptado','Comentario'])

            # Iterar sobre cada variable en Variables_T_d
            for variable, time_var in zip(Variables_T_d, Variables_T_d_Time):
                # Calcular Media_aritmética_T_d  y desviación estándar si hay datos
                if not df_mes.empty:
                    Media_aritmética_T_d  = df_mes[variable].mean()
                    Desviación_estándar_T_d = df_mes[variable].std()
                    P25_T_d = df_mes[variable].quantile(0.25)
                    P50_T_d = df_mes[variable].quantile(0.50)  # Median
                    P75_T_d = df_mes[variable].quantile(0.75)
                    IQR_T_d = P75_T_d - P25_T_d
                    BI_T_d = P25_T_d - 1.5 * IQR_T_d
                    BS_T_d = P75_T_d + 1.5 * IQR_T_d
                    Min_T_d = df_mes[variable].min()
                    Max_T_d = df_mes[variable].max()
                    MinZ_T_d = (Min_T_d - Media_aritmética_T_d) / Desviación_estándar_T_d
                    MaxZ_T_d = (Max_T_d - Media_aritmética_T_d) / Desviación_estándar_T_d
                    lim_inf_T_d = np.fix(MinZ_T_d) * Desviación_estándar_T_d + Media_aritmética_T_d
                    lim_sup_T_d = np.fix(MaxZ_T_d) * Desviación_estándar_T_d + Media_aritmética_T_d

                    # Inicializar los DataFrames para valores menores y mayores
                    valores_menores = pd.DataFrame(columns=['TIMESTAMP', variable, 'Limite'])
                    valores_mayores = pd.DataFrame(columns=['TIMESTAMP', variable, 'Limite'])

                    # Definir condiciones para valores menores al límite inferior
                    cond1_T_d = (lim_inf_T_d <= BI_T_d) or (MinZ_T_d <= -3)
                    cond1b_T_d = Min_T_d < BI_T_d
                    if cond1_T_d:
                        # Check if the minimum value is less than the lower whisker
                        valores_menores = df_mes.loc[(df_mes[variable] < lim_inf_T_d), ['TIMESTAMP', variable]]
                        valores_menores['Limite'] = f"Menor_a_{lim_inf_T_d:.2f}"
                    elif cond1b_T_d:
                        # Register the minimum value
                        valores_menores = df_mes.loc[df_mes[variable] == Min_T_d, ['TIMESTAMP', variable]]
                        valores_menores['Limite'] = f"Menor_a_{BI_T_d:.2f}"

                    # Definir condiciones para valores mayores al límite superior
                    cond2_T_d = (lim_sup_T_d >= BS_T_d) or (MaxZ_T_d >= 3)
                    cond2b_T_d = Max_T_d > BS_T_d
                    if cond2_T_d:
                        # Check if the maximum value is greater than the upper whisker
                        valores_mayores = df_mes.loc[(df_mes[variable] > lim_sup_T_d), ['TIMESTAMP', variable]]
                        valores_mayores['Limite'] = f"Mayor_a_{lim_sup_T_d:.2f}"
                    elif cond2b_T_d:
                        # Register the maximum value
                        valores_mayores = df_mes.loc[df_mes[variable] == Max_T_d, ['TIMESTAMP', variable]]
                        valores_mayores['Limite'] = f"Mayor_a_{BS_T_d:.2f}"

                    # Concatenar los dos DataFrames de valores filtrados
                    valores_fuera = pd.concat([valores_menores, valores_mayores])

                    # Agregar el nombre de la variable a la columna 'Elemento'
                    valores_fuera['Elemento'] = variable

                    # Extract specific time values corresponding to the flagged data points
                    valores_fuera['Fecha_Especifica'] = df_mes.loc[valores_fuera.index, time_var].values

                    # Renombrar la columna de valores originales
                    valores_fuera = valores_fuera.rename(columns={variable: 'Valor_Original'})

                    # Agregar la columna 'valor_reemplazo' con la misma información que 'Valor_Original'
                    valores_fuera = valores_fuera.assign(Valor_reemplazo=valores_fuera['Valor_Original'])

                    # Agregar la columna 'Procedimiento_adoptado' con el valor 'dato_sospechoso'
                    valores_fuera['Procedimiento_adoptado'] = 'dato_sospechoso'

                    valores_fuera['Comentario'] = ''

                    # Verificar si hay datos filtrados
                    if not valores_fuera.empty:
                        # Agregar los valores fuera de los límites al DataFrame total
                        if not valores_fuera_mes.empty:
                            valores_fuera_mes = pd.concat([valores_fuera_mes, valores_fuera])
                        else:
                            valores_fuera_mes = valores_fuera

            if not valores_fuera_mes.empty:
                # Obtener el nombre del mes en español
                nombre_mes_espanol = nombres_meses[mes - 1]

                # Nombre del archivo CSV con el nombre del mes en español
                nombre_archivo = f"{nombre_mes_espanol}_T_d.csv"

                # Save the DataFrame to a CSV file in the folder containing the Spanish month name
                for root, dirs, files in os.walk(ruta_guardado):
                    for dir in dirs:
                        if nombre_mes_espanol.lower() in dir.lower():
                            ruta_archivo = os.path.join(root, dir, nombre_archivo)

                            # Reorder columns to match the specified order
                            valores_fuera_mes = valores_fuera_mes[['Elemento','TIMESTAMP', 'Fecha_Especifica', 'Valor_Original', 'Valor_reemplazo', 'Limite', 'Procedimiento_adoptado','Comentario']]

                            # Cambiar el nombre de la columna 'TIMESTAMP' a 'Fecha'
                            valores_fuera_mes.rename(columns={'TIMESTAMP': 'Fecha'}, inplace=True)

                            valores_fuera_mes.to_csv(ruta_archivo, index=False)
                            break

    # Print statement placed outside the loop
    if 'df_T_d_bd2' in locals():
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Se han generado exitosamente las pruebas de valores atipicos mensuales extremos para la temperatura diaria a partir de los archivos bd2.")
        print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se realizaron pruebas de valores atípicos mensuales extemos para la temperatura diaria porque no se encontro el archivo diario tipo bd2.")
        print('')

rubextremes_T_d(df_T_d_bd2, Variables_T_d, Variables_T_d_Time, nombres_meses, ruta_guardado)


def genera_modif_tec():
    # Nombres de las columnas
    nombres_columnas = ['Elemento', 'Fecha', 'Valor_Original', 'Valor_reemplazo', 'Procedimiento_adoptado', 'Comentario']

    # Crear DataFrames vacíos con las columnas especificadas
    df_tec_h = pd.DataFrame(columns=nombres_columnas)
    df_tec_d = pd.DataFrame(columns=nombres_columnas)

    # Guardar los DataFrames como archivos CSV vacíos
    ruta_archivo_tec_h = os.path.join(ruta_analisis_T, 'Modif_Tec_T_h.csv')
    ruta_archivo_tec_d = os.path.join(ruta_analisis_T, 'Modif_Tec_T_d.csv')

    df_tec_h.to_csv(ruta_archivo_tec_h, index=False)
    df_tec_d.to_csv(ruta_archivo_tec_d, index=False)

genera_modif_tec()
