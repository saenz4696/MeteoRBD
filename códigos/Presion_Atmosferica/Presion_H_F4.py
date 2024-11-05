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
ruta_archivo = next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Presión" in file and file.endswith(".xlsx")), None)

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

# Establece la ruta para los archivos de presión atmosférica según el número de estación obtenido del archivo Excel
ruta_analisis_PA = f"C:\\MeteoRBD.v1.0.0\\revisión\\{num_estacion}-ema\\Presión Atmosférica"

# Crea las carpetas si no existen
for carpeta in ["", "Pruebas_estadisticas"]:
    ruta_pruebas_b = os.path.join(ruta_analisis_PA, carpeta)
    os.makedirs(ruta_pruebas_b, exist_ok=True)
    
# Ruta donde se guardarán los archivos CSV
ruta_guardado = os.path.join(ruta_analisis_PA, "Pruebas_estadisticas")
    
# Encuentra el archivo PA.h.bd2.csv de presión atmosférica en la ruta de la estación
ruta_PA_h_bd2 = next((os.path.join(ruta_analisis_PA, archivo) for archivo in os.listdir(ruta_analisis_PA) if archivo.endswith(".csv") and 'PA.h.bd2' in archivo), None)

unidad = 'mbar'

# Variables para PA.h
Variables_PA_h = ['Press.mbar.avg.1h.s1']

#-----------------------------------------------------------------------------------------------------------------
#Estadisticas chebyshev
if ruta_PA_h_bd2:
    # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if ruta_PA_h_bd2:
            df_PA_h_bd2 = pd.read_csv(ruta_PA_h_bd2, na_values=['NA'])
            df_PA_h_bd2['TIMESTAMP'] = pd.to_datetime(df_PA_h_bd2['TIMESTAMP'])  # Convertir a tipo de dato de fecha y hora

# Definir los nombres de los meses en español
nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

def Estadisticos_PA_h(ruta_pruebas_b, num_estacion):

    # Inicializar diccionarios para almacenar estadísticas de PA_h y PA_d
    Estadisticos_PA_h = {var: {mes: [] for mes in nombres_meses} for var in Variables_PA_h}

    # Iterar sobre cada mes en los datos de PA_h y PA_d
    for mes in range(1, 13):
        # Filtrar datos por mes para PA_h y PA_d
        df_mes_PA_h = df_PA_h_bd2[df_PA_h_bd2['TIMESTAMP'].dt.month == mes]

        # Iterar sobre cada variable en Variables_PA_h y Variables_PA_d
        for variable in Variables_PA_h:
            # Seleccionar el dataframe correspondiente
            df_mes = df_mes_PA_h 

            # Calcular estadísticas si hay valores que no son NaN
            if not df_mes[variable].empty:
                # Calcular máximo, mínimo, media y desviación estándar
                max_val = df_mes[variable].max()
                min_val = df_mes[variable].min()
                mean_val = df_mes[variable].mean()
                std_val = df_mes[variable].std()

                # Almacenar estadísticas en el diccionario
                Estadisticos_PA_h[variable][nombres_meses[mes - 1]] = [max_val, min_val, mean_val, std_val]

    # Guardar estadísticas para PA_h y PA_d en un archivo de texto
    with open(os.path.join(ruta_pruebas_b, "Estadisticos_PA_h.txt"), "w") as file:
        for variable in Variables_PA_h:
            file.write(f"\nEstación: {num_estacion} - Variable: {variable}\n")
            file.write("{:<12} {:<8} {:<8} {:<17} {:<17}\n".format("Mes", "Máximo", "Mínimo", "Media aritmética", "Desviación estándar"))
            for mes in range(1, 13):
                max_val, min_val, mean_val, std_val = Estadisticos_PA_h[variable][nombres_meses[mes - 1]]
                file.write("{:<12} {:<8.2f} {:<8.2f} {:<17.2f} {:<17.2f}\n".format(nombres_meses[mes - 1], max_val, min_val, mean_val, std_val))

# Llamada a la función
Estadisticos_PA_h(ruta_pruebas_b, num_estacion)

#-----------------------------------------------------------------------------------------------------------------

#Genera diagramas de caja totales y mensuales para cada variable.
def Diagrama_caja_total_PA(unidades):

    if ruta_PA_h_bd2:
        # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            if ruta_PA_h_bd2:
                df_PA_h_bd2 = pd.read_csv(ruta_PA_h_bd2, na_values=['NA'])
                df_PA_h_bd2['TIMESTAMP'] = pd.to_datetime(df_PA_h_bd2['TIMESTAMP'])  # Convertir a tipo de dato de fecha y hora

            # Genera una figura con cuatro subtramas (3 filas, 2 columnas)
            fig, axes = plt.subplots(1, 2, figsize=(16, 25), dpi=300)
            
            # Boxplots para PA.h
            if ruta_PA_h_bd2:
                for i, variable_PA_h in enumerate(Variables_PA_h):
                    # Boxplot de la serie total (orientación vertical)
                    sns.boxplot(y=df_PA_h_bd2[variable_PA_h], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[0])
                    
                    axes[0].set_title(f'{num_estacion} - {variable_PA_h}- Total')
                    axes[0].set_ylabel(f'{unidad}')
                    axes[0].set_ylim(np.floor(df_PA_h_bd2[variable_PA_h].min()), np.ceil(df_PA_h_bd2[variable_PA_h].max()))
                    axes[0].set_yticks(np.arange(np.floor(df_PA_h_bd2[variable_PA_h].min()), np.ceil(df_PA_h_bd2[variable_PA_h].max()), 1))
                    #axes[0].set_yticks(range(int(df_PA_h_bd2[variable_PA_h].min()), int(df_PA_h_bd2[variable_PA_h].max()) + 1))
                    axes[0].tick_params(axis='y', rotation=0)

                    # Boxplots mensuales
                    sns.boxplot(x=df_PA_h_bd2['TIMESTAMP'].dt.month, y=df_PA_h_bd2[variable_PA_h], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[1])
                    
                    axes[1].set_title(f'{num_estacion} - {variable_PA_h}- Mensual')
                    axes[1].set_xlabel('Mes')
                    axes[1].set_ylabel(f'{unidad}')
                    axes[1].set_xticks(range(0, 13))  # 13 meses
                    axes[1].set_ylim(np.floor(df_PA_h_bd2[variable_PA_h].min()), np.ceil(df_PA_h_bd2[variable_PA_h].max()))
                    axes[1].set_yticks(np.arange(np.floor(df_PA_h_bd2[variable_PA_h].min()), np.ceil(df_PA_h_bd2[variable_PA_h].max()), 1))
                    #axes[1].set_yticks(range(int(df_PA_h_bd2[variable_PA_h].min()), int(df_PA_h_bd2[variable_PA_h].max()) + 1))
                    axes[1].tick_params(axis='x', rotation=45)

            # Ajusta la disposición general y muestra el gráfico
            plt.tight_layout()
            plt.subplots_adjust(top=0.95)
            # Agrega un título a la figura
            fig.suptitle(f'Diagramas de cajas - Estación: {num_estacion}', fontsize=16)
            nombre_diag_caja_PA = 'DC_PA_Total.png'
            plt.savefig(os.path.join(ruta_pruebas_b, 'DC_PA_Total.png'))
            plt.close()
            print('-----------------------------------------------------------------------------------------------------------')
            print(f'Se ha generado exitosamente el diagrama de cajas de la serie total para la presión atmosférica como: {nombre_diag_caja_PA}.')
            print('')
            return True
    else:
        print("No se encontraron archivos PA.h.bd2 y/o PA.d.bd2 en la ruta especificada.")
        return False
    
#-----------------------------------------------------------------------------------------------------------------

def plot_time_series(df_PA_h_bd2, var1, title=f"Serie de tiempo - Estación: {num_estacion}", xlabel="Tiempo", ylabel= f"Presión Atmósferica ({unidad})"):
    
    plt.figure(figsize=(60, 8), dpi=300)  # Adjusted figure size and DPI as per your requirement

    # Resample data to monthly frequency and calculate max and min
    df_PA_h_bd2_monthly_max = df_PA_h_bd2.resample('M', on='TIMESTAMP')[var1].max()
    df_PA_h_bd2_monthly_min = df_PA_h_bd2.resample('M', on='TIMESTAMP')[var1].min()

    
    # Create a combined dataframe for seaborn
    combined_df = pd.DataFrame({
        'Date': df_PA_h_bd2_monthly_max.index,
        f'Max {var1}': df_PA_h_bd2_monthly_max.values,
        f'Min {var1}': df_PA_h_bd2_monthly_min.values,
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
        for y_value in range(int(y_limits[0]), int(y_limits[1])+2):
            plt.text(year_date, y_value, f'{y_value}', ha='center', va='bottom', color='gray', fontsize=10)

    plt.tight_layout()
    
    # Save the plot (assuming ruta_guardado is defined in your environment)
    plt.savefig(os.path.join(ruta_guardado, 'ST_Extremos_PA.png'))
    
    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print('Se ha generado exitosamente la serie de tiempo de los extremos mensuales de la serie total para la presión atmósferica como: ST_Extremos_PA.png.')
    print('')

# Define una función para ajustar la mejor distribucion posible a las variables analizadas.

def Dist_prob_PA_h():

    # Variables para verificar si se encontraron ambos archivos
    encontrado_PA_h_bd2 = ruta_PA_h_bd2 is not None

    #Establece el nivel de ocnfianza
    niv_conf = 0.9995

    if encontrado_PA_h_bd2:
        # Crea una figura 
        fig, ax = plt.subplots(1, 1, figsize=(15, 10), dpi=300)

        # Procesa PA.h.bd2 si está presente
        if encontrado_PA_h_bd2:
            # Lee el archivo .csv y realiza operaciones de limpieza y corrección de timestamps para PA.h.bd2
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df_PA_h_bd2 = pd.read_csv(ruta_PA_h_bd2, na_values=['NA'])
                           
            # Selecciona las columnas de interés para presión atmosférica del aire y presión atmosférica de rocío
            columnas_interes_PA_h = ['Press.mbar.avg.1h.s1', 'TIMESTAMP']

            # Filtra solo las columnas que contienen las variables de presión atmosférica hoaria y 'TIMESTAMP'
            df_filtrado_PA_h = df_PA_h_bd2[columnas_interes_PA_h].dropna()

            # Asigna las columnas a las variables de interés
            timestamps_PA_h = df_filtrado_PA_h['TIMESTAMP']

            # Selecciona las columnas de interés para presión atmosférica del aire y presión atmosférica de rocío
            col_PA_h = df_filtrado_PA_h['Press.mbar.avg.1h.s1']
            # Inicializa el objeto distfit para la presión atmosférica del aire
            dist_PA_h = distfit()
            dist_PA_h.fit_transform(col_PA_h, verbose=0)

            # Obtiene la mejor distribución y sus parámetros para la presión atmosférica del aire
            Dist_Ajust_PA_h = dist_PA_h.model['name']
            Dist_Ajust_Param_PA_h = dist_PA_h.model['params']
            Dist_Ajust_Stats_PA_h = getattr(stats, Dist_Ajust_PA_h)
            Dist_Ajust_rvs_PA_h = Dist_Ajust_Stats_PA_h.rvs(*Dist_Ajust_Param_PA_h, size=len(col_PA_h))
            Ajusta_datos_PA_h = Dist_Ajust_rvs_PA_h

            # Calcula los intervalos de confianza para la mejor distribución de la presión atmosférica del aire
            lim_inf_PA_h, lim_sup_PA_h =Dist_Ajust_Stats_PA_h.interval(niv_conf, *Dist_Ajust_Param_PA_h)
            
            
            #Calculo de parametros estadisticos.
            μ_PA_h = col_PA_h.mean()
            std_dev_PA_h = col_PA_h.std()
            Asimetría_PA_h = skew(col_PA_h)
            kurtosis_PA_h = kurtosis(col_PA_h)
            
            #ax1 = ax1

            # Grafica la distribución ajustada junto con el histograma de los datos originales para la presión atmosférica del aire
            sns.histplot(col_PA_h, kde=True, color='blue', label=f'Datos originales\nKurtosis = {kurtosis_PA_h:.2f} - Asimetría = {Asimetría_PA_h:.2f}\nMedia aritmética: = {μ_PA_h:.2f} mbar\nDesviación estándar = {std_dev_PA_h:.2f} mbar', ax=ax)
            sns.histplot(Ajusta_datos_PA_h, kde=True, color='red', label=f'Distribución ajustada ({Dist_Ajust_PA_h})\nIC: ({lim_inf_PA_h:.2f} mbar - {lim_sup_PA_h:.2f} mbar) - NC: {niv_conf*100:.2f} %', ax=ax)
            
            # Ajusta los límites del eje X para mostrar cada unidad
            ax.set_xticks(np.arange(int(col_PA_h.min()), int(col_PA_h.max()) + 1, 1))
            ax.set_xticklabels(ax.get_xticks(), rotation='vertical')

            # Ajusta los límites del eje X para mostrar una unidad de
            ax.grid(True, linestyle='--', alpha=0.7, color='black')

            ax.set_title(f'{num_estacion} - {columnas_interes_PA_h[0]}')
            ax.set_xlabel(f'Presión atmosférica ({unidad})')
            ax.set_ylabel('Frecuencia')
            ax.legend()
            
        # Ajusta la disposición de las subfiguras
        plt.tight_layout()
        
        # Agrega un título a la imagen general con ajuste de posición vertical
        plt.suptitle(f'Distribuciones de presión atmosférica - Estación: {num_estacion}', fontsize=16, y=0.95)
        
        # Ajusta la posición de la figura para dejar espacio para el título
        plt.subplots_adjust(top=0.9, bottom=0.1)

        # Guarda la imagen con ambas subfiguras
        plt.savefig(os.path.join(ruta_pruebas_b, 'H_PA_Total.png'))
        plt.show()
        
        print('-----------------------------------------------------------------------------------------------------------')
        print('Se ha generado exitosamente el histograma de la serie total para la presión atmosférica horaria como: H_PA_Total.png.')
        
#-----------------------------------------------------------------------------------------------------------------
#Funcion para generar boxplots mensuales de todas las variables.

def Diagrama_caja_mensual_PA(unidades):
    
    # Leer archivos .csv y realizar operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        df_PA_h_bd2 = None

        if ruta_PA_h_bd2:
            df_PA_h_bd2 = pd.read_csv(ruta_PA_h_bd2, na_values=['NA'])
            df_PA_h_bd2['TIMESTAMP'] = pd.to_datetime(df_PA_h_bd2['TIMESTAMP']) 

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
        fig, ax = plt.subplots(1, 1, figsize=(10, 14), dpi=300)

        # Diagramas de caja para PA.h si df_PA_h_bd2 no es None
        if df_PA_h_bd2 is not None:
            for i, variable_PA_h in enumerate(Variables_PA_h):
                data = df_PA_h_bd2[variable_PA_h][df_PA_h_bd2['TIMESTAMP'].dt.month == month]
                
                # Calcular estadísticas
                Media_aritmética_PA_h = data.mean()
                Desviación_estándar_PA_h = data.std()
                P25_PA_h = data.quantile(0.25)
                P50_PA_h = data.quantile(0.50)  # Median
                P75_PA_h = data.quantile(0.75)
                IQR_PA_h = P75_PA_h - P25_PA_h
                BI_PA_h = P25_PA_h - 1.5 * IQR_PA_h
                BS_PA_h = P75_PA_h + 1.5 * IQR_PA_h
                Min_PA_h = data.min()
                Max_PA_h = data.max()
                MinZ_PA_h = (Min_PA_h - Media_aritmética_PA_h) / Desviación_estándar_PA_h
                MaxZ_PA_h = (Max_PA_h - Media_aritmética_PA_h) / Desviación_estándar_PA_h
                lim_inf_PA_h = np.fix(MinZ_PA_h)*Desviación_estándar_PA_h + Media_aritmética_PA_h
                lim_sup_PA_h = np.fix(MaxZ_PA_h)*Desviación_estándar_PA_h + Media_aritmética_PA_h
                
                sns.boxplot(y=data, color="blue", linewidth=1.5,
                            boxprops=dict(facecolor='blue', edgecolor='black'),
                            flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'),
                            ax=ax)
                ax.set_title(f'{num_estacion} - {variable_PA_h} - {nombre_mes}')
                ax.set_xlabel('')
                ax.set_ylabel(f'Presión Atmosférica ({unidad})')
                # Set the y-axis limits
                ax.set_ylim(np.floor(data.min()), np.ceil(data.max()))
                # Automatically adjust the number of y-ticks based on the data range
                ax.yaxis.set_major_locator(ticker.MaxNLocator(15, integer=True))
                ax.tick_params(axis='y', rotation=00)

                # Agregar información estadística en la esquina superior derecha de cada subplot
                ax.text(0.95, 0.95, f'Media aritmética = {Media_aritmética_PA_h:.2f}{unidad}\nDesviación estándar = {Desviación_estándar_PA_h:.2f}{unidad}\nLím.Vec. superior = {lim_sup_PA_h:.2f}{unidad}\nLím.Vec.inferior = {lim_inf_PA_h:.2f}{unidad}\nBigote superior = {BS_PA_h:.2f}{unidad}\nBigote inferior = {BI_PA_h:.2f}{unidad}',
                                      transform=ax.transAxes,
                                      fontsize=8, verticalalignment='top', horizontalalignment='right', backgroundcolor='white')

    # Ajustar el diseño
        plt.tight_layout()

    # Guardar el gráfico
        plt.savefig(os.path.join(ruta_meses, f'DC_PA_{nombre_mes}.png'))
        plt.close()

    print('-----------------------------------------------------------------------------------------------------------')
    print('Se han generado exitosamente los diagramas de cajas mensuales para la presión atmosférica horaria.')
    print('')
    return True if (df_PA_h_bd2 is not None) else False

#-----------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------
#Llama funciones:

Diagrama_caja_total_PA(['mbar', 'mbar'])

# Example call to the function (adjust variables and dataframes as per your dataset)
plot_time_series(df_PA_h_bd2, 'Press.mbar.avg.1h.s1')

Dist_prob_PA_h()

Diagrama_caja_mensual_PA("")

#-----------------------------------------------------------------------------------------------------------------
# Definir los nombres de los meses en español
nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

# Inicializar el DataFrame fuera del bucle para acumular datos de todos los meses
valores_fuera_total = pd.DataFrame(columns=['TIMESTAMP', 'Valor_Original', 'Limite', 'ELEMENTO'])

# Iterar sobre cada mes en tus datos
def rubextremes_PA_h(df_PA_h_bd2, Variables_PA_h, nombres_meses, ruta_guardado):
    for mes in range(1, 13):
        # Filtrar datos por mes si df_PA_h_bd2 está definido
        if 'df_PA_h_bd2' in locals():
            df_mes = df_PA_h_bd2[df_PA_h_bd2['TIMESTAMP'].dt.month == mes]

            # Inicializar el DataFrame para cada mes
            valores_fuera_mes = pd.DataFrame(columns=['ELEMENTO','TIMESTAMP', 'Valor_Original', 'Valor_reemplazo', 'Limite', 'Procedimiento_adoptado','Comentario'])

            # Iterar sobre cada variable en Variables_PA_h
            for variable in Variables_PA_h:
                # Calcular Media_aritmética_PA_h  y desviación estándar si hay datos
                if not df_mes.empty:
                    Media_aritmética_PA_h = df_mes[variable].mean()
                    Desviación_estándar_PA_h = df_mes[variable].std()
                    P25_PA_h = df_mes[variable].quantile(0.25)
                    P50_PA_h = df_mes[variable].quantile(0.50)  # Median
                    P75_PA_h = df_mes[variable].quantile(0.75)
                    IQR_PA_h = P75_PA_h - P25_PA_h
                    BI_PA_h = P25_PA_h - 1.5 * IQR_PA_h
                    BS_PA_h = P75_PA_h + 1.5 * IQR_PA_h
                    Min_PA_h = df_mes[variable].min()
                    Max_PA_h = df_mes[variable].max()
                    MinZ_PA_h = (Min_PA_h - Media_aritmética_PA_h) / Desviación_estándar_PA_h
                    MaxZ_PA_h = (Max_PA_h - Media_aritmética_PA_h) / Desviación_estándar_PA_h
                    lim_inf_PA_h = np.fix(MinZ_PA_h)*Desviación_estándar_PA_h + Media_aritmética_PA_h
                    lim_sup_PA_h = np.fix(MaxZ_PA_h)*Desviación_estándar_PA_h + Media_aritmética_PA_h

                    # Inicializar los DataFrames para valores menores y mayores
                    valores_menores = pd.DataFrame(columns=['TIMESTAMP', variable, 'Limite'])
                    valores_mayores = pd.DataFrame(columns=['TIMESTAMP', variable, 'Limite'])

                    # Definir condiciones para valores menores al límite inferior
                    cond1_PA_h = (lim_inf_PA_h <= BI_PA_h) or (MinZ_PA_h <= -3)
                    cond1b_PA_h = Min_PA_h < BI_PA_h
                    if cond1_PA_h:
                        # Check if the minimum value is less than the lower whisker
                        valores_menores = df_mes.loc[(df_mes[variable] < lim_inf_PA_h), ['TIMESTAMP', variable]]
                        valores_menores['Limite'] = f"Menor_a_{lim_inf_PA_h:.2f}"
                    elif cond1b_PA_h:
                        # Register the minimum value
                        valores_menores = df_mes.loc[df_mes[variable] == Min_PA_h, ['TIMESTAMP', variable]]
                        valores_menores['Limite'] = f"Menor_a_{BI_PA_h:.2f}"

                    # Definir condiciones para valores mayores al límite superior
                    cond2_PA_h = (lim_sup_PA_h >= BS_PA_h) or (MaxZ_PA_h >= 3)
                    cond2b_PA_h = Max_PA_h > BS_PA_h
                    if cond2_PA_h:
                        # Check if the maximum value is greater than the upper whisker
                        valores_mayores = df_mes.loc[(df_mes[variable] > lim_sup_PA_h), ['TIMESTAMP', variable]]
                        valores_mayores['Limite'] = f"Mayor_a_{lim_sup_PA_h:.2f}"
                    elif cond2b_PA_h:
                        # Register the maximum value
                        valores_mayores = df_mes.loc[df_mes[variable] == Max_PA_h, ['TIMESTAMP', variable]]
                        valores_mayores['Limite'] = f"Mayor_a_{BS_PA_h:.2f}"

                    # Concatenar los dos DataFrames de valores filtrados
                    valores_fuera = pd.concat([valores_menores, valores_mayores])
                    
                    # Agregar el nombre de la variable a la columna 'ELEMENTO'
                    valores_fuera['ELEMENTO'] = variable

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
                nombre_archivo = f"{nombre_mes_espanol}_PA_h.csv"

                # Save the DataFrame to a CSV file in the folder containing the Spanish month name
                for root, dirs, files in os.walk(ruta_guardado):
                    for dir in dirs:
                        if nombre_mes_espanol.lower() in dir.lower():
                            ruta_archivo = os.path.join(root, dir, nombre_archivo)

                            # Reorder columns to match the specified order
                            valores_fuera_mes = valores_fuera_mes[['ELEMENTO','TIMESTAMP', 'Valor_Original', 'Valor_reemplazo', 'Limite', 'Procedimiento_adoptado','Comentario']]

                            # Cambiar el nombre de la columna 'TIMESTAMP' a 'FECHA'
                            valores_fuera_mes.rename(columns={'TIMESTAMP': 'FECHA'}, inplace=True)

                            valores_fuera_mes.to_csv(ruta_archivo, index=False)
                            break

    # Print statement placed outside the loop
    if 'df_PA_h_bd2' in locals():
        print('-----------------------------------------------------------------------------------------------------------')
        print("Se han generado exitosamente las pruebas de valores atipicos mensuales extremos para la presión atmosférica horaria a partir de los archivos bd2.")
        print('')
    else:
        print('-----------------------------------------------------------------------------------------------------------')
        print("No se realizaron pruebas de valores atípicos mensuales extemos para la presión atmosférica horaria porque no se encontro el archivo horario tipo bd2.")
        print('')


rubextremes_PA_h(df_PA_h_bd2, Variables_PA_h, nombres_meses, ruta_guardado)
    

def genera_modif_tec():
    # Nombres de las columnas
    nombres_columnas = ['Elemento', 'Fecha', 'Valor_Original', 'Valor_reemplazo', 'Procedimiento_adoptado', 'Comentario']

    # Crear DataFrames vacíos con las columnas especificadas
    df_tec_h = pd.DataFrame(columns=nombres_columnas)

    # Guardar los DataFrames como archivos CSV vacíos
    ruta_archivo_tec_h = os.path.join(ruta_analisis_PA, 'Modif_Tec_PA_h.csv')

    df_tec_h.to_csv(ruta_archivo_tec_h, index=False)

genera_modif_tec()