import pandas as pd
import os
import warnings
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
from distfit import distfit
import scipy.stats as stats
import numpy as np
from scipy.stats import skew, kurtosis

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
    
# Encuentra el archivo T.h.bd3.csv de la temperatura en la ruta de la estación
ruta_T_h_bd3 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.h.bd3' in archivo), None)

# Encuentra el archivo T.d.bd3.csv de la temperatura en la ruta de la estación
ruta_T_d_bd3 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.d.bd3' in archivo), None)
    
unidad = '°C'

# Variables para T.h
Variables_T_h = ['Temp.degC.avg.1h.s1']
# Variables para T.d
Variables_T_d = ['Temp.degC.max.dm.s1', 'Temp.degC.min.dm.s1']
Variables_T_d_Time = ['Temp.CST.max.dm.s1', 'Temp.CST.min.dm.s1']

# Cargar datos
df_T_h_bd3 = pd.read_csv(ruta_T_h_bd3, na_values=['NA'])
df_T_h_bd3['TIMESTAMP'] = pd.to_datetime(df_T_h_bd3['TIMESTAMP'])
df_T_d_bd3 = pd.read_csv(ruta_T_d_bd3, na_values=['NA'])
df_T_d_bd3['TIMESTAMP'] = pd.to_datetime(df_T_d_bd3['TIMESTAMP'])

def plot_time_series(df_T_h_bd3, df_T_d_bd3, var1, var2, var3, title=f"Serie de tiempo - Estación: {num_estacion}", xlabel="Tiempo", ylabel="Temperatura (°C)"):
    plt.figure(figsize=(45, 8), dpi=300)  # Adjusted figure size and DPI as per your requirement

    # Resample data to monthly frequency and calculate max and min
    df_T_h_bd3_monthly_max = df_T_h_bd3.resample('M', on='TIMESTAMP')[var1].max()
    df_T_h_bd3_monthly_min = df_T_h_bd3.resample('M', on='TIMESTAMP')[var1].min()
    df_T_d_bd3_monthly_max = df_T_d_bd3.resample('M', on='TIMESTAMP')[var2].max()
    df_T_d_bd3_monthly_min = df_T_d_bd3.resample('M', on='TIMESTAMP')[var3].min()
    
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
    plt.savefig(os.path.join(ruta_guardado, 'ST_Extremos_T.png'))
    plt.show()
    
    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print('Se ha generado exitosamente la serie de tiempo de los extremos mensuales de la serie total para la temperatura como: ST_Extremos_T.png.')
    print('')

# Example call to the function (adjust variables and dataframes as per your dataset)
plot_time_series(df_T_h_bd3, df_T_d_bd3, 'Temp.degC.avg.1h.s1', 'Temp.degC.max.dm.s1', 'Temp.degC.min.dm.s1')