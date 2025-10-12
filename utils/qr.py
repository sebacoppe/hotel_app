import qrcode
import os
from utils.format import limpiar_nombre


def generar_qr_para_reserva(reserva_id, nombre_cliente, fecha_entrada):
    url = f"https://hotel-app.onrender.com/reserva/{reserva_id}"
    qr = qrcode.make(url)

    nombre_limpio = limpiar_nombre(nombre_cliente)
    fecha_formateada = fecha_entrada.strftime('%Y%m%d')
    nombre_archivo = f"reserva_{reserva_id}_{nombre_limpio}_{fecha_formateada}.png"

    ruta = os.path.join("static/qr", nombre_archivo)
    os.makedirs("static/qr", exist_ok=True)
    qr.save(ruta)
    return ruta
