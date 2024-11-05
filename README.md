English

MeteoRBD - Quality Control Program for Meteorological Data
Overview
MeteoRBD is a specialized Python program developed to facilitate the quality control and review of meteorological data stored in institutional databases. The program is designed to streamline the process, improving data integrity and efficiency for meteorological analyses. It includes structured modules that guide users through data formatting, cleaning, validation, analysis, and backup.

Objective
The purpose of MeteoRBD is to provide a reliable tool for systematically performing quality control on meteorological datasets. Through structured phases, the program processes raw data, identifies and corrects anomalies, and ensures accurate storage, ultimately supporting high-quality data analysis.

Features and Structure
Installation
Requirements:

Python 3.12.x (included in the Instalación folder).
Necessary Python libraries, which can be installed using the get-pip.py file.
Folder Structure:

MeteoRBD executable.
Instalación: Contains Python installation files and instructions.
códigos: Holds Python scripts for various meteorological variables (e.g., temperature, humidity).
datos_rbd: Stores the raw data files for processing.
revisión: Temporary storage for data under review.
Usage Guide
Data Preparation:

Place the daily and hourly datasets for a specific weather station in the datos_rbd folder. Ensure file names and formats remain unaltered for successful analysis.
Execution:

Run the executable to open a command-line interface with options for selecting variables and processing stages.
Stages of Processing:

Stage 1: Data Formatting
Formats files to include consistent timestamp columns, standardized variable names, and saves outputs in .csv format.
Stage 2: Data Cleaning
Detects outliers, missing values, and incorrect station identifiers, logging adjustments in dedicated files for traceability.
Stage 3: Date and Timestamp Analysis
Fills missing timestamps, removes duplicates, and logs any corrections. Outputs a clean version of the data for further analysis.
Stage 4: Extreme Value Detection
Generates statistical summaries and visualizations (e.g., box plots) to detect extreme values. Monthly summaries and adjustments are logged for documentation.
Stage 5: Final Data Preparation
Applies corrections from previous stages to generate a fully reviewed dataset, prepared for integration with the institutional database.
Stage 6: Data Backup
Finalized files are stored in a secure location, ensuring traceable and organized storage of processed data.
Risks and Precautions
Unauthorized Modifications: The integrity of the data depends on careful handling, avoiding unintended changes to raw or processed files.
Data Loss: To prevent loss, intermediate files are preserved through each processing phase until the final review is complete.
Outlier Detection Accuracy: The algorithms used are sensitive to predefined thresholds and may require adjustment to avoid excluding valid data points.
Usage Notes
Backups: Once Stage 6 is complete, data in datos_rbd can be safely removed for a fresh analysis cycle.
Restoration: If additional corrections are needed, users can edit specific files from Stage 4 and rerun Stage 5.

Español

MeteoRBD - Programa de Control de Calidad para Datos Meteorológicos
Resumen
MeteoRBD es un programa especializado en Python desarrollado para facilitar el control de calidad y la revisión de datos meteorológicos almacenados en bases de datos institucionales. Este programa permite optimizar el proceso, mejorando la integridad de los datos y facilitando un análisis meteorológico preciso. MeteoRBD guía a los usuarios a través de módulos estructurados para formateo, limpieza, validación, análisis y respaldo de datos.

Objetivo
El objetivo de MeteoRBD es proporcionar una herramienta fiable para realizar el control de calidad en conjuntos de datos meteorológicos de manera sistemática. A través de fases estructuradas, el programa procesa los datos crudos, identifica y corrige anomalías, y asegura el almacenamiento preciso, apoyando un análisis de datos de alta calidad.

Funciones y Estructura
Instalación
Requisitos:

Python 3.12.3 (incluido en la carpeta Instalación).
Librerías de Python necesarias, que se pueden instalar usando el archivo get-pip.py.
Estructura de Carpetas:

MeteoRBD ejecutable.
Instalación: Contiene archivos e instrucciones de instalación de Python.
códigos: Almacena los scripts de Python para varias variables meteorológicas (e.g., temperatura, humedad).
datos_rbd: Guarda los archivos de datos crudos para el procesamiento.
revisión: Almacenamiento temporal para los datos en revisión.
Guía de Uso
Preparación de Datos:

Colocar los conjuntos de datos diarios y horarios de una estación meteorológica específica en la carpeta datos_rbd. Es importante no cambiar el nombre o formato de los archivos para asegurar un análisis exitoso.
Ejecución:

Ejecutar el programa para abrir una interfaz de línea de comandos con opciones para seleccionar variables y etapas de procesamiento.
Fases del Procesamiento:

Fase 1: Formateo de Datos
Formatea los archivos para incluir columnas consistentes de timestamps, nombres estandarizados de variables, y guarda los archivos en formato .csv.
Fase 2: Limpieza de Datos
Detecta valores atípicos, datos faltantes y errores en los identificadores de estaciones, registrando los ajustes en archivos dedicados para asegurar la trazabilidad.
Fase 3: Análisis y Corrección de Fechas
Completa los timestamps faltantes, elimina duplicados y registra cualquier corrección realizada. Genera una versión limpia de los datos para el análisis.
Fase 4: Detección de Valores Extremos
Genera resúmenes estadísticos y visualizaciones (como diagramas de caja) para detectar valores extremos. Los resúmenes mensuales y ajustes se registran para su documentación.
Fase 5: Preparación Final de Datos
Aplica las correcciones de fases previas para generar un conjunto de datos revisado, listo para su integración en la base de datos institucional.
Fase 6: Respaldo de Datos
Los archivos finales se almacenan en una ubicación segura, garantizando un respaldo organizado y trazable de los datos procesados.
Riesgos y Precauciones
Modificaciones No Autorizadas: La integridad de los datos depende de un manejo cuidadoso, evitando cambios no intencionados en archivos crudos o procesados.
Pérdida de Datos: Para prevenir la pérdida de datos, los archivos intermedios se preservan en cada fase de procesamiento hasta completar la revisión final.
Precisión en la Detección de Valores Atípicos: Los algoritmos utilizados son sensibles a umbrales predefinidos y pueden requerir ajustes para evitar la exclusión de datos válidos.
Notas de Uso
Respaldo: Una vez que la Fase 6 está completa, los datos en datos_rbd pueden eliminarse de manera segura para un nuevo ciclo de análisis.
Restauración: Si se requieren correcciones adicionales, los usuarios pueden editar archivos específicos de la Fase 4 y volver a ejecutar la Fase 5.
