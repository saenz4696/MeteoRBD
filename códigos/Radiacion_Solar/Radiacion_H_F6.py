import pandas as pd
import os
import warnings
import shutil

# Ignora los UserWarnings
warnings.simplefilter('ignore', category=UserWarning)

# Directorio de los datos crudos
datos_crudos = r'C:\MeteoRBD.v1.0.0\datos_rbd'

# Ruta del archivo Excel Rra extraer datos
archivo_crudo = next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Radiación" in file and file.endswith(".xlsx")), None)

if archivo_crudo:
    archivo_excel = pd.read_excel(archivo_crudo)
    if all(col in archivo_excel.columns for col in ['Cuenca', 'Estación']):
        # Obtiene el número de estación a Rrtir del archivo Excel
        cuenca = str(archivo_excel['Cuenca'].iloc[0])
        estacion = str(archivo_excel['Estación'].iloc[0])

        # Asegúrate de que la cuenca tenga tres dígitos
        cuenca = cuenca.zfill(3)

        # Asegúrate de que la estación tenga tres dígitos
        estacion = estacion.zfill(3)

        # Concatenar cuenca y estación
        num_estacion = cuenca + estacion

        # Ruta del directorio de análisis
        ruta_analisis_R = rf"C:\MeteoRBD.v1.0.0\revisión\{num_estacion}-ema\Radiación solar"

        # Verifica si existe la ruta de análisis
        if os.path.exists(ruta_analisis_R):
            # Tomar el primer archivo encontrado
            nombre_archivo = next((item for item in os.listdir(ruta_analisis_R) if "R.h.bd3" in item), None)

            if nombre_archivo:
                # Crear el nuevo nombre de archivo
                nombre_carpeta_R = os.path.splitext(nombre_archivo)[0].replace("R.h.bd3", "R.bd.ema")

                ruta_respaldo_R = rf"\\respaldos\CC-RBD\{num_estacion}\Radiacion"

                # Crear la subcarpeta con el nombre_carpeta_T dentro de 'ruta_respaldo_T'
                ruta_respaldo = os.path.join(ruta_respaldo_R, nombre_carpeta_R)
                os.makedirs(ruta_respaldo, exist_ok=True)

                # Mover todo el contenido del directorio de análisis a la subcarpeta con nombre_carpeta_T
                for item in os.listdir(ruta_analisis_R):
                    ruta_origen = os.path.join(ruta_analisis_R, item)
                    ruta_destino = os.path.join(ruta_respaldo, item)
                    shutil.move(ruta_origen, ruta_destino)

                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f"Se han guardado los archivos de la ruta {ruta_analisis_R} en la ruta: {ruta_respaldo_R}\{nombre_carpeta_R}")
            else:
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f"No se encontraron archivos R.h.bd# o R.d.bd# en la ruta: {ruta_analisis_R}.")
        else:
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"No se encontraron archivos en la ruta: {ruta_analisis_R}.")
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("El archivo Excel no tiene las columnas 'Cuenca' y 'Estación'.")
else:
    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print(f"No se encontró ningún archivo Excel en la ruta {datos_crudos}.")
