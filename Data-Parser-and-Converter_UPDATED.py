import PySimpleGUI as sg
import logging, numpy, os
from pathlib import Path
import pandas as pd
import xml.etree.ElementTree as ET
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create a rotating file handler
file_handler = RotatingFileHandler(filename="GUI_Log.log",
                                   maxBytes=25 * 1024 * 1024,  # Max File Size: 25 MB
                                   backupCount=2,  # Number of backup files to keep
                                   encoding="utf-8",  # Specify the encoding if needed
                                   delay=False)  # Set to True if you want to delay file opening
# Define the log format
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s",
                              datefmt="Date: %d-%m-%Y Time: %H:%M:%S")
# Set the formatter for the file handler
file_handler.setFormatter(formatter)

# Create a logger and add the file handler
logger = logging.getLogger()
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)  # Set the desired log level

# Define a mapping of file extensions to corresponding read and write functions
CONVERSION_FUNCTIONS = {
    ("csv", "xml"): (pd.read_csv, pd.DataFrame.to_xml),
    ("xml", "csv"): (pd.read_xml, pd.DataFrame.to_csv),
    ("csv","md"): (pd.read_csv,pd.DataFrame.to_markdown),
    ("xml", "md"): (pd.read_xml, pd.DataFrame.to_markdown),
    ("csv","json"): (pd.read_csv,pd.DataFrame.to_json),
    ("xml","json"): (pd.read_xml,pd.DataFrame.to_json),
    ("json","csv"): (pd.read_json,pd.DataFrame.to_csv),
    ("json","xml"): (pd.read_json,pd.DataFrame.to_xml)
}

# Generic conversion function
def convert_files(input_path, output_path, input_ext, output_ext):
    try:
        read_func, write_func = CONVERSION_FUNCTIONS.get((input_ext, output_ext), (None, None))
        if read_func is None or write_func is None:
            window["-OUTPUT_WINDOW-"].print(">>> Unsupported conversion!")
            return
        
        df = read_func(input_path)
        write_func(df, output_path)
        window["-OUTPUT_WINDOW-"].print(
            f"Successfully converted {Path(input_path).stem} {input_ext.upper()} "
            f"to {Path(output_path).stem} {output_ext.upper()}"
        )
        logger.info(
            f">>> Successfully converted {Path(input_path).stem} {input_ext.upper()} "
            f"to {Path(output_path).stem} {output_ext.upper()}"
        )
    except FileNotFoundError:
        window["-OUTPUT_WINDOW-"].print(f">>> {input_ext.upper()} File not found!")

# Function to read input files with Pandas 
def read_file_data(file):
    
    file_suffix_in = Path(file).suffix.upper().strip(".")
    
    if file_suffix_in == "CSV":
        file_csv = pd.read_csv(file,index_col=None,engine="python")
        window["-OUTPUT_WINDOW-"].print(file_csv)
        
    elif file_suffix_in == "XML":
        file_xml = pd.read_xml(file)
        window["-OUTPUT_WINDOW-"].print(file_xml)
    
    elif file_suffix_in == "":
        window["-OUTPUT_WINDOW-"].print(">>> Error Input is empty, cannot read nothing!")

# Graphical User Interface settings #

# Add your new theme colors and settings
my_new_theme = {"BACKGROUND": "#3d3f46",
                "TEXT": "#d2d2d3",
                "INPUT": "#1c1e23",
                "TEXT_INPUT": "#d2d2d3",
                "SCROLL": "#1c1e23",
                "BUTTON": ("#e6d922", "#313641"),
                "PROGRESS": ("#e6d922", "#4a6ab3"),
                "BORDER": 1,
                "SLIDER_DEPTH": 0,
                "PROGRESS_DEPTH": 0}
# Add your dictionary to the PySimpleGUI themes
sg.theme_add_new("MyYellow", my_new_theme)

# Switch your theme to use the newly added one. You can add spaces to make it more readable
sg.theme("MyYellow")
font = ("Consolas", 16)

# Graphical User Interface layout #
MENU_RIGHT_CLICK = ["",["Clear Output", "Version", "Exit"]]
FILE_TYPES_OUTPUT = (("CSV (Comma Seperated Value)", ".csv"),("XML (Extensible Markup Language)",".xml"),("JSON (JavaScript Object Notation)",".json"),("Markdown",".md"),("Configuration-File",".config"))
FILE_TYPES_INPUT = (("CSV (Comma Seperated Value)", ".csv"),("XML (Extensible Markup Language)",".xml"),("JSON (JavaScript Object Notation)",".json"),("Configuration-File",".config"))


layout = [[sg.Text("Data Parser and Converter",font="Consolas 28 bold underline",text_color="#1d77eb")],
          [sg.Text()],
          [sg.Text("Select an input file for conversion:")],
          [sg.Text("Input:"),sg.Input(size=(43,1),key="-FILE_INPUT-"),sg.FileBrowse(file_types=FILE_TYPES_INPUT),sg.Button("Read",key="-READ_FILE-")],
          [sg.Text("Convert the input file to a different one:")],
          [sg.Text("Output:"),sg.Input(size=(42,1),key="-FILE_OUTPUT-"),sg.FileSaveAs(button_text="Save as",file_types=FILE_TYPES_OUTPUT,target="-FILE_OUTPUT-",key="-SAVE_AS_BUTTON-"),sg.Button("Save",key="-SAVE-")],
          [sg.Multiline(size=(80,15),key="-OUTPUT_WINDOW-")],
          [sg.Button("Exit",expand_x=True)]]

window = sg.Window("Data Parser and Converter",layout,font=font, finalize=True,right_click_menu=MENU_RIGHT_CLICK)

# Main Window events and functionality #
while True:
    event,values = window.read()
    
    if event == sg.WIN_CLOSED or event == "Exit":
        break
    
    # VARIABLES #
    input_path = values["-FILE_INPUT-"]
    output_path = values["-FILE_OUTPUT-"]
    input_ext = Path(input_path).suffix.lower().strip(".")
    output_ext = Path(output_path).suffix.lower().strip(".")

    if event == "-READ_FILE-":
        window.perform_long_operation(lambda: read_file_data(input_path), "-OUTPUT_WINDOW-")
    elif event == "-SAVE-":
        window.perform_long_operation(lambda: convert_files(input_path, output_path, input_ext, output_ext), "-OUTPUT_WINDOW-")

    
window.close() # Kill program