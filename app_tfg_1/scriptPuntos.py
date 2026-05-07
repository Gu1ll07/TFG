import matplotlib.pyplot as plt
import numpy as np
import serial.tools.list_ports
import serial
import time
import keyboard  # Librería para detectar teclas
from mpl_toolkits.mplot3d import proj3d

# =========================
#  CONFIGURACIÓN / MODOS
# =========================

MAX_PUNTOS = 6        # Límite de puntos en la lista
SIMULACION = False    # Se activará si no se puede abrir el puerto serie
arduino = None

def detectar_puerto_arduino():
    """
    Detecta automáticamente un puerto serie compatible con Arduino.
    Devuelve el nombre del puerto si lo encuentra, o None si no detecta ninguno.
    """

    puertos = list(serial.tools.list_ports.comports())

    if not puertos:
        return None

    print("Puertos serie detectados:")
    for puerto in puertos:
        print(f"   - {puerto.device}: {puerto.description}")

    # Primero se prueban puertos habituales en este proyecto
    puertos_preferidos = ["COM4", "COM3", "COM5"]

    for nombre_puerto in puertos_preferidos:
        for puerto in puertos:
            if puerto.device == nombre_puerto:
                return puerto.device

    # Después se buscan descripciones típicas de Arduino o adaptadores USB-serie
    palabras_clave = [
        "arduino",
        "ch340",
        "usb serial",
        "usb-serial",
        "cp210",
        "silicon labs",
        "ftdi"
    ]

    for puerto in puertos:
        descripcion = puerto.description.lower()

        if any(palabra in descripcion for palabra in palabras_clave):
            return puerto.device

    return None

def conectar_arduino():
    """
    Intenta conectar con Arduino.
    Si no se detecta o no se puede abrir el puerto, activa el modo simulación.
    """

    global SIMULACION
    global arduino

    puerto = detectar_puerto_arduino()

    if puerto is None:
        SIMULACION = True
        arduino = None
        print("⚠️  No se ha detectado Arduino. Entrando en MODO SIMULACIÓN.")
        return

    try:
        arduino = serial.Serial(puerto, 115200, timeout=1)
        time.sleep(2)
        SIMULACION = False
        print(f"✅ MODO REAL: Conectado a Arduino en {puerto}")

    except (serial.SerialException, OSError) as error:
        SIMULACION = True
        arduino = None
        print(f"⚠️  No se ha podido abrir el puerto {puerto}.")
        print(f"Detalle del error: {error}")
        print("Entrando en MODO SIMULACIÓN.")

conectar_arduino()

# Lista para almacenar puntos (empezamos en el origen)
puntos = [(0.0, 0.0, 0.0)]

# Variable para debouncing de 'c' y 'r'
key_pressed = False


# =========================
#  FUNCIONES PRINCIPALES
# =========================

def leer_datos():
    """
    Devuelve (distancia, azimut, pitch, roll)
    - En modo REAL: lee de Arduino.
    - En modo SIMULACIÓN: genera datos al pulsar 'P'.
    """
    global SIMULACION, arduino

    # ---------- MODO SIMULACIÓN ----------
    if SIMULACION:
        # Solo generamos datos cuando el usuario pulsa 'P'
        if keyboard.is_pressed('p'):
            distancia = np.random.uniform(1.0, 30.0)
            azimut = np.random.uniform(0, 360)     # º
            pitch = np.random.uniform(-30, 30)     # º
            roll = np.random.uniform(-10, 10)      # º (ahora no lo usamos)
            print(f"[SIM] Distancia={distancia:.2f}, Azimut={azimut:.2f}, Pitch={pitch:.2f}, Roll={roll:.2f}")
            time.sleep(0.2)  # evita múltiples lecturas de una misma pulsación
            return distancia, azimut, pitch, roll
        else:
            return None

    # ---------- MODO REAL (ARDUINO) ----------
    if arduino is None:
        return None

    try:
        datos = arduino.readline().decode('utf-8', errors='ignore').strip()
    except serial.SerialException as e:
        print(f"Error leyendo de Arduino: {e}")
        return None

    if not datos:
        return None
    
    if datos in ["READY", "ERROR_BNO055", "ERROR_LASER"]:
        print(f"Mensaje Arduino: {datos}")
        return None

    partes = datos.split(',')
    if len(partes) != 4:
        print(f"Formato incorrecto recibido: {partes}")
        return None

    try:
        distancia = float(partes[0])
        azimut    = float(partes[1])
        pitch     = float(partes[2])
        roll      = float(partes[3])
        return distancia, azimut, pitch, roll
    except ValueError:
        print(f"No se pudo convertir a float: {partes}")
        return None

def calcular_punto_siguiente(punto_actual, distancia, azimut, pitch):
    x = punto_actual[0] + distancia * np.cos(np.radians(azimut)) * np.cos(np.radians(pitch))
    y = punto_actual[1] + distancia * np.sin(np.radians(azimut)) * np.cos(np.radians(pitch))
    z = punto_actual[2] + distancia * np.sin(np.radians(pitch))
    return (float(x), float(y), float(z))

"""Devuelve un punto 3D, sin muchos decimales, en formato legible."""
def formatear_punto(punto):
    return f"X={punto[0]:.3f}, Y={punto[1]:.3f}, Z={punto[2]:.3f}"

def dibujar_recorrido():
    """Dibuja el recorrido en 3D con Matplotlib y muestra coordenadas al pasar el ratón."""
    if len(puntos) < 2:
        print("No hay suficientes puntos para plasmar en 3D el recorrido (mínimo 2).")
        return

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # Extraer coordenadas
    xs, ys, zs = zip(*puntos)

    # Dibujar puntos y líneas
    scatter = ax.scatter(xs, ys, zs, c='blue')
    for i in range(len(puntos) - 1):
        p1 = puntos[i]
        p2 = puntos[i + 1]
        ax.plot(
            [p1[0], p2[0]],
            [p1[1], p2[1]],
            [p1[2], p2[2]],
            'r-'
        )

    # ---------- Anotación flotante ----------
    anotacion = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(15, 15),
        textcoords="offset points",
        bbox=dict(boxstyle="round", fc="w"),
        arrowprops=dict(arrowstyle="->")
    )
    anotacion.set_visible(False)

    def actualizar_anotacion(ind):
        """Actualiza la posición y el texto de la anotación."""
        idx = ind["ind"][0]          # índice del punto
        x, y, z = xs[idx], ys[idx], zs[idx]

        # Proyectar el punto 3D a 2D para colocar la anotación
        x2d, y2d, _ = proj3d.proj_transform(x, y, z, ax.get_proj())
        anotacion.xy = (x2d, y2d)
        anotacion.set_text(f"({x:.2f}, {y:.2f}, {z:.2f})")

    def on_move(event):
        """Se ejecuta cuando mueves el ratón sobre la figura."""
        if event.inaxes != ax:
            if anotacion.get_visible():
                anotacion.set_visible(False)
                fig.canvas.draw_idle()
            return

        # ¿El ratón está cerca de algún punto?
        cont, ind = scatter.contains(event)
        if cont:
            actualizar_anotacion(ind)
            anotacion.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if anotacion.get_visible():
                anotacion.set_visible(False)
                fig.canvas.draw_idle()

    # Conectar el evento de movimiento del ratón
    fig.canvas.mpl_connect("motion_notify_event", on_move)

    plt.show()

# =========================
#  BUCLE PRINCIPAL
# =========================

if SIMULACION:
    print("MODO SIMULACIÓN:")
    print("   - Pulsa 'P' para generar un punto simulado.")
else:
    print("MODO ARDUINO:")
    print("   - Usa el botón del Arduino para enviar una medición y calcular el punto.")

print("   - Pulsa 'G' para plasmar en 3D el recorrido el recorrido.")
print("   - Pulsa 'R' para borrar la última medición.")
print("   - Ctrl + C para salir.\n")

try:
    while True:
        # 1) Leer medida (real o simulada)
        datos = leer_datos()

        if datos:
            distancia, azimut, pitch, roll = datos
            print(f"Datos usados -> Distancia={distancia:.2f}, Azimut={azimut:.2f}, Pitch={pitch:.2f}, Roll={roll:.2f}")

            # Calcular el siguiente punto
            punto_siguiente = calcular_punto_siguiente(puntos[-1], distancia, azimut, pitch)

            # Limitar a MAX_PUNTOS puntos
            if len(puntos) >= MAX_PUNTOS:
                eliminado = puntos.pop(0)
                print(f"Se ha eliminado el punto más antiguo: {formatear_punto(eliminado)}")

            puntos.append(punto_siguiente)
            print(f"Punto añadido: {formatear_punto(punto_siguiente)}")

        # 2) Tecla 'G' -> plasmar en 3D el recorrido
        if keyboard.is_pressed('g') and not key_pressed:
            key_pressed = True
            print("Dibujando recorrido...")
            dibujar_recorrido()

        # 3) Tecla 'R' -> borrar última medición (sin borrar el origen)
        if keyboard.is_pressed('r') and not key_pressed:
            key_pressed = True
            if len(puntos) > 1:
                eliminado = puntos.pop()
                print(f"Último punto medido eliminado: {formatear_punto(eliminado)}. Repite la medición cuando quieras.")
            else:
                print("Solo queda el punto origen, no se puede eliminar más.")

        # 4) Reset del debouncing cuando no se pulsan 'g' ni 'r'
        if not keyboard.is_pressed('g') and not keyboard.is_pressed('r'):
            key_pressed = False

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nSaliendo...")
    if arduino is not None and not SIMULACION:
        arduino.close()
        print("Puerto serie cerrado.")
