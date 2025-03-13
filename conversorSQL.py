import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog

def inferir_tipo_sql(serie):
    """Inferir el tipo de dato SQL basado en los valores de la columna."""
    if pd.api.types.is_integer_dtype(serie.dropna()):
        return "INT"
    elif pd.api.types.is_float_dtype(serie.dropna()):
        return "FLOAT"
    else:
        return "NVARCHAR(255)"  # Texto por defecto

def excel_a_sql():
    """Permite al usuario seleccionar un archivo Excel y generar un SQL dinámico."""
    # Abrir ventana para seleccionar archivo
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal de Tkinter
    archivo_excel = filedialog.askopenfilename(title="Seleccione un archivo Excel", filetypes=[("Archivos Excel", "*.xlsx;*.xls")])
    
    if not archivo_excel:  # Si el usuario no selecciona archivo, salir
        print("No se seleccionó ningún archivo.")
        return
    
    # Pedir al usuario el nombre del archivo SQL de salida
    nombre_sql = input("Ingrese el nombre del archivo SQL (sin extensión): ") + ".sql"

    # Cargar el archivo Excel
    df = pd.read_excel(archivo_excel)

    # Inferir los tipos de datos de cada columna
    tipos_sql = {col: inferir_tipo_sql(df[col]) for col in df.columns}

    # Crear la sentencia CREATE TABLE
    nombre_tabla = nombre_sql.replace(".sql", "")  # Usar el nombre del archivo como nombre de tabla
    sql_create = f"CREATE TABLE [{nombre_tabla}] (\n"
    sql_create += ",\n".join([f"    [{col}] {tipo_sql} NULL" for col, tipo_sql in tipos_sql.items()])
    sql_create += "\n);\n"

    # Generar los valores del INSERT
    columnas = ", ".join([f"[{col}]" for col in df.columns])
    sql_insert = f"INSERT INTO [{nombre_tabla}] ({columnas}) VALUES \n"

    valores = []
    for _, row in df.iterrows():
        fila = []
        for col in df.columns:
            valor = row[col]
            if pd.isna(valor):  # Manejo de NULL
                fila.append("NULL")
            elif isinstance(valor, str):  # Manejo de texto
                fila.append(f"N'{valor.replace("'", "''")}'")  
            else:  # Número (int o float)
                fila.append(str(valor))
        valores.append(f"    ({', '.join(fila)})")

    # Unir todos los valores en una sola sentencia INSERT
    sql_insert += ",\n".join(valores) + ";\n"

    # Unir todo el SQL final
    sql_final = sql_create + sql_insert

    # Guardar el SQL en un archivo
    with open(nombre_sql, "w", encoding="utf-8") as f:
        f.write(sql_final)

    print(f"Archivo '{nombre_sql}' generado correctamente.")

# Ejecutar la función para pedir archivo y generar SQL
excel_a_sql()
