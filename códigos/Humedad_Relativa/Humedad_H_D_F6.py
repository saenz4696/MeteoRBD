import pandas as pd
import os
import warnings
import shutil

# Ignora los UserWarnings
warnings.simplefilter('ignore', category=UserWarning)

# Directorio de los datos crudos
datos_crudos = r'C:\MeteoRBD.v1.0.0\data_rbd'

# Ruta del archivo Excel para extraer datos
archivo_crudo = next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Humedad" in file and file.endswith(".xlsx")), None)

if archivo_crudo:
    archivo_excel = pd.read_excel(archivo_crudo)
    if all(col in archivo_excel.columns for col in ['Cuenca', 'Estación']):
        # Obtiene el número de estación a partir del archivo Excel
        cuenca = str(archivo_excel['Cuenca'].iloc[0])
        estacion = str(archivo_excel['Estación'].iloc[0])
        if len(estacion) == 2:
            estacion = '0' + estacion  # Add leading zero if 'Estación' has only two digits
        elif len(estacion) == 1:
            estacion = '00' + estacion
            
        num_estacion = cuenca + estacion
        num_estacion = int(num_estacion)

        # Ruta del directorio de análisis
        ruta_analisis_HR = rf"C:\MeteoRBD.v1.0.0\Data_Lake\{num_estacion}-ema\base_datos\Humedad relativa\análisis_datos"

        # Buscar archivos y carpetas en el directorio de análisis
        contenido_analisis_HR = os.listdir(ruta_analisis_HR)

        if contenido_analisis_HR:
            # Tomar el primer archivo encontrado
            nombre_archivo = next((item for item in contenido_analisis_HR if "HR.h.bd3" in item), None)

            if nombre_archivo:
                # Crear el nuevo nombre de archivo
                nombre_carpeta_HR = os.path.splitext(nombre_archivo)[0].replace("HR.h.bd3", "HR.bd.ema")

                # Crear la ruta completa del nuevo directorio
                directorio_base_HR = rf"C:\MeteoRBD.v1.0.0\Data_Lake\{num_estacion}-ema\base_datos\Humedad"

                # Crear la carpeta 'reportes_rbd' dentro de directorio_base_HR
                carpeta_reportes_rbd = os.path.join(directorio_base_HR, 'reportes_rbd')
                os.makedirs(carpeta_reportes_rbd, exist_ok=True)

                # Crear la subcarpeta con el nombre_carpeta_HR dentro de 'reportes_rbd'
                subcarpeta_nombre_HR = os.path.join(carpeta_reportes_rbd, nombre_carpeta_HR)
                os.makedirs(subcarpeta_nombre_HR, exist_ok=True)

                # Mover todo el contenido del directorio de análisis a la subcarpeta con nombre_carpeta_HR
                for item in contenido_analisis_HR:
                    ruta_origen = os.path.join(ruta_analisis_HR, item)
                    ruta_destino = os.path.join(subcarpeta_nombre_HR, item)
                    shutil.move(ruta_origen, ruta_destino)

                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f"Archivos guardados en la ruta: {subcarpeta_nombre_HR}")
            else:
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f"No se encontraron archivos HR.h.bd# o HR.d.bd# en la ruta: {ruta_analisis_HR}.")
        else:
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"No se encontraron archivos en la ruta: {ruta_analisis_HR}.")
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("El archivo Excel no tiene las columnas 'Cuenca' y 'Estación'.")
else:
    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print(f"No se encontró ningún archivo Excel en la ruta {datos_crudos}.")
