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
from matplotlib.ticker import MaxNLocator
import matplotlib.dates as mdates

sns.set_style("whitegrid")
matplotlib.use('Agg')

# -------------------------------Rutas generales

# Eliminar UserWarnings de openpyxl
warnings.simplefilter('ignore', category=UserWarning)


datos_crudos = r'C:\\MeteoRBD.v1.0.0\\datos_rbd'

# Encuentra el archivo .xlsx en la datos_crudos que contiene 'Cuenca' y 'Estación' como columnas
ruta_archivo =next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Radiación" in file and file.endswith(".xlsx")), None)

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
        
# Establece la ruta para los archivos de la radiación solar horaria según el número de estación obtenido del archivo Excel
ruta_analisis_R = f"C:\\MeteoRBD.v1.0.0\\revisión\\{num_estacion}-ema\\Radiación solar"

# Crea las carpetas si no existen
for carpeta in ["", "Pruebas_estadisticas"]:
    ruta_pruebas_b = os.path.join(ruta_analisis_R, carpeta)
    os.makedirs(ruta_pruebas_b, exist_ok=True)
    
# Ruta donde se guardarán los archivos CSV
ruta_guardado = os.path.join(ruta_analisis_R, "Pruebas_estadisticas")
    
# Encuentra el archivo T.h.bd2.csv de la radiación solar horaria en la ruta de la estación
ruta_R_h_bd2 = next((os.path.join(ruta_analisis_R, archivo) for archivo in os.listdir(ruta_analisis_R) if archivo.endswith(".csv") and 'R.h.bd2' in archivo), None)

unidades = ['$MJ/m^2$', 'kW/m$^2$', 'kW/m$^2$', 'min']

# Variables para T.h
Variables_R_h = ['Rad.MJ_m2.tot.1h.s1', 'Rad.kW_m2.max.1h.s1', 'Rad.kW_m2.min.1h.s1']

Variable_nombre = ['Radiación solar total','Radiación solar máxima','Radiación solar mínima']

#-----------------------------------------------------------------------------------------------------------------
#Estadisticas chebyshev
if ruta_R_h_bd2:
    # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if ruta_R_h_bd2:
            df_R_h_bd2 = pd.read_csv(ruta_R_h_bd2, na_values=['NA'])
            df_R_h_bd2['TIMESTAMP'] = pd.to_datetime(df_R_h_bd2['TIMESTAMP'])  # Convertir a tipo de dato de fecha y hora

#-----------------------------------------------------------------------------------------------------------------

# Definir los nombres de los meses en esRñol
nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

def Estadisticos_R_h_d(ruta_pruebas_b, num_estacion):

    # Inicializar diccionarios para almacenar estadísticas de R_h y R_d
    estadisticos_R_h_d = {var: {mes: [] for mes in nombres_meses} for var in Variables_R_h}

    # Iterar sobre cada mes en los datos de R_h y R_d
    for mes in range(1, 13):
        # Filtrar datos por mes para R_h y R_d
        df_mes_R_h = df_R_h_bd2[df_R_h_bd2['TIMESTAMP'].dt.month == mes]

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
    with open(os.path.join(ruta_pruebas_b, "Estadisticos_R.txt"), "w") as file:
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

    if ruta_R_h_bd2:
        # Lee los archivos .csv y realiza operaciones de limpieza y corrección de TIMESTAMPs
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            if ruta_R_h_bd2:
                df_R_h_bd2 = pd.read_csv(ruta_R_h_bd2, na_values=['NA'])
                df_R_h_bd2['TIMESTAMP'] = pd.to_datetime(df_R_h_bd2['TIMESTAMP'])  # Convertir a tipo de dato de fecha y hora

            # Genera una figura con cuatro subtramas (4 filas, 2 columnas)
            fig, axes = plt.subplots(3, 2, figsize=(16, 25), dpi=300)

            # Boxplots para T.h
            if ruta_R_h_bd2:
                for i, variable_R_h in enumerate(Variables_R_h):
                    unidad = unidades[i]
                    # Boxplot de la serie total (orientación vertical)
                    sns.boxplot(y=df_R_h_bd2[variable_R_h], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i, 0])
                    
                    axes[i, 0].set_title(f'{num_estacion} - {variable_R_h}- Total')
                    axes[i, 0].set_ylabel(unidad)
                    axes[i, 0].set_ylim(np.floor(df_R_h_bd2[variable_R_h].min()), np.ceil(df_R_h_bd2[variable_R_h].max()))
                    locator = MaxNLocator(prune='both')
                    axes[i, 0].yaxis.set_major_locator(locator)
                    
                    # Force the figure to update the y-ticks
                    fig.canvas.draw_idle()
                    axes[i, 0].tick_params(axis='y', rotation=0)

                    # Boxplots mensuales
                    sns.boxplot(x=df_R_h_bd2['TIMESTAMP'].dt.month, y=df_R_h_bd2[variable_R_h], color="blue", linewidth=1.5,
                                boxprops=dict(facecolor='blue', edgecolor='black'),
                                flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'), ax=axes[i, 1])
                    
                    axes[i, 1].set_title(f'{num_estacion} - {variable_R_h}- Mensual')
                    axes[i, 1].set_xlabel('Mes')
                    axes[i, 1].set_ylabel(unidad)
                    axes[i, 1].set_xticks(range(0, 13))  # 13 meses
                    axes[i, 1].set_ylim(np.floor(df_R_h_bd2[variable_R_h].min()), np.ceil(df_R_h_bd2[variable_R_h].max()))
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
            nombre_diag_caja_T = 'DC_R_Total.png'
            plt.savefig(os.path.join(ruta_pruebas_b, 'DC_R_Total.png'))
            plt.close()
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f'Se ha generado exitosamente el diagrama de cajas de la serie total para la radiación solar horaria como: {nombre_diag_caja_T}.')
            print('')
            return True
    else:
        print("No se encontro el archivo R.h.bd2 en la ruta especificada.")
        return False

Diagrama_caja_total_R(unidades)

def plot_time_series(df_R_h_bd2, var1, var2, var3, title=f"Serie de tiempo - Estación: {num_estacion}", xlabel="Tiempo", ylabel= "Radiación Solar"):
    
    plt.figure(figsize=(60, 8), dpi=300)  # Adjusted figure size and DPI as per your requirement

    # Resample data to monthly frequency and calculate max and min
    df_R_h_bd2_monthly_max = df_R_h_bd2.resample('M', on='TIMESTAMP')[var1].max()
    df_R_h_bd2_monthly_max_Rmax = df_R_h_bd2.resample('M', on='TIMESTAMP')[var2].max()
    df_R_h_bd2_monthly_max_Rmin = df_R_h_bd2.resample('M', on='TIMESTAMP')[var3].max()
    #df_R_h_bd2_monthly_min = df_R_h_bd2.resample('M', on='TIMESTAMP')[var1].min()

    
    # Create a combined dataframe for seaborn
    combined_df = pd.DataFrame({
        'Date': df_R_h_bd2_monthly_max.index,
        f'Max {var1}': df_R_h_bd2_monthly_max.values,
        f'Max {var2}': df_R_h_bd2_monthly_max_Rmax.values,
        f'Max {var3}': df_R_h_bd2_monthly_max_Rmin.values,
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
    plt.savefig(os.path.join(ruta_guardado, 'ST_Extremos_R.png'))
    
    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print('Se ha generado exitosamente la serie de tiempo de los extremos mensuales de la serie total para la radiación solar como: ST_Extremos_R.png.')
    print('')

plot_time_series(df_R_h_bd2, 'Rad.MJ_m2.tot.1h.s1', 'Rad.kW_m2.max.1h.s1', 'Rad.kW_m2.min.1h.s1')

#-----------------------------------------------------------------------------------------------------------------

def Dist_prob_R_h():

    # Variables para verificar si se encontraron ambos archivos
    encontrado_R_h_bd2 = ruta_R_h_bd2 is not None
    
    #Establece el nivel de ocnfianza
    niv_conf = 0.9995

    if encontrado_R_h_bd2 :
        # Crea una figura con cuatro subfiguras en 3 filas y 1 columnas
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(20, 15), dpi=300)

        # Procesa T.h.bd2 si está presente
        if encontrado_R_h_bd2:
            # Lee el archivo .csv y realiza operaciones de limpieza y corrección de timestamps para T.h.bd2
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df_R_h_bd2 = pd.read_csv(ruta_R_h_bd2, na_values=['NA'])
                           
            # Selecciona las columnas de interés para radiación solar horaria del aire y radiación solar horaria de rocío
            columnas_interes_R_h = ['Rad.MJ_m2.tot.1h.s1', 'Rad.kW_m2.max.1h.s1','Rad.kW_m2.min.1h.s1', 'Rad-int_sol.min_hour.tot.1h.s1', 'TIMESTAMP']

            # Filtra solo las columnas que contienen las variables de la radiación solar horaria hoaria y 'TIMESTAMP'
            df_filtrado_R_h = df_R_h_bd2[columnas_interes_R_h].dropna()

            # Asigna las columnas a las variables de interés
            timestamps_R_h = df_filtrado_R_h['TIMESTAMP']

            # Selecciona las columnas de interés para radiación solar horaria del aire y radiación solar horaria de rocío
            col_rtotR_h = df_filtrado_R_h['Rad.MJ_m2.tot.1h.s1']
            col_rmaxR_h = df_filtrado_R_h['Rad.kW_m2.max.1h.s1']
            col_rmin_R_h = df_filtrado_R_h['Rad.kW_m2.min.1h.s1']
            col_intsol_R_h = df_filtrado_R_h['Rad-int_sol.min_hour.tot.1h.s1']
            
            # For ax1, ax2, and ax3 (with one decimal place)
            formatter = ticker.StrMethodFormatter("{x:.1f}")

#-----------------------------------------------------------------------------------------------------------------------------
            # Inicializa el objeto distfit para la radiación solar horaria del aire
            dist_R_h = distfit()
            dist_R_h.fit_transform(col_rtotR_h, verbose=0)

            # Obtiene la mejor distribución y sus Rrámetros para la radiación solar horaria del aire
            Dist_Ajust_R_h = dist_R_h.model['name']
            Dist_Ajust_param_R_h = dist_R_h.model['params']
            Dist_Ajust_Stats_R_h = getattr(stats, Dist_Ajust_R_h)
            Dist_Ajust_rvs_R_h =Dist_Ajust_Stats_R_h.rvs(*Dist_Ajust_param_R_h, size=len(col_rtotR_h))
            Ajusta_datos_R_h = Dist_Ajust_rvs_R_h

            # Calcula los intervalos de confianza para la mejor distribución de la radiación solar horaria del aire
            lim_inf_R_h, lim_sup_R_h =Dist_Ajust_Stats_R_h.interval(niv_conf, *Dist_Ajust_param_R_h)
            
            # Inicializa el objeto distfit para la radiación solar horaria de rocío
            dist_rmaxh = distfit()
            dist_rmaxh.fit_transform(col_rmaxR_h, verbose=0)

            # Obtiene la mejor distribución y sus Rrámetros para la radiación solar horaria de rocío
            Dist_Ajust_rmaxh = dist_rmaxh.model['name']
            Dist_Ajust_param_rmaxh = dist_rmaxh.model['params']
            Dist_Ajust_Stats_rmaxh = getattr(stats, Dist_Ajust_rmaxh)
            Dist_Ajust_rvs_rmaxh =Dist_Ajust_Stats_rmaxh.rvs(*Dist_Ajust_param_rmaxh, size=len(col_rmaxR_h))
            Ajusta_datos_rmaxh = Dist_Ajust_rvs_rmaxh
            
            # Calcula los intervalos de confianza para la mejor distribución de la radiación solar horaria del aire
            lim_inf_rmaxh, lim_sup_rmaxh = Dist_Ajust_Stats_rmaxh.interval(niv_conf, *Dist_Ajust_param_rmaxh)
            
            #Calculo de parametros estadisticos.
            μ_R_h = col_rtotR_h.mean()
            srmaxdev_R_h = col_rtotR_h.std()
            Asimetría_R_h = skew(col_rtotR_h)
            kurtosis_R_h = kurtosis(col_rtotR_h)

            # Grafica la distribución ajustada junto con el histograma de los datos originales para la radiación total
            sns.histplot(col_rtotR_h, kde=True, color='blue', 
             label=f'Datos originales\nKurtosis = {kurtosis_R_h:.2f} - Asimetría = {Asimetría_R_h:.2f}\nMedia aritmética: = {μ_R_h:.2f} $MJ/m^2$\nDesviación estándar = {srmaxdev_R_h:.2f} $MJ/m^2$', 
             ax=ax1)

            sns.histplot(Ajusta_datos_R_h, kde=True, color='red', 
             label=f'Distribución ajustada ({Dist_Ajust_R_h})\nIC: ({lim_inf_R_h:.2f} $MJ/m^2$ - {lim_sup_R_h:.2f} $MJ/m^2$) - NC: {niv_conf*100:.2f}%',
             ax=ax1)

            # Ajusta los límites del eje X para mostrar cada unidades
            ax1.set_xticks(np.arange(float(np.floor(col_rtotR_h.min())), float(np.ceil(col_rtotR_h.max())) + 0.1, 0.1))
            ax1.set_xticklabels(ax1.get_xticks(), rotation='vertical')
            ax1.xaxis.set_major_formatter(formatter)

            # Ajusta los límites del eje X para mostrar una unidades de
            ax1.grid(True, linestyle='--', alpha=0.7, color='black')

            ax1.set_title(f'{num_estacion} - {columnas_interes_R_h[0]}')
            ax1.set_xlabel('Radiación solar total $(MJ/m^2)$')
            ax1.set_ylabel('Frecuencia')
            ax1.legend()
            
            μ_rmaxh = col_rmaxR_h.mean()
            srmaxdev_rmaxh = col_rmaxR_h.std()
            Asimetría_rmaxh = skew(col_rmaxR_h)
            kurtosis_rmaxh = kurtosis(col_rmaxR_h)

            # Grafica la distribución ajustada junto con el histograma de los datos originales para la radiación maxima
            sns.histplot(col_rmaxR_h, kde=True, color='blue', 
             label=f'Datos originales\nKurtosis = {kurtosis_rmaxh:.2f} - Asimetría = {Asimetría_rmaxh:.2f}\nMedia aritmética = {μ_rmaxh:.2f} kW/m$^2$\nDesviación estándar = {srmaxdev_rmaxh:.2f} kW/m$^2$', 
             ax=ax2)

            sns.histplot(Ajusta_datos_rmaxh, kde=True, color='red', 
             label=f'Distribución ajustada ({Dist_Ajust_rmaxh})\nIC: ({lim_inf_rmaxh:.2f} kW/m$^2$ - {lim_sup_rmaxh:.2f} kW/m$^2$) - NC: {niv_conf*100:.2f}%',
             ax=ax2)


            # Ajusta los límites del eje X para mostrar cada unidades
            ax2.set_xticks(np.arange(float(np.floor(col_rmaxR_h.min())), float(np.ceil(col_rmaxR_h.max())) + 0.1, 0.1))
            ax2.set_xticklabels(ax2.get_xticks(), rotation='vertical')
            ax2.xaxis.set_major_formatter(formatter)

            # Ajusta los límites del eje X para mostrar una unidades de
            ax2.grid(True, linestyle='--', alpha=0.7, color='black')

            ax2.set_title(f'{num_estacion} - {columnas_interes_R_h[1]}')
            ax2.set_xlabel('Radiación solar máxima (kW/m$^2$)')
            ax2.set_ylabel('Frecuencia')
            ax2.legend()

#-----------------------------------------------------------------------------------------------------------------------------

            # Inicializa el objeto distfit para T.d.bd2 - Temp. Máxima
            dist_rmin_d = distfit()
            dist_rmin_d.fit_transform(col_rmin_R_h, verbose=0)

            # Obtiene la mejor distribución y sus Rrámetros para T.d.bd2 - Temp. Máxima
            Dist_Ajust_rmin_d = dist_rmin_d.model['name']
            Dist_Ajust_param_rmin_d = dist_rmin_d.model['params']
            Dist_Ajust_Stats_rmin_d = getattr(stats, Dist_Ajust_rmin_d)
            Dist_Ajust_rvs_rmin_d =Dist_Ajust_Stats_rmin_d.rvs(*Dist_Ajust_param_rmin_d, size=len(col_rmin_R_h))
            Ajusta_datos_rmin_d = Dist_Ajust_rvs_rmin_d

            # Calcula los intervalos de confianza para la mejor distribución de T.d.bd2 - Temp. Máxima
            lim_inf_rmin_d, lim_sup_rmin_d =Dist_Ajust_Stats_rmin_d.interval(niv_conf, *Dist_Ajust_param_rmin_d)

            # Inicializa el objeto distfit para T.d.bd2 - Temp. Mínima
            dist_intsol_d = distfit()
            dist_intsol_d.fit_transform(col_intsol_R_h, verbose=0)

            # Obtiene la mejor distribución y sus Rrámetros para T.d.bd2 - Temp. Mínima
            Dist_Ajust_intsol_d = dist_intsol_d.model['name']
            Dist_Ajust_param_intsol_d = dist_intsol_d.model['params']
            Dist_Ajust_Stats_intsol_d = getattr(stats, Dist_Ajust_intsol_d)
            Dist_Ajust_rvs_intsol_d =Dist_Ajust_Stats_intsol_d.rvs(*Dist_Ajust_param_intsol_d, size=len(col_intsol_R_h))
            Ajusta_datos_intsol_d = Dist_Ajust_rvs_intsol_d

            # Calcula los intervalos de confianza para la mejor distribución de T.d.bd2 - Temp. Mínima
            lim_inf_intsol_d, lim_sup_intsol_d =Dist_Ajust_Stats_intsol_d.interval(niv_conf, *Dist_Ajust_param_intsol_d)
            
            μ_rmin_d = col_rmin_R_h.mean()
            srmaxdev_rmin_d = col_rmin_R_h.std()
            Asimetría_rmin_d = skew(col_rmin_R_h)
            kurtosis_rmin_d = kurtosis(col_rmin_R_h)

            # Grafica la distribución ajustada junto con el histograma de los datos originales para la radiación mínima
            sns.histplot(col_rmin_R_h, kde=True, color='blue', 
             label=f'Datos originales\nKurtosis = {kurtosis_rmin_d:.2f} - Asimetría = {Asimetría_rmin_d:.2f}\nMedia aritmética = {μ_rmin_d:.2f} kW/m$^2$\nDesviación estándar = {srmaxdev_rmin_d:.2f} kW/m$^2$', 
             ax=ax3)

            sns.histplot(Ajusta_datos_rmin_d, kde=True, color='red', 
             label=f'Distribución ajustada ({Dist_Ajust_rmin_d})\nIC: ({lim_inf_rmin_d:.2f} kW/m$^2$ - {lim_sup_rmin_d:.2f} kW/m$^2$) - NC: {niv_conf*100:.2f}%',
             ax=ax3)

            # Ajusta los límites del eje X para mostrar cada unidades
            ax3.set_xticks(np.arange(float(np.floor(col_rmin_R_h.min())), float(np.ceil(col_rmin_R_h.max())) + 0.1, 0.1))
            ax3.set_xticklabels(ax3.get_xticks(), rotation='vertical')
            ax3.xaxis.set_major_formatter(formatter)

            # Ajusta los límites del eje X para mostrar una unidades de
            ax3.grid(True, linestyle='--', alpha=0.7, color='black')

            ax3.set_title(f'{num_estacion} - {columnas_interes_R_h[2]}')
            ax3.set_xlabel('Radiación solar mínima (kW/m$^2$)')
            ax3.set_ylabel('Frecuencia')
            ax3.legend()
              
        # Ajusta la disposición de las subfiguras
        plt.tight_layout()
        
        # Agrega un título a la imagen general con ajuste de posición vertical
        plt.suptitle(f'Distribuciones de la radiación solar - Estación: {num_estacion}', fontsize=16, y=0.95)
        
        # Ajusta la posición de la figura para dejar esRcio para el título
        plt.subplots_adjust(top=0.9, bottom=0.1)

        # Guarda la imagen con ambas subfiguras
        plt.savefig(os.path.join(ruta_pruebas_b, 'H_T_Total.png'))
        plt.show()
        
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print('Se ha generado exitosamente el histograma de la serie total para la radiación solar como: H_R_Total.png.')
        
Dist_prob_R_h()
        
#-----------------------------------------------------------------------------------------------------------------
#Funcion para generar boxplots mensuales de todas las variables.

def Diagrama_caja_mensual_R(unidadeses):
    
    # Leer archivos .csv y realizar operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        df_R_h_bd2 = None

        if ruta_R_h_bd2:
            df_R_h_bd2 = pd.read_csv(ruta_R_h_bd2, na_values=['NA'])
            df_R_h_bd2['TIMESTAMP'] = pd.to_datetime(df_R_h_bd2['TIMESTAMP']) 

    # Lista de nombres de los meses en esRñol
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    # Iterar a través de cada mes
    for month in range(1, 13):
        # Nombre del mes en esRñol
        nombre_mes_carpeta = f"{month:02d}.{meses[month - 1]}"
        nombre_mes = meses[month - 1]
        ruta_meses = os.path.join(ruta_pruebas_b, nombre_mes_carpeta)
        os.makedirs(ruta_meses, exist_ok=True)

        # Genera una figura con cuatro subtramas (3 filas, 1 columna)
        fig, axes = plt.subplots(3, 1, figsize=(8, 15), dpi=300)

        # Diagramas de caja para T.h si df_R_h_bd2 no es None
        if df_R_h_bd2 is not None:
            for i, (variable_R_h, nombre_variable, unidades_variable) in enumerate(zip(Variables_R_h, Variable_nombre, unidades)):
                data = df_R_h_bd2[variable_R_h][df_R_h_bd2['TIMESTAMP'].dt.month == month]
                
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

                # Agregar información estadística en la esquina superior derecha de cada subplot
                axes[i].text(0.95, 0.95, f'Media aritmética = {Media_aritmética_R_h:.2f} {unidades_variable}\nDesviación estándar = {Desviación_estándar_R_h:.2f} {unidades_variable}\nLím.Vec. superior = {lim_sup_R_h:.2f}{unidades_variable}\nBigote superior = {BS_R_h:.2f}{unidades_variable}',
                                      transform=axes[i].transAxes,
                                      fontsize=8, verticalalignment='top', horizontalalignment='right', backgroundcolor='white')

    # Ajustar el diseño
        plt.tight_layout()

    # Guardar el gráfico
        plt.savefig(os.path.join(ruta_meses, f'DC_R_{nombre_mes}.png'))
        plt.close()

    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print('Se han generado exitosamente los diagramas de cajas mensuales para la radiación solar horaria.')
    print('')
    return True if (df_R_h_bd2 is not None) else False

#-----------------------------------------------------------------------------------------------------------------
#Llama funciones:


Diagrama_caja_mensual_R("")

#-----------------------------------------------------------------------------------------------------------------

# Variables para T.h
Variables_R_h_lim = ['Rad.MJ_m2.tot.1h.s1', 'Rad.kW_m2.max.1h.s1', 'Rad.kW_m2.min.1h.s1']

# Definir los nombres de los meses en esRñol
nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

# Inicializar el DataFrame fuera del bucle para acumular datos de todos los meses
valores_fuera_total = pd.DataFrame(columns=['TIMESTAMP', 'Valor_Original', 'Limite', 'ELEMENTO'])

# Iterar sobre cada mes en tus datos
def rubextremes_R_h(df_R_h_bd2, Variables_R_h_lim, nombres_meses, ruta_guardado):
    for mes in range(1, 13):
        # Filtrar datos por mes si df_R_h_bd2 está definido
        if 'df_R_h_bd2' in locals():
            df_mes = df_R_h_bd2[df_R_h_bd2['TIMESTAMP'].dt.month == mes]

            # Inicializar el DataFrame para cada mes
            valores_fuera_mes = pd.DataFrame(columns=['ELEMENTO','TIMESTAMP', 'Valor_Original', 'Valor_reemplazo', 'Limite', 'Procedimiento_adoptado','Comentario'])

            # Iterar sobre cada variable en Variables_R_h
            for variable in Variables_R_h_lim:
                # Calcular Media_aritmética_R_h  y desviación estándar si hay datos
                if not df_mes.empty:
                    Media_aritmética_R_h = df_mes[variable].mean()
                    Desviación_estándar_R_h = df_mes[variable].std()
                    P25_R_h = df_mes[variable].quantile(0.25)
                    P50_R_h = df_mes[variable].quantile(0.50)  # Median
                    P75_R_h = df_mes[variable].quantile(0.75)
                    IQR_R_h = P75_R_h - P25_R_h
                    BI_R_h = P25_R_h - 1.5 * IQR_R_h
                    BS_R_h = P75_R_h + 1.5 * IQR_R_h
                    Min_R_h = df_mes[variable].min()
                    Max_R_h = df_mes[variable].max()
                    MinZ_R_h = (Min_R_h - Media_aritmética_R_h) / Desviación_estándar_R_h
                    MaxZ_R_h = (Max_R_h - Media_aritmética_R_h) / Desviación_estándar_R_h
                    lim_inf_R_h = np.fix(MinZ_R_h)*Desviación_estándar_R_h + Media_aritmética_R_h
                    lim_sup_R_h = np.fix(MaxZ_R_h)*Desviación_estándar_R_h + Media_aritmética_R_h

                    # Inicializar los DataFrames para valores menores y mayores
                    valores_menores = pd.DataFrame(columns=['TIMESTAMP', variable, 'Limite'])
                    valores_mayores = pd.DataFrame(columns=['TIMESTAMP', variable, 'Limite'])

                    # Definir condiciones para valores mayores al límite superior
                    cond2_R_h = (lim_sup_R_h >= BS_R_h) or (MaxZ_R_h >= 3)
                    cond2b_R_h = Max_R_h > BS_R_h
                    if cond2_R_h:
                        # Check if the maximum value is greater than the upper whisker
                        valores_mayores = df_mes.loc[(df_mes[variable] > lim_sup_R_h), ['TIMESTAMP', variable]]
                        valores_mayores['Limite'] = f"Mayor_a_{lim_sup_R_h:.2f}"
                    elif cond2b_R_h:
                        # Register the maximum value
                        valores_mayores = df_mes.loc[df_mes[variable] == Max_R_h, ['TIMESTAMP', variable]]
                        valores_mayores['Limite'] = f"Mayor_a_{BS_R_h:.2f}"
                    
                    valores_fuera = pd.concat([valores_mayores])

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
                # Obtener el nombre del mes en esRñol
                nombre_mes_esRnol = nombres_meses[mes - 1]

                # Nombre del archivo CSV con el nombre del mes en esRñol
                nombre_archivo = f"{nombre_mes_esRnol}_R_h.csv"

                # Save the DataFrame to a CSV file in the folder containing the SRnish month name
                for root, dirs, files in os.walk(ruta_guardado):
                    for dir in dirs:
                        if nombre_mes_esRnol.lower() in dir.lower():
                            ruta_archivo = os.path.join(root, dir, nombre_archivo)

                            # Reorder columns to match the specified order
                            valores_fuera_mes = valores_fuera_mes[['ELEMENTO','TIMESTAMP', 'Valor_Original', 'Valor_reemplazo', 'Limite', 'Procedimiento_adoptado','Comentario']]

                            # Cambiar el nombre de la columna 'TIMESTAMP' a 'FECHA'
                            valores_fuera_mes.rename(columns={'TIMESTAMP': 'FECHA'}, inplace=True)

                            valores_fuera_mes.to_csv(ruta_archivo, index=False)
                            break

    # Print statement placed outside the loop
    if 'df_R_h_bd2' in locals():
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Se han generado exitosamente las pruebas de valores atipicos mensuales extremos para la radiación solar horaria a partir de los archivos bd2.")
        print('')
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("No se realizaron pruebas de valores atípicos mensuales extemos para la radiación solar horaria porque no se encontro el archivo horario tipo bd2.")
        print('')


rubextremes_R_h(df_R_h_bd2, Variables_R_h_lim, nombres_meses, ruta_guardado)
    

def genera_modif_tec():
    # Nombres de las columnas
    nombres_columnas = ['Elemento', 'Fecha', 'Valor_Original', 'Valor_reemplazo', 'Procedimiento_adoptado', 'Comentario']

    # Crear DataFrames vacíos con las columnas especificadas
    df_tec_h = pd.DataFrame(columns=nombres_columnas)

    # Guardar los DataFrames como archivos CSV vacíos
    ruta_archivo_tec_h = os.path.join(ruta_analisis_R, 'Modif_Tec_R_h.csv')

    df_tec_h.to_csv(ruta_archivo_tec_h, index=False)

genera_modif_tec()