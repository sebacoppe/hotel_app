from modelos import (
    cargar_habitaciones, guardar_habitacion, Habitacion,
    cargar_clientes, guardar_cliente, Cliente,
    cargar_reserva, guardar_reserva, Reserva
)

def menu_principal():
    while True:
        print("\n📋 MENÚ PRINCIPAL")
        print("1. Ver habitaciones")
        print("2. Ver clientes")
        print("3. Ver reservas")
        print("4. Agregar habitación")
        print("5. Agregar cliente")
        print("6. Agregar reserva")
        print("0. Salir")

        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            ver_habitaciones()
        elif opcion == "2":
            ver_clientes()
        elif opcion == "3":
            ver_reservas()
        elif opcion == "4":
            agregar_habitacion()
        elif opcion == "5":
            agregar_cliente()
        elif opcion == "6":
            agregar_reserva()
        elif opcion == "0":
            print("👋 Cerrando el sistema...")
            break
        else:
            print("❌ Opción inválida")

def ver_habitaciones():
    habitaciones = cargar_habitaciones()
    print("\n🏨 Habitaciones registradas:")
    for h in habitaciones:
        print(f"- Nº {h.numero} | Tipo: {h.tipo} | Estado: {h.estado} | Precio: ${h.precio}")

def ver_clientes():
    clientes = cargar_clientes()
    print("\n🧍 Clientes registrados:")
    for c in clientes:
        print(f"- ID: {c.id} | {c.nombre} {c.apellido} | DNI: {c.dni} | Tel: {c.telefono} | Email: {c.email}")

def ver_reservas():
    reservas = cargar_reserva()
    print("\n📅 Reservas registradas:")
    for r in reservas:
        print(f"- ID: {r.id_reserva} | Cliente: {r.id_cliente} | Habitación: {r.numero_habitacion} | Entrada: {r.fecha_entrada} | Salida: {r.fecha_salida} | Estado: {r.estado} | Total: ${r.total}")

def agregar_habitacion():
    print("\n➕ Agregar nueva habitación")
    numero = input("Número: ")
    tipo = input("Tipo: ")
    estado = input("Estado (disponible/ocupada/mantenimiento): ")
    precio = input("Precio: ")
    nueva = Habitacion(numero, tipo, estado, precio)
    guardar_habitacion(nueva)
    print("✅ Habitación guardada")

def agregar_cliente():
    print("\n➕ Agregar nuevo cliente")
    id = input("ID: ")
    nombre = input("Nombre: ")
    apellido = input("Apellido: ")
    dni = input("DNI: ")
    telefono = input("Teléfono: ")
    email = input("Email: ")
    nuevo = Cliente(id, nombre, apellido, dni, telefono, email)
    guardar_cliente(nuevo)
    print("✅ Cliente guardado")

def agregar_reserva():
    print("\n➕ Agregar nueva reserva")
    id_reserva = input("ID Reserva: ")
    id_cliente = input("ID Cliente: ")
    numero_habitacion = input("Número de habitación: ")
    fecha_entrada = input("Fecha entrada (YYYY-MM-DD): ")
    fecha_salida = input("Fecha salida (YYYY-MM-DD): ")
    estado = input("Estado (activa/finalizada/cancelada): ")
    total = input("Total: ")
    nueva = Reserva(id_reserva, id_cliente, numero_habitacion, fecha_entrada, fecha_salida, estado, total)
    guardar_reserva(nueva)
    print("✅ Reserva guardada")

if __name__ == "__main__":
    menu_principal()
