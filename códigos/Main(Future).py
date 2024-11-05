import sys
import subprocess

print('')
print('----------------------------------------------------------------------------------------Bienvenido a MeteoRBD.v1.0.0------------------------------------------------------------------------------------------')
print('')

Variable = ['Temperatura','Humedad Relativa','Presión Atmosférica','Radiación Solar','Precipitación','Viento']

def Etapas(Variable):
    while True:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Variable: {Variable}\nSeleccione la etapa (r para retroceder o q para salir):")
        print("")
        print("Etapa [1]: Formateo de datos y rangos")
        print("Etapa [2]: Repetidos consecutivos y saltos")
        print('')
        opcion_etapa = input("Ingrese el número de la etapa deseada: ")
        print('')
        if opcion_etapa in ['1', '2', 'r']:
            return opcion_etapa
        elif opcion_etapa == 'q':
            print("Saliendo del programa...")
            sys.exit()  
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")

def Fases_Etapa_Uno(Variable):
    while True:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Variable: {Variable}\nSeleccione alguna de las opciones (r para retroceder o q para salir):")
        print("")
        print("Fase [1]: Edición del formato de los archivos.")
        print("Fase [2]: Depuración de datos.")
        print("Fase [3]: Análisis de fechas faltantes y repetidas.")
        print("Fase [4]: Detección de valores atípicos extremos.")
        print("Fase [5]: Generación del archivo revisado.")
        print("Fase [6]: Respaldo de datos en Data_Lake.")
        print('')
        opcion_F = input("Ingrese el número de la opción deseada: ")
        print('')
        if opcion_F in ['1', '2', '3', '4', '5', '6', 'r']:
            return opcion_F
        elif opcion_F == 'q':
            print("Saliendo del programa...")
            sys.exit() 
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")
            
def Fases_Etapa_Dos(Variable):
    while True:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print(f"Variable: {Variable}\nSeleccione alguna de las opciones (r para retroceder o q para salir):")
        print("")
        print("Fase [1]: Pruebas temporales.")
        print('')
        opcion_FD = input("Ingrese el número de la opción deseada: ")
        print('')
        if opcion_FD in ['1', 'r']:
            return opcion_FD
        elif opcion_FD == 'q':
            print("Saliendo del programa...")
            sys.exit() 
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")

def Etapas_scripts(opcion_variable, opcion_etapa, opcion_F, opcion_FD):
    if opcion_variable == '1':
        if opcion_etapa == '1':
            if opcion_F == '1':
                print('Editando los archivos crudos de la temperatura...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Temperatura\Temperatura_H_D_F1.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '2':
                print('Depurando los archivos bd0 de la temperatura...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Temperatura\Temperatura_H_D_F2.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '3':
                print('Analizando y editando las fechas de los archivos bd1 de la temperatura...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Temperatura\Temperatura_H_D_F3.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '4':
                print('Detectando valores atípicos extremos y generando las figuras de los archivos bd2 de la temperatura...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Temperatura\Temperatura_H_D_F4.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '5':
                print('Generando los archivos bd3 revisados de la temperatura...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Temperatura\Temperatura_H_D_F5.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '6':
                print('Guardando todos los archivos de la carpeta análisis_datos en Data_Lake...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Temperatura\Temperatura_H_D_F6.py'], capture_output=True, text=True).stdout)
                # Aquí puedes llamar a tu script correspondiente 
            else:
                print("Opción no válida. Por favor, seleccione una opción válida.")

#------------------------------------------------------------------------------------------------------------------------------------------------------------

        elif opcion_etapa == '2':
            if opcion_FD == '1':
                print("Funcionalidad de la etapa 2 de la temperatura.")
            elif opcion_FD == '2':
                print('Esto deberia de imprimirse')
            else:
                print("Opción no válida. Por favor, seleccione una opción válida.")

            
    if opcion_variable == '2':
        if opcion_etapa == '1':
            if opcion_F == '1':
                print('Editando los archivos crudos de la humedad relativa...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Humedad_relativa\Humedad_H_D_F1.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '2':
                print('Depurando los archivos bd0 de la humedad relativa...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Humedad_relativa\Humedad_H_D_F2.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '3':
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Humedad_relativa\Humedad_H_D_F3.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '4':
                print('Detectando valores atípicos extremos y generando las figuras de los archivos bd2 de la humedad relativa...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Humedad_relativa\Humedad_H_D_F4.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '5':
                print('Generando los archivos bd3 revisados de la humedad relativa...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Humedad_relativa\Humedad_H_D_F5.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '6':
                print('Guardando todos los archivos de la carpeta análisis_datos en Data_Lake...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Humedad_relativa\Humedad_H_D_F6.py'], capture_output=True, text=True).stdout)  
            else:
                print("Opción no válida. Por favor, seleccione una opción válida.")

            
        elif opcion_etapa == '2':
              if opcion_FD == '1':
                  print("Funcionalidad de la etapa 2 de la humedad.")
              else:
                  print("Opción no válida. Por favor, seleccione una opción válida.")

                
    if opcion_variable == '3':
        if opcion_etapa == '1':
            if opcion_F == '1':
                print('Editando los archivos crudos de la presión atmosférica...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Presion_Atmosferica\Presion_H_F1.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '2':
                print('Depurando los archivos bd0 de la presión atmosférica...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Presion_Atmosferica\Presion_H_F2.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '3':
                print('Analizando y editando las fechas de los archivos bd1 de la presión atmosférica...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Presion_Atmosferica\Presion_H_F3.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '4':
                print('Detectando valores atípicos extremos y generando las figuras de los archivos bd2 de la presión atmosférica...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Presion_Atmosferica\Presion_H_F4.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '5':
                print('Generando los archivos bd3 revisados de la presión atmosférica...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Presion_Atmosferica\Presion_H_F5.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '6':
                print('Guardando todos los archivos de la carpeta análisis_datos en Data_Lake...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Presion_Atmosferica\Presion_H_F6.py'], capture_output=True, text=True).stdout)
            else:
                print("Opción no válida. Por favor, seleccione una opción válida.")

                
    if opcion_variable == '4':
        if opcion_etapa == '1':
            if opcion_F == '1':
                print('Editando los archivos crudos de la radiación solar...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Radiacion_Solar\Radiacion_H_F1.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '2':
                print('Depurando los archivos bd0 de la radiación solar...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Radiacion_Solar\Radiacion_H_F2.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '3':
                print('Analizando y editando las fechas de los archivos bd1 de la radiación solar...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Radiacion_Solar\Radiacion_H_F3.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '4':
                print('Detectando valores atípicos extremos y generando las figuras de los archivos bd2 de la radiación solar...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Radiacion_Solar\Radiacion_H_F4.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '5':
                print('Generando los archivos bd3 revisados de la radiación solar...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Radiacion_Solar\Radiacion_H_F5.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '6':
                print('Guardando todos los archivos de la carpeta análisis_datos en Data_Lake...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Radiacion_Solar\Radiacion_H_F6.py'], capture_output=True, text=True).stdout)
            else:
                print("Opción no válida. Por favor, seleccione una opción válida.")
                
    if opcion_variable == '5':
        if opcion_etapa == '1':
            if opcion_F == '1':
                print('Editando los archivos crudos de la lluvia...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Precipitacion\Precipitacion_H_D_F1.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '2':
                print('Depurando los archivos bd0 de la lluvia...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Precipitacion\Precipitacion_H_D_F2.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '3':
                print('Analizando y editando las fechas de los archivos bd1 de la lluvia...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Precipitacion\Precipitacion_H_D_F3.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '4':
                print('Detectando valores atípicos extremos y generando las figuras de los archivos bd2 de la lluvia...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Precipitacion\Precipitacion_H_D_F4.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '5':
                print('Generando los archivos bd3 revisados de la lluvia...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Precipitacion\Precipitacion_H_D_F5.py'], capture_output=True, text=True).stdout)
            elif opcion_F == '6':
                print('Guardando todos los archivos de la carpeta análisis_datos en Data_Lake...')
                print(subprocess.run(['python', r'C:\MeteoRBD.v1.0.0\scripts\Precipitacion\Precipitacion_H_D_F6.py'], capture_output=True, text=True).stdout)
            else:
                print("Opción no válida. Por favor, seleccione una opción válida.")

opcion_F = None
opcion_FD = None
if __name__ == "__main__":
    while True:
        print('')
        print('----------------------------------------------------------------------------------------Menú principal----------------------------------------------------------------------------')
        print('')
        print('Seleccione alguna variable:')
        print('')
        print(f"[1]: {Variable[0]}")
        print(f"[2]: {Variable[1]}")
        print(f"[3]: {Variable[2]}")
        print(f"[4]: {Variable[3]}")
        print(f"[5]: {Variable[4]}")
        print(f"[6]: {Variable[5]}")
        print('')
        opcion_variable = input("Ingrese el número de la variable deseada (q para salir): ")

        if opcion_variable in ['1', '2', '3', '4','5']:  
            while True:
                opcion_etapa = Etapas(Variable[int(opcion_variable) - 1])  # Pass the selected variable
                if opcion_etapa == 'r':
                    break  
                if opcion_etapa == '1':
                    while True:
                        opcion_F = Fases_Etapa_Uno(Variable[int(opcion_variable) - 1])  # Pass the selected variable
                        if opcion_F == 'r':
                            break
                        Etapas_scripts(opcion_variable, opcion_etapa, opcion_F, opcion_FD)
                elif opcion_etapa == '2':
                    while True:
                        opcion_FD = Fases_Etapa_Dos(Variable[int(opcion_variable) - 1])  # Pass the selected variable
                        if opcion_FD == 'r':
                            break
                        Etapas_scripts(opcion_variable, opcion_etapa, opcion_F, opcion_FD)
                
        elif opcion_variable == 'q':
            print('')
            print("Saliendo del programa...")
            sys.exit()
        else:
            print('')
            print("Variable no válida. Por favor, ingrese una opción válida.")
            print('')
            continue
            