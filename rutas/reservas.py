from modelos import Reserva,cargar_reserva,guardar_reserva,cargar_clientes,cargar_habitaciones,guardar_una_reserva,sincronizar_estados_habitaciones
from flask import Blueprint,render_template,request,redirect,url_for,flash
from datetime import datetime
from utils.qr import generar_qr_para_reserva
from utils.format import limpiar_nombre

reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route('/reserva/<int:id>')
def ver_reserva(id): # reserva individual
    reservas = cargar_reserva()
    clientes = cargar_clientes()

    reserva = next((r for r in reservas if r.id_reserva == str(id)), None)
    if not reserva:
        flash("Reserva no encontrada")
        return redirect(url_for('reservas.ver_reservas'))

    cliente = next((c for c in clientes if c.id == reserva.id_cliente), None)
    nombre_cliente = f"{cliente.nombre} {cliente.apellido}" if cliente else "Cliente"
    nombre_limpio = limpiar_nombre(nombre_cliente)
    fecha_formateada = reserva.fecha_entrada.strftime('%Y%m%d')

    nombre_archivo = f"reserva_{id}_{nombre_limpio}_{fecha_formateada}.png"
    ruta_qr = f"qr/{nombre_archivo}"

    return render_template('reserva_individual.html', reserva=reserva, ruta_qr=ruta_qr, cliente=cliente)

    
    
    
    


@reservas_bp.route('/reservas')
def ver_reservas(): # ver el listado de reservas 
    lista = cargar_reserva()
    return render_template('reservas.html', reservas=lista)

        
    
    



@reservas_bp.route('/reservas/agregar', methods=['GET', 'POST'])
def agregar_reserva():
    clientes = cargar_clientes()
    habitaciones = cargar_habitaciones()

    if request.method == 'POST':
        # Generar ID automáticamente
        reservas_existentes = cargar_reserva()
        if reservas_existentes:
            ultimo_id = max(int(r.id_reserva) for r in reservas_existentes)
            nuevo_id = str(ultimo_id + 1)
        else:
            nuevo_id = "1"

        id_cliente = request.form['id_cliente']
        numero_habitacion = request.form['numero_habitacion']
        fecha_entrada = datetime.strptime(request.form['fecha_entrada'], '%Y-%m-%d')
        fecha_salida = datetime.strptime(request.form['fecha_salida'], '%Y-%m-%d')
        estado = request.form['estado']
        total = request.form['total']

        # Validar cliente
        cliente = next((c for c in clientes if c.id == id_cliente), None)
        if not cliente:
            flash('Cliente no encontrado')
            return redirect(url_for('reservas.agregar_reserva'))

        nueva = Reserva(nuevo_id, id_cliente, numero_habitacion, fecha_entrada, fecha_salida, estado, total)

        # Validar disponibilidad
        for r in reservas_existentes:
            if r.numero_habitacion == numero_habitacion and r.estado in ['activa', 'reservada']:
                if fecha_entrada < r.fecha_salida and fecha_salida > r.fecha_entrada:
                    flash('La habitación ya está reservada en ese periodo')
                    return redirect(url_for('reservas.agregar_reserva'))

        guardar_una_reserva(nueva)
        
        sincronizar_estados_habitaciones()

        # Generar QR personalizado
        nombre_cliente = f"{cliente.nombre} {cliente.apellido}"
        generar_qr_para_reserva(nuevo_id, nombre_cliente, fecha_entrada)

        flash('Reserva creada correctamente')
        return redirect(url_for('reservas.ver_reservas'))

    return render_template('agregar_reserva.html', clientes=clientes, habitaciones=habitaciones)


@reservas_bp.route('/reservas/cliente/<id_cliente>')
def historial_por_cliente(id_cliente):
    reservas = cargar_reserva()
    historial = [r for r in reservas if r.id_cliente == id_cliente]
    return render_template('historial_cliente.html', reservas=historial, id_cliente=id_cliente)

@reservas_bp.route('/reservas/editar/<id_reserva>', methods=['GET','POST'])
def editar_reserva(id_reserva):
    reservas = cargar_reserva()
    reserva = next((r for r in reservas if r.id_reserva == id_reserva),None)
    
    if not reserva:
        flash("Reserva no entontrada ")
        return redirect(url_for('reservas.ver_reservas'))

    if request.method == 'POST':
        reserva.fecha_entrada = request.form['fecha_entrada']
        reserva.fecha_salida = request.form['fecha_salida']
        reserva.estado = request.form['estado']
        reserva.total = request.form['total']
        guardar_reserva(reservas) # guarda toda la lista 
        flash('Reserva actualizada correctamente')
        return redirect(url_for('reservas.ver_reservas'))
    
    return render_template('editar_reserva.html', reserva=reserva) 

@reservas_bp.route('/reservas/cancelar/<id_reserva>')
def cancelar_reserva(id_reserva):
    reservas = cargar_reserva()
    reserva = next((r for r in reservas if r.id_reserva == id_reserva), None)
    
    if reserva:
        reserva.estado = 'cancelada'
        guardar_reserva(reservas)
        sincronizar_estados_habitaciones()
        flash('Reserva cancelada ')
        
    else: 
        flash('Reserva no encontrada')
            
    return redirect(url_for('reservas.ver_reservas'))


@reservas_bp.route('/reservas/eliminar/<id_reserva>', methods=['POST'])
def eliminar_reserva(id_reserva):
    reservas = cargar_reserva()
    reservas_filtradas = [r for r in reservas if r.id_reserva != id_reserva]

    if len(reservas_filtradas) < len(reservas):
        guardar_reserva(reservas_filtradas)
        flash('Reserva eliminada correctamente')
    else:
        flash('Reserva no encontrada')

    return redirect(url_for('reservas.ver_reservas'))






@reservas_bp.route('/reservas/calendario')
def ver_calendario():
    reservas = cargar_reserva()
    clientes = cargar_clientes()
    eventos = []

    for r in reservas:
        cliente = next((c for c in clientes if c.id == r.id_cliente),None)
        nombre = f"{cliente.nombre} {cliente.apellido} " if cliente else "Cliente desconocido"
        
        
        eventos.append({
            'id': r.id_reserva,
            'title': f"Habitación {r.numero_habitacion}",
            'start': r.fecha_entrada.strftime('%Y-%m-%d'),
            'end': r.fecha_salida.strftime('%Y-%m-%d'),
            'color': estado_color(r.estado),
            'cliente': nombre  # nombre completo del cliente
        })

    return render_template('calendario.html', eventos=eventos)

def estado_color(estado):
    colores = {
        'reservada': '#007bff',    # azul
        'ocupada': '#28a745',      # verde
        'cancelada': '#dc3545',    # rojo
        'finalizada': '#6c757d'    # gris
    }
    return colores.get(estado, '#ffc107')  # amarillo por defecto


@reservas_bp.route('/reservas/crear_desde_habitacion/<numero>', methods=['GET','POST'])
def crear_reserva_desde_habitacion(numero):
    clientes = cargar_clientes()
    habitaciones = cargar_habitaciones()
    habitacion = next((h for h in habitaciones if h.numero == numero),None)
    
    if not habitacion:
        flash("Habitacion no encontrada")
        return redirect(url_for('habitaciones.ver_habitaciones'))
    
    if request.method == 'POST':
        reservas_existentes = cargar_reserva()
        nuevo_id = str(max([int(r.id_reserva) for r in reservas_existentes], default=0) +1)
        
        id_cliente = request.form['id_cliente']
        fecha_entrada = datetime.strptime(request.form['fecha_entrada'], '%Y-%m-%d')
        fecha_salida  = datetime.strptime(request.form['fecha_salida'], '%Y-%m-%d')
        estado = request.form['estado']
        total = request.form['total']
        
        
        cliente = next((c for c in clientes if c.id == id_cliente), None)
        if not cliente:
            flash("Cliente no encontrado")
            return redirect(url_for('reservas.crear_reserva_desde_habitacion', numero=numero))
        
        nueva = Reserva(nuevo_id, id_cliente , numero, fecha_entrada, fecha_salida, estado, total)
        
        for r in reservas_existentes:
            if r.numero_habitacion == numero and r.estado in ['activa', 'reservada']:
                if fecha_entrada < r.fecha_salida and fecha_salida > r.fecha_entrada:
                    flash("La Habitacion ya esta reservada en ese periodo ")
                    return redirect(url_for('reservas.crear_reserva_desde_habitacion', numero=numero))
                
        guardar_una_reserva(nueva)
        sincronizar_estados_habitaciones()
        
        nombre_cliente = f"{cliente.nombre} {cliente.apellido} "
        nombre_limpio = limpiar_nombre(nombre_cliente)
        generar_qr_para_reserva(nuevo_id, nombre_limpio, fecha_entrada)
        
        flash("Reserva creada correctamente ")
        return redirect(url_for('reservas.ver_reservas'))
    
    return render_template('crear_reserva_desde_habitacion.html', clientes=clientes, habitacion=habitacion)        
        




        