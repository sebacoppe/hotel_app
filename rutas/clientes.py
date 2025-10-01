from flask import Blueprint, render_template, request, redirect, url_for, flash
from modelos import Cliente, cargar_clientes, guardar_cliente, RUTA_CLIENTES
import csv

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/clientes')
def ver_clientes():
    lista = cargar_clientes()
    return render_template('clientes.html', clientes=lista)

@clientes_bp.route('/clientes/agregar', methods=['GET', 'POST'])
def agregar_cliente():
    if request.method == 'POST':
        id = request.form['id']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        dni = request.form['dni']
        telefono = request.form['telefono']
        email = request.form['email']
        
        nuevo = Cliente(id, nombre, apellido, dni, telefono, email)
        guardar_cliente(nuevo)
        flash('Cliente agregado correctamente')
        return redirect(url_for('clientes.ver_clientes'))
    return render_template('agregar_cliente.html')

@clientes_bp.route('/clientes/editar/<id>', methods=['GET', 'POST'])
def editar_cliente(id):
    clientes = cargar_clientes()
    cliente = next((c for c in clientes if c.id == id), None)
    if not cliente:
        flash('Cliente no encontrado')
        return redirect(url_for('clientes.ver_clientes'))

    if request.method == 'POST':
        cliente.nombre = request.form['nombre']
        cliente.apellido = request.form['apellido']
        cliente.dni = request.form['dni']
        cliente.telefono = request.form['telefono']
        cliente.email = request.form['email']

        with open(RUTA_CLIENTES, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'nombre', 'apellido', 'dni', 'telefono', 'email'])
            writer.writeheader()
            for c in clientes:
                writer.writerow(c.to_dict())

        flash(f'Datos del cliente {cliente.nombre} actualizados')
        return redirect(url_for('clientes.ver_clientes'))

    return render_template('editar_cliente.html', cliente=cliente)




                            