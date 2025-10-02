from flask import Flask,render_template
from rutas.habitaciones import habitaciones_bp,actualizar_estados_por_fecha
from rutas.clientes import clientes_bp
from rutas.reservas import reservas_bp
from modelos import inicializar_csv,cargar_reserva,cargar_habitaciones

habitaciones = cargar_habitaciones()
reservas = cargar_reserva()
actualizar_estados_por_fecha(habitaciones, reservas)

# Opcional: guardar los estados actualizados
from modelos import RUTA_HABITACIONES
import csv

with open(RUTA_HABITACIONES, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['numero','tipo','estado','precio','planta'])
    writer.writeheader()
    for h in habitaciones:
        writer.writerow(h.to_dict())



app = Flask(__name__)
app.secret_key = 'clave-secreta'

inicializar_csv()

app.register_blueprint(habitaciones_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(reservas_bp)

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/')
def bienvenida():
    return render_template('bienvenida.html')




if __name__ == '__main__':
    app.run(debug=True)


