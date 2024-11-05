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
    
# Encuentra el archivo T.h.bd2.csv de la temperatura en la ruta de la estación
ruta_T_h_bd2 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.h.bd2' in archivo), None)

# Encuentra el archivo T.d.bd2.csv de la temperatura en la ruta de la estación
ruta_T_d_bd2 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.d.bd2' in archivo), None)
    
unidad = '°C'

# Variables para T.h
Variables_T_h = ['Temp.degC.avg.1h.s1']
# Variables para T.d
Variables_T_d = ['Temp.degC.max.dm.s1', 'Temp.degC.min.dm.s1']
Variables_T_d_Time = ['Temp.CST.max.dm.s1', 'Temp.CST.min.dm.s1']

# Cargar datos
df_h = pd.read_csv(ruta_T_h_bd2, parse_dates=['TIMESTAMP'], na_values=['NA'])
df_h['TIMESTAMP'] = pd.to_datetime(df_h['TIMESTAMP'])
df_d = pd.read_csv(ruta_T_d_bd2, parse_dates=['TIMESTAMP'], na_values=['NA'])
df_d['TIMESTAMP'] = pd.to_datetime(df_d['TIMESTAMP'])

def plot_time_series(df_h, df_d, var1, var2, var3, title=f"Serie de tiempo - Estación: {num_estacion}", xlabel="Tiempo", ylabel=""):
    plt.figure(figsize=(45, 6), dpi=300)  # Adjusted figure size and DPI as per your requirement

    # Resample data to monthly frequency and calculate max and min
    df_h_monthly_max = df_h.resample('M', on='TIMESTAMP')[var1].max()
    df_h_monthly_min = df_h.resample('M', on='TIMESTAMP')[var1].min()
    df_d_monthly_max = df_d.resample('M', on='TIMESTAMP')[var2].max()
    df_d_monthly_min = df_d.resample('M', on='TIMESTAMP')[var3].min()
    
    # Create a combined dataframe for seaborn
    combined_df = pd.DataFrame({
        'Date': df_h_monthly_max.index,
        f'Max {var1}': df_h_monthly_max.values,
        f'Min {var1}': df_h_monthly_min.values,
        f'Max {var2}': df_d_monthly_max.values,
        f'Min {var3}': df_d_monthly_min.values
    }).melt('Date', var_name='Variable', value_name='Value')
    
    # Plot using seaborn
    sns.lineplot(data=combined_df, x='Date', y='Value', hue='Variable', palette=['orange', 'green', 'red', 'blue'], markers=True)
    
    # Add markers to the maximum and minimum points
    sns.scatterplot(data=combined_df, x='Date', y='Value', hue='Variable', palette=['orange', 'green', 'red', 'blue'], s=50, legend=False)
    
    # Formatting the plot
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    
    # Set major ticks format
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    plt.gca().xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=-1))  # Set minor ticks at the end of each month
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%b'))  # Use '%b' for month abbreviation
    
    # Rotate and align x-axis labels
    plt.xticks(rotation=90, ha='center')
    
    plt.grid(True, which='both', axis='x')
    
    # Set y-axis major and minor tick locators
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(1))  # Set major ticks every 1 unit
    plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(0.5))  # Set minor ticks every 0.5 units
    
    plt.tight_layout()
    
    # Save the plot (assuming ruta_guardado is defined in your environment)
    plt.savefig(os.path.join(ruta_guardado, 'ST_Extremos_T.png'))
    plt.show()

# Example call to the function (adjust variables and dataframes as per your dataset)
plot_time_series(df_h, df_d, 'Temp.degC.avg.1h.s1', 'Temp.degC.max.dm.s1', 'Temp.degC.min.dm.s1')