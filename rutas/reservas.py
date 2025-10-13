from modelos import Reserva,cargar_reserva,guardar_reserva,cargar_clientes,cargar_habitaciones,guardar_una_reserva,sincronizar_estados_habitaciones
from flask import Blueprint,render_template,request,redirect,url_for,flash,send_file
from datetime import datetime
from utils.qr import generar_qr_para_reserva
from utils.format import limpiar_nombre
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
import os



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
        

@reservas_bp.route('/reserva/<int:id>/pdf')
def generar_pdf_reserva(id):
    reservas = cargar_reserva()
    clientes = cargar_clientes()
    reserva = next((r for r in reservas if r.id_reserva == str(id)), None)
    cliente = next((c for c in clientes if c.id == reserva.id_cliente), None)

    if not reserva or not cliente:
        flash("Reserva no encontrada")
        return redirect(url_for('reservas.ver_reservas'))

    # Crear PDF en memoria
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle(f"Reserva #{id}")
    
    # Dimensiones de la hoja A4
    ancho, alto = A4
    
    
    # 🖼️ Borde decorativo
    pdf.setStrokeColorRGB(0.5, 0.5, 0.5)  # gris suave
    pdf.setLineWidth(2)
    pdf.rect(30, 30, ancho - 60, alto - 60)  # margen de 30 pts en cada lado

    # Encabezado
    pdf.drawImage("static/img/pleno_mar_1.jpg", 50, 730, width=60, height=60)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(160, 780, "Hotel Pleno Mar Necochea")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(160, 765, "Calle 87 y 2, Necochea, Buenos Aires") 
    pdf.drawString(160, 750, "Tel: (2262) 485287 | plenomar@gmail.com")
    pdf.drawString(400, 740, f"Fecha: {datetime.today().strftime('%d/%m/%Y')}")
    
    
    # 📏 Línea divisoria entre encabezado y datos
    pdf.setLineWidth(1)
    pdf.line(30, 720, ancho - 30, 720)  # debajo del encabezado

    # Datos del cliente
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, 660, "Datos del cliente")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 640, f"Nombre: {cliente.nombre} {cliente.apellido}")
    pdf.drawString(50, 620, f"DNI: {cliente.dni}")
    pdf.drawString(50, 600, f"Email: {cliente.email}")
    pdf.drawString(50, 580, f"Teléfono: {cliente.telefono}")
    
    # 📏 Línea entre datos del cliente y reserva
    pdf.line(30, 560, ancho - 30, 560)

    # Datos de la reserva
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, 520, "Datos de la reserva")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 500, f"Reserva #: {reserva.id_reserva}")
    pdf.drawString(50, 480, f"Habitación: {reserva.numero_habitacion}")
    pdf.drawString(50, 460, f"Entrada: {reserva.fecha_entrada.strftime('%Y-%m-%d')}")
    pdf.drawString(50, 440, f"Salida: {reserva.fecha_salida.strftime('%Y-%m-%d')}")
    pdf.drawString(50, 420, f"Estado: {reserva.estado}")
    pdf.drawString(50, 400, f"Total: ${reserva.total}")
    
    
    # 📏 Línea entre datos de reserva y QR
    pdf.line(30, 380, ancho - 30, 380)

    # QR
    nombre_cliente = f"{cliente.nombre} {cliente.apellido}".strip()
    nombre_limpio = limpiar_nombre(nombre_cliente)
    fecha_formateada = reserva.fecha_entrada.strftime('%Y%m%d')
    nombre_archivo = f"reserva_{id}_{nombre_limpio}_{fecha_formateada}.png"
    ruta_qr = os.path.join("static", "qr", nombre_archivo)
    
    if os.path.exists(ruta_qr):
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, 360, "Código QR de la reserva")
        pdf.drawImage(ruta_qr, 50, 190, width=150, height=150)
        
    # 📏 Línea antes de la firma
    pdf.line(30, 150, ancho - 30, 150)    

    # Firma y pie
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 100, "Documento generado automáticamente por Hotel Pleno Mar Necochea")
    pdf.drawString(50, 85, "Firma autorizada: Guillermo Federico Comas")
    pdf.drawString(200, 40, "Rosana Comas – Gerente de Recepción")



    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f"reserva_{id}.pdf", mimetype='application/pdf')


        