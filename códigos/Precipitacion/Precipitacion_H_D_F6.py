import pandas as pd
import os
import warnings
import shutil

# Ignora los UserWarnings
warnings.simplefilter('ignore', category=UserWarning)

# Directorio de los datos crudos
datos_crudos = r'C:\MeteoRBD.v1.0.0\datos_rbd'

# Ruta del archivo Excel para extraer datos
archivo_crudo_Ll = next((os.path.join(datos_crudos, file) for file in os.listdir(datos_crudos) if "Lluvia" in file and file.endswith(".xlsx")), None)

if archivo_crudo_Ll:
    archivo_excel = pd.read_excel(archivo_crudo_Ll)
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

        # Ruta del directorio de análisis
        ruta_analisis_Ll = rf"C:\MeteoRBD.v1.0.0\revisión\{num_estacion}-ema\Precipitación"

        # Verifica si existe la ruta de análisis
        if os.path.exists(ruta_analisis_Ll):
            # Tomar el primer archivo encontrado
            nombre_archivo = next((item for item in os.listdir(ruta_analisis_Ll) if "Ll.h.bd3" in item), None)

            if nombre_archivo:
                # Crear el nuevo nombre de archivo
                nombre_carpeta_Ll = os.path.splitext(nombre_archivo)[0].replace("Ll.h.bd3", "Ll.bd.ema")

                ruta_respaldo_Ll = rf"\\respaldos\CC-RBD\{num_estacion}\Lluvia"

                # Crear la subcarpeta con el nombre_carpeta_Ll dentro de 'ruta_respaldo_Ll'
                ruta_respaldo = os.path.join(ruta_respaldo_Ll, nombre_carpeta_Ll)
                os.makedirs(ruta_respaldo, exist_ok=True)

                # Mover todo el contenido del directorio de análisis a la subcarpeta con nombre_carpeta_Ll
                for item in os.listdir(ruta_analisis_Ll):
                    ruta_origen = os.path.join(ruta_analisis_Ll, item)
                    ruta_destino = os.path.join(ruta_respaldo, item)
                    shutil.move(ruta_origen, ruta_destino)

                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f"Se han guardado los archivos de la ruta {ruta_analisis_Ll} en la ruta: {ruta_respaldo_Ll}\{nombre_carpeta_Ll}")
            else:
                print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f"No se encontro el archivo Ll.h.bd3 en la ruta: {ruta_analisis_Ll}, no es posible respaldar los archivos.")
        else:
            print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(f"No se encontraron archivos en la ruta: {ruta_analisis_Ll}.")
    else:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("El archivo Excel no tiene las columnas 'Cuenca' y 'Estación'.")
else:
    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print(f"No se encontró ningún archivo Excel en la ruta {datos_crudos}.")