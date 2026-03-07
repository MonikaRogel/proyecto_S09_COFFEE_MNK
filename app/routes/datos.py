from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
import json
import csv
import re

bp = Blueprint("datos", __name__, url_prefix="/datos")

# Ruta base del proyecto (raíz)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(BASE_DIR, 'inventario', 'data')
print("DATA_DIR:", DATA_DIR)  # Para depuración

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
    print("Carpeta asegurada:", DATA_DIR)

def validar_nombre(nombre):
    """Solo letras y espacios"""
    return re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$', nombre) is not None

def validar_cedula(cedula):
    """Exactamente 10 dígitos numéricos"""
    return re.match(r'^\d{10}$', cedula) is not None

def validar_telefono(telefono):
    """Comienza con 09 y 10 dígitos en total"""
    return re.match(r'^09\d{8}$', telefono) is not None

@bp.route("/", methods=["GET", "POST"])
def index():
    ensure_data_dir()
    if request.method == "POST":
        print("POST recibido:", request.form)
        nombre = request.form.get("nombre", "").strip()
        cedula = request.form.get("cedula", "").strip()
        email = request.form.get("email", "").strip()
        telefono = request.form.get("telefono", "").strip()

        # Validaciones
        if not nombre:
            flash("El nombre es obligatorio", "error")
        elif not validar_nombre(nombre):
            flash("El nombre solo puede contener letras y espacios", "error")
        elif cedula and not validar_cedula(cedula):
            flash("La cédula debe tener exactamente 10 dígitos numéricos", "error")
        elif telefono and not validar_telefono(telefono):
            flash("El teléfono debe comenzar con 09 y tener 10 dígitos (ej. 0991234567)", "error")
        else:
            # Guardar en TXT
            txt_path = os.path.join(DATA_DIR, "datos.txt")
            with open(txt_path, "a", encoding="utf-8") as f:
                f.write(f"{nombre},{cedula},{email},{telefono}\n")
            print("TXT guardado en:", txt_path)
            
            # Guardar en JSON
            json_path = os.path.join(DATA_DIR, "datos.json")
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = []
            data.append({"nombre": nombre, "cedula": cedula, "email": email, "telefono": telefono})
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("JSON guardado en:", json_path)
            
            # Guardar en CSV
            csv_path = os.path.join(DATA_DIR, "datos.csv")
            file_exists = os.path.isfile(csv_path)
            with open(csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["nombre", "cedula", "email", "telefono"])
                writer.writerow([nombre, cedula, email, telefono])
            print("CSV guardado en:", csv_path)
            
            flash("Datos guardados correctamente", "success")
            return redirect(url_for("datos.index"))
    
    # Leer datos de los archivos para mostrarlos
    datos_txt = []
    txt_path = os.path.join(DATA_DIR, "datos.txt")
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(",")
                if len(partes) == 4:
                    datos_txt.append({
                        "nombre": partes[0],
                        "cedula": partes[1],
                        "email": partes[2],
                        "telefono": partes[3]
                    })
    
    datos_json = []
    json_path = os.path.join(DATA_DIR, "datos.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                datos_json = json.load(f)
        except:
            pass
    
    datos_csv = []
    csv_path = os.path.join(DATA_DIR, "datos.csv")
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            datos_csv = list(reader)
    
    return render_template("datos.html", 
                           titulo="Persistencia con archivos",
                           datos_txt=datos_txt,
                           datos_json=datos_json,
                           datos_csv=datos_csv)