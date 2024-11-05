import sys
import subprocess

print('')
print('----------------------------------------------------------------------------------------Bienvenido a MeteoRBD.v1.0.0------------------------------------------------------------------------------------------')
print('')

def Fases():
    while True:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Seleccione alguna de las opciones (r para retroceder o q para salir):")
        print("")
        print("Etapa 1: Valores admisibles.")
        print("")
        print("Fase [1]: Edición del formato de los archivos.")
        print("Fase [2]: Depuración de datos.")
        print("Fase [3]: Análisis y correción de fechas.")
        print("Fase [4]: Detección de valores atípicos extremos.")
        print("Fase [5]: Generación de los archivos revisados.")
        print("Fase [6]: Respaldo de datos en CC-RBD.")
        print('')
        opcion_F = input("Ingrese el número de la opción deseada: ")
        print('')
        if opcion_F in ['1', '2', '3', '4', '5', '6', 'r']:
            return opcion_F
        elif opcion_F == 'q':
            print("Saliendo del programa...")
            sys.exit()  # Forcefully exit the program
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")

def etapa_rangos(opcion_variable, opcion_F):
    if opcion_variable == '1':
        
        #if opcion_F == 'C':
            #print('Cortando los archivos crudos...')
            #print("Pronto estara disponible...")
        if opcion_F == '1':
            print('Editando los archivos crudos de la temperatura...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Temperatura\Temperatura_H_D_F1.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '2':
            print('Depurando los archivos bd0 de la temperatura...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Temperatura\Temperatura_H_D_F2.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '3':
            print('Analizando y editando las fechas de los archivos bd1 de la temperatura...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Temperatura\Temperatura_H_D_F3.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '4':
            print('Detectando valores atípicos extremos y generando las figuras de los archivos bd2 de la temperatura...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Temperatura\Temperatura_H_D_F4.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '5':
            print('Generando los archivos finales revisados de la temperatura...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Temperatura\Temperatura_H_D_F5.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '6':
            print('Guardando todos los archivos en la carpeta CC-RBD del servidor respaldos...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Temperatura\Temperatura_H_D_F6.py'], capture_output=True, text=True).stdout)

    elif opcion_variable == '2':
        if opcion_F == '1':
            print('Editando los archivos crudos de la humedad relativa...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Humedad_relativa\Humedad_H_D_F1.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '2':
            print('Depurando los archivos bd0 de la humedad relativa...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Humedad_relativa\Humedad_H_D_F2.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '3':
            print('Analizando y editando las fechas de los archivos bd1 de la humedad relativa...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Humedad_relativa\Humedad_H_D_F3.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '4':
            print('Detectando valores atípicos extremos y generando las figuras de los archivos bd2 de la humedad relativa...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Humedad_relativa\Humedad_H_D_F4.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '5':
            print('Generando los archivos bd3 revisados de la humedad relativa...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Humedad_relativa\Humedad_H_D_F5.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '6':
            print('Guardando todos los archivos en la carpeta CC-RBD del servidor respaldos...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Humedad_relativa\Humedad_H_D_F6.py'], capture_output=True, text=True).stdout)

    elif opcion_variable == '3':
        if opcion_F == '1':
            print('Editando los archivos crudos de la presión atmosférica...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Presion_Atmosferica\Presion_H_F1.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '2':
            print('Depurando los archivos bd0 de la presión atmosférica...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Presion_Atmosferica\Presion_H_F2.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '3':
            print('Analizando y editando las fechas de los archivos bd1 de la presión atmosférica...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Presion_Atmosferica\Presion_H_F3.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '4':
            print('Detectando valores atípicos extremos y generando las figuras de los archivos bd2 de la presión atmosférica...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Presion_Atmosferica\Presion_H_F4.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '5':
            print('Generando los archivos bd3 revisados de la presión atmosférica...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Presion_Atmosferica\Presion_H_F5.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '6':
            print('Guardando todos los archivos en la carpeta CC-RBD del servidor respaldos...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Presion_Atmosferica\Presion_H_F6.py'], capture_output=True, text=True).stdout)
            
    elif opcion_variable == '4':
        if opcion_F == '1':
            print('Editando los archivos crudos de la radiación solar...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Radiacion_Solar\Radiacion_H_F1.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '2':
            print('Depurando los archivos bd0 de la radiación solar...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Radiacion_Solar\Radiacion_H_F2.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '3':
            print('Analizando y editando las fechas de los archivos bd1 de la radiación solar...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Radiacion_Solar\Radiacion_H_F3.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '4':
            print('Detectando valores atípicos extremos y generando las figuras de los archivos bd2 de la radiación solar...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Radiacion_Solar\Radiacion_H_F4.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '5':
            print('Generando los archivos bd3 revisados de la radiación solar...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Radiacion_Solar\Radiacion_H_F5.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '6':
            print('Guardando todos los archivos en la carpeta CC-RBD del servidor respaldos...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Radiacion_Solar\Radiacion_H_F6.py'], capture_output=True, text=True).stdout)
            
    elif opcion_variable == '5':
        if opcion_F == '1':
            print('Editando los archivos crudos de la lluvia...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Precipitacion\Precipitacion_H_D_F1.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '2':
            print('Depurando los archivos bd0 de la lluvia...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Precipitacion\Precipitacion_H_D_F2.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '3':
            print('Analizando y editando las fechas de los archivos bd1 de la lluvia...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Precipitacion\Precipitacion_H_D_F3.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '4':
            print('Detectando valores atípicos extremos y generando las figuras de los archivos bd2 de la lluvia...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Precipitacion\Precipitacion_H_D_F4.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '5':
            print('Generando los archivos bd3 revisados de la lluvia...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Precipitacion\Precipitacion_H_D_F5.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '6':
            print('Guardando todos los archivos en la carpeta CC-RBD del servidor respaldos...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Precipitacion\Precipitacion_H_D_F6.py'], capture_output=True, text=True).stdout)

    elif opcion_variable == '6':
        if opcion_F == '1':
            print('Editando los archivos crudos del viento...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Viento\Viento_H_D_F1.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '2':
            print('Depurando los archivos bd0 del viento...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Viento\Viento_H_D_F2.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '3':
            print('Analizando y editando las fechas de los archivos bd1 del viento...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Viento\Viento_H_D_F3.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '4':
            print('Detectando valores atípicos extremos y generando las figuras de los archivos bd2 del viento...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Viento\Viento_H_D_F4.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '5':
            print('Generando los archivos bd3 revisados del viento...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Viento\Viento_H_D_F5.py'], capture_output=True, text=True).stdout)
        elif opcion_F == '6':
            print('Guardando todos los archivos en la carpeta CC-RBD del servidor respaldos...')
            print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\códigos\Viento\Viento_H_D_F6.py'], capture_output=True, text=True).stdout)

if __name__ == "__main__":
    while True:
        print('')
        print('----------------------------------------------------------------------------------------Menú principal----------------------------------------------------------------------------')
        print('')
        print('Seleccione alguna variable:')
        print('')
        print("[1]: Temperatura")
        print("[2]: Humedad Relativa")
        print("[3]: Presión Atmosférica")
        print("[4]: Radiación Solar")
        print("[5]: Precipitación")
        print("[6]: Viento")
        print('')
        opcion_variable = input("Ingrese el número de la fase deseada (q para salir): ")

        if opcion_variable in ['1', '2', '3','4','5', '6']:  # Verifica si la opción es válida
            while True:
                opcion_variable_fase = Fases()
                if opcion_variable_fase == 'r':
                    break  # Return to previous menu

                # Llama al procesamiento correspondiente según la opción seleccionada
                etapa_rangos(opcion_variable, opcion_variable_fase)
                
        elif opcion_variable == 'q':
            print('')
            print("Saliendo del programa...")
            sys.exit()
        else:
            print('')
            print("Variable no válida. Por favor, ingrese una opción válida.")
            print('')
            continue  # Reinicia el bucle para seleccionar la variable

#Linea shebang poner ! entre # y C: y pasarla al inicio del programa.
#C:\Users\jsaenz\AppData\Local\Programs\Python\Python312\python.exe