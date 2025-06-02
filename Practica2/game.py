import pygame
import random
import pickle
import numpy as np
from tensorflow.keras.models import load_model
import pickle
from red_neuronal import entrenar_red_neuronal
from arbol_decision import entrenar_arbol_decision
from regresion_lineal import entrenar_regresion_lineal
from k_nearest_neighbor import entrenar_knn

modelo_actual = "manual"

# Inicializar Pygame
pygame.init()

# Dimensiones de la pantalla
w, h = 800, 400
pantalla = pygame.display.set_mode((w, h))
pygame.display.set_caption("Juego: Disparo de Bala, Salto, Nave y Menú")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

# Variables del jugador, bala, nave, fondo, etc.
jugador = None
bala = None
bala_vertical = None
fondo = None
nave = None
menu = None

# Variables de salto
salto = False
salto_altura = 15  # Velocidad inicial de salto
gravedad = 1
en_suelo = True

# Variables de pausa y menú
pausa = False
fuente = pygame.font.SysFont('Arial', 24)
menu_activo = True
modo_auto = False  # Indica si el modo de juego es automático

# Lista para guardar los datos de velocidad, distancia y salto (target)
datos_modelo = []

# Cargar las imágenes
jugador_frames = [
    pygame.image.load(r"C:\Users\ulise\OneDrive\Escritorio\IA\Practica2\assets\sprites\mono_frame_1.png"),
    pygame.image.load(r"C:\Users\ulise\OneDrive\Escritorio\IA\Practica2\assets\sprites\mono_frame_2.png"),
    pygame.image.load(r"C:\Users\ulise\OneDrive\Escritorio\IA\Practica2\assets\sprites\mono_frame_3.png")
    
]

bala_img = pygame.image.load(r"C:\Users\ulise\OneDrive\Escritorio\IA\Practica2\assets\sprites\purple_ball.png")
fondo_img = pygame.image.load(r"C:\Users\ulise\OneDrive\Escritorio\IA\Practica2\assets\game\fondo.png")
nave_img = pygame.image.load(r"C:\Users\ulise\OneDrive\Escritorio\IA\Practica2\assets\game\cannon.png")
menu_img = pygame.image.load(r"C:\Users\ulise\OneDrive\Escritorio\IA\Practica2\assets\game\menu.png")
bala_vertical_img = pygame.image.load(r"C:\Users\ulise\OneDrive\Escritorio\IA\Practica2\assets\sprites\purple_ball.png")

# Escalar la imagen de fondo para que coincida con el tamaño de la pantalla
fondo_img = pygame.transform.scale(fondo_img, (w, h))

# Crear el rectángulo del jugador y de la bala
jugador = pygame.Rect(50, h - 100, 32, 48)
bala = pygame.Rect(w - 50, h - 90, 16, 16)
nave = pygame.Rect(w - 100, h - 100, 64, 64)
bala_vertical = pygame.Rect(w // 2, 0, 16, 16)
menu_rect = pygame.Rect(w // 2 - 135, h // 2 - 90, 270, 180)  # Tamaño del menú

# Variables para la animación del jugador
current_frame = 0
frame_speed = 10  # Cuántos frames antes de cambiar a la siguiente imagen
frame_count = 0

# Variables para la bala
velocidad_bala = -10  # Velocidad de la bala hacia la izquierda
bala_disparada = False
velocidad_bala_vertical = 10  # Velocidad hacia abajo
bala_vertical_disparada = False

# Variables para el fondo en movimiento
fondo_x1 = 0
fondo_x2 = w

# Cargar el modelo entrenado de la red neuronal
#modelo_red_neuronal = None
#modelo = load_model("modelo_red_neuronal.h5")

#modelo_red_neuronal = load_model("modelo_red_neuronal.h5")

def cargar_modelo():
    global modelo_red_neuronal
    try:
        modelo_red_neuronal = load_model("modelo_red_neuronal.h5")  # Cargar modelo .h5
        print("Modelo cargado correctamente.")
    except FileNotFoundError:
        print("No se encontró un modelo previamente entrenado.")
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")


# Función para predecir el salto usando el modelo de red neuronal
def predecir_salto(velocidad_bala, distancia):
    if modelo_red_neuronal:
        # Convertir la entrada a un array NumPy compatible con el modelo
        entrada = np.array([[velocidad_bala, distancia]], dtype=np.float32)
        
        # Realizar la predicción
        prediccion = modelo_red_neuronal.predict(entrada)
        
        # Mostrar la predicción
        print("Valor de predicción:", prediccion[0][0])
        
        # Determinar si debe saltar según el umbral (0.5)
        if prediccion[0][0] >= 0.5:
            return 1  # Saltar
        else:
            return 0  # No saltar
    
    # Si no hay modelo cargado, no saltar
    print("No se ha cargado un modelo.")
    return 0

# Función para cargar el modelo entrenado de Árbol de Decisión
def cargar_modelo_arbol():
    global modelo_arbol_decision
    try:
        with open("modelo_arbol_decision.pkl", "rb") as archivo_modelo:
            modelo_arbol_decision = pickle.load(archivo_modelo)
            print("Modelo de Árbol de Decisión cargado correctamente.")
    except FileNotFoundError:
        print("No se encontró un modelo previamente entrenado de Árbol de Decisión.")

# Función para predecir el salto usando el modelo de Árbol de Decisión
def predecir_salto_arbol(velocidad_bala, distancia):
    if modelo_arbol_decision:
        prediccion = modelo_arbol_decision.predict([[velocidad_bala, distancia]])  
        print("Valor Predicho por Árbol de Decisión:", prediccion[0])
        return prediccion[0]  # Retorna 1 si saltó, 0 si no saltó
    return 0  # Si no hay modelo cargado, no saltar

# Función para cargar el modelo entrenado de Regresion Lineal
def cargar_modelo_regresion():
    global modelo_regresion
    try:
        modelo_regresion = load_model("modelo_regresion_lineal.h5")
        print("Modelo de regresión lineal cargado correctamente.")
    except Exception as e:
        print(f"Error al cargar el modelo de regresión lineal: {e}")

# Función para predecir el salto usando el modelo de Regresion Lineal
def predecir_salto_regresion(velocidad_bala, distancia):
    if modelo_regresion:
        
        entrada = np.array([[velocidad_bala, distancia]], dtype=np.float32)
        
        prediccion = modelo_regresion.predict(entrada)
        
        print("Valor de predicción (Regresión):", prediccion[0][0])
        
        if prediccion[0][0] >= 0.5:
            return 1  
        else: 
            return 0
        
    print("No se ha cargado un modelo de regresión lineal.")
    
    return 0 # Si no hay modelo cargado, no saltar


# Función para cargar el modelo entrenado de KNN
def cargar_modelo_knn():
    global modelo_knn
    try:
        with open("modelo_knn.pkl", "rb") as archivo_modelo:
            modelo_knn = pickle.load(archivo_modelo)
            print("Modelo KNN cargado correctamente.")
    except FileNotFoundError:
        print("No se encontró un modelo previamente entrenado de KNN.")

# Función para predecir el salto usando KNN
def predecir_salto_knn(velocidad_bala, distancia):
    if modelo_knn:
        entrada = np.array([[velocidad_bala, distancia]])
        prediccion = modelo_knn.predict(entrada)
        print("Predicción KNN:", prediccion[0])
        return prediccion[0]
    return 0

# Función para disparar la bala
def disparar_bala():
    global bala_disparada, velocidad_bala
    if not bala_disparada:
        velocidad_bala = random.randint(-8, -3)  # Velocidad aleatoria negativa para la bala
        bala_disparada = True

# Función para reiniciar la posición de la bala
def reset_bala():
    global bala, bala_disparada
    bala.x = w - 50  # Reiniciar la posición de la bala
    bala_disparada = False

def debe_moverse_derecha_por_bala_vertical():
    if bala_vertical_disparada:
        distancia_x = jugador.x - bala_vertical.x
        distancia_y = bala_vertical.y - jugador.y

        # Si la bala vertical está bastante cerca horizontalmente y a punto de caer
        if abs(distancia_x) < 50 and 0 < distancia_y < 150:
            return True
    return False



def disparar_bala_vertical():
    global bala_vertical_disparada, velocidad_bala_vertical
    if not bala_vertical_disparada:
        velocidad_bala_vertical = random.randint(3, 8)  # Velocidad aleatoria positiva para caer
        bala_vertical_disparada = True

        posicion_inicial = jugador.x + jugador.width // 2 - bala_vertical.width // 2
        bala_vertical.x = posicion_inicial
        bala_vertical.y = 0  # Desde arriba

def reset_bala_vertical():
    global bala_vertical, bala_vertical_disparada
    bala_vertical.x = jugador.x + jugador.width // 2 - bala_vertical.width // 2  # Centrada horizontalmente sobre el jugador
    bala_vertical.y = 0  # Reiniciar arriba
    bala_vertical_disparada = False



# Función para manejar el salto
def manejar_movimiento():
    global jugador, salto, salto_altura, gravedad, en_suelo

    keys = pygame.key.get_pressed()

    # Mover a la derecha con la tecla "d"
    if keys[pygame.K_d]:
        jugador.x += 5  # Ajusta la velocidad de movimiento a la derecha si quieres


def manejar_salto():
    global jugador, salto, salto_altura, gravedad, en_suelo

    # Manejo del salto
    if salto:
        jugador.y -= salto_altura
        salto_altura -= gravedad

        if jugador.y >= h - 100:
            jugador.y = h - 100
            salto = False
            salto_altura = 15
            en_suelo = True




# Función para actualizar el juego
def update():
    global bala, velocidad_bala, current_frame, frame_count, fondo_x1, fondo_x2
    global bala_vertical, velocidad_bala_vertical, bala_vertical_disparada

    # Mover el fondo
    fondo_x1 -= 1
    fondo_x2 -= 1

    if fondo_x1 <= -w:
        fondo_x1 = w
    if fondo_x2 <= -w:
        fondo_x2 = w

    # Dibujar fondos
    pantalla.blit(fondo_img, (fondo_x1, 0))
    pantalla.blit(fondo_img, (fondo_x2, 0))

    # Animación del jugador
    frame_count += 1
    if frame_count >= frame_speed:
        current_frame = (current_frame + 1) % len(jugador_frames)
        frame_count = 0

    # Dibujar jugador animado
    pantalla.blit(jugador_frames[current_frame], (jugador.x, jugador.y))

    # Dibujar la nave
    pantalla.blit(nave_img, (nave.x, nave.y))

    # --- Bala horizontal ---
    if bala_disparada:
        bala.x += velocidad_bala
    if bala.x < 0:
        reset_bala()
    pantalla.blit(bala_img, (bala.x, bala.y))

    # Colisión bala horizontal
    if jugador.colliderect(bala):
        print("¡Colisión horizontal detectada!")
        reiniciar_juego()

    
    if bala_vertical_disparada:
        bala_vertical.y += velocidad_bala_vertical
        pantalla.blit(bala_vertical_img, (bala_vertical.x, bala_vertical.y))

        if bala_vertical.y > h:
            reset_bala_vertical()

    # Colisión bala vertical
    if bala_vertical_disparada and jugador.colliderect(bala_vertical):
        print("¡Colisión vertical detectada!")
        reiniciar_juego()

# Función para guardar datos del modelo en modo manual
def guardar_datos():
    global jugador, bala, velocidad_bala, salto
    distancia = abs(jugador.x - bala.x)
    salto_hecho = 1 if salto else 0  # 1 si saltó, 0 si no saltó
    # Guardar velocidad de la bala, distancia al jugador y si saltó o no
    datos_modelo.append((velocidad_bala, distancia, salto_hecho))

def guardar_datos_vertical():
    global jugador, bala_vertical, velocidad_bala_vertical, salto
    distancia_vertical = abs(jugador.y - bala_vertical.y)
    salto_hecho = 1 if salto else 0
    datos_modelo.append((velocidad_bala_vertical, distancia_vertical, salto_hecho))

# Función para pausar el juego y guardar los datos
def pausa_juego():
    global pausa
    pausa = not pausa
    if pausa:
        print("Juego pausado. Datos registrados hasta ahora:", datos_modelo)
    else:
        print("Juego reanudado.")


# Función para mostrar el menú y seleccionar el modo de juego
def mostrar_menu():
    global menu_activo, modo_auto, modelo_actual 
    menu_activo = True# muestra menu

    pantalla.fill(NEGRO)
    texto = fuente.render("1.- Juego Manual", True, BLANCO)
    texto1 = fuente.render("2.- Redes Neuronales", True, BLANCO)
    texto2 = fuente.render("3.- Árbol de Decisión", True, BLANCO)
    texto3 = fuente.render("4.- Regresión Lineal", True, BLANCO)
    texto4 = fuente.render("5.- K Nearest Neighbor", True, BLANCO)
    texto5 = fuente.render("6.- Salir", True, BLANCO)

    
    x_centro = w // 2
    y_inicial = h // 4
    espacio_entre_renglones = 50  # renglones

    pantalla.blit(texto, (x_centro - texto.get_width() // 2, y_inicial))
    pantalla.blit(texto1, (x_centro - texto1.get_width() // 2, y_inicial + espacio_entre_renglones))
    pantalla.blit(texto2, (x_centro - texto2.get_width() // 2, y_inicial + 2 * espacio_entre_renglones))
    pantalla.blit(texto3, (x_centro - texto3.get_width() // 2, y_inicial + 3 * espacio_entre_renglones))
    pantalla.blit(texto4, (x_centro - texto4.get_width() // 2, y_inicial + 4 * espacio_entre_renglones))
    pantalla.blit(texto5, (x_centro - texto5.get_width() // 2, y_inicial + 5 * espacio_entre_renglones))
    pygame.display.flip() 

    while menu_activo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_m:
                    menu_activo = True
                    mostrar_menu()
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    print("MODO MANUAL")
                    modo_auto = False
                    menu_activo = False
                elif evento.key == pygame.K_2:
                    print("REDES NEURONALES")
                    modo_auto = True
                    menu_activo = False
                    entrenar_red_neuronal(datos_modelo)
                    cargar_modelo()
                    modelo_actual = "red_neuronal"
                elif evento.key == pygame.K_3:
                    print("ÁRBOL DE DECISIÓN")
                    modo_auto = True
                    menu_activo = False
                    entrenar_arbol_decision(datos_modelo)
                    cargar_modelo_arbol()
                    modelo_actual = "arbol"    
                elif evento.key == pygame.K_4:
                    print("REGRESIÓN LINEAL")
                    modo_auto = True
                    menu_activo = False
                    entrenar_regresion_lineal(datos_modelo)
                    cargar_modelo_regresion()
                    modelo_actual = "regresion"
                elif evento.key == pygame.K_5:
                    print("K-NEAREST NEIGHBORS")
                    modo_auto = True
                    menu_activo = False
                    entrenar_knn(datos_modelo)
                    cargar_modelo_knn()
                    modelo_actual = "knn"
                elif evento.key == pygame.K_6:
                    print("Juego terminado. Datos recopilados:", datos_modelo)
                    pygame.quit()
                    exit()


def reiniciar_juego():
    global menu_activo, jugador, bala, nave, bala_disparada, salto, en_suelo, bala_vertical, bala_vertical_disparada
    menu_activo = True  # Activar de nuevo el menú
    jugador.x, jugador.y = 50, h - 100  # Reiniciar posición del jugador
    bala.x = w - 50  # Reiniciar posición de la bala
    nave.x, nave.y = w - 100, h - 100  # Reiniciar posición de la nave
    bala_disparada = False
    salto = False
    en_suelo = True
    # Reiniciar bala vertical
    bala_vertical.x = jugador.x + jugador.width // 2 - bala_vertical.width // 2
    bala_vertical.y = 0
    bala_vertical_disparada = False

    # Mostrar los datos recopilados hasta el momento
    print("Datos recopilados para el modelo: ", datos_modelo)
    mostrar_menu()  # Mostrar el menú de nuevo para seleccionar modo


def main():
    global salto, en_suelo, bala_disparada, modelo_actual

    reloj = pygame.time.Clock()
    mostrar_menu()  # Mostrar el menú al inicio
    correr = True

    posicion_original_x = jugador.x

    while correr:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                correr = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE and en_suelo and not pausa:
                    salto = True
                    en_suelo = False
            if evento.type == pygame.KEYUP:
                if evento.key == pygame.K_d:
                    jugador.x = posicion_original_x
                if evento.key == pygame.K_p:
                    pausa_juego()
                if evento.key == pygame.K_q:
                    print("Juego terminado. Datos recopilados:", datos_modelo)
                    pygame.quit()
                    exit()
                if evento.key == pygame.K_m:
                    print("Volviendo al menú para seleccionar otro modelo...")
                    mostrar_menu()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            jugador.x = posicion_original_x + 60  # Mover manualmente a la derecha

    # Disparar bala vertical cada 2 segundos aprox.
        if pygame.time.get_ticks() % 2000 < 30:
            if not bala_vertical_disparada:
                disparar_bala_vertical()

        if not pausa:
            if not modo_auto:
            # Modo manual
                if salto:
                    manejar_salto()
                guardar_datos()
            else:
            # Modo automático
                distancia = abs(jugador.x - bala.x)
                decision_salto = 0

                if modelo_actual == "arbol":
                    decision_salto = predecir_salto_arbol(velocidad_bala, distancia)
                elif modelo_actual == "red_neuronal":
                    decision_salto = predecir_salto(velocidad_bala, distancia)
                elif modelo_actual == "regresion":
                    decision_salto = predecir_salto_regresion(velocidad_bala, distancia)
                elif modelo_actual == "knn":
                    decision_salto = predecir_salto_knn(velocidad_bala, distancia)

            # Forzar salto si la bala vertical está cerca
                if bala_vertical_disparada:
                    distancia_x = jugador.x - bala_vertical.x
                    distancia_y = bala_vertical.y - jugador.y

                    if abs(distancia_x) < 50 and 0 < distancia_y < 150:
                        decision_salto = 1

            # Ejecutar salto si se requiere y el jugador está en suelo
                if decision_salto == 1 and en_suelo:
                    salto = True
                    en_suelo = False

                if salto:
                    manejar_salto()

            # Movimiento lateral para esquivar bala vertical
                if bala_vertical_disparada:
                    distancia_x = jugador.x - bala_vertical.x
                    distancia_y = bala_vertical.y - jugador.y

                    if abs(distancia_x) < 50 and 0 < distancia_y < 150:
                        if jugador.x + 5 < w - jugador.width:
                            jugador.x += 5
                    else:
                    # Regresar a posición original suavemente
                        if jugador.x > posicion_original_x:
                            jugador.x -= 5



        # Disparar bala horizontal si no está activa
            if not bala_disparada:
                disparar_bala()

            update()

        pygame.display.flip()
        reloj.tick(45)


    pygame.quit()

if __name__ == "__main__":
    main()
