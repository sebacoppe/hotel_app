# ESTE ARCHIVO DEFINE LAS CLASES , COMO LAS RESERVAS , HABITACION , CLIENTE CON METODOS
# PARA CARGAR , GUARDAD Y VALIDAR DATOS . 



import os
import csv
from datetime import datetime,timedelta

def inicializar_csv():
    archivos = {
        'datos/clientes.csv': ['id', 'nombre', 'apellido', 'dni', 'telefono', 'email'],
        'datos/habitaciones.csv': ['numero', 'tipo', 'estado', 'precio','planta'],
        'datos/reservas.csv': ['id_reserva', 'id_cliente', 'numero_habitacion', 'fecha_entrada', 'fecha_salida', 'estado', 'total','fecha_reserva']
    }

    os.makedirs('datos', exist_ok=True)

    for ruta, encabezados in archivos.items():
        if not os.path.exists(ruta):
            with open(ruta, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=encabezados)
                writer.writeheader()
            print(f'✅ Archivo creado: {ruta}')
        else:
            print(f'✔️ Archivo ya existe: {ruta}')




RUTA_CLIENTES = 'datos/clientes.csv'   
RUTA_HABITACIONES = 'datos/habitaciones.csv'
RUTA_RESERVAS = 'datos/reservas.csv'



class Habitacion:
    def __init__(self,numero,tipo,estado,precio,planta="baja"):
        self.numero = numero
        self.tipo = tipo 
        self.estado = estado
        self.precio = precio 
        self.planta = planta
        
    def to_dict(self):
        return {
            'numero': self.numero,
            'tipo': self.tipo,
            'estado':self.estado,
            'precio':self.precio,
            'planta':self.planta 
            
            
            
        }    
def cargar_habitaciones():
    habitaciones = []
    with open(RUTA_HABITACIONES, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for fila in reader:
            numero = fila['numero']
            tipo = fila['tipo']
            estado = fila['estado']
            precio = fila['precio']
            planta = fila.get('planta', 'baja')  # ✅ lee planta o asigna "baja" por defecto
            habitacion = Habitacion(numero, tipo, estado, precio, planta)
            habitaciones.append(habitacion)
    return habitaciones 


def guardar_habitacion(habitacion):
    with open(RUTA_HABITACIONES, 'a' ,newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['numero','tipo','estado','precio','planta'])
        writer.writerow(habitacion.to_dict())
        
    


    
class Cliente:
    def __init__(self, id, nombre , apellido, dni, telefono, email):
        self.id = id
        self.nombre = nombre 
        self.apellido = apellido
        self.dni = dni 
        self.telefono = telefono
        self.email = email
        
        
    def to_dict(self):
        return{
            'id':self.id,
            'nombre':self.nombre,
            'apellido':self.apellido,
            'dni':self.dni,
            'telefono':self.telefono,
            'email':self.email
            
        }    
def cargar_clientes():
    clientes = []
    with open(RUTA_CLIENTES, newline="", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for fila in reader:
            clientes.append(Cliente(**fila))
    return clientes


def guardar_cliente(cliente):
    with open(RUTA_CLIENTES, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id','nombre','apellido','dni','telefono','email'])
        writer.writerow(cliente.to_dict())
        
        
        
class Reserva:
    def __init__(self, id_reserva, id_cliente, numero_habitacion, fecha_entrada, fecha_salida, estado, total, fecha_reserva=None):
        self.id_reserva = id_reserva
        self.id_cliente = id_cliente
        self.numero_habitacion = numero_habitacion
        self.fecha_entrada = fecha_entrada
        self.fecha_salida = fecha_salida
        self.estado = estado
        self.total = total
        self.fecha_reserva = fecha_reserva or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        
        
        
    def to_dict(self):
        return{
            'id_reserva': self.id_reserva,
            'id_cliente': self.id_cliente,
            'numero_habitacion': self.numero_habitacion,
            'fecha_entrada': self.fecha_entrada.strftime('%Y-%m-%d'),
            'fecha_salida': self.fecha_salida.strftime('%Y-%m-%d'),
            'estado': self.estado,
            'total': self.total,
            'fecha_reserva':self.fecha_reserva
        }  
        
# modelos.py

def reserva_superpuesta(nueva, existentes):
    for r in existentes:
        if r.numero_habitacion == nueva.numero_habitacion:
            if not (nueva.fecha_salida <= r.fecha_entrada or nueva.fecha_entrada >= r.fecha_salida):
                return True
    return False
        
        
def cargar_reserva():
    reservas = []
    with open(RUTA_RESERVAS, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for fila in reader:
            fecha_entrada = datetime.strptime(fila['fecha_entrada'], '%Y-%m-%d')
            fecha_salida = datetime.strptime(fila['fecha_salida'], '%Y-%m-%d')
            reservas.append(Reserva(
                fila['id_reserva'],
                fila['id_cliente'],
                fila['numero_habitacion'],
                fecha_entrada,
                fecha_salida,
                fila['estado'],
                fila['total'],
                fila.get('fecha_reserva')
            ))
    return reservas        

def guardar_reserva(lista):
    with open(RUTA_RESERVAS, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'id_reserva','id_cliente','numero_habitacion',
            'fecha_entrada','fecha_salida','estado','total','fecha_reserva'])
        writer.writeheader()
        for reserva in lista:
            writer.writerow(reserva.to_dict())
            
            
def fechas_libres(numero_habitacion, reservas, desde=None, dias=3, rango_busqueda=30):
    desde = desde or datetime.today()
    libres = []

    for i in range(rango_busqueda):
        inicio = desde + timedelta(days=i)
        fin = inicio + timedelta(days=dias)

        nueva = Reserva("temp", "x", numero_habitacion, inicio, fin, "pendiente", "0")
        if not reserva_superpuesta(nueva, reservas):
            libres.append((inicio.strftime('%Y-%m-%d'), fin.strftime('%Y-%m-%d')))

    return libres

    
    

            
        
        
    

            
        