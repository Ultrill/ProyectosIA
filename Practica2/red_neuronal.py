import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split


def entrenar_red_neuronal(datos_modelo):
    # Separar las características y las etiquetas
    X = []  # Características (velocidad de la bala, distancia)
    y = []  # Etiquetas (si saltó o no)

    for datos in datos_modelo:
        X.append([datos[0], datos[1]])  # Tomamos velocidad y distancia como características
        y.append(datos[2])  # Tomamos si saltó o no como la etiqueta

    X = np.array(X)
    y = np.array(y)

    # Dividir los datos en conjunto de entrenamiento y conjunto de prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Crear el modelo de red neuronal multicapa
    model = Sequential([
        Dense(4, input_dim=2, activation='relu'),  # Capa oculta con 10 neuronas y activación ReLU
        Dense(1, activation='sigmoid')            # Capa de salida con 1 neurona y activación sigmoide
    ])

    # Compilar el modelo
    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    # Entrenar el modelo
    model.fit(X_train, y_train, epochs=20, batch_size=32, verbose=1)

    # Evaluar el modelo en el conjunto de prueba
    loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"\nPrecisión en el conjunto de prueba: {accuracy:.2f}")

    # Guardar el modelo entrenado en un archivo (opcional)
    model.save("modelo_red_neuronal.h5")  # Guardamos el modelo en formato H5

    print("El modelo de red neuronal ha sido entrenado y guardado correctamente.")

    # Retornar el modelo entrenado por si se necesita en otro contexto
    return model
