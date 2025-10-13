import csv
from flask import Blueprint,render_template,request,redirect,url_for,flash
from modelos import Habitacion,cargar_habitaciones,guardar_habitaciones,RUTA_HABITACIONES,cargar_reserva,guardar_habitacion,actualizar_estados_por_fecha
from datetime import datetime, date

habitaciones_bp = Blueprint('habitaciones',__name__)




@habitaciones_bp.route('/habitaciones')
def ver_habitaciones():
    estado_filtro = request.args.get('estado')
    tipo_filtro = request.args.get('tipo')
    fecha_entrada = request.args.get('fecha_entrada')
    fecha_salida = request.args.get('fecha_salida')

    habitaciones = cargar_habitaciones()
    reservas = cargar_reserva()

    actualizar_estados_por_fecha(habitaciones, reservas)
    guardar_habitaciones(habitaciones)

    # Filtro por estado
    if estado_filtro:
        habitaciones = [h for h in habitaciones if h.estado == estado_filtro]

    # Filtro por tipo
    if tipo_filtro:
        habitaciones = [h for h in habitaciones if h.tipo == tipo_filtro]

    # Filtro por disponibilidad en fechas
    if fecha_entrada and fecha_salida:
        try:
            entrada = datetime.strptime(fecha_entrada, '%Y-%m-%d')
            salida = datetime.strptime(fecha_salida, '%Y-%m-%d')

            ocupadas = set()
            for r in reservas:
                if r.estado in ['activa', 'reservada']:
                    if entrada < r.fecha_salida and salida > r.fecha_entrada:
                        ocupadas.add(r.numero_habitacion)

            habitaciones = [h for h in habitaciones if h.numero not in ocupadas]
        except ValueError:
            flash("Fechas inválidas")

    disponibles = sum(1 for h in habitaciones if h.estado == 'disponible')

    return render_template(
        'habitaciones.html',
        habitaciones=habitaciones,
        disponibles=disponibles,
        estado_filtro=estado_filtro,
        tipo_filtro=tipo_filtro,
        fecha_entrada=fecha_entrada,
        fecha_salida=fecha_salida
    )



@habitaciones_bp.route('/habitaciones/agregar',methods=['GET','POST'])
def agregar_habitacion():
    if request.method =='POST':
        numero = request.form['numero']
        tipo = request.form['tipo']
        estado = request.form['estado']
        precio = request.form['precio']
        planta = request.form['planta']
        nueva = Habitacion(numero,tipo,estado,precio,planta)
        guardar_habitacion(nueva)
        flash('Habitacion agregada correctamente')
        return redirect(url_for('habitaciones.ver_habitaciones'))
    return render_template('agregar_habitacion.html')


@habitaciones_bp.route('/habitaciones/editar/<numero>', methods=['GET','POST'])
def editar_estado(numero):
    habitaciones = cargar_habitaciones()
    habitacion = next((h for h in habitaciones if h.numero == numero),None)
    if not habitacion:
        flash(" Habitacion no encontrada")
        return redirect(url_for('habitaciones.ver_habitaciones'))
    
    if request.method =='POST':
        nuevo_estado = request.form['estado']
        habitacion.estado = nuevo_estado
        
        # guardar todas las habitaciones actualizadas 
        guardar_habitaciones(habitaciones)

        flash(f"Estado de la habitacion {numero} actualizado")
        return redirect(url_for('habitaciones.ver_habitaciones'))
                        
    return render_template('editar_estado.html', habitacion=habitacion)
    
    
@habitaciones_bp.route('/habitaciones/editar_completa/<numero>', methods=['GET','POST'])
def editar_habitacion(numero):
    habitaciones = cargar_habitaciones()
    habitacion = next((h for h in habitaciones if h.numero == numero), None)
    
    if not habitacion:
        flash("Habitación no encontrada")
        return redirect(url_for('habitaciones.ver_habitaciones'))

    if request.method == 'POST':
        habitacion.numero = request.form['numero']
        habitacion.tipo = request.form['tipo']
        habitacion.estado = request.form['estado']
        habitacion.precio = request.form['precio']
        habitacion.planta = request.form['planta']
        guardar_habitaciones(habitaciones)
        flash("Habitacion actualizada correctamente")
        return redirect(url_for('habitaciones.ver_habitaciones'))

    

    return render_template('editar_habitacion.html', habitacion=habitacion)
    
    

        



        