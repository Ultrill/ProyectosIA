import pygame
import random
import csv
import os
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np
from joblib import dump, load
import shutil

# Inicializar Pygame
pygame.init()

# Dimensiones de la pantalla
w, h = 800, 400
pantalla = pygame.display.set_mode((w, h))
pygame.display.set_caption("Juego: Disparo de Bala, Salto, Nave y Menú")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

# Variables globales
jugador = None
bala = None
bala2 = None
fondo = None
nave = None
nave2 = None
menu = None
ultimo_movimiento = "quieto"

modelo_decision_tree = None
modelo_red_neuronal = None
modelo_knn = None
modelo_actual = None
scaler = None
modo_auto = False  # Añadir esta línea


# Variables de salto
salto = False
salto_altura = 15
gravedad = 1
en_suelo = True

# Variables de pausa y menú
pausa = False
fuente = pygame.font.SysFont('Arial', 24)
menu_activo = True
modo_auto = False


movimiento_horizontal = False
direccion_movimiento = None
contador_movimiento = 0
posicion_central = 30
velocidad_retorno = 2.5


# Datos para modelos y CSV
datos_modelo = []
datos_csv = []

# Ruta CSV
ruta_csv = r"dataset.csv"

ruta_modelos = r"models"

# Cargar imágenes
jugador_frames = [
    pygame.image.load(r"C:\Users\ulise\OneDrive\Escritorio\IA\Practica2\assets\sprites\mono_frame_1.png"),
    pygame.image.load(r"C:\Users\ulise\OneDrive\Escritorio\IA\Practica2\assets\sprites\mono_frame_2.png"),
    pygame.image.load(r"C:\Users\ulise\OneDrive\Escritorio\IA\Practica2\assets\sprites\mono_frame_3.png")
]

bala_img = pygame.image.load(r"C:\Users\ulise\OneDrive\Escritorio\IA\Practica2\assets\sprites\purple_ball.png")
fondo_img = pygame.image.load(r"C:\Users\ulise\OneDrive\Escritorio\IA\Practica2\assets\game\fondo.png")
nave_img = pygame.image.load(r"C:\Users\ulise\OneDrive\Escritorio\IA\Practica2\assets\game\cannon.png")
menu_img = pygame.image.load(r"C:\Users\ulise\OneDrive\Escritorio\IA\Practica2\assets\game\menu.png")

# Escalar fondo
fondo_img = pygame.transform.scale(fondo_img, (w, h))

# Crear rectángulos
jugador = pygame.Rect(50, h - 100, 32, 48)
bala = pygame.Rect(w - 50, h - 90, 16, 16)
nave = pygame.Rect(w - 100, h - 100, 64, 64)
nave2 = pygame.Rect(10, h - 400, 64, 64)
bala2 = pygame.Rect(w - 750, h - 400 , 16, 16)
menu_rect = pygame.Rect(w // 2 - 135, h // 2 - 90, 270, 180)

# Animación del jugador
current_frame = 0
frame_speed = 10
frame_count = 0
movimiento_horizontal = False
direccion_movimiento = None
contador_movimiento = 0

# Balas
velocidad_bala = -10
velocidad_bala2 = 7
bala_disparada = False
bala2_disparada = False

# Fondo en movimiento
fondo_x1 = 0
fondo_x2 = w

def limpiar_datos_modelo():
    global datos_modelo

    datos_modelo = []

    if os.path.exists(datos_csv):
        os.remove(datos_csv)

    if os.path.exists(ruta_modelos):
        shutil.rmtree(ruta_modelos)

    print("Modelos y dataset eliminados. Obteniendo nuevos datos...")

# Función para cargar y preparar los datos del CSV
def cargar_datos_entrenamiento():
    global scaler
    X = []
    y = []
    
    if not os.path.exists(ruta_csv):
        return None, None
    
    with open(ruta_csv, mode='r') as archivo:
        lector = csv.reader(archivo, delimiter=';')
        next(lector)  # Saltar la cabecera
        for fila in lector:
            if len(fila) < 8:
                continue
                
            jugador_x = float(fila[0])
            jugador_y = float(fila[1])
            bala1_x = float(fila[2])
            bala1_y = float(fila[3])
            bala2_x = float(fila[4])
            bala2_y = float(fila[5])
            salto = int(fila[6])
            movimiento = fila[7]
            
            # Características: distancia a bala1, distancia a bala2, velocidad bala1, posición jugador
            distancia_bala1 = abs(jugador_x - bala1_x)
            distancia_bala2 = abs(jugador_x - bala2_x)
            altura_bala2 = bala2_y
            
            # Calcular velocidad aproximada de la bala1 (asumiendo que es constante)
            velocidad_bala1 = -5  # Valor aproximado basado en el código
            
            X.append([distancia_bala1, distancia_bala2, altura_bala2, velocidad_bala1, jugador_x])
            
            # Etiqueta: qué acción tomar (0: quieto, 1: izquierda, 2: derecha, 3: saltar)
            if salto == 1:
                y.append(3)
            elif movimiento == "izquierda":
                y.append(1)
            elif movimiento == "derecha":
                y.append(2)
            else:
                y.append(0)
    
    if not X:
        return None, None
    
    X = np.array(X)
    y = np.array(y)
    
    # Normalizar los datos
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    
    return X, y

# Función para entrenar los modelos
def entrenar_modelos():
    global modelo_decision_tree, modelo_red_neuronal, modelo_knn
    
    X, y = cargar_datos_entrenamiento()
    if X is None or y is None:
        print("No hay datos suficientes para entrenar los modelos. Juega en modo manual primero.")
        return False
    
    # Dividir datos en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Entrenar Decision Tree
    modelo_decision_tree = DecisionTreeClassifier(max_depth=7)
    modelo_decision_tree.fit(X_train, y_train)
    print(f"Decision Tree - Precisión: {modelo_decision_tree.score(X_test, y_test):.2f}")
    
    # Entrenar Red Neuronal
    modelo_red_neuronal = MLPClassifier(hidden_layer_sizes=(60, 60), max_iter=10000)
    modelo_red_neuronal.fit(X_train, y_train)
    print(f"Red Neuronal - Precisión: {modelo_red_neuronal.score(X_test, y_test):.2f}")
    
    # Entrenar KNN
    modelo_knn = KNeighborsClassifier(n_neighbors=3)
    modelo_knn.fit(X_train, y_train)
    print(f"KNN - Precisión: {modelo_knn.score(X_test, y_test):.2f}")
    
    return True

# Función para que el modelo tome una decisión
def decidir_accion(modelo):
    global jugador, bala, bala2, scaler

    # Preparar características actuales
    distancia_bala1 = abs(jugador.x - bala.x)
    distancia_bala2 = abs(jugador.x - bala2.x)
    altura_bala2 = bala2.y
    velocidad_bala1 = velocidad_bala

    caracteristicas = np.array([[distancia_bala1, distancia_bala2, altura_bala2, velocidad_bala1, jugador.x]])

    # Normalizar si tienes un scaler entrenado
    if scaler:
        caracteristicas = scaler.transform(caracteristicas)

    # Predecir acción: 0=quieto, 1=izquierda, 2=derecha, 3=saltar
    accion = modelo.predict(caracteristicas)[0]

    # Aquí ya no filtramos la acción, dejamos que sea cualquiera de las 4
    return accion

def mover_derecha_con_retorno():
    global jugador, movimiento_horizontal, direccion_movimiento, contador_movimiento

    if not movimiento_horizontal:
        # Mover 20 píxeles a la derecha
        jugador.x += 20
        # Activar movimiento de retorno
        movimiento_horizontal = True
        direccion_movimiento = "derecha"
        contador_movimiento = 0

# Disparo nave 1
def disparar_bala():
    global bala_disparada, velocidad_bala
    if not bala_disparada:
        velocidad_bala = -3
        bala_disparada = True

# Disparo nave 2
def disparar_bala2():
    global bala2_disparada, velocidad_bala2_x, velocidad_bala2_y, bala2
    if not bala2_disparada:
        bala2.x = 40
        bala2.y = 0
        velocidad_bala2_x = 0
        velocidad_bala2_y = 2
        bala2_disparada = True

# Reset balas
def reset_bala():
    global bala, bala_disparada
    bala.x = w - 50
    bala_disparada = False

def reset_bala2():
    global bala2, bala2_disparada
    bala2.x = w - 750
    bala2.y = h - 400
    bala2_disparada = False

# Salto
def manejar_salto():
    global jugador, salto, salto_altura, gravedad, en_suelo
    if salto:
        jugador.y -= salto_altura
        salto_altura -= gravedad
        if jugador.y >= h - 100:
            jugador.y = h - 100
            salto = False
            salto_altura = 15
            en_suelo = True

# Guardar datos en CSV
def guardar_datos_csv():
    global modo_auto
    if not modo_auto:
        archivo_existe = os.path.exists(ruta_csv)
        with open(ruta_csv, mode='a', newline='') as archivo:
            escritor = csv.writer(archivo, delimiter=';')
            if not archivo_existe:
                escritor.writerow(['jugador_x', 'jugador_y', 'bala1_x', 'bala1_y', 'bala2_x', 'bala2_y', 'salto', 'movimiento'])
            for fila in datos_csv:
                escritor.writerow(fila)
    else:
        pass



def limpiar_datos_modelo():
    global datos_modelo, datos_csv, ruta_modelos, ruta_csv

    datos_modelo = []
    datos_csv = []


    if os.path.exists(ruta_csv):
        os.remove(ruta_csv)

    if os.path.exists(ruta_modelos):
        shutil.rmtree(ruta_modelos)

    print("Modelos y dataset eliminados. Obteniendo nuevos datos...")

# Guardar datos para el modelo y CSV
# Contador global para "quieto"
contador_quieto = 0

def guardar_datos():
    global contador_quieto, modo_auto

    if not modo_auto:
        salto_actual = 1 if salto else 0

        # Determinar el movimiento actual
        if direccion_movimiento == "izquierda":
            movimiento = "izquierda"
        elif direccion_movimiento == "derecha":
            movimiento = "derecha"
        else:
            movimiento = "quieto"

        # Limitar cuántos "quieto" se guardan
        if movimiento == "quieto":
            contador_quieto += 1
            if contador_quieto % 10 != 0:  # solo guarda 1 de cada 10 "quieto"
                return
        else:
            contador_quieto = 0  # reinicia si no es quieto

        datos_csv.append([
            jugador.x, jugador.y,
            bala.x, bala.y,
            bala2.x, bala2.y,
            salto_actual, movimiento
        ])


# Actualizar juego
def update():
    global bala, velocidad_bala, current_frame, frame_count, fondo_x1, fondo_x2
    global bala2, velocidad_bala2_x, velocidad_bala2_y
    global movimiento_horizontal, direccion_movimiento, contador_movimiento

    fondo_x1 -= 1
    fondo_x2 -= 1
    if fondo_x1 <= -w:
        fondo_x1 = w
    if fondo_x2 <= -w:
        fondo_x2 = w
    pantalla.blit(fondo_img, (fondo_x1, 0))
    pantalla.blit(fondo_img, (fondo_x2, 0))

    frame_count += 1
    if frame_count >= frame_speed:
        current_frame = (current_frame + 1) % len(jugador_frames)
        frame_count = 0
    pantalla.blit(jugador_frames[current_frame], (jugador.x, jugador.y))

    pantalla.blit(nave_img, (nave.x, nave.y))
    if bala_disparada:
        bala.x += velocidad_bala
    if bala.x < 0:
        reset_bala()
    pantalla.blit(bala_img, (bala.x, bala.y))

    pantalla.blit(nave_img, (nave2.x, nave2.y))
    if bala2_disparada:
        bala2.x += velocidad_bala2_x
        bala2.y += velocidad_bala2_y
    if bala2.x < 0 or bala2.y > h:
        reset_bala2()
    pantalla.blit(bala_img, (bala2.x, bala2.y))

    if jugador.colliderect(bala) or jugador.colliderect(bala2):
        print("¡Colisión detectada!")
        reiniciar_juego()

    # Movimiento horizontal temporal con retorno suave
    if movimiento_horizontal:
        contador_movimiento += 1
        if contador_movimiento >= 10:
            if jugador.x > posicion_central:
                jugador.x -= velocidad_retorno
                if jugador.x <= posicion_central:
                    jugador.x = posicion_central
                    movimiento_horizontal = False
                    direccion_movimiento = None
                    contador_movimiento = 0
            elif jugador.x < posicion_central:
                jugador.x += velocidad_retorno
                if jugador.x >= posicion_central:
                    jugador.x = posicion_central
                    movimiento_horizontal = False
                    direccion_movimiento = None
                    contador_movimiento = 0



# Pausa
def pausa_juego():
    global pausa
    pausa = not pausa
    if pausa:
        print("Juego pausado. Datos registrados hasta ahora:", datos_modelo)
    else:
        print("Juego reanudado.")

# Menú
def mostrar_menu():
    global menu_activo, modo_auto
    pantalla.fill(NEGRO)
    texto = fuente.render("Presiona 'A' para Auto, 'M' para Manual, o 'Q' para Salir", True, BLANCO)
    pantalla.blit(texto, (w // 4, h // 2))
    pygame.display.flip()

    while menu_activo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_a:
                    mostrar_menu_automatico()
                    modo_auto = True
                    menu_activo = False
                elif evento.key == pygame.K_m:
                    limpiar_datos_modelo()
                    modo_auto = False
                    menu_activo = False
                elif evento.key == pygame.K_q:
                    guardar_datos_csv()
                    pygame.quit()
                    exit()

# Submenú automático
def mostrar_menu_automatico():
    global modelo_actual, modo_auto
    
    if not entrenar_modelos():
        modo_auto = False
        return
    
    pantalla.fill(NEGRO)
    opciones = ["1 - Decision Trees", "2 - Redes neuronales", "3 - K nearest neighbor", "4 - Volver"]
    for i, opcion in enumerate(opciones):
        texto = fuente.render(opcion, True, BLANCO)
        pantalla.blit(texto, (w // 4, h // 2 + i * 30))
    pygame.display.flip()
    
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    modelo_actual = modelo_decision_tree
                    esperando = False
                elif evento.key == pygame.K_2:
                    modelo_actual = modelo_red_neuronal
                    esperando = False
                elif evento.key == pygame.K_3:
                    modelo_actual = modelo_knn
                    esperando = False
                elif evento.key == pygame.K_4:
                    modo_auto = False
                    esperando = False


# Reinicio
def reiniciar_juego():
    global jugador, bala, bala2, nave, nave2
    global bala_disparada, bala2_disparada, salto, en_suelo, menu_activo
    # Reset posiciones y estados
    jugador.x, jugador.y = 50, h - 100
    bala.x = w - 50
    bala2.x = nave2.right
    bala2.y = nave2.centery
    nave.x, nave.y = w - 100, h - 100
    nave2.x, nave2.y = 20, 20
    bala_disparada = False
    bala2_disparada = False
    salto = False
    en_suelo = True
    guardar_datos_csv()
    print("Datos recopilados guardados en CSV.")
    # Reactivar menú
    menu_activo = True
    mostrar_menu()

#Main Loop
def main():
    global salto, en_suelo, bala_disparada, bala2_disparada, ultimo_movimiento, modelo_actual, modo_auto
    global movimiento_horizontal, direccion_movimiento, contador_movimiento

    if 'modo_auto' not in globals():
        modo_auto = False

    reloj = pygame.time.Clock()
    mostrar_menu()
    correr = True

    while correr:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                guardar_datos_csv()
                correr = False

            if evento.type == pygame.KEYDOWN:
                tecla = evento.key

                if evento.key == pygame.K_SPACE and en_suelo and not pausa and not modo_auto:
                    salto = True
                    en_suelo = False
                    ultimo_movimiento = "salto"

                if evento.key == pygame.K_p:
                    pausa_juego()
                if evento.key == pygame.K_q:
                    guardar_datos_csv()
                    pygame.quit()
                    exit()
                if evento.key == pygame.K_m:
                    modo_auto = False
                if evento.key == pygame.K_a:
                    mostrar_menu_automatico()

                # Movimiento manual por tecla puntual (ya no se usa si estás manteniendo teclas)
                if not modo_auto and not movimiento_horizontal:
                    if tecla == pygame.K_a:
                        jugador.x = 10
                        direccion_movimiento = "izquierda"
                        movimiento_horizontal = True
                        contador_movimiento = 0
                        ultimo_movimiento = "izquierda"
                    elif tecla == pygame.K_d:
                        jugador.x = 50
                        direccion_movimiento = "derecha"
                        movimiento_horizontal = True
                        contador_movimiento = 0
                        ultimo_movimiento = "derecha"

        if modo_auto and modelo_actual and not pausa:
            distancia_bala1 = abs(jugador.x - bala.x)
            accion = decidir_accion(modelo_actual)  # 0=quieto, 1=izquierda, 2=derecha, 3=salto


            if distancia_bala1 < 40 and en_suelo:
                salto = True
                en_suelo = False
                ultimo_movimiento = "salto"
            else:
                if accion == 1 and jugador.x > 50:
                    jugador.x -= 15
                    ultimo_movimiento = "izquierda"
                elif accion == 2 and jugador.x < 120:
                    jugador.x += 20
                    mover_derecha_con_retorno()
                    ultimo_movimiento = "derecha"
                elif accion == 3 and en_suelo:
                    salto = True
                    en_suelo = False
                    ultimo_movimiento = "salto"
                else:
                    ultimo_movimiento = "quieto"

        else:
            # Modo manual continuo (mantener tecla presionada)
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_a] and jugador.x > 50:
                jugador.x -= 15
                ultimo_movimiento = "izquierda"
            elif teclas[pygame.K_d] and jugador.x < 120:
                jugador.x += 20
                ultimo_movimiento = "derecha"
            else:
                ultimo_movimiento = "quieto"

        if not pausa:
            if salto:
                manejar_salto()
            if not modo_auto:
                guardar_datos()
            if not bala_disparada:
                disparar_bala()
            if not bala2_disparada:
                disparar_bala2()
            update()

            # DIBUJAR MARCAS DESPUÉS DEL UPDATE
            if bala.x == 372 and bala.y == 310:
                pygame.draw.circle(pantalla, (255, 0, 0), (bala.x, bala.y), 5)
            if bala2.y == 200:
                pygame.draw.circle(pantalla, (0, 255, 0), (bala2.x, bala2.y), 5)

        pygame.display.flip()
        reloj.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()