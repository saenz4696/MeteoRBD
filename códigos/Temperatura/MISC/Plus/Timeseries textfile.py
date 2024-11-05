import pandas as pd
import os
import warnings
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates

# Set seaborn style and matplotlib backend
sns.set_style("whitegrid")
matplotlib.use('Agg')

# Ignore UserWarnings from openpyxl
warnings.simplefilter('ignore', category=UserWarning)

# Path to raw data folder
datos_crudos = r'C:\\MeteoRBD.v1.0.0\\datos_rbd'

# Path to Excel file for data extraction
archivo_crudo_T = next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Temperatura" in file and file.endswith(".xlsx")), None)

if archivo_crudo_T:
    archivo_excel = pd.read_excel(archivo_crudo_T)
    if all(col in archivo_excel.columns for col in ['Cuenca', 'Estación']):
        # Extract station number from Excel file
        cuenca = str(archivo_excel['Cuenca'].iloc[0]).zfill(3)
        estacion = str(archivo_excel['Estación'].iloc[0]).zfill(3)
        num_estacion = cuenca + estacion

# Path to temperature analysis folder
ruta_analisis_T = f"C:\\MeteoRBD.v1.0.0\\revisión\\{num_estacion}-ema\\Temperatura"

# Create necessary folders if they don't exist
for carpeta in ["", "Pruebas_estadisticas"]:
    ruta_pruebas_b = os.path.join(ruta_analisis_T, carpeta)
    os.makedirs(ruta_pruebas_b, exist_ok=True)

# Path to save CSV files
ruta_guardado = os.path.join(ruta_analisis_T, "Pruebas_estadisticas")

# Find T.h.bd2.csv file in station path
ruta_T_h_bd2 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.h.bd2' in archivo), None)

# Find T.d.bd2.csv file in station path
ruta_T_d_bd2 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.d.bd2' in archivo), None)

unidad = '°C'

# Variables for T.h
Variables_T_h = ['Temp.degC.avg.1h.s1']

# Variables for T.d
Variables_T_d = ['Temp.degC.max.dm.s1', 'Temp.degC.min.dm.s1']
Variables_T_d_Time = ['Temp.CST.max.dm.s1', 'Temp.CST.min.dm.s1']

# Load data
df_h = pd.read_csv(ruta_T_h_bd2, parse_dates=['TIMESTAMP'], na_values=['NA'])
df_d = pd.read_csv(ruta_T_d_bd2, parse_dates=['TIMESTAMP'], na_values=['NA'])

# Ensure TIMESTAMP column is datetime
df_h['TIMESTAMP'] = pd.to_datetime(df_h['TIMESTAMP'])
df_d['TIMESTAMP'] = pd.to_datetime(df_d['TIMESTAMP'])

#Sort TIMESTAMP column chronologically
df_h.sort_values(by='TIMESTAMP', inplace=True)
df_d.sort_values(by='TIMESTAMP', inplace=True)

# Calculate monthly maximum for Temp.degC.max.dm.s1 and Temp.degC.avg.1h.s1
df_h_monthly_max = df_h.set_index('TIMESTAMP')[['Temp.degC.avg.1h.s1']].resample('M').max()
df_d_monthly_max = df_d.set_index('TIMESTAMP')[['Temp.degC.max.dm.s1']].resample('M').max()

# Calculate monthly minimum for Temp.degC.min.dm.s1 and Temp.degC.avg.1h.s1
df_h_monthly_min = df_h.set_index('TIMESTAMP')[['Temp.degC.avg.1h.s1']].resample('M').min()
df_d_monthly_min = df_d.set_index('TIMESTAMP')[['Temp.degC.min.dm.s1']].resample('M').min()

# Combine results into a single DataFrame
monthly_stats = pd.concat([
    df_h_monthly_max.add_suffix('_max'),
    df_h_monthly_min.add_suffix('_min'),
    df_d_monthly_max.add_suffix('_max'),
    df_d_monthly_min.add_suffix('_min')
], axis=1)

# Save to text file
output_file = os.path.join(ruta_guardado, 'monthly_stats.txt')
monthly_stats.to_csv(output_file, sep='\t')

print(f"Monthly statistics saved to: {output_file}")