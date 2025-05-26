from sklearn.tree import DecisionTreeClassifier
import pickle

def entrenar_arbol_decision(datos_modelo):
    # Separar las características y las etiquetas
    X = []  # Características (velocidad de la bala, distancia)
    y = []  # Etiquetas (si saltó o no)

    for datos in datos_modelo:
        X.append([datos[0], datos[1]])  # Tomamos velocidad y distancia como características
        y.append(datos[2])  # Tomamos si saltó o no como la etiqueta

    # Entrenar el modelo de Árbol de Decisión
    arbol = DecisionTreeClassifier(random_state=42)
    arbol.fit(X, y)

    # Guardar el modelo entrenado
    with open("modelo_arbol_decision.pkl", "wb") as archivo_modelo:
        pickle.dump(arbol, archivo_modelo)
    
    print("Modelo de Árbol de Decisión entrenado y guardado correctamente.")
