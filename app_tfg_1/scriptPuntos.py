import matplotlib.pyplot as plt
import numpy as np
import serial
import time
import keyboard  # Librería para detectar teclas

# Configuración de la comunicación serial con Arduino
arduino = serial.Serial('COM4', 115200, timeout=1)  # Cambia 'COM4' por el puerto correcto
time.sleep(2)  # Esperar a que se establezca la conexión

# Lista para almacenar puntos
puntos = [(0, 0, 0)]  # Iniciar en el origen
MAX_PUNTOS = 6  # Límite de puntos en la lista

# Variables para el debouncing de teclas
key_pressed = False  # Evita múltiples detecciones de la misma tecla

def leer_datos_arduino():
    """ Lee los datos enviados por Arduino tras presionar el botón. """
    datos = arduino.readline().decode('utf-8').strip()
    
    if not datos:
        return None

    datos = datos.split(',')
    
    if len(datos) != 4:
        print(f"Formato incorrecto recibido: {datos}")
        return None
    
    try:
        return float(datos[0]), float(datos[1]), float(datos[2]), float(datos[3])
    except ValueError:
        print(f"No se pudo convertir a float: {datos}")
        return None

def calcular_punto_siguiente(punto_actual, distancia, azimut, pitch):
    """ Calcula el siguiente punto en el espacio 3D. """
    x = punto_actual[0] + distancia * np.cos(np.radians(azimut)) * np.cos(np.radians(pitch))
    y = punto_actual[1] + distancia * np.sin(np.radians(azimut)) * np.cos(np.radians(pitch))
    z = punto_actual[2] + distancia * np.sin(np.radians(pitch))
    return (x, y, z)

def dibujar_recorrido():
    """ Dibuja el recorrido en 3D con Matplotlib. """
    if len(puntos) < 2:
        print("No hay suficientes puntos para graficar.")
        return

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # Dibujar los puntos y las líneas
    ax.scatter(*zip(*puntos), c='blue')
    for i in range(len(puntos) - 1):
        p1, p2 = puntos[i], puntos[i + 1]
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], 'r-')

    plt.show()

# Bucle principal
print("Presiona el botón en Arduino para capturar puntos. Pulsa 'C' para graficar o 'R' para repetir la última medición.")

while True:
    datos = leer_datos_arduino()
    
    if datos:
        distancia, azimut, pitch, roll = datos
        print(f"Datos recibidos: Distancia = {distancia}, Azimut = {azimut}, Pitch = {pitch}, Roll = {roll}")
        
        # Calcular el siguiente punto
        punto_siguiente = calcular_punto_siguiente(puntos[-1], distancia, azimut, pitch)
        
        # Limitar a MAX_PUNTOS puntos
        if len(puntos) >= MAX_PUNTOS:
            puntos.pop(0)  # Eliminar el primer punto si se alcanza el límite

        puntos.append(punto_siguiente)  # Añadir el nuevo punto
        print(f"Punto añadido: {punto_siguiente}")

    # Detectar si se presiona 'C' para graficar
    if keyboard.is_pressed('c') and not key_pressed:
        key_pressed = True  # Evitar múltiples detecciones
        print("Dibujando recorrido...")
        dibujar_recorrido()

    # Detectar si se presiona 'R' para repetir la última medición
    if keyboard.is_pressed('r') and not key_pressed:
        key_pressed = True  # Evitar múltiples detecciones
        if len(puntos) > 1:  # Asegurarse de que hay al menos un punto para eliminar
            punto_eliminado = puntos.pop()  # Eliminar el último punto
            print(f"Última medición eliminada: {punto_eliminado}. Repite la medición.")

    # Restablecer key_pressed cuando se suelta la tecla
    if not keyboard.is_pressed('c') and not keyboard.is_pressed('r'):
        key_pressed = False

    # Para evitar una lectura demasiado rápida de la tecla
    time.sleep(0.1)

'''
FUNCIONA GUAY PERO VER LO DE REPETIR PUNTOS
import matplotlib.pyplot as plt
import numpy as np
import serial
import time
import keyboard  # Librería para detectar teclas

# Configuración de la comunicación serial con Arduino
arduino = serial.Serial('COM4', 115200, timeout=1)  # Cambia 'COM4' por el puerto correcto
time.sleep(2)  # Esperar a que se establezca la conexión

# Lista para almacenar puntos
puntos = [(0, 0, 0)]  # Iniciar en el origen

def leer_datos_arduino():
    """ Lee los datos enviados por Arduino tras presionar el botón. """
    datos = arduino.readline().decode('utf-8').strip()
    
    if not datos:
        return None

    datos = datos.split(',')
    
    if len(datos) != 4:
        print(f"Formato incorrecto recibido: {datos}")
        return None
    
    try:
        return float(datos[0]), float(datos[1]), float(datos[2]), float(datos[3])
    except ValueError:
        print(f"No se pudo convertir a float: {datos}")
        return None

def calcular_punto_siguiente(punto_actual, distancia, azimut, pitch):
    """ Calcula el siguiente punto en el espacio 3D. """
    x = punto_actual[0] + distancia * np.cos(np.radians(azimut)) * np.cos(np.radians(pitch))
    y = punto_actual[1] + distancia * np.sin(np.radians(azimut)) * np.cos(np.radians(pitch))
    z = punto_actual[2] + distancia * np.sin(np.radians(pitch))
    return (x, y, z)

def dibujar_recorrido():
    """ Dibuja el recorrido en 3D con Matplotlib. """
    if len(puntos) < 2:
        print("No hay suficientes puntos para graficar.")
        return

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # Dibujar los puntos y las líneas
    ax.scatter(*zip(*puntos), c='blue')
    for i in range(len(puntos) - 1):
        p1, p2 = puntos[i], puntos[i + 1]
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], 'r-')

    plt.show()

# Bucle principal
print("Presiona el botón en Arduino para capturar puntos. Pulsa 'C' para graficar.")

while True:
    datos = leer_datos_arduino()
    
    if datos:
        distancia, azimut, pitch, roll = datos
        print(f"Datos recibidos: Distancia = {distancia}, Azimut = {azimut}, Pitch = {pitch}, Roll = {roll}")
        
        # Calcular el siguiente punto
        punto_siguiente = calcular_punto_siguiente(puntos[-1], distancia, azimut, pitch)
        
        # Limitar a 6 puntos
        if len(puntos) >= 6:
            puntos.pop(0)  # Eliminar el primer punto si hay 6 puntos

        puntos.append(punto_siguiente)  # Añadir el nuevo punto

    # Esperar el comando 'C' para graficar
    if keyboard.is_pressed('c'):
        print("Dibujando recorrido...")
        dibujar_recorrido()

    # Para evitar una lectura demasiado rápida de la tecla
    time.sleep(0.1)

'''

'''import matplotlib.pyplot as plt
import numpy as np
import serial
import time

# Configuración de la comunicación serial con Arduino
arduino = serial.Serial('COM4', 115200, timeout=1)  # Cambia 'COM3' por el puerto correcto
time.sleep(2)  # Esperar a que se establezca la conexión

def leer_datos_arduino():
    """
    Lee los datos de distancia y orientación desde Arduino.
    Retorna: distancia (float), azimut (float), pitch (float), roll (float)
    """
    arduino.write(b'M')  # Enviar comando para medir
    time.sleep(0.5)  # Esperar a que Arduino procese la medición
    datos = arduino.readline().decode('utf-8').strip().split(',')
    if len(datos) == 4:
        return float(datos[0]), float(datos[1]), float(datos[2]), float(datos[3])
    else:
        return None

def calcular_punto_siguiente(punto_actual, distancia, azimut, pitch):
    """
    Calcula las coordenadas del siguiente punto basado en la distancia y la orientación.
    """
    x = punto_actual[0] + distancia * np.cos(np.radians(azimut)) * np.cos(np.radians(pitch))
    y = punto_actual[1] + distancia * np.sin(np.radians(azimut)) * np.cos(np.radians(pitch))
    z = punto_actual[2] + distancia * np.sin(np.radians(pitch))
    return (x, y, z)

def main():
    # Inicializar lista de puntos
    puntos = [(0, 0, 0)]  # Punto inicial en el origen

    # Crear la figura
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # Función para actualizar el gráfico
    def actualizar_grafico():
        ax.clear()
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        # Dibujar todos los puntos y líneas
        scatter = ax.scatter(*zip(*puntos), c='blue')
        for i in range(len(puntos) - 1):
            p1 = puntos[i]
            p2 = puntos[i + 1]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], 'r-')
            distancia = np.linalg.norm(np.array(p2) - np.array(p1))
            punto_medio = [(p1[j] + p2[j]) / 2 for j in range(3)]
            ax.text(punto_medio[0], punto_medio[1], punto_medio[2], f'{distancia:.2f}', color='black')

        plt.draw()

    # Bucle principal
    print("Presiona el botón en Arduino para agregar un punto...")
    while True:
        # Leer datos de Arduino
        datos = leer_datos_arduino()
        if datos:
            distancia, azimut, pitch, roll = datos
            print(f"Datos recibidos: Distancia = {distancia}, Azimut = {azimut}, Pitch = {pitch}, Roll = {roll}")

            # Calcular el siguiente punto
            punto_siguiente = calcular_punto_siguiente(puntos[-1], distancia, azimut, pitch)
            puntos.append(punto_siguiente)

            # Actualizar el gráfico
            actualizar_grafico()

        # Esperar un momento antes de la siguiente lectura
        time.sleep(0.1)

if __name__ == "__main__":
    main()
'''

'''import matplotlib.pyplot as plt
import numpy as np
import serial

def generar_puntos_aleatorios(num_puntos):
    # Generar coordenadas aleatorias en el rango [-0, 50] ambos incluidos
    xs = np.random.randint(0, 100, num_puntos)
    ys = np.random.randint(0, 100, num_puntos)
    zs = np.random.randint(0, 100, num_puntos)
    return list(zip(xs, ys, zs))

def calcular_distancia(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def main():
    num_puntos = 6
    puntos = generar_puntos_aleatorios(num_puntos)

    # Crear la figura
    fig = plt.figure()
    aux = fig.add_subplot(111, projection='3d')

    # Configurar los márgenes
    fig.subplots_adjust(top=1.0, bottom=0.075, left=0.125, right=0.9, hspace=0.2, wspace=0.2)

    scatter = aux.scatter(*zip(*puntos))

    # Dibujar líneas entre puntos y calcular distancias
    distancia_total = 0
    for i in range(len(puntos) - 1):
        p1 = puntos[i]
        p2 = puntos[i + 1]
        aux.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], 'r-')
        distancia = calcular_distancia(p1, p2)
        distancia_total += distancia
        punto_medio = [(p1[j] + p2[j]) / 2 for j in range(3)]
        aux.text(punto_medio[0], punto_medio[1], punto_medio[2], f'{distancia:.2f}', color='black')

    print(f'Distancia total: {distancia_total:.2f}')

    # Mostrar la distancia total en el gráfico
    aux.text2D(0.05, 0.95, f'Distancia total: {distancia_total:.2f}', transform=aux.transAxes, color='blue')

    aux.set(xticklabels=[], yticklabels=[], zticklabels=[])

    # Función para mostrar las coordenadas al pasar el ratón
    anotacion = aux.annotate("", xy=(0,0), xytext=(20,20),
                            textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
    anotacion.set_visible(False)

    def actualizar_anotacion(ind):
        pos = scatter.get_offsets()[ind["ind"][0]]
        anotacion.xy = pos
        texto = f"{puntos[ind['ind'][0]]}"
        anotacion.set_text(texto)
        anotacion.get_bbox_patch().set_facecolor('yellow')
        anotacion.get_bbox_patch().set_alpha(0.6)

    def pasar_raton(event):
        vis = anotacion.get_visible()
        if event.inaxes == aux:
            cont, ind = scatter.contains(event)
            if cont:
                actualizar_anotacion(ind)
                anotacion.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    anotacion.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", pasar_raton)

    plt.show()

if __name__ == "__main__":
    main()
'''

'''
ESTE ES EL BUENO
import matplotlib.pyplot as plt
import numpy as np
import serial

def generar_puntos_aleatorios(num_puntos):
    # Generar coordenadas aleatorias en el rango [-0, 50] ambos incluidos
    xs = np.random.randint(0, 100, num_puntos)
    ys = np.random.randint(0, 100, num_puntos)
    zs = np.random.randint(0, 100, num_puntos)
    return list(zip(xs, ys, zs))

def calcular_distancia(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def main():
    num_puntos = 6
    puntos = generar_puntos_aleatorios(num_puntos)

    # Graficar
    fig = plt.figure()
    aux = fig.add_subplot(111, projection='3d')
    scatter = aux.scatter(*zip(*puntos))

    # Dibujar líneas entre puntos y calcular distancias
    distancia_total = 0
    for i in range(len(puntos) - 1):
        p1 = puntos[i]
        p2 = puntos[i + 1]
        aux.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], 'r-')
        distancia = calcular_distancia(p1, p2)
        distancia_total += distancia
        punto_medio = [(p1[j] + p2[j]) / 2 for j in range(3)]
        aux.text(punto_medio[0], punto_medio[1], punto_medio[2], f'{distancia:.2f}', color='black')

    print(f'Distancia total: {distancia_total:.2f}')

    # Mostrar la distancia total en el gráfico
    aux.text2D(0.05, 0.95, f'Distancia total: {distancia_total:.2f}', transform=aux.transAxes, color='blue')

    aux.set(xticklabels=[], yticklabels=[], zticklabels=[])

    # Función para mostrar las coordenadas al pasar el ratón
    anotacion = aux.annotate("", xy=(0,0), xytext=(20,20),
                            textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
    anotacion.set_visible(False)

    def actualizar_anotacion(ind):
        pos = scatter.get_offsets()[ind["ind"][0]]
        anotacion.xy = pos
        texto = f"{puntos[ind['ind'][0]]}"
        anotacion.set_text(texto)
        anotacion.get_bbox_patch().set_facecolor('yellow')
        anotacion.get_bbox_patch().set_alpha(0.6)

    def pasar_raton(event):
        vis = anotacion.get_visible()
        if event.inaxes == aux:
            cont, ind = scatter.contains(event)
            if cont:
                actualizar_anotacion(ind)
                anotacion.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    anotacion.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", pasar_raton)

    plt.show()

if __name__ == "__main__":
    main()
'''

'''import matplotlib.pyplot as plt
import numpy as np

# Lista de puntos guardados
puntos = [(0, 0, 0)]  # Punto inicial en (0, 0, 0)

def calcular_nuevo_punto(punto_actual, distancia, inclinacion, giro):
    # Convertir ángulos a radianes para los cálculos
    inclinacion_rad = np.radians(inclinacion)
    giro_rad = np.radians(giro)

    # Calcular desplazamientos en las coordenadas X, Y, Z
    delta_x = distancia * np.cos(inclinacion_rad) * np.cos(giro_rad)
    delta_y = distancia * np.cos(inclinacion_rad) * np.sin(giro_rad)
    delta_z = distancia * np.sin(inclinacion_rad)

    # Calcular las nuevas coordenadas sumando los desplazamientos al punto actual
    nuevo_punto = (
        punto_actual[0] + delta_x,
        punto_actual[1] + delta_y,
        punto_actual[2] + delta_z
    )

    return nuevo_punto

def agregar_punto(distancia, inclinacion, giro):
    global puntos
    nuevo_punto = calcular_nuevo_punto(puntos[-1], distancia, inclinacion, giro)
    puntos.append(nuevo_punto)

def graficar_puntos():
    if len(puntos) < 2:
        print("Se requieren al menos dos puntos para calcular distancias y dibujar líneas.")
        return

    # Extraer coordenadas para el gráfico
    xs, ys, zs = zip(*puntos)

    # Graficar
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Dibujar puntos en color vistoso (rojo en este caso)
    scatter = ax.scatter(xs, ys, zs, color='red', s=50)  # Cambia 'red' por cualquier color y 's' es el tamaño del punto

    # Dibujar líneas entre puntos (en color negro)
    for i in range(len(puntos) - 1):
        p1 = puntos[i]
        p2 = puntos[i + 1]
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color='black')  # Rectas en negro

    # Mostrar las coordenadas en cada punto con fuente más pequeña
    for x, y, z in zip(xs, ys, zs):
        ax.text(x, y, z, f'({x:.2f}, {y:.2f}, {z:.2f})', color='blue', fontsize=7)  # Ajuste de tamaño de fuente

    # Eliminar las etiquetas de los ejes
    ax.set(xticklabels=[], yticklabels=[], zticklabels=[])

    plt.show()

if __name__ == "__main__":
    # Supón que recibes estos datos del Arduino:
    agregar_punto(10, 30, 45)  # Ejemplo de agregar un punto (distancia, inclinación, giro)
    agregar_punto(5, 15, 90)
    
    graficar_puntos()  # Graficar los puntos guardados

'''

# import matplotlib.pyplot as plt
# import numpy as np

# def obtener_entrada_usuario():
#     puntos = [(0, 0, 0)]  # Punto inicial en (0, 0, 0)
#     while True:
#         entrada = input("Introduce la distancia, inclinación (grados) y giro (grados), o escribe 'listo' para terminar: ")
#         if entrada.lower() == 'listo':
#             break
#         try:
#             distancia, inclinacion, giro = map(float, entrada.split(','))
#             nuevo_punto = calcular_nuevo_punto(puntos[-1], distancia, inclinacion, giro)
#             puntos.append(nuevo_punto)
#         except ValueError:
#             print("Entrada inválida. Por favor, introduce los valores en el formato: distancia,inclinación,giro.")
#     return puntos

# def calcular_nuevo_punto(punto_actual, distancia, inclinacion, giro):
#     # Convertir ángulos a radianes para los cálculos
#     inclinacion_rad = np.radians(inclinacion)
#     giro_rad = np.radians(giro)

#     # Calcular desplazamientos en las coordenadas X, Y, Z
#     delta_x = distancia * np.cos(inclinacion_rad) * np.cos(giro_rad)
#     delta_y = distancia * np.cos(inclinacion_rad) * np.sin(giro_rad)
#     delta_z = distancia * np.sin(inclinacion_rad)

#     # Calcular las nuevas coordenadas sumando los desplazamientos al punto actual
#     nuevo_punto = (
#         punto_actual[0] + delta_x,
#         punto_actual[1] + delta_y,
#         punto_actual[2] + delta_z
#     )

#     return nuevo_punto

# def main():
#     puntos = obtener_entrada_usuario()
    
#     if len(puntos) < 2:
#         print("Se requieren al menos dos puntos para calcular distancias y dibujar líneas.")
#         return

#     # Extraer coordenadas para el gráfico
#     xs, ys, zs = zip(*puntos)

#     # Graficar
#     fig = plt.figure()
#     ax = fig.add_subplot(111, projection='3d')

#     # Dibujar puntos en color vistoso (rojo en este caso)
#     scatter = ax.scatter(xs, ys, zs, color='red', s=50)  # Cambia 'red' por cualquier color y 's' es el tamaño del punto

#     # Dibujar líneas entre puntos (en color negro)
#     for i in range(len(puntos) - 1):
#         p1 = puntos[i]
#         p2 = puntos[i + 1]
#         ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color='black')  # Rectas en negro

#     # Mostrar las coordenadas en cada punto con fuente más pequeña
#     for x, y, z in zip(xs, ys, zs):
#         ax.text(x, y, z, f'({x:.2f}, {y:.2f}, {z:.2f})', color='blue', fontsize=7)  # Ajuste de tamaño de fuente

#     # Eliminar las etiquetas de los ejes
#     ax.set(xticklabels=[], yticklabels=[], zticklabels=[])

#     plt.show()

# if __name__ == "__main__":
#     main()




'''import serial
import time
import matplotlib.pyplot as plt
# Configura el puerto serial (ajusta 'COM4' o '/dev/ttyUSB0' según tu sistema)
ser = serial.Serial('COM4', 9600, timeout=1)
time.sleep(2)  # Espera a que el puerto serial esté listo

positions = []
x, y, z = 0, 0, 0
prev_time = time.time()

try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line.startswith('Aceleración'):
            try:
                # Extraer valores de aceleración
                parts = line.split(',')
                accel_x = float(parts[0].split(' ')[2])  # Extraer el valor de X
                accel_y = float(parts[1].split(' ')[2])  # Extraer el valor de Y
                accel_z = float(parts[2].split(' ')[2])  # Extraer el valor de Z

                current_time = time.time()
                dt = current_time - prev_time
                prev_time = current_time

                # Calcular la nueva posición
                x += accel_x * dt ** 2
                y += accel_y * dt ** 2
                z += accel_z * dt ** 2

                # Almacenar la posición
                positions.append((x, y, z))

            except ValueError as e:
                print(f"Error de valor al convertir a float: {e}")
            except IndexError:
                print("Error: formato de línea incorrecto:", line)

except KeyboardInterrupt:
    ser.close()

# Visualizar los datos
positions = list(zip(*positions))
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot(positions[0], positions[1], positions[2])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.show()'''





'''import matplotlib.pyplot as plt
import numpy as np
import serial

def obtener_entrada_usuario():
    puntos = []
    while True:
        entrada_usuario = input("Introduce un punto (x, y, z) o escribe 'listo' para terminar: ")
        if entrada_usuario.lower() == 'listo':
            break
        try:
            punto = tuple(map(float, entrada_usuario.split(',')))
            if len(punto) != 3:
                print("Por favor, introduce un punto 3D válido.")
                continue
            puntos.append(punto)
        except ValueError:
            print("Entrada inválida. Por favor, introduce un punto en el formato x,y,z.")
    return puntos

def calcular_distancia(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def main():
    puntos = obtener_entrada_usuario()
    
    if len(puntos) < 2:
        print("Se requieren al menos dos puntos para calcular distancias y dibujar líneas.")
        return

    # Extraer coordenadas para el gráfico
    xs, ys, zs = zip(*puntos)

    # Graficar
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    scatter = ax.scatter(xs, ys, zs)

    # Dibujar líneas entre puntos y calcular distancias
    distancia_total = 0
    for i in range(len(puntos) - 1):
        p1 = puntos[i]
        p2 = puntos[i + 1]
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], 'r-')
        distancia = calcular_distancia(p1, p2)
        distancia_total += distancia
        punto_medio = [(p1[j] + p2[j]) / 2 for j in range(3)]
        ax.text(punto_medio[0], punto_medio[1], punto_medio[2], f'{distancia:.2f}', color='black')

    print(f'Distancia total: {distancia_total:.2f}')

    # Mostrar la distancia total en el gráfico
    ax.text2D(0.05, 0.95, f'Distancia total: {distancia_total:.2f}', transform=ax.transAxes, color='blue')

    ax.set(xticklabels=[], yticklabels=[], zticklabels=[])

    # Función para mostrar las coordenadas al pasar el ratón
    anotacion = ax.annotate("", xy=(0,0), xytext=(20,20),
                            textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
    anotacion.set_visible(False)

    def actualizar_anotacion(ind):
        pos = scatter.get_offsets()[ind["ind"][0]]
        anotacion.xy = pos
        texto = f"{xs[ind['ind'][0]]}, {ys[ind['ind'][0]]}, {zs[ind['ind'][0]]}"
        anotacion.set_text(texto)
        anotacion.get_bbox_patch().set_facecolor('yellow')
        anotacion.get_bbox_patch().set_alpha(0.6)

    def pasar_raton(event):
        vis = anotacion.get_visible()
        if event.inaxes == ax:
            cont, ind = scatter.contains(event)
            if cont:
                actualizar_anotacion(ind)
                anotacion.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    anotacion.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", pasar_raton)

    plt.show()

if __name__ == "__main__":
    main()
'''

'''import matplotlib.pyplot as plt
import numpy as np

def obtener_entrada_usuario():
    puntos = []
    while True:
        entrada_usuario = input("Introduce un punto (x, y, z) o escribe 'listo' para terminar: ")
        if entrada_usuario.lower() == 'listo':
            break
        try:
            punto = tuple(map(float, entrada_usuario.split(',')))
            if len(punto) != 3:
                print("Por favor, introduce un punto 3D válido.")
                continue
            puntos.append(punto)
        except ValueError:
            print("Entrada inválida. Por favor, introduce un punto en el formato x,y,z.")
    return puntos

def calcular_distancia(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def main():
    puntos = obtener_entrada_usuario()
    
    if len(puntos) < 2:
        print("Se requieren al menos dos puntos para calcular distancias y dibujar líneas.")
        return

    # Extraer coordenadas para el gráfico
    xs, ys, zs = zip(*puntos)

    # Graficar
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    scatter = ax.scatter(xs, ys, zs)

    # Dibujar líneas entre puntos y calcular distancias
    distancia_total = 0
    for i in range(len(puntos) - 1):
        p1 = puntos[i]
        p2 = puntos[i + 1]
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], 'r-')
        distancia = calcular_distancia(p1, p2)
        distancia_total += distancia
        punto_medio = [(p1[j] + p2[j]) / 2 for j in range(3)]
        ax.text(punto_medio[0], punto_medio[1], punto_medio[2], f'{distancia:.2f}', color='black')

    print(f'Distancia total: {distancia_total:.2f}')

    # Mostrar la distancia total en el gráfico
    ax.text2D(0.05, 0.95, f'Distancia total: {distancia_total:.2f}', transform=ax.transAxes, color='blue')

    # Mostrar las coordenadas de cada punto
    for i, punto in enumerate(puntos):
        ax.text(punto[0], punto[1], punto[2], f'({punto[0]}, {punto[1]}, {punto[2]})', color='black')

    ax.set(xticklabels=[], yticklabels=[], zticklabels=[])

    plt.show()

if __name__ == "__main__":
    main()
'''