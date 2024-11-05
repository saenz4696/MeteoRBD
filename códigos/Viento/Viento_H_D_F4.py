import pandas as pd
import os
import warnings
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
from distfit import distfit
import scipy.stats as stats
import numpy as np
import matplotlib.dates as mdates
from scipy.stats import skew, kurtosis

sns.set_style("whitegrid")
matplotlib.use('Agg')

# -------------------------------Rutas generales

# Eliminar UserWarnings de openpyxl
warnings.simplefilter('ignore', category=UserWarning)


datos_crudos = r'C:\\MeteoRBD.v1.0.0\\datos_rbd'

# Encuentra el archivo .xlsx en la datos_crudos que contiene 'Cuenca' y 'Estación' como columnas
ruta_archivo_V =next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Viento" in file and file.endswith(".xlsx")), None)

if ruta_archivo_V:
    archivo_excel = pd.read_excel(ruta_archivo_V)
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

# Establece la ruta para los archivos del viento según el número de estación obtenido del archivo Excel
ruta_analisis_V = f"C:\\MeteoRBD.v1.0.0\\revisión\\{num_estacion}-ema\\Viento"

# Crea las carpetas si no existen
for carpeta in ["", "Pruebas_estadisticas"]:
    ruta_pruebas_b = os.path.join(ruta_analisis_V, carpeta)
    os.makedirs(ruta_pruebas_b, exist_ok=True)
    
# Ruta donde se guardarán los archivos CSV
ruta_guardado = os.path.join(ruta_analisis_V, "Pruebas_estadisticas")
    
# Encuentra el archivo V.h.bd2.csv del viento en la ruta de la estación
ruta_V_h_bd2 = next((os.path.join(ruta_analisis_V, archivo) for archivo in os.listdir(ruta_analisis_V) if archivo.endswith(".csv") and 'V.h.bd2' in archivo), None)

# Encuentra el archivo V.d.bd2.csv del viento en la ruta de la estación
ruta_V_d_bd2 = next((os.path.join(ruta_analisis_V, archivo) for archivo in os.listdir(ruta_analisis_V) if archivo.endswith(".csv") and 'V.d.bd2' in archivo), None)
    
unidad = ''

# Variables para V.h
Variables_V_h = ['Wind-scalar.m_s.avg.1h.s1']
# Variables para V.d
Variables_V_d = ['Wind.m_s.max.dm.s1']
Variables_V_d_time = ['Wind.CST.max.dm.s1']

#-----------------------------------------------------------------------------------------------------------------
#Estadisticas chebyshev
if ruta_V_h_bd2 or ruta_V_d_bd2:
    # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if ruta_V_h_bd2:
            df_V_h_bd2 = pd.read_csv(ruta_V_h_bd2, na_values=['NA'])
            df_V_h_bd2['TIMESTAMP'] = pd.to_datetime(df_V_h_bd2['TIMESTAMP'])  # Convertir a tipo de dato de Fecha y hora

        if ruta_V_d_bd2:
            df_V_d_bd2 = pd.read_csv(ruta_V_d_bd2, na_values=['NA'])
            df_V_d_bd2['TIMESTAMP'] = pd.to_datetime(df_V_d_bd2['TIMESTAMP'])

#-----------------------------------------------------------------------------------------------------------------
# Definir los nombres de los meses en español
nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

def Estadisticos_V_h_d(ruta_pruebas_b, num_estacion):

    # Inicializar diccionarios para almacenar estadísticas de T_h y T_d
    estadisticos_V_h_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_V_h + Variables_V_d}

    # Iterar sobre cada mes en los datos de T_h y T_d
    for mes in range(1, 13):
        # Filtrar datos por mes para T_h y T_d
        df_mes_V_h = df_V_h_bd2[df_V_h_bd2['TIMESTAMP'].dt.month == mes]
        df_mes_V_d = df_V_d_bd2[df_V_d_bd2['TIMESTAMP'].dt.month == mes]

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

    # Guardar estadísticas para T_h y T_d en un archivo de texto
    with open(os.path.join(ruta_pruebas_b, "Estadisticos_V.txt"), "w") as file:
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
def Diagrama_caja_Votal_V(unidades):

    if ruta_V_h_bd2 or ruta_V_d_bd2:
        # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            if ruta_V_h_bd2:
                df_V_h_bd2 = pd.read_csv(ruta_V_h_bd2, na_values=['NA'])
                df_V_h_bd2['TIMESTAMP'] = pd.to_datetime(df_V_h_bd2['TIMESTAMP'])  # Convertir a tipo de dato de Fecha y hora

            if ruta_V_d_bd2:
                df_V_d_bd2 = pd.read_csv(ruta_V_d_bd2, na_values=['NA'])
                df_V_d_bd2['TIMESTAMP'] = pd.to_datetime(df_V_d_bd2['TIMESTAMP'])

            # Genera una figura con cuatro subtramas (2 filas, 2 columnas)
            fig, axes = plt.subplots(2, 2, figsize=(16, 25), dpi=300)

            # Boxplots para V.h
            if ruta_V_h_bd2:
                for i, variable_V_h in enumerate(Variables_V_h):
                    # Boxplot de la serie total (orientación vertical)
                    sns.boxplot(y=df_V_h_bd2[variable_V_h].dropna(), color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i, 0])
                    
                    axes[i, 0].set_title(f'{num_estacion} - {variable_V_h}- Total')
                    axes[i, 0].set_ylabel('Viento escalar (m/s)')
                    axes[i, 0].set_yticks(range(int(df_V_h_bd2[variable_V_h].min()), int(df_V_h_bd2[variable_V_h].max()) + 1))
                    axes[i, 0].tick_params(axis='y', rotation=0)
                    axes[i, 0].grid(True, axis='y')

                    # Boxplots mensuales
                    sns.boxplot(x=df_V_h_bd2['TIMESTAMP'].dt.month, y=df_V_h_bd2[variable_V_h], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i, 1])
                    
                    axes[i, 1].set_title(f'{num_estacion} - {variable_V_h}- Mensual')
                    axes[i, 1].set_xlabel('Mes')
                    axes[i, 1].set_ylabel('Viento escalar (m/s)')
                    axes[i, 1].set_xticks(range(0, 13))  # 13 meses
                    axes[i, 1].set_yticks(range(int(df_V_h_bd2[variable_V_h].min()), int(df_V_h_bd2[variable_V_h].max()) + 1))
                    axes[i, 1].tick_params(axis='x', rotation=45)
                    axes[i, 1].grid(True, axis='y')

            # Boxplots para V.d
            if ruta_V_d_bd2:
                for i, variable_V_d in enumerate(Variables_V_d):
                    # Boxplot de la serie total (orientación vertical)
                    sns.boxplot(y=df_V_d_bd2[variable_V_d].dropna(), color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i+1, 0])
                    
                    axes[i+1, 0].set_title(f'{num_estacion} - {variable_V_d}- Total')
                    axes[i+1, 0].set_ylabel('Viento máximo (m/s)')
                    axes[i+1, 0].set_yticks(range(int(df_V_d_bd2[variable_V_d].min()), int(df_V_d_bd2[variable_V_d].max()) + 1))
                    axes[i+1, 0].tick_params(axis='y', rotation=0)
                    axes[i+1, 0].grid(True, axis='y')

                    # Boxplots mensuales
                    sns.boxplot(x=df_V_d_bd2['TIMESTAMP'].dt.month, y=df_V_d_bd2[variable_V_d], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i+1, 1])
                    
                    axes[i+1, 1].set_title(f'{num_estacion} - {variable_V_d}- Mensual')
                    axes[i+1, 1].set_xlabel('Mes')
                    axes[i+1, 1].set_ylabel('Viento máximo (m/s)')
                    axes[i+1, 1].set_xticks(range(0, 13))  # 13 meses
                    axes[i+1, 1].set_yticks(range(int(df_V_d_bd2[variable_V_d].min()), int(df_V_d_bd2[variable_V_d].max()) + 1))
                    axes[i+1, 1].tick_params(axis='x', rotation=45)
                    axes[i+1, 1].grid(True, axis='y')

            # Ajusta la disposición general y muestra el gráfico
            plt.tight_layout()
            plt.subplots_adjust(top=0.95)
            # Agrega un título a la figura
            fig.suptitle(f'Diagramas de cajas - Estación: {num_estacion}', fontsize=16)
            nombre_diag_caja_V = 'DC_V_Votal.png'
            plt.savefig(os.path.join(ruta_pruebas_b, 'DC_V_Votal.png'))
            plt.close()
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f'Se ha generado exitosamente el diagrama de cajas de la serie total para el viento como: {nombre_diag_caja_V}.')
            print('')
            return True
    else:
        print("No se encontraron archivos V.h.bd2 y/o V.d.bd2 en la ruta especificada.")
        return False

Diagrama_caja_Votal_V(['', ''])

#-----------------------------------------------------------------------------------------------------------------

def plot_time_series(df_V_h_bd2, df_V_d_bd2, var1, var2, title=f"Serie de tiempo - Estación: {num_estacion}", xlabel="Tiempo", ylabel="Viento (m/s)"):
    plt.figure(figsize=(60, 8), dpi=300)  # Adjusted figure size and DPI as per your requirement

    # Resample data to monthly frequency and calculate max and min
    df_V_h_bd2_monthly_max = df_V_h_bd2.resample('M', on='TIMESTAMP')[var1].max()
    df_V_d_bd2_monthly_max = df_V_d_bd2.resample('M', on='TIMESTAMP')[var2].max()

     # Reindex to ensure both series cover the same time range
    df_V_d_bd2_monthly_max = df_V_d_bd2_monthly_max.reindex(df_V_h_bd2_monthly_max.index)
    

    # Create a combined dataframe for seaborn
    combined_df = pd.DataFrame({
        'Date': df_V_h_bd2_monthly_max.index,
        f'Max {var1}': df_V_h_bd2_monthly_max.values,
        f'Max {var2}': df_V_d_bd2_monthly_max.values,
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
    plt.savefig(os.path.join(ruta_guardado, 'ST_Extremos_V.png'))
    plt.show()
    
    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print('Se ha generado exitosamente la serie de tiempo de los extremos mensuales de la serie total para el viento como: ST_Extremos_V.png.')
    print('')

# Example call to the function (adjust variables and dataframes as per your dataset)
plot_time_series(df_V_h_bd2, df_V_d_bd2, 'Wind-scalar.m_s.avg.1h.s1', 'Wind.m_s.max.dm.s1')

# Define una función para ajustar la mejor distribucion posible a las variables analizadas.

def Dist_prob_V_h_d():

    # Variables para verificar si se encontraron ambos archivos
    encontrado_V_h_bd2 = ruta_V_h_bd2 is not None
    encontrado_V_d_bd2 = ruta_V_d_bd2 is not None
    
    #Establece el nivel de ocnfianza
    niv_conf = 0.9995

    if encontrado_V_h_bd2 or encontrado_V_d_bd2:
        # Crea una figura con cuatro subfiguras en dos filas y dos columnas
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 15), dpi=300)

        # Procesa V.h.bd2 si está presente
        if encontrado_V_h_bd2:
            # Lee el archivo .csv y realiza operaciones de limpieza y corrección de timestamps para V.h.bd2
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df_V_h_bd2 = pd.read_csv(ruta_V_h_bd2, na_values=['NA'])
                           
            # Selecciona las columnas de interés para temperatura del aire y temperatura de rocío
            columnas_interes_V_h = ['Wind-scalar.m_s.avg.1h.s1', 'TIMESTAMP']

            # Filtra solo las columnas que contienen las variables del viento hoaria y 'TIMESTAMP'
            df_filtrado_V_h = df_V_h_bd2[columnas_interes_V_h].dropna()

            # Asigna las columnas a las variables de interés
            timestamps_V_h = df_filtrado_V_h['TIMESTAMP']

            # Selecciona las columnas de interés para temperatura del aire y temperatura de rocío
            col_Vemp_V_h = df_filtrado_V_h['Wind-scalar.m_s.avg.1h.s1']

            # Inicializa el objeto distfit para el viento del aire
            dist_V_h = distfit()
            dist_V_h.fit_transform(col_Vemp_V_h, verbose=0)

            # Obtiene la mejor distribución y sus parámetros para el viento del aire
            Dist_Ajust_V_h = dist_V_h.model['name']
            Dist_Ajust_Param_V_h = dist_V_h.model['params']
            Dist_Ajust_Stats_V_h = getattr(stats, Dist_Ajust_V_h)
            Dist_Ajust_rvs_V_h =Dist_Ajust_Stats_V_h.rvs(*Dist_Ajust_Param_V_h, size=len(col_Vemp_V_h))
            Ajusta_datos_V_h = Dist_Ajust_rvs_V_h

            # Calcula los intervalos de confianza para la mejor distribución del viento del aire
            lim_inf_V_h, lim_sup_V_h =Dist_Ajust_Stats_V_h.interval(niv_conf, *Dist_Ajust_Param_V_h)
            
            #Calculo de parametros estadisticos.
            μ_V_h = col_Vemp_V_h.mean()
            std_dev_V_h = col_Vemp_V_h.std()
            Asimetría_V_h = skew(col_Vemp_V_h)
            kurtosis_V_h = kurtosis(col_Vemp_V_h)

            # Grafica la distribución ajustada junto con el histograma de los datos originales para el viento del aire
            sns.histplot(col_Vemp_V_h, kde=True, color='blue', label=f'Datos originales\nKurtosis = {kurtosis_V_h:.2f} - Asimetría = {Asimetría_V_h:.2f}\nMedia aritmética: = {μ_V_h:.2f}°C\nDesviación estándar = {std_dev_V_h:.2f}°C', ax=ax1)
            sns.histplot(Ajusta_datos_V_h, kde=True, color='red', label=f'Distribución ajustada ({Dist_Ajust_V_h})\nIC: ({lim_inf_V_h:.2f} °C - {lim_sup_V_h:.2f} °C) - NC: {niv_conf*100:.2f}%', ax=ax1)

            # Ajusta los límites del eje X para mostrar cada unidad
            ax1.set_xticks(np.arange(int(col_Vemp_V_h.min()), int(col_Vemp_V_h.max()) + 1, 1))
            ax1.set_xticklabels(ax1.get_xticks(), rotation='vertical')

            # Ajusta los límites del eje X para mostrar una unidad de
            ax1.grid(True, linestyle='--', alpha=0.7, color='black')

            ax1.set_title(f'{num_estacion} - {columnas_interes_V_h[0]}')
            ax1.set_xlabel('Viento escalar (m/s)')
            ax1.set_ylabel('Frecuencia')
            ax1.legend()
            
        # Procesa V.d.bd2 si está presente
        if encontrado_V_d_bd2:
            # Lee el archivo .csv y realiza operaciones de limpieza y corrección de timestamps para V.d.bd2
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df_V_d_bd2 = pd.read_csv(ruta_V_d_bd2, na_values=['NA'])
                
            # Selecciona las columnas de interés para temperatura del aire y temperatura de rocío
            columnas_interes_V_d = ['Wind.m_s.max.dm.s1', 'TIMESTAMP']

            # Filtra solo las filas que contienen ambos 'Temp.degC.avg.1h.s1' y 'TIMESTAMP'
            df_filtrado_V_d = df_V_d_bd2[columnas_interes_V_d].dropna()

            # Asigna las columnas a las variables de interés
            timestamps_V_d = df_filtrado_V_d['TIMESTAMP']

            # Selecciona las columnas de interés para temperatura del aire y temperatura de rocío
            col_Vmax_V_d = df_filtrado_V_d['Wind.m_s.max.dm.s1']

            # Inicializa el objeto distfit para V.d.bd2 - Temp. Máxima
            dist_Vmax_d = distfit()
            dist_Vmax_d.fit_transform(col_Vmax_V_d, verbose=0)

            # Obtiene la mejor distribución y sus parámetros para V.d.bd2 - Temp. Máxima
            Dist_Ajust_Vmax_d = dist_Vmax_d.model['name']
            Dist_Ajust_Param_Vmax_d = dist_Vmax_d.model['params']
            Dist_Ajust_Stats_Vmax_d = getattr(stats, Dist_Ajust_Vmax_d)
            Dist_Ajust_rvs_Vmax_d =Dist_Ajust_Stats_Vmax_d.rvs(*Dist_Ajust_Param_Vmax_d, size=len(col_Vmax_V_d))
            Ajusta_datos_Vmax_d = Dist_Ajust_rvs_Vmax_d

            # Calcula los intervalos de confianza para la mejor distribución de V.d.bd2 - Temp. Máxima
            lim_inf_Vmax_d, lim_sup_Vmax_d =Dist_Ajust_Stats_Vmax_d.interval(niv_conf, *Dist_Ajust_Param_Vmax_d)

            μ_Vmax_d= col_Vmax_V_d.mean()
            std_dev_Vmax_d = col_Vmax_V_d.std()
            Asimetría_Vmax_d = skew(col_Vmax_V_d)
            kurtosis_Vmax_d = kurtosis(col_Vmax_V_d)

            # Grafica la distribución ajustada junto con el histograma de los datos originales para V.d.bd2 - Temp. Máxima
            sns.histplot(col_Vmax_V_d, kde=True, color='blue', label=f'Datos originales\nKurtosis = {kurtosis_Vmax_d:.2f} - Asimetría = {Asimetría_Vmax_d:.2f}\nMedia aritmética = {μ_Vmax_d:.2f}°C\nDesviación estándar = {std_dev_Vmax_d:.2f}°C', ax=ax2)
            sns.histplot(Ajusta_datos_Vmax_d, kde=True, color='red', label=f'Distribución ajustada ({Dist_Ajust_Vmax_d})\nIC: ({lim_inf_Vmax_d:.2f} °C - {lim_sup_Vmax_d:.2f} °C) - NC: {niv_conf*100:.2f}%', ax=ax2)

            # Ajusta los límites del eje X para mostrar cada unidad
            ax2.set_xticks(np.arange(int(col_Vmax_V_d.min()), int(col_Vmax_V_d.max()) + 1, 1))
            ax2.set_xticklabels(ax2.get_xticks(), rotation='vertical')

            # Ajusta los límites del eje X para mostrar una unidad de
            ax2.grid(True, linestyle='--', alpha=0.7, color='black')

            ax2.set_title(f'{num_estacion} - {columnas_interes_V_d[0]}')
            ax2.set_xlabel('Viento máximo (m/s)')
            ax2.set_ylabel('Frecuencia')
            ax2.legend()

        # Ajusta la disposición de las subfiguras
        plt.tight_layout()
        
        # Agrega un título a la imagen general con ajuste de posición vertical
        plt.suptitle(f'Distribuciones del viento - Estación: {num_estacion}', fontsize=16, y=0.95)
        
        # Ajusta la posición de la figura para dejar espacio para el título
        plt.subplots_adjust(top=0.9, bottom=0.1)

        # Guarda la imagen con ambas subfiguras
        plt.savefig(os.path.join(ruta_pruebas_b, 'H_V_Votal.png'))
        plt.show()
        
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print('Se ha generado exitosamente el histograma de la serie total para el viento como: H_V_Votal.png.')

Dist_prob_V_h_d()

#-----------------------------------------------------------------------------------------------------------------
#Funcion para generar boxplots mensuales de todas las variables.

def Diagrama_caja_mensual_V(unidades):
    
    # Leer archivos .csv y realizar operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        df_V_h_bd2 = None
        df_V_d_bd2 = None

        if ruta_V_h_bd2:
            df_V_h_bd2 = pd.read_csv(ruta_V_h_bd2, na_values=['NA'])
            df_V_h_bd2['TIMESTAMP'] = pd.to_datetime(df_V_h_bd2['TIMESTAMP']) 

        if ruta_V_d_bd2:
            df_V_d_bd2 = pd.read_csv(ruta_V_d_bd2, na_values=['NA'])
            df_V_d_bd2['TIMESTAMP'] = pd.to_datetime(df_V_d_bd2['TIMESTAMP'])
            
    # Lista de nombres de los meses en español
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    # Iterar a través de cada mes
    for month in range(1, 13):
        # Nombre del mes en español
        nombre_mes_carpeta = f"{month:02d}.{meses[month - 1]}"
        nombre_mes = meses[month - 1]
        ruta_meses = os.path.join(ruta_pruebas_b, nombre_mes_carpeta)
        os.makedirs(ruta_meses, exist_ok=True)

        # Genera una figura con 2 subtramas (2 filas, 1 columnas)
        fig, axes = plt.subplots(2, 1, figsize=(10, 20), dpi=300)

        # Diagramas de caja para V.h si df_V_h_bd2 no es None
        if df_V_h_bd2 is not None:
            for i, variable_V_h in enumerate(Variables_V_h):
                data = df_V_h_bd2[variable_V_h][df_V_h_bd2['TIMESTAMP'].dt.month == month].dropna()
                
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
                
                # Agregar información estadística en la esquina superior derecha de cada subplot
                axes[i].text(0.95, 0.95, f'Media aritmética = {Media_aritmética_V_h:.2f}{unidad}\nDesviación estándar = {Desviación_estándar_V_h:.2f}{unidad}\nLím.Tec. superior = {lim_sup_V_h:.2f}{unidad}\nBigote superior = {BS_V_h:.2f}{unidad}',
                                      transform=axes[i].transAxes,
                                      fontsize=8, verticalalignment='top', horizontalalignment='right', backgroundcolor='white')

        # Diagramas de caja para V.d si df_V_d_bd2 no es None
        if df_V_d_bd2 is not None:
            for i, variable_V_d in enumerate(Variables_V_d):
                data = df_V_d_bd2[variable_V_d][df_V_d_bd2['TIMESTAMP'].dt.month == month].dropna()
                
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

                # Agregar información estadística en la esquina superior derecha de cada subplot
                axes[i+1].text(0.95, 0.95, f'Media aritmética = {Media_aritmética_V_d:.2f}{unidad}\nDesviación estándar = {Desviación_estándar_V_d:.2f}{unidad}\nLím.Tec.superior = {lim_sup_V_d:.2f}{unidad}\nLím.Tec. inferior = {lim_inf_V_d:.2f}{unidad}\nBigote superior = {BS_V_d:.2f}{unidad}\nBigote inferior = {BI_V_d:.2f}{unidad}',
                                             transform=axes[i+1].transAxes,
                                             fontsize=8, verticalalignment='top', horizontalalignment='right', backgroundcolor='white')
    # Ajustar el diseño
        plt.tight_layout()

    # Guardar el gráfico
        plt.savefig(os.path.join(ruta_meses, f'{nombre_mes}_DC.png'))
        plt.close()

    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print('Se han generado exitosamente los diagramas de cajas mensuales para el viento.')
    print('')
    return True if (df_V_h_bd2 is not None or df_V_d_bd2 is not None) else False

Diagrama_caja_mensual_V("")

#-----------------------------------------------------------------------------------------------------------------

# Inicializar el DataFrame fuera del bucle para acumular datos de todos los meses
valores_fuera_Votal = pd.DataFrame(columns=['TIMESTAMP', 'Valor_Original', 'Limite', 'Elemento'])

# Iterar sobre cada mes en tus datos
# Iterar sobre cada mes en tus datos
def rubextremes_V_h(df_V_h_bd2, Variables_V_h, nombres_meses, ruta_guardado):
    for mes in range(1, 13):
        # Filtrar datos por mes si df_V_h_bd2 está definido
        if 'df_V_h_bd2' in locals():
            df_mes = df_V_h_bd2[df_V_h_bd2['TIMESTAMP'].dt.month == mes]

            # Inicializar el DataFrame para cada mes
            valores_fuera_mes = pd.DataFrame(columns=['Elemento','TIMESTAMP', 'Valor_Original', 'Valor_reemplazo', 'Limite', 'Procedimiento_adoptado','Comentario'])

            # Iterar sobre cada variable en Variables_V_h
            for variable in Variables_V_h:
                # Calcular Media_aritmética_V_h  y desviación estándar si hay datos
                if not df_mes.empty:
                    Media_aritmética_V_h  = df_mes[variable].mean()
                    Desviación_estándar_V_h = df_mes[variable].std()
                    P25_V_h = df_mes[variable].quantile(0.25)
                    P50_V_h = df_mes[variable].quantile(0.50)  # Median
                    P75_V_h = df_mes[variable].quantile(0.75)
                    IQR_V_h = P75_V_h - P25_V_h
                    BI_V_h = P25_V_h - 1.5 * IQR_V_h
                    BS_V_h = P75_V_h + 1.5 * IQR_V_h
                    Min_V_h = df_mes[variable].min()
                    Max_V_h = df_mes[variable].max()
                    MinZ_V_h = (Min_V_h - Media_aritmética_V_h) / Desviación_estándar_V_h
                    MaxZ_V_h = (Max_V_h - Media_aritmética_V_h) / Desviación_estándar_V_h
                    lim_inf_V_h = np.fix(MinZ_V_h) * Desviación_estándar_V_h + Media_aritmética_V_h
                    lim_sup_V_h = np.fix(MaxZ_V_h) * Desviación_estándar_V_h + Media_aritmética_V_h

                    # Inicializar los DataFrames para valores menores y mayores
                    valores_mayores = pd.DataFrame(columns=['TIMESTAMP', variable, 'Limite'])

                    # Definir condiciones para valores mayores al límite superior
                    cond2_V_h = (lim_sup_V_h >= BS_V_h) or (MaxZ_V_h >= 3)
                    cond2b_V_h = Max_V_h > BS_V_h
                    if cond2_V_h:
                        # Check if the maximum value is greater than the upper whisker
                        valores_mayores = df_mes.loc[(df_mes[variable] > lim_sup_V_h), ['TIMESTAMP', variable]]
                        valores_mayores['Limite'] = f"Mayor_a_{lim_sup_V_h:.2f}"
                    elif cond2b_V_h:
                        # Register the maximum value
                        valores_mayores = df_mes.loc[df_mes[variable] == Max_V_h, ['TIMESTAMP', variable]]
                        valores_mayores['Limite'] = f"Mayor_a_{BS_V_h:.2f}"

                    # Concatenar los dos DataFrames de valores filtrados
                    valores_fuera = pd.concat([valores_mayores])

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
                nombre_archivo = f"{nombre_mes_espanol}_V_h.csv"

                # Save the DataFrame to a CSV file in the folder containing the Spanish month name
                for root, dirs, files in os.walk(ruta_guardado):
                    for dir in dirs:
                        if nombre_mes_espanol.lower() in dir.lower():
                            ruta_archivo_V = os.path.join(root, dir, nombre_archivo)

                            # Reorder columns to match the specified order
                            valores_fuera_mes = valores_fuera_mes[['Elemento','TIMESTAMP', 'Valor_Original', 'Valor_reemplazo', 'Limite', 'Procedimiento_adoptado','Comentario']]

                            # Cambiar el nombre de la columna 'TIMESTAMP' a 'Fecha'
                            valores_fuera_mes.rename(columns={'TIMESTAMP': 'Fecha'}, inplace=True)

                            valores_fuera_mes.to_csv(ruta_archivo_V, index=False)
                            break

    # Print statement placed outside the loop
    if 'df_V_h_bd2' in locals():
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Se han generado exitosamente las pruebas de valores atipicos mensuales extremos para el viento diario a partir de los archivos bd2.")
        print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se realizaron pruebas de valores atípicos mensuales extemos para el viento diario porque no se encontro el archivo diario tipo bd2.")
        print('')

rubextremes_V_h(df_V_h_bd2, Variables_V_h, nombres_meses, ruta_guardado)
    
# Iterar sobre cada mes en tus datos
def rubextremes_V_d(df_V_d_bd2, Variables_V_d, Variables_V_d_time, nombres_meses, ruta_guardado):
    for mes in range(1, 13):
        # Filtrar datos por mes si df_V_d_bd2 está definido
        if 'df_V_d_bd2' in locals():
            df_mes = df_V_d_bd2[df_V_d_bd2['TIMESTAMP'].dt.month == mes]

            # Inicializar el DataFrame para cada mes
            valores_fuera_mes = pd.DataFrame(columns=['Elemento','TIMESTAMP', 'Fecha_Especifica', 'Valor_Original', 'Valor_reemplazo', 'Limite', 'Procedimiento_adoptado','Comentario'])

            # Iterar sobre cada variable en Variables_V_d
            for variable, time_var in zip(Variables_V_d, Variables_V_d_time):
                # Calcular Media_aritmética_V_d  y desviación estándar si hay datos
                if not df_mes.empty:
                    Media_aritmética_V_d  = df_mes[variable].mean()
                    Desviación_estándar_V_d = df_mes[variable].std()
                    P25_V_d = df_mes[variable].quantile(0.25)
                    P50_V_d = df_mes[variable].quantile(0.50)  # Median
                    P75_V_d = df_mes[variable].quantile(0.75)
                    IQR_V_d = P75_V_d - P25_V_d
                    BI_V_d = P25_V_d - 1.5 * IQR_V_d
                    BS_V_d = P75_V_d + 1.5 * IQR_V_d
                    Min_V_d = df_mes[variable].min()
                    Max_V_d = df_mes[variable].max()
                    MinZ_V_d = (Min_V_d - Media_aritmética_V_d) / Desviación_estándar_V_d
                    MaxZ_V_d = (Max_V_d - Media_aritmética_V_d) / Desviación_estándar_V_d
                    lim_inf_V_d = np.fix(MinZ_V_d) * Desviación_estándar_V_d + Media_aritmética_V_d
                    lim_sup_V_d = np.fix(MaxZ_V_d) * Desviación_estándar_V_d + Media_aritmética_V_d

                    # Inicializar los DataFrames para valores menores y mayores
                    valores_menores = pd.DataFrame(columns=['TIMESTAMP', variable, 'Limite'])
                    valores_mayores = pd.DataFrame(columns=['TIMESTAMP', variable, 'Limite'])

                    # Definir condiciones para valores menores al límite inferior
                    cond1_V_d = (lim_inf_V_d <= BI_V_d) or (MinZ_V_d <= -3)
                    cond1b_V_d = Min_V_d < BI_V_d
                    if cond1_V_d:
                        # Check if the minimum value is less than the lower whisker
                        valores_menores = df_mes.loc[(df_mes[variable] < lim_inf_V_d), ['TIMESTAMP', variable]]
                        valores_menores['Limite'] = f"Menor_a_{lim_inf_V_d:.2f}"
                    elif cond1b_V_d:
                        # Register the minimum value
                        valores_menores = df_mes.loc[df_mes[variable] == Min_V_d, ['TIMESTAMP', variable]]
                        valores_menores['Limite'] = f"Menor_a_{BI_V_d:.2f}"

                    # Definir condiciones para valores mayores al límite superior
                    cond2_V_d = (lim_sup_V_d >= BS_V_d) or (MaxZ_V_d >= 3)
                    cond2b_V_d = Max_V_d > BS_V_d
                    if cond2_V_d:
                        # Check if the maximum value is greater than the upper whisker
                        valores_mayores = df_mes.loc[(df_mes[variable] > lim_sup_V_d), ['TIMESTAMP', variable]]
                        valores_mayores['Limite'] = f"Mayor_a_{lim_sup_V_d:.2f}"
                    elif cond2b_V_d:
                        # Register the maximum value
                        valores_mayores = df_mes.loc[df_mes[variable] == Max_V_d, ['TIMESTAMP', variable]]
                        valores_mayores['Limite'] = f"Mayor_a_{BS_V_d:.2f}"

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
                nombre_archivo = f"{nombre_mes_espanol}_V_d.csv"

                # Save the DataFrame to a CSV file in the folder containing the Spanish month name
                for root, dirs, files in os.walk(ruta_guardado):
                    for dir in dirs:
                        if nombre_mes_espanol.lower() in dir.lower():
                            ruta_archivo_V = os.path.join(root, dir, nombre_archivo)

                            # Reorder columns to match the specified order
                            valores_fuera_mes = valores_fuera_mes[['Elemento','TIMESTAMP', 'Fecha_Especifica', 'Valor_Original', 'Valor_reemplazo', 'Limite', 'Procedimiento_adoptado','Comentario']]

                            # Cambiar el nombre de la columna 'TIMESTAMP' a 'Fecha'
                            valores_fuera_mes.rename(columns={'TIMESTAMP': 'Fecha'}, inplace=True)

                            valores_fuera_mes.to_csv(ruta_archivo_V, index=False)
                            break

    # Print statement placed outside the loop
    if 'df_V_d_bd2' in locals():
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Se han generado exitosamente las pruebas de valores atipicos mensuales extremos para el viento diario a partir de los archivos bd2.")
        print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se realizaron pruebas de valores atípicos mensuales extemos para el viento diario porque no se encontro el archivo diario tipo bd2.")
        print('')

rubextremes_V_d(df_V_d_bd2, Variables_V_d, Variables_V_d_time, nombres_meses, ruta_guardado)


def genera_modif_Tec():
    # Nombres de las columnas
    nombres_columnas = ['Elemento', 'Fecha', 'Valor_Original', 'Valor_reemplazo', 'Procedimiento_adoptado', 'Comentario']

    # Crear DataFrames vacíos con las columnas especificadas
    df_Tec_h = pd.DataFrame(columns=nombres_columnas)
    df_Tec_d = pd.DataFrame(columns=nombres_columnas)

    # Guardar los DataFrames como archivos CSV vacíos
    ruta_archivo_V_Tec_h = os.path.join(ruta_analisis_V, 'Modif_Tec_V_h.csv')
    ruta_archivo_V_Tec_d = os.path.join(ruta_analisis_V, 'Modif_Tec_V_d.csv')

    df_Tec_h.to_csv(ruta_archivo_V_Tec_h, index=False)
    df_Tec_d.to_csv(ruta_archivo_V_Tec_d, index=False)

genera_modif_Tec()