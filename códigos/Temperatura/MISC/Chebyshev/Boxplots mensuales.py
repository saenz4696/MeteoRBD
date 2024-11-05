import pandas as pd
import os
import warnings
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
from scipy.stats import describe, skew, kurtosis
import numpy as np

sns.set_style("whitegrid")
matplotlib.use('Agg')

# -------------------------------General Paths

# Eliminamos UserWarnings de openpyxl
warnings.simplefilter('ignore', category=UserWarning)

datos_crudos = r'C:\MeteoRBD.v1.0.0\raw_data_rbd'

# Encontramos el archivo .xlsx en datos_crudos que contiene 'Cuenca' y 'Estación' como columnas
ruta_archivo = next((os.path.join(datos_crudos, archivo) for archivo in os.listdir(datos_crudos) if archivo.endswith(".xlsx")), None)

if ruta_archivo:
    archivo_excel = pd.read_excel(ruta_archivo)
    if all(col in archivo_excel.columns for col in ['Cuenca', 'Estación']):
        # Obtenemos el número de estación del archivo Excel
        cuenca = str(archivo_excel['Cuenca'].iloc[0])
        estacion = str(archivo_excel['Estación'].iloc[0])
        if len(estacion) == 2:
            estacion = '0' + estacion  # Añadimos un cero inicial si 'Estación' tiene solo dos dígitos
        num_estacion = cuenca + estacion
        num_estacion = int(num_estacion)

# Establecemos la ruta para los archivos de temperatura basados en el número de estación obtenido del archivo Excel
ruta_analisis_T = f"C:\MeteoRBD.v1.0.0\Data_Lake\{num_estacion}-ema\\base_datos\\Temperatura\\análisis_datos"

# Creamos carpetas si no existen
for carpeta in ["", "Pruebas_estadisticas"]:
    ruta_pruebas_b = os.path.join(ruta_analisis_T, carpeta)
    os.makedirs(ruta_pruebas_b, exist_ok=True)

# Encontramos el archivo T.h.bd2.csv de temperatura en la ruta de la estación
ruta_T_h_bd2 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.h.bd2' in archivo), None)

# Encontramos el archivo T.d.bd2.csv de temperatura en la ruta de la estación
ruta_T_d_bd2 = next((os.path.join(ruta_analisis_T, archivo) for archivo in os.listdir(ruta_analisis_T) if archivo.endswith(".csv") and 'T.d.bd2' in archivo), None)

unidad = '°C'


def Diagrama_caja_mensual_T(unidades):
    # Variables para T.h
    Variables_T_h = ['Temp.degC.avg.1h.s1', 'Td.degC.avg.1h.c1']
    # Variables para T.d
    Variables_T_d = ['Temp.degC.max.dm.s1', 'Temp.degC.min.dm.s1']

    # Leer archivos .csv y realizar operaciones de limpieza y corrección de TIMESTAMPs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        df_T_h_bd2 = None
        df_T_d_bd2 = None

        if ruta_T_h_bd2:
            df_T_h_bd2 = pd.read_csv(ruta_T_h_bd2, na_values=['NA'])
            df_T_h_bd2['TIMESTAMP'] = pd.to_datetime(df_T_h_bd2['TIMESTAMP']) 
            df_T_h_bd2 = df_T_h_bd2.dropna()

        if ruta_T_d_bd2:
            df_T_d_bd2 = pd.read_csv(ruta_T_d_bd2, na_values=['NA'])
            df_T_d_bd2['TIMESTAMP'] = pd.to_datetime(df_T_d_bd2['TIMESTAMP'])
            df_T_d_bd2 = df_T_d_bd2.dropna()

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
        fig, axes = plt.subplots(2, 2, figsize=(16, 10), dpi=300)

        # Diagramas de caja para T.h si df_T_h_bd2 no es None
        if df_T_h_bd2 is not None:
            for i, variable_T_h in enumerate(Variables_T_h):
                data = df_T_h_bd2[variable_T_h][df_T_h_bd2['TIMESTAMP'].dt.month == month].dropna()
                sns.boxplot(y=data, color="blue", linewidth=1.5,
                            boxprops=dict(facecolor='blue', edgecolor='black'),
                            flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'),
                            ax=axes[i//2, i%2])
                axes[i//2, i%2].set_title(f'{variable_T_h} - {nombre_mes}')
                axes[i//2, i%2].set_xlabel('')
                axes[i//2, i%2].set_ylabel(f'Temperatura ({unidad})')
                axes[i//2, i%2].set_yticks(range(int(data.min()), int(data.max()) + 1))
                axes[i//2, i%2].tick_params(axis='y', rotation=90)

                # Calcular estadísticas
                Media_aritmética_T_h = np.mean(data)
                Desviación_estándar_T_h = np.std(data)
                Sesgo_T_h = skew(data)
                Kurtosis_T_h = kurtosis(data)

                # Agregar información estadística en la esquina superior derecha de cada subplot
                axes[i//2, i%2].text(0.95, 0.95, f'Asimetría = {Sesgo_T_h:.2f}\nMedia aritmética = {Media_aritmética_T_h:.2f}{unidad}\nDesviación estándar = {Desviación_estándar_T_h:.2f}{unidad}\nKurtosis = {Kurtosis_T_h:.2f}',
                                      transform=axes[i//2, i%2].transAxes,
                                      fontsize=8, verticalalignment='top', horizontalalignment='right', backgroundcolor='white')

        # Diagramas de caja para T.d si df_T_d_bd2 no es None
        if df_T_d_bd2 is not None:
            for i, variable_T_d in enumerate(Variables_T_d):
                data = df_T_d_bd2[variable_T_d][df_T_d_bd2['TIMESTAMP'].dt.month == month].dropna()
                sns.boxplot(y=data, color="blue", linewidth=1.5,
                            boxprops=dict(facecolor='blue', edgecolor='black'),
                            flierprops=dict(markerfacecolor='white', markeredgecolor='black', marker='o'),
                            ax=axes[(i+2)//2, (i+2)%2])
                axes[(i+2)//2, (i+2)%2].set_title(f'{variable_T_d} - {nombre_mes}')
                axes[(i+2)//2, (i+2)%2].set_xlabel('')
                axes[(i+2)//2, (i+2)%2].set_ylabel(f'Temperatura ({unidad})')
                axes[(i+2)//2, (i+2)%2].set_yticks(range(int(data.min()), int(data.max()) + 1))
                axes[(i+2)//2, (i+2)%2].tick_params(axis='y', rotation=90)

                # Calcular estadísticas
                Media_aritmética_T_d = np.mean(data)
                Desviación_estándar_T_d = np.std(data)
                Sesgo_T_d = skew(data)
                Kurtosis_T_d = kurtosis(data)

                # Agregar información estadística en la esquina superior derecha de cada subplot
                axes[(i+2)//2, (i+2)%2].text(0.95, 0.95, f'Kurtosis: {Kurtosis_T_d:.2f}\nSesgo: {Sesgo_T_d:.2f}\nMedia aritmética: {Media_aritmética_T_d:.2f}{unidad}\nDesviación estándar = {Desviación_estándar_T_d:.2f}{unidad}',
                                             transform=axes[(i+2)//2, (i+2)%2].transAxes,
                                             fontsize=8, verticalalignment='top', horizontalalignment='right', backgroundcolor='white')
        # Ajustar el diseño
        plt.tight_layout()

        # Guardar el gráfico
        plt.savefig(os.path.join(ruta_meses, f'{nombre_mes}_DC.png'))
        plt.close()

    print('-----------------------------------------------------------------------------------------------------------')
    print('Se han generado exitosamente los diagramas de cajas mensuales para la temperatura.')
    print('')
    return True if (df_T_h_bd2 is not None or df_T_d_bd2 is not None) else False

# Llamar a la función
Diagrama_caja_mensual_T("")