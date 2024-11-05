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
import matplotlib.ticker as ticker
import matplotlib.dates as mdates

sns.set_style("whitegrid")
matplotlib.use('Agg')

# -------------------------------Rutas generales

# Eliminar UserWarnings de openpyxl
warnings.simplefilter('ignore', category=UserWarning)


datos_crudos = r'C:\\MeteoRBD.v1.0.0\\datos_rbd'

# Encuentra el archivo .xlsx en la datos_crudos que contiene 'Cuenca' y 'Estación' como columnas
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

# Establece la ruta para los archivos de lluvia según el número de estación obtenido del archivo Excel
ruta_analisis_Ll = f"C:\\MeteoRBD.v1.0.0\\revisión\\{num_estacion}-ema\\Precipitación"

# Crea las carpetas si no existen
for carpeta in ["", "Pruebas_estadisticas"]:
    ruta_pruebas_b = os.path.join(ruta_analisis_Ll, carpeta)
    os.makedirs(ruta_pruebas_b, exist_ok=True)
    
# Ruta donde se guardarán los archivos CSV
ruta_guardado = os.path.join(ruta_analisis_Ll, "Pruebas_estadisticas")
    
# Encuentra el archivo Ll.h.bd2.csv de lluvia en la ruta de la estación
ruta_Ll_h_bd2 = next((os.path.join(ruta_analisis_Ll, archivo) for archivo in os.listdir(ruta_analisis_Ll) if archivo.endswith(".csv") and 'Ll.h.bd2' in archivo), None)

# Encuentra el archivo Ll.d.bd2.csv de lluvia en la ruta de la estación
ruta_Ll_d_bd2 = next((os.path.join(ruta_analisis_Ll, archivo) for archivo in os.listdir(ruta_analisis_Ll) if archivo.endswith(".csv") and 'Ll.d.bd2' in archivo), None)
    
unidad = 'mm'

# Variables para Ll.h
Variables_Ll_h = ['Precip.mm.tot.1h.s1']
# Variables para Ll.d
Variables_Ll_d = ['Precip.mm.tot.dm.s1']

#-----------------------------------------------------------------------------------------------------------------
#Estadisticas chebyshev
if ruta_Ll_h_bd2 or ruta_Ll_d_bd2:
    # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if ruta_Ll_h_bd2:
            df_Ll_h_bd2 = pd.read_csv(ruta_Ll_h_bd2, na_values=['NA'])
            df_Ll_h_bd2['TIMESTAMP'] = pd.to_datetime(df_Ll_h_bd2['TIMESTAMP'])  # Convertir a tipo de dato de Fecha y hora

        if ruta_Ll_d_bd2:
            df_Ll_d_bd2 = pd.read_csv(ruta_Ll_d_bd2, na_values=['NA'])
            df_Ll_d_bd2['TIMESTAMP'] = pd.to_datetime(df_Ll_d_bd2['TIMESTAMP'])

#-----------------------------------------------------------------------------------------------------------------

# Definir los nombres de los meses en español
nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

def Estadisticos_Ll_h_d(ruta_pruebas_b, num_estacion):

    # Inicializar diccionarios para almacenar estadísticas de Ll_h y Ll_d
    estadisticos_Ll_h_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_Ll_h + Variables_Ll_d}

    # Iterar sobre cada mes en los datos de Ll_h y Ll_d
    for mes in range(1, 13):
        # Filtrar datos por mes para Ll_h y Ll_d
        df_mes_Ll_h = df_Ll_h_bd2[df_Ll_h_bd2['TIMESTAMP'].dt.month == mes]
        df_mes_Ll_d = df_Ll_d_bd2[df_Ll_d_bd2['TIMESTAMP'].dt.month == mes]

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
    with open(os.path.join(ruta_pruebas_b, "Estadisticos_Ll.txt"), "w") as file:
        for variable in Variables_Ll_h + Variables_Ll_d:
            file.write(f"\nEstación: {num_estacion} - Variable: {variable}\n")
            file.write("{:<12} {:<8} {:<8} {:<17} {:<17}\n".format("Mes", "Máximo", "Mínimo", "Media aritmética", "Desviación estándar"))
            for mes in range(1, 13):
                max_val, min_val, mean_val, std_val = estadisticos_Ll_h_d[variable][nombres_meses[mes - 1]]
                file.write("{:<12} {:<8.2f} {:<8.2f} {:<17.2f} {:<17.2f}\n".format(nombres_meses[mes - 1], max_val, min_val, mean_val, std_val))

# Llamada a la función
Estadisticos_Ll_h_d(ruta_pruebas_b, num_estacion)

#Genera diagramas de caja totales y mensuales para cada variable.
def Diagrama_caja_total_Ll(unidades):

    if ruta_Ll_h_bd2 or ruta_Ll_d_bd2:
        # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            if ruta_Ll_h_bd2:
                df_Ll_h_bd2 = pd.read_csv(ruta_Ll_h_bd2, na_values=['NA'])
                df_Ll_h_bd2['TIMESTAMP'] = pd.to_datetime(df_Ll_h_bd2['TIMESTAMP'])  # Convertir a tipo de dato de Fecha y hora

            if ruta_Ll_d_bd2:
                df_Ll_d_bd2 = pd.read_csv(ruta_Ll_d_bd2, na_values=['NA'])
                df_Ll_d_bd2['TIMESTAMP'] = pd.to_datetime(df_Ll_d_bd2['TIMESTAMP'])

            # Genera una figura con cuatro subtramas (3 filas, 2 columnas)
            fig, axes = plt.subplots(2, 2, figsize=(16, 25), dpi=300)
            
            # Boxplots para Ll.h
            if ruta_Ll_h_bd2:
                for i, variable_Ll_h in enumerate(Variables_Ll_h):
                    # Boxplot de la serie total (orientación vertical)
                    sns.boxplot(y=df_Ll_h_bd2[variable_Ll_h], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i, 0])
                    
                    axes[i, 0].set_title(f'{num_estacion} - {variable_Ll_h}- Total')
                    axes[i, 0].set_ylabel('Lluvia (mm)')
                    axes[i, 0].set_ylim(np.floor(df_Ll_h_bd2[variable_Ll_h].min()), np.ceil(df_Ll_h_bd2[variable_Ll_h].max()))
                    axes[i, 0].set_yticks(np.arange(np.floor(df_Ll_h_bd2[variable_Ll_h].min()), np.ceil(df_Ll_h_bd2[variable_Ll_h].max()), 5))
                    axes[i, 0].tick_params(axis='y', rotation=0)

                    # Boxplots mensuales
                    sns.boxplot(x=df_Ll_h_bd2['TIMESTAMP'].dt.month, y=df_Ll_h_bd2[variable_Ll_h], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i, 1])
                    
                    axes[i, 1].set_title(f'{num_estacion} - {variable_Ll_h}- Mensual')
                    axes[i, 1].set_xlabel('Mes')
                    axes[i, 1].set_ylabel('Lluvia (mm)')
                    axes[i, 1].set_xticks(range(0, 13))  # 13 meses
                    axes[i, 1].set_ylim(np.floor(df_Ll_h_bd2[variable_Ll_h].min()), np.ceil(df_Ll_h_bd2[variable_Ll_h].max()))
                    axes[i, 1].set_yticks(np.arange(np.floor(df_Ll_h_bd2[variable_Ll_h].min()), np.ceil(df_Ll_h_bd2[variable_Ll_h].max()), 5))
                    axes[i, 1].tick_params(axis='x', rotation=45)

            # Boxplots para Ll.d
            if ruta_Ll_d_bd2:
                for i, variable_Ll_d in enumerate(Variables_Ll_d):
                    # Boxplot de la serie total (orientación vertical)
                    sns.boxplot(y=df_Ll_d_bd2[variable_Ll_d], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i+1, 0])
                    
                    axes[i+1, 0].set_title(f'{num_estacion} - {variable_Ll_d}- Total')
                    axes[i+1, 0].set_ylabel('Lluvia (mm)')
                    axes[i+1, 0].set_ylim(np.floor(df_Ll_d_bd2[variable_Ll_d].min()), np.ceil(df_Ll_d_bd2[variable_Ll_d].max()))
                    axes[i+1, 0].set_yticks(np.arange(np.floor(df_Ll_d_bd2[variable_Ll_d].min()), np.ceil(df_Ll_d_bd2[variable_Ll_d].max()), 5))
                    axes[i+1, 0].tick_params(axis='y', rotation=0)

                    # Boxplots mensuales
                    sns.boxplot(x=df_Ll_d_bd2['TIMESTAMP'].dt.month, y=df_Ll_d_bd2[variable_Ll_d], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i+1, 1])
                    
                    axes[i+1, 1].set_title(f'{num_estacion} - {variable_Ll_d}- Mensual')
                    axes[i+1, 1].set_xlabel('Mes')
                    axes[i+1, 1].set_ylabel('Lluvia (mm)')
                    axes[i+1, 1].set_xticks(range(0, 13))  # 13 meses
                    axes[i+1, 1].set_ylim(np.floor(df_Ll_d_bd2[variable_Ll_d].min()), np.ceil(df_Ll_d_bd2[variable_Ll_d].max()))
                    axes[i+1, 1].set_yticks(np.arange(np.floor(df_Ll_d_bd2[variable_Ll_d].min()), np.ceil(df_Ll_d_bd2[variable_Ll_d].max()), 5))
                    axes[i+1, 1].tick_params(axis='x', rotation=45)

            # Ajusta la disposición general y muestra el gráfico
            plt.tight_layout()
            plt.subplots_adjust(top=0.95)
            # Agrega un título a la figura
            fig.suptitle(f'Diagramas de cajas - Estación: {num_estacion}', fontsize=16)
            nombre_diag_caja_Ll = 'DC_Ll_Total.png'
            plt.savefig(os.path.join(ruta_pruebas_b, 'DC_Ll_Total.png'))
            plt.close()
            print('-----------------------------------------------------------------------------------------------------------')
            print(f'Se ha generado exitosamente el diagrama de cajas de la serie total para la lluvia como: {nombre_diag_caja_Ll}.')
            print('')
            return True
    else:
        print("No se encontraron archivos Ll.h.bd2 y/o Ll.d.bd2 en la ruta especificada.")
        return False
    
#-----------------------------------------------------------------------------------------------------------------

def plot_time_series(df_Ll_h_bd2, df_Ll_d_bd2, var1, var2, title=None, xlabel="Tiempo", ylabel="Lluvia (mm)"):
    if title is None:
        title = f"Serie de tiempo - Estación: {num_estacion}"
    
    plt.figure(figsize=(60, 8), dpi=300)

    # Resample data to monthly frequency and calculate max
    df_Ll_h_bd2_monthly_max = df_Ll_h_bd2.resample('M', on='TIMESTAMP')[var1].max()
    df_Ll_d_bd2_monthly_max = df_Ll_d_bd2.resample('M', on='TIMESTAMP')[var2].max()
    
    # Reindex to the same date range
    date_range = pd.date_range(start=min(df_Ll_h_bd2_monthly_max.index.min(), df_Ll_d_bd2_monthly_max.index.min()), 
                               end=max(df_Ll_h_bd2_monthly_max.index.max(), df_Ll_d_bd2_monthly_max.index.max()), 
                               freq='M')
    df_Ll_h_bd2_monthly_max = df_Ll_h_bd2_monthly_max.reindex(date_range)
    df_Ll_d_bd2_monthly_max = df_Ll_d_bd2_monthly_max.reindex(date_range)
    
    # Create a combined dataframe for seaborn
    combined_df = pd.DataFrame({
        'Date': date_range,
        f'Max {var1}': df_Ll_h_bd2_monthly_max.values,
        f'Max {var2}': df_Ll_d_bd2_monthly_max.values,
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
    plt.savefig(os.path.join(ruta_guardado, 'ST_Extremos_Ll.png'))
    plt.show()
    
    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print('Se ha generado exitosamente la serie de tiempo de los extremos mensuales de la serie total para la lluvia como: ST_Extremos_Ll.png.')
    print('')

# Define una función para ajustar la mejor distribucion posible a las variables analizadas.

def Dist_prob_Ll_h_d():

    # Variables para verificar si se encontraron ambos archivos
    encontrado_Ll_h_bd2 = ruta_Ll_h_bd2 is not None
    encontrado_Ll_d_bd2 = ruta_Ll_d_bd2 is not None
    
    #Establece el nivel de ocnfianza
    niv_conf = 0.9995

    if encontrado_Ll_h_bd2 or encontrado_Ll_d_bd2:
        # Crea una figura con cuatro subfiguras en dos filas y 1 columnas
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 15), dpi=300)

        # Procesa Ll.h.bd2 si está presente
        if encontrado_Ll_h_bd2:
            # Lee el archivo .csv y realiza operaciones de limpieza y corrección de timestamps para Ll.h.bd2
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df_Ll_h_bd2 = pd.read_csv(ruta_Ll_h_bd2, na_values=['NA'])
                           
            # Selecciona las columnas de interés para lluvia del aire y lluvia de rocío
            columnas_interes_Ll_h = ['Precip.mm.tot.1h.s1', 'TIMESTAMP']

            # Filtra solo las columnas que contienen las variables de lluvia hoaria y 'TIMESTAMP'
            df_filtrado_Ll_h = df_Ll_h_bd2[columnas_interes_Ll_h].dropna()

            # Asigna las columnas a las variables de interés
            timestamps_Ll_h = df_filtrado_Ll_h['TIMESTAMP']

            # Selecciona las columnas de interés para lluvia del aire y lluvia de rocío
            col_Ll_h = df_filtrado_Ll_h['Precip.mm.tot.1h.s1']
            # Inicializa el objeto distfit para la lluvia del aire
            disLl_Ll_h = distfit()
            disLl_Ll_h.fit_transform(col_Ll_h, verbose=0)

            # Obtiene la mejor distribución y sus parámetros para la lluvia del aire
            Dist_AjusLl_Ll_h = disLl_Ll_h.model['name']
            Dist_Ajust_Param_Ll_h = disLl_Ll_h.model['params']
            Dist_Ajust_Stats_Ll_h = getattr(stats, Dist_AjusLl_Ll_h)
            Dist_Ajust_rvs_Ll_h = Dist_Ajust_Stats_Ll_h.rvs(*Dist_Ajust_Param_Ll_h, size=len(col_Ll_h))
            Ajusta_datos_Ll_h = Dist_Ajust_rvs_Ll_h

            # Calcula los intervalos de confianza para la mejor distribución de la lluvia del aire
            lim_inf_Ll_h, lim_sup_Ll_h =Dist_Ajust_Stats_Ll_h.interval(niv_conf, *Dist_Ajust_Param_Ll_h)
            
            #Calculo de parametros estadisticos.
            μ_Ll_h = col_Ll_h.mean()
            std_dev_Ll_h = col_Ll_h.std()
            Asimetría_Ll_h = skew(col_Ll_h)
            kurtosis_Ll_h = kurtosis(col_Ll_h)
            
            #ax1 = ax1

            # Grafica la distribución ajustada junto con el histograma de los datos originales para la lluvia del aire
            sns.histplot(col_Ll_h, kde=True, color='blue', label=f'Datos originales\nKurtosis = {kurtosis_Ll_h:.2f} - Asimetría = {Asimetría_Ll_h:.2f}\nMedia aritmética: = {μ_Ll_h:.2f}%\nDesviación estándar = {std_dev_Ll_h:.2f}%', ax=ax1)
            sns.histplot(Ajusta_datos_Ll_h, kde=True, color='red', label=f'Distribución ajustada ({Dist_AjusLl_Ll_h})\nIC: ({lim_inf_Ll_h:.2f} % - {lim_sup_Ll_h:.2f} %) - NC: {niv_conf*100:.2f}%', ax=ax1)
            
            # Ajusta los límites del eje X para mostrar cada unidad
            
            ax1.set_xticks(np.arange(int(col_Ll_h.min()), int(col_Ll_h.max()) + 1, 5))
            ax1.set_xticklabels(ax1.get_xticks(), rotation='horizontal')

            # Ajusta los límites del eje X para mostrar una unidad de
            ax1.grid(True, linestyle='--', alpha=0.7, color='black')

            ax1.set_title(f'{num_estacion} - {columnas_interes_Ll_h[0]}')
            ax1.set_xlabel('Lluvia (mm)')
            ax1.set_ylabel('Frecuencia')
            ax1.legend()
            
        # Procesa Ll.d.bd2 si está presente
        if encontrado_Ll_d_bd2:
            # Lee el archivo .csv y realiza operaciones de limpieza y corrección de timestamps para Ll.d.bd2
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df_Ll_d_bd2 = pd.read_csv(ruta_Ll_d_bd2, na_values=['NA'])

            # Selecciona las columnas de interés para lluvia del aire y lluvia de rocío
            columnas_interes_Ll_d = ['Precip.mm.tot.dm.s1', 'TIMESTAMP']

            # Filtra solo las filas que contienen ambos 'Temp.degC.avg.1h.s1' y 'TIMESTAMP'
            df_filtrado_Ll_d = df_Ll_d_bd2[columnas_interes_Ll_d].dropna()

            # Asigna las columnas a las variables de interés
            timestamps_Ll_d = df_filtrado_Ll_d['TIMESTAMP']

            # Selecciona las columnas de interés para lluvia del aire y lluvia de rocío
            col_Ll_d = df_filtrado_Ll_d['Precip.mm.tot.dm.s1']

            # Inicializa el objeto distfit para Ll.d.bd2 - Temp. Máxima
            disLl_Llmax_d = distfit()
            disLl_Llmax_d.fit_transform(col_Ll_d, verbose=0)

            # Obtiene la mejor distribución y sus parámetros para Ll.d.bd2 - Temp. Máxima
            Dist_AjusLl_Llmax_d = disLl_Llmax_d.model['name']
            Dist_Ajust_Param_Llmax_d = disLl_Llmax_d.model['params']
            Dist_Ajust_Stats_Llmax_d = getattr(stats, Dist_AjusLl_Llmax_d)
            Dist_Ajust_rvs_Llmax_d =Dist_Ajust_Stats_Llmax_d.rvs(*Dist_Ajust_Param_Llmax_d, size=len(col_Ll_d))
            Ajusta_datos_Llmax_d = Dist_Ajust_rvs_Llmax_d

            # Calcula los intervalos de confianza para la mejor distribución de Ll.d.bd2 - Temp. Máxima
            lim_inf_Llmax_d, lim_sup_Llmax_d =Dist_Ajust_Stats_Llmax_d.interval(niv_conf, *Dist_Ajust_Param_Llmax_d)
           
            μ_Llmax_d = col_Ll_d.mean()
            std_dev_Llmax_d = col_Ll_d.std()
            Asimetría_Llmax_d = skew(col_Ll_d)
            kurtosis_Llmax_d = kurtosis(col_Ll_d)
            
            # Grafica la distribución ajustada junto con el histograma de los datos originales para Ll.d.bd2 - Temp. Máxima
            sns.histplot(col_Ll_d, kde=True, color='blue', label=f'Datos originales\nKurtosis = {kurtosis_Llmax_d:.2f} - Asimetría = {Asimetría_Llmax_d:.2f}\nMedia aritmética = {μ_Llmax_d:.2f}%\nDesviación estándar = {std_dev_Llmax_d:.2f}%', ax=ax2)
            sns.histplot(Ajusta_datos_Llmax_d, kde=True, color='red', label=f'Distribución ajustada ({Dist_AjusLl_Llmax_d})\nIC: ({lim_inf_Llmax_d:.2f} % - {lim_sup_Llmax_d:.2f} %) - NC: {niv_conf*100:.2f}%', ax=ax2)
            
            # Ajusta los límites del eje X para mostrar cada unidad
            ax2.set_xticks(np.arange(int(col_Ll_d.min()), int(col_Ll_d.max()) + 1, 5))
            ax2.set_xticklabels(ax2.get_xticks(), rotation='horizontal')

            # Ajusta los límites del eje X para mostrar una unidad de
            ax2.grid(True, linestyle='--', alpha=0.7, color='black')

            ax2.set_title(f'{num_estacion} - {columnas_interes_Ll_d[0]}')
            ax2.set_xlabel('Lluvia total (mm)')
            ax2.set_ylabel('Frecuencia')
            ax2.legend()
            
        # Ajusta la disposición de las subfiguras
        plt.tight_layout()
        
        # Agrega un título a la imagen general con ajuste de posición vertical
        plt.suptitle(f'Distribuciones de lluvia - Estación: {num_estacion}', fontsize=16, y=0.95)
        
        # Ajusta la posición de la figura para dejar espacio para el título
        plt.subplots_adjust(top=0.9, bottom=0.1)

        # Guarda la imagen con ambas subfiguras
        plt.savefig(os.path.join(ruta_pruebas_b, 'H_Ll_Total.png'))
        plt.show()
        
        print('-----------------------------------------------------------------------------------------------------------')
        print('Se ha generado exitosamente el histograma de la serie total para la lluvia como: H_Ll_Total.png.')
        
#-----------------------------------------------------------------------------------------------------------------
#Funcion para generar boxplots mensuales de todas las variables.

def Diagrama_caja_mensual_T(unidades):
    
    # Leer archivos .csv y realizar operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        df_Ll_h_bd2 = None
        df_Ll_d_bd2 = None

        if ruta_Ll_h_bd2:
            df_Ll_h_bd2 = pd.read_csv(ruta_Ll_h_bd2, na_values=['NA'])
            df_Ll_h_bd2['TIMESTAMP'] = pd.to_datetime(df_Ll_h_bd2['TIMESTAMP']) 

        if ruta_Ll_d_bd2:
            df_Ll_d_bd2 = pd.read_csv(ruta_Ll_d_bd2, na_values=['NA'])
            df_Ll_d_bd2['TIMESTAMP'] = pd.to_datetime(df_Ll_d_bd2['TIMESTAMP'])

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

        # Diagramas de caja para Ll.h si df_Ll_h_bd2 no es None
        if df_Ll_h_bd2 is not None:
            for i, variable_Ll_h in enumerate(Variables_Ll_h):
                data = df_Ll_h_bd2[variable_Ll_h][df_Ll_h_bd2['TIMESTAMP'].dt.month == month]
                
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

        # Diagramas de caja para Ll.d si df_Ll_d_bd2 no es None
        if df_Ll_d_bd2 is not None:
            for i, variable_Ll_d in enumerate(Variables_Ll_d):
                data = df_Ll_d_bd2[variable_Ll_d][df_Ll_d_bd2['TIMESTAMP'].dt.month == month]
                
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
        plt.savefig(os.path.join(ruta_meses, f'DC_Ll_{nombre_mes}.png'))
        plt.close()

    print('-----------------------------------------------------------------------------------------------------------')
    print('Se han generado exitosamente los diagramas de cajas mensuales para la lluvia.')
    print('')
    return True if (df_Ll_h_bd2 is not None or df_Ll_d_bd2 is not None) else False

#-----------------------------------------------------------------------------------------------------------------
#Llama funciones:

Diagrama_caja_total_Ll(['%', '%'])

# Example call to the function (adjust variables and dataframes as per your dataset)
plot_time_series(df_Ll_h_bd2, df_Ll_d_bd2, 'Precip.mm.tot.1h.s1', 'Precip.mm.tot.dm.s1')

Dist_prob_Ll_h_d()

Diagrama_caja_mensual_T("")

#-----------------------------------------------------------------------------------------------------------------
# Definir los nombres de los meses en español
nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

# Inicializar el DataFrame fuera del bucle para acumular datos de todos los meses
valores_fuera_total = pd.DataFrame(columns=['TIMESTAMP', 'Valor_Original', 'Limite', 'Elemento'])

# Iterar sobre cada mes en tus datos
def rubextremes_Ll_h(df_Ll_h_bd2, Variables_Ll_h, nombres_meses, ruta_guardado):
    for mes in range(1, 13):
        # Filtrar datos por mes si df_Ll_h_bd2 está definido
        if 'df_Ll_h_bd2' in locals():
            df_mes = df_Ll_h_bd2[df_Ll_h_bd2['TIMESTAMP'].dt.month == mes]

            # Inicializar el DataFrame para cada mes
            valores_fuera_mes = pd.DataFrame(columns=['Elemento','TIMESTAMP', 'Valor_Original', 'Valor_reemplazo', 'Limite', 'Procedimiento_adoptado','Comentario'])

            # Iterar sobre cada variable en Variables_Ll_h
            for variable in Variables_Ll_h:
                # Calcular Media_aritmética_Ll_h  y desviación estándar si hay datos
                if not df_mes.empty:
                    Media_aritmética_Ll_h = df_mes[variable].mean()
                    Desviación_estándar_Ll_h = df_mes[variable].std()
                    P25_Ll_h = df_mes[variable].quantile(0.25)
                    P50_Ll_h = df_mes[variable].quantile(0.50)  # Median
                    P75_Ll_h = df_mes[variable].quantile(0.75)
                    IQR_Ll_h = P75_Ll_h - P25_Ll_h
                    BI_Ll_h = P25_Ll_h - 1.5 * IQR_Ll_h
                    BS_Ll_h = P75_Ll_h + 1.5 * IQR_Ll_h
                    Min_Ll_h = df_mes[variable].min()
                    Max_Ll_h = df_mes[variable].max()
                    MinZ_Ll_h = (Min_Ll_h - Media_aritmética_Ll_h) / Desviación_estándar_Ll_h
                    MaxZ_Ll_h = (Max_Ll_h - Media_aritmética_Ll_h) / Desviación_estándar_Ll_h
                    lim_inf_Ll_h = np.fix(MinZ_Ll_h)*Desviación_estándar_Ll_h + Media_aritmética_Ll_h
                    lim_sup_Ll_h = np.fix(MaxZ_Ll_h)*Desviación_estándar_Ll_h + Media_aritmética_Ll_h

                    # Inicializar los DataFrames para valores menores y mayores
                    valores_mayores = pd.DataFrame(columns=['TIMESTAMP', variable, 'Limite'])

                    # Definir condiciones para valores mayores al límite superior
                    cond2_Ll_h = (lim_sup_Ll_h >= BS_Ll_h) or (MaxZ_Ll_h >= 3)
                    cond2b_Ll_h = Max_Ll_h > BS_Ll_h

                    # Filtrar y etiquetar valores mayores al límite superior
                    if cond2_Ll_h:
                        # Check if the maximum value is greater than the upper whisker
                        valores_mayores = df_mes.loc[(df_mes[variable] > lim_sup_Ll_h), ['TIMESTAMP', variable]]
                        valores_mayores['Limite'] = f"Mayor_a_{lim_sup_Ll_h:.2f}"
                    elif cond2b_Ll_h:
                        # Register the maximum value
                        valores_mayores = df_mes.loc[df_mes[variable] == Max_Ll_h, ['TIMESTAMP', variable]]
                        valores_mayores['Limite'] = f"Mayor_a_{BS_Ll_h:.2f}"

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
                        if not valores_fuera.empty:
                           if valores_fuera_mes.empty:
                               valores_fuera_mes = valores_fuera
                           else:
                               valores_fuera_mes = pd.concat([valores_fuera_mes, valores_fuera])

            if not valores_fuera_mes.empty:
                # Obtener el nombre del mes en español
                nombre_mes_espanol = nombres_meses[mes - 1]

                # Nombre del archivo CSV con el nombre del mes en español
                nombre_archivo = f"{nombre_mes_espanol}_Ll_h.csv"

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
    if 'df_Ll_h_bd2' in locals():
        print('-----------------------------------------------------------------------------------------------------------')
        print("Se han generado exitosamente las pruebas de valores atipicos mensuales extremos para la lluvia horaria a partir de los archivos bd2.")
        print('')
    else:
        print('-----------------------------------------------------------------------------------------------------------')
        print("No se realizaron pruebas de valores atípicos mensuales extemos para la lluvia horaria porque no se encontro el archivo horario tipo bd2.")
        print('')


rubextremes_Ll_h(df_Ll_h_bd2, Variables_Ll_h, nombres_meses, ruta_guardado)
    
# Iterar sobre cada mes en tus datos
def rubextremes_Ll_d(df_Ll_d_bd2, Variables_Ll_d, nombres_meses, ruta_guardado):
    for mes in range(1, 13):
        # Filtrar datos por mes si df_Ll_d_bd2 está definido
        if 'df_Ll_d_bd2' in locals():
            df_mes = df_Ll_d_bd2[df_Ll_d_bd2['TIMESTAMP'].dt.month == mes]

            # Inicializar el DataFrame para cada mes
            valores_fuera_mes = pd.DataFrame(columns=['Elemento','TIMESTAMP', 'Valor_Original', 'Valor_reemplazo', 'Limite', 'Procedimiento_adoptado','Comentario'])
            valores_mayores = pd.DataFrame()

            # Iterar sobre cada variable en Variables_Ll_d
            for variable in Variables_Ll_d:
                
                # Calcular Media_aritmética_Ll_d  y desviación estándar si hay datos
                if not df_mes.empty:
                    Media_aritmética_Ll_d  = df_mes[variable].mean()
                    Desviación_estándar_Ll_d = df_mes[variable].std()
                    P25_Ll_d = df_mes[variable].quantile(0.25)
                    P50_Ll_d = df_mes[variable].quantile(0.50)  # Median
                    P75_Ll_d = df_mes[variable].quantile(0.75)
                    IQR_Ll_d = P75_Ll_d - P25_Ll_d
                    BI_Ll_d = P25_Ll_d - 1.5 * IQR_Ll_d
                    BS_Ll_d = P75_Ll_d + 1.5 * IQR_Ll_d
                    Min_Ll_d = df_mes[variable].min()
                    Max_Ll_d = df_mes[variable].max()
                    MinZ_Ll_d = (Min_Ll_d - Media_aritmética_Ll_d) / Desviación_estándar_Ll_d
                    MaxZ_Ll_d = (Max_Ll_d - Media_aritmética_Ll_d) / Desviación_estándar_Ll_d
                    lim_inf_Ll_d = np.fix(MinZ_Ll_d)*Desviación_estándar_Ll_d + Media_aritmética_Ll_d
                    lim_sup_Ll_d = np.fix(MaxZ_Ll_d)*Desviación_estándar_Ll_d + Media_aritmética_Ll_d
                    
                    # Inicializar los DataFrames para valores menores y mayores
                    valores_mayores = pd.DataFrame(columns=['TIMESTAMP', variable, 'Limite'])

                    # Definir condiciones para valores mayores al límite superior
                    cond2_Ll_d = (lim_sup_Ll_d >= BS_Ll_d) or (MaxZ_Ll_d >= 3)
                    cond2b_Ll_d = Max_Ll_d > BS_Ll_d

                    # Filtrar y etiquetar valores mayores al límite superior
                    if cond2_Ll_d:
                        # Check if the maximum value is greater than the upper whisker
                        valores_mayores = df_mes.loc[(df_mes[variable] > lim_sup_Ll_d), ['TIMESTAMP', variable]]
                        valores_mayores['Limite'] = f"Mayor_a_{lim_sup_Ll_d:.2f}"
                    elif cond2b_Ll_d:
                        # Register the maximum value
                        valores_mayores = df_mes.loc[df_mes[variable] == Max_Ll_d, ['TIMESTAMP', variable]]
                        valores_mayores['Limite'] = f"Mayor_a_{BS_Ll_d:.2f}"

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
                        if not valores_fuera.empty:
                           if valores_fuera_mes.empty:
                               valores_fuera_mes = valores_fuera
                           else:
                               valores_fuera_mes = pd.concat([valores_fuera_mes, valores_fuera])

            if not valores_fuera_mes.empty:
                # Obtener el nombre del mes en español
                nombre_mes_espanol = nombres_meses[mes - 1]

                # Nombre del archivo CSV con el nombre del mes en español
                nombre_archivo = f"{nombre_mes_espanol}_Ll_d.csv"

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
    if 'df_Ll_d_bd2' in locals():
        print('-----------------------------------------------------------------------------------------------------------')
        print("Se han generado exitosamente las pruebas de valores atipicos mensuales extremos para la lluvia diaria a partir de los archivos bd2.")
        print('')
    else:
        print('-----------------------------------------------------------------------------------------------------------')
        print("No se realizaron pruebas de valores atípicos mensuales extemos para la lluvia diaria porque no se encontro el archivo diario tipo bd2.")
        print('')

rubextremes_Ll_d(df_Ll_d_bd2, Variables_Ll_d, nombres_meses, ruta_guardado)
    

def genera_modif_tec():
    # Nombres de las columnas
    nombres_columnas = ['Elemento', 'Fecha', 'Valor_Original', 'Valor_reemplazo', 'Procedimiento_adoptado', 'Comentario']

    # Crear DataFrames vacíos con las columnas especificadas
    df_tec_h = pd.DataFrame(columns=nombres_columnas)
    df_tec_d = pd.DataFrame(columns=nombres_columnas)

    # Guardar los DataFrames como archivos CSV vacíos
    ruta_archivo_tec_h = os.path.join(ruta_analisis_Ll, 'Modif_Tec_Ll_h.csv')
    ruta_archivo_tec_d = os.path.join(ruta_analisis_Ll, 'Modif_Tec_Ll_d.csv')

    df_tec_h.to_csv(ruta_archivo_tec_h, index=False)
    df_tec_d.to_csv(ruta_archivo_tec_d, index=False)

genera_modif_tec()