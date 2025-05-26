# k_nearest_neighbor.py

from sklearn.neighbors import KNeighborsClassifier
import pickle

def entrenar_knn(datos):

    if not datos:
        print("No hay datos para entrenar el modelo KNN.")
        return

    # Separar características (X) y etiquetas (y)
    X = [[d[0], d[1]] for d in datos]  # velocidad y distancia
    y = [d[2] for d in datos]          # salto (0 o 1)

    # Crear el modelo con k=3 vecinos
    knn = KNeighborsClassifier(n_neighbors=3)

    # Entrenar el modelo
    knn.fit(X, y)

    # Guardar el modelo entrenado en un archivo
    with open("modelo_knn.pkl", "wb") as f:
        pickle.dump(knn, f)

    print("Modelo KNN entrenado y guardado como modelo_knn.pkl")
