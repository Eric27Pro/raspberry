from flask import Flask, Response, render_template, request
import cv2
import numpy as np

app = Flask(__name__)

# Estados de máscaras
mascara_amarilla = False
mascara_verde = False
mascara_roja = False

# URL de la cámara IP
url = "http://192.168.40.54:8080/video"
cap = cv2.VideoCapture(url)

def aplicar_mascaras(frame):
    global mascara_amarilla, mascara_verde, mascara_roja

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    resultado = frame.copy()

    # --- AMARILLO ---
    if mascara_amarilla:
        lower = np.array([20, 100, 100])
        upper = np.array([30, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
        resultado = cv2.bitwise_and(resultado, resultado, mask=mask)

    # --- VERDE ---
    if mascara_verde:
        lower = np.array([40, 70, 70])
        upper = np.array([80, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
        resultado = cv2.bitwise_and(resultado, resultado, mask=mask)

    # --- ROJO ---
    if mascara_roja:
        lower1 = np.array([0, 120, 70])
        upper1 = np.array([10, 255, 255])
        lower2 = np.array([170, 120, 70])
        upper2 = np.array([180, 255, 255])
        mask1 = cv2.inRange(hsv, lower1, upper1)
        mask2 = cv2.inRange(hsv, lower2, upper2)
        mask = cv2.bitwise_or(mask1, mask2)
        resultado = cv2.bitwise_and(resultado, resultado, mask=mask)

    return resultado


def generar_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = aplicar_mascaras(frame)

        _, jpeg = cv2.imencode('.jpg', frame)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n")


@app.route("/video_feed")
def video_feed():
    return Response(generar_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


# Cambia el estado de cada mascara
@app.route("/toggle_color", methods=["POST"])
def toggle_color():
    global mascara_amarilla, mascara_verde, mascara_roja

    color = request.form["color"]

    if color == "yellow":
        mascara_amarilla = not mascara_amarilla
    elif color == "green":
        mascara_verde = not mascara_verde
    elif color == "red":
        mascara_roja = not mascara_roja

    print(f"Estado -> Amarillo:{mascara_amarilla} Verde:{mascara_verde} Rojo:{mascara_roja}")

    return ("OK", 200)


@app.route("/")
def index():
    return render_template("pagina.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
