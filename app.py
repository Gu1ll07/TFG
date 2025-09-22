import flet as ft
import sqlite3
import numpy as np
import time
import serial
import plotly.graph_objs as go

# Imagen transparente 1x1 para inicializar el componente Image
TRANSPARENTE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAqMB9Ym5i+MAAAAASUVORK5CYII="

# Intentar conectar con Arduino, si falla, activar simulación
try:
    arduino = serial.Serial("COM4", 115200, timeout=1)
    time.sleep(2)
    modo_simulacion = False
except serial.SerialException:
    print("⚠ No se encontró Arduino | Modo simulación activado ⚠")
    modo_simulacion = True

# Conectar a SQLite
conn = sqlite3.connect("recorridos.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS recorridos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE,
        datos TEXT
    )
""")
conn.commit()

recorrido_actual = []
MAX_PUNTOS = 6

def app(page: ft.Page):
    page.title = "Monitor de Arduino 🚀"
    page.scroll = "adaptive"
    page.theme_mode = "dark"

    output = ft.Text(value="Bienvenido 👋", size=16)
    nombre_input = ft.TextField(label="Nombre del recorrido")
    recorridos_dropdown = ft.Dropdown()

    # Imagen inicial transparente
    # grafico = ft.Image(width=400, height=400, src_base64=TRANSPARENTE_BASE64)
    grafico = ft.PlotlyChart(
        figure=go.Figure(),
        width=400,
        height=400
    )

    # Función para refrescar lista de recorridos
    def cargar_lista():
        recorridos_dropdown.options.clear()
        c.execute("SELECT nombre FROM recorridos")
        for row in c.fetchall():
            recorridos_dropdown.options.append(ft.dropdown.Option(row[0]))
        page.update()

    cargar_lista()

    # Leer nueva medición
    def leer_click(e):
        global recorrido_actual
        if modo_simulacion:
            distancia = np.random.uniform(1, 10)
            azimut = np.random.uniform(0, 360)
            pitch = np.random.uniform(-90, 90)
        else:
            datos = arduino.readline().decode("utf-8").strip()
            if not datos:
                return
            datos = datos.split(",")
            if len(datos) != 4:
                output.value = f"Formato incorrecto: {datos}"
                page.update()
                return
            try:
                distancia, azimut, pitch, _ = map(float, datos)
            except ValueError:
                output.value = "Error al convertir datos"
                page.update()
                return

        punto_siguiente = calcular_punto(
            recorrido_actual[-1] if recorrido_actual else (0, 0, 0),
            distancia, azimut, pitch
        )

        if len(recorrido_actual) >= MAX_PUNTOS:
            recorrido_actual.pop(0)
        recorrido_actual.append(punto_siguiente)

        output.value = f"Punto añadido: {punto_siguiente}"
        page.update()

    # Calcular punto
    def calcular_punto(punto_actual, distancia, azimut, pitch):
        x = punto_actual[0] + distancia * np.cos(np.radians(azimut)) * np.cos(np.radians(pitch))
        y = punto_actual[1] + distancia * np.sin(np.radians(azimut)) * np.cos(np.radians(pitch))
        z = punto_actual[2] + distancia * np.sin(np.radians(pitch))
        return (x, y, z)

    # Graficar recorrido 3D
    def graficar_click(e):
        if len(recorrido_actual) < 2:
            output.value = "No hay suficientes puntos para graficar"
            page.update()
            return
        x, y, z = zip(*recorrido_actual)
        fig = go.Figure()
        fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='markers+lines', marker=dict(size=5, color='blue'), line=dict(color='red')))
        fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
        grafico.figure = fig
        page.update()

    # Guardar recorrido
    def guardar_click(e):
        global recorrido_actual
        nombre = nombre_input.value.strip()
        if not nombre:
            output.value = "⚠ Ingresa un nombre"
            page.update()
            return
        datos = str(recorrido_actual)
        c.execute("""
            INSERT INTO recorridos (nombre, datos)
            VALUES (?, ?)
            ON CONFLICT(nombre) DO UPDATE SET datos=excluded.datos
        """, (nombre, datos))
        conn.commit()
        output.value = f"Recorrido guardado como {nombre}"
        cargar_lista()
        page.update()

    # Cargar recorrido
    def cargar_click(e):
        global recorrido_actual
        nombre = recorridos_dropdown.value
        c.execute("SELECT datos FROM recorridos WHERE nombre=?", (nombre,))
        row = c.fetchone()
        if row:
            recorrido_actual = eval(row[0])
            output.value = f"Recorrido {nombre} cargado"
            page.update()

    # Eliminar último
    def eliminar_click(e):
        if len(recorrido_actual) > 1:
            eliminado = recorrido_actual.pop()
            output.value = f"Último eliminado: {eliminado}"
        else:
            output.value = "No hay puntos suficientes"
        page.update()

    # Layout
    page.add(
        ft.Column([
            output,
            ft.Row([
                ft.ElevatedButton("Leer Datos", on_click=leer_click),
                ft.ElevatedButton("Graficar Recorrido", on_click=graficar_click),
            ]),
            ft.Row([
                ft.ElevatedButton("Eliminar Última", on_click=eliminar_click),
                ft.ElevatedButton("Guardar Recorrido", on_click=guardar_click),
            ]),
            nombre_input,
            recorridos_dropdown,
            ft.ElevatedButton("Cargar Recorrido", on_click=cargar_click),
            grafico
        ], spacing=15, alignment="center")
    )

if __name__ == "__main__":
    ft.app(target=app, view=ft.AppView.FLET_APP)
