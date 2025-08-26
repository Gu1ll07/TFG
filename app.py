import sys
import time
import serial
import sqlite3
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QComboBox, QLineEdit
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

# Intentar conectar con Arduino, si falla, activar modo simulación
try:
    arduino = serial.Serial('COM4', 115200, timeout=1)
    time.sleep(2)
    modo_simulacion = False
except serial.SerialException:
    print("⚠⚠⚠ No se encontró el la placa de Arduino | Modo simulación activado ⚠⚠⚠")
    modo_simulacion = True

# Conectar con SQLite
conn = sqlite3.connect("recorridos.db")
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

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.inicializar_interfaz()
        self.cargar_lista_recorridos()
    
    def inicializar_interfaz(self):
        self.setWindowTitle("Monitor de Arduino")
        self.showFullScreen() 
    
        layout = QVBoxLayout()
        
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)
        
        self.boton_leer = QPushButton("Leer Datos")
        self.boton_leer.clicked.connect(self.leer_nueva_medicion)
        layout.addWidget(self.boton_leer)
        
        self.boton_graficar = QPushButton("Graficar Recorrido")
        self.boton_graficar.clicked.connect(self.mostrar_grafico_recorrido)
        layout.addWidget(self.boton_graficar)
        
        self.boton_eliminar = QPushButton("Eliminar Última Medición")
        self.boton_eliminar.clicked.connect(self.eliminar_ultima_medicion)
        layout.addWidget(self.boton_eliminar)
        
        self.campo_nombre_recorrido = QLineEdit()
        self.campo_nombre_recorrido.setPlaceholderText("Nombre del recorrido")
        layout.addWidget(self.campo_nombre_recorrido)
        
        self.boton_guardar = QPushButton("Guardar Recorrido")
        self.boton_guardar.clicked.connect(self.guardar_recorrido_actual)
        layout.addWidget(self.boton_guardar)
        
        self.lista_recorridos = QComboBox()
        layout.addWidget(self.lista_recorridos)
        
        self.boton_cargar = QPushButton("Cargar Recorrido")
        self.boton_cargar.clicked.connect(self.cargar_recorrido_seleccionado)
        layout.addWidget(self.boton_cargar)
        
        self.boton_modificar = QPushButton("Modificar Recorrido")
        self.boton_modificar.clicked.connect(self.modificar_recorrido_actual)
        layout.addWidget(self.boton_modificar)
        
        self.setLayout(layout)
    
    def leer_nueva_medicion(self):
        global recorrido_actual
        if modo_simulacion:
            distancia = np.random.uniform(1, 10)
            azimut = np.random.uniform(0, 360)
            pitch = np.random.uniform(-90, 90)
        else:
            datos = arduino.readline().decode('utf-8').strip()
            if not datos:
                return
            datos = datos.split(',')
            if len(datos) != 4:
                self.text_area.append(f"Formato incorrecto recibido: {datos}")
                return
            try:
                distancia, azimut, pitch, _ = map(float, datos)
            except ValueError:
                self.text_area.append("Error al convertir datos a float")
                return
        
        punto_siguiente = self.calcular_siguiente_punto(recorrido_actual[-1] if recorrido_actual else (0,0,0), distancia, azimut, pitch)
        if len(recorrido_actual) >= MAX_PUNTOS:
            recorrido_actual.pop(0)
        recorrido_actual.append(punto_siguiente)
        self.text_area.append(f"Punto añadido: {punto_siguiente}")
    
    def calcular_siguiente_punto(self, punto_actual, distancia, azimut, pitch):
        x = punto_actual[0] + distancia * np.cos(np.radians(azimut)) * np.cos(np.radians(pitch))
        y = punto_actual[1] + distancia * np.sin(np.radians(azimut)) * np.cos(np.radians(pitch))
        z = punto_actual[2] + distancia * np.sin(np.radians(pitch))
        return (x, y, z)
    
    def mostrar_grafico_recorrido(self):
        if len(recorrido_actual) < 2:
            self.text_area.append("No hay suficientes puntos para graficar.")
            return
        
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.scatter(*zip(*recorrido_actual), c='blue')
        for i in range(len(recorrido_actual) - 1):
            p1, p2 = recorrido_actual[i], recorrido_actual[i + 1]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], 'r-')
        plt.show()
    
    def eliminar_ultima_medicion(self):
        if len(recorrido_actual) > 1:
            punto_eliminado = recorrido_actual.pop()
            self.text_area.append(f"Última medición eliminada: {punto_eliminado}")
        else:
            self.text_area.append("No hay puntos suficientes para eliminar.")
    
    def guardar_recorrido_actual(self):
        global recorrido_actual
        nombre = self.campo_nombre_recorrido.text().strip()
        if not nombre:
            self.text_area.append("⚠ Ingresa un nombre para el recorrido.")
            return
        datos = str(recorrido_actual)
        c.execute("INSERT INTO recorridos (nombre, datos) VALUES (?, ?) ON CONFLICT(nombre) DO UPDATE SET datos = excluded.datos", (nombre, datos))
        conn.commit()
        self.lista_recorridos.addItem(nombre)
        self.text_area.append(f"Recorrido guardado como {nombre}")
    
    def cargar_lista_recorridos(self):
        c.execute("SELECT nombre FROM recorridos")
        for row in c.fetchall():
            self.lista_recorridos.addItem(row[0])
    
    def cargar_recorrido_seleccionado(self):
        global recorrido_actual
        nombre = self.lista_recorridos.currentText()
        c.execute("SELECT datos FROM recorridos WHERE nombre = ?", (nombre,))
        row = c.fetchone()
        if row:
            recorrido_actual = eval(row[0])
            self.text_area.append(f"Recorrido {nombre} cargado")
    
    def modificar_recorrido_actual(self):
        self.guardar_recorrido_actual()
        self.text_area.append("Recorrido modificado correctamente.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = App()
    ventana.show()
    sys.exit(app.exec_())
