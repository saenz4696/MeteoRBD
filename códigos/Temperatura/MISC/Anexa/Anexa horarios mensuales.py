import pandas as pd
import os
import re
import warnings

# General paths
warnings.simplefilter('ignore', category=UserWarning)
raw_data_path = r'C:\\MeteoRBD.v1.0.0\\raw_data_rbd'

# Find the .xlsx file containing 'Cuenca' and 'Estación' as columns in raw_data_path
xlsx_file = next((os.path.join(raw_data_path, file) for file in os.listdir(raw_data_path) if file.endswith(".xlsx")), None)

if xlsx_file:
    excel_data = pd.read_excel(xlsx_file)
    if all(col in excel_data.columns for col in ['Cuenca', 'Estación']):
        # Extract station number from the Excel file
        cuenca = str(excel_data['Cuenca'].iloc[0])
        estacion = str(excel_data['Estación'].iloc[0])
        if len(estacion) == 2:
            estacion = '0' + estacion  # Add leading zero if 'Estación' has only two digits
        station_number = cuenca + estacion
        station_number = int(station_number)

# Set path for temperature files based on station number from the Excel file
temperature_analysis_path = f"C:\\MeteoRBD.v1.0.0\\Data_Lake\\{station_number}-ema\\base_datos\\Temperatura\\análisis_datos"

# Create folders if they don't exist
for folder in ["", "Pruebas_estadisticas"]:
    folder_path = os.path.join(temperature_analysis_path, folder)
    os.makedirs(folder_path, exist_ok=True)

months_names = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

# Define a function to process temperature data
def process_temperature_files():
    processed_files = False  # Variable to control if files were processed
    
    # Iterate over month names
    for month_name in months_names:
        # Find folders containing month names within the Pruebas_estadisticas folder
        month_folders = [folder for folder in os.listdir(os.path.join(temperature_analysis_path, "Pruebas_estadisticas")) if re.search(month_name, folder, re.IGNORECASE)]
        
        # Iterate over found month folders
        for month_folder in month_folders:
            month_folder_path = os.path.join(temperature_analysis_path, "Pruebas_estadisticas", month_folder)
        
            # Find .csv temperature files in the month folder
            temperature_files = [file for file in os.listdir(month_folder_path) if file.endswith(".csv") and '_T_h' in file]

            for temperature_file in temperature_files:
                temperature_file_path = os.path.join(month_folder_path, temperature_file)

                # Read the .csv file and perform cleaning and timestamp correction operations
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    df_temperature = pd.read_csv(temperature_file_path)

                # Find the bd2 file in the main folder
                bd2_file_path = next((os.path.join(temperature_analysis_path, file) for file in os.listdir(temperature_analysis_path) if file.endswith(".csv") and 'T.h.bd2' in file), None)

                if bd2_file_path:
                    # Read the bd2 file
                    df_bd2 = pd.read_csv(bd2_file_path)

                    # Iterate over 'valor_reemplazo_T_h' values and update df_bd2
                    for index, row in df_temperature.iterrows():
                        timestamp_temperature = row['FECHA']
                        element_temperature = row['ELEMENTO']
                        replacement_value_temperature = row['Valor_reemplazo']

                        # Fill NaN or NA values with the original value
                        df_bd2.loc[(df_bd2['TIMESTAMP'] == timestamp_temperature) & (df_bd2[element_temperature].isna()), element_temperature] = replacement_value_temperature

                        # Update the value in df_bd2
                        df_bd2.loc[df_bd2['TIMESTAMP'] == timestamp_temperature, element_temperature] = replacement_value_temperature

                    # Create the new file
                    start_time = pd.to_datetime(df_bd2['TIMESTAMP'].min())
                    end_time = pd.to_datetime(df_bd2['TIMESTAMP'].max())
                    revised_file_name = f"{station_number}.{start_time.strftime('%Y%m%d-%H')}.{end_time.strftime('%Y%m%d-%H')}.T.h.bd3.csv"
                    revised_file_path = os.path.join(temperature_analysis_path, revised_file_name)
                    
                    # Save the updated DataFrame to a CSV file
                    df_bd2.to_csv(revised_file_path, index=False, na_rep='NA')
                    processed_files = True

    if processed_files:
        print('-----------------------------------------------------------------------------------------------------------')
        print('Successfully generated the revised files for hourly temperature.')
        print('')
        return True
    else:
        print('-----------------------------------------------------------------------------------------------------------')
        print("No temperature files T_h.csv were found in any month folder.")
        return False

process_temperature_files()
