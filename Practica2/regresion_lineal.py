import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split

def entrenar_regresion_lineal(datos_modelo):
    X = []
    y = []

    for datos in datos_modelo:
        X.append([datos[0], datos[1]])  # velocidad, distancia
        y.append(datos[2])  # 0 o 1 si saltó o no

    X = np.array(X)
    y = np.array(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = Sequential([
        Dense(1, input_dim=2)  # Capa de salida sin activación (regresión lineal)
    ])

    model.compile(optimizer='adam',
                  loss='mean_squared_error',
                  metrics=['mae'])

    model.fit(X_train, y_train, epochs=20, batch_size=32, verbose=1)

    loss, mae = model.evaluate(X_test, y_test, verbose=0)
    print(f"\nError absoluto medio en el conjunto de prueba: {mae:.2f}")

    model.save("modelo_regresion_lineal.h5")
    print("El modelo de regresión lineal ha sido entrenado y guardado correctamente.")
    return model
