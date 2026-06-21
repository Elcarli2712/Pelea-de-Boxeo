import datetime
import json
from typing import List, Dict, Optional
# Clase para los recursos
class Recurso:
    def __init__(self, nombre: str, cantidad_total: int):
        self.nombre = nombre
        self.cantidad_total = cantidad_total
        self.cantidad_asignada = 0  # Cantidad actualmente asignada en eventos activos

    def asignar(self, cantidad: int) -> bool:
        if self.cantidad_asignada + cantidad <= self.cantidad_total:
            self.cantidad_asignada += cantidad
            return True
        return False

    def liberar(self, cantidad: int):
        self.cantidad_asignada = max(self.cantidad_asignada - cantidad, 0)

    def disponible(self) -> int:
        return self.cantidad_total - self.cantidad_asignada

    def __repr__(self):
        return f"{self.nombre} (Total: {self.cantidad_total}, Asignados: {self.cantidad_asignada})"

# Clase para un evento de boxeo
class Evento:
    def __init__(self, id_evento: int, fecha: datetime.date, hora_inicio: datetime.time,
                 hora_fin: datetime.time, recursos_solicitados: Dict[str, int]):
        self.id_evento = id_evento
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.recursos_solicitados = recursos_solicitados  # {nombre_recurso: cantidad}

    def intervalo(self):
        inicio = datetime.datetime.combine(self.fecha, self.hora_inicio)
        fin = datetime.datetime.combine(self.fecha, self.hora_fin)
        return (inicio, fin)

    def __repr__(self):
        return (f"Evento {self.id_evento} - {self.fecha} {self.hora_inicio.strftime('%H:%M')} a \n"
                f"{self.hora_fin.strftime('%H:%M')} - Recursos: {self.recursos_solicitados}")

# Estructura inicial del planificador
class Planificador:
    def __init__(self):
        self.recursos: Dict[str, Recurso] = {}
        self.eventos: List[Evento] = []
        self.ultimo_id_evento = 0
        self.ultimo_evento_no_reutilizable_fecha: Optional[datetime.date] = None

    def agregar_recurso(self, nombre: str, cantidad: int):
        self.recursos[nombre] = Recurso(nombre, cantidad)

    def listar_recursos(self):
        for recurso in self.recursos.values():
            print(recurso)

    def listar_eventos(self):
        for evento in self.eventos:
            print(evento)

    def _hay_conflicto_horario(self, nuevo_evento: Evento) -> bool:
        nuevo_inicio, nuevo_fin = nuevo_evento.intervalo()
        eventos_solapados = []
        for evento in self.eventos:
            inicio, fin = evento.intervalo()
            # Verificar si hay solapamiento de horarios
            if nuevo_inicio < fin and nuevo_fin > inicio:
                eventos_solapados.append(evento)
        if not eventos_solapados:
            return False
        # Verificar si hay conflicto en recursos
        for recurso, cantidad_solicitada in nuevo_evento.recursos_solicitados.items():
            cantidad_usada = 0
            for evento in eventos_solapados:
                if recurso in evento.recursos_solicitados:
                        cantidad_usada += evento.recursos_solicitados[recurso]
            if recurso in self.recursos:
                if cantidad_solicitada + cantidad_usada > self.recursos[recurso].cantidad_total:
                    return True
        return False

    def _validar_restricciones(self, recursos_solicitados: Dict[str, int]):
        #Validacion generica: todas las cantidades deben ser no negativas
        for recurso, cantidad in recursos_solicitados.items():
            if cantidad<0:
                return False, f"la cantidad para '{recurso}' no puede ser negativa"
            
        # 1. Solo un tipo de guantes por peleador (16 oz o 14 oz)
        guantes_16 = recursos_solicitados.get("Guantes 16 oz", 0)
        guantes_14 = recursos_solicitados.get("Guantes 14 oz", 0)
        if guantes_16 > 0 and guantes_14 > 0:
            return False, "No se pueden pedir ambos tipos de guantes para un mismo evento"

        # 2. Vendas obligatorias si hay guantes
        if (guantes_16 > 0 or guantes_14 > 0) and recursos_solicitados.get("Vendas", 0) <= 0:
            return False, "Las vendas son obligatorias cuando se usan guantes."

        # 3. Peleadores y equipo de entrenamiento
        peleadores = recursos_solicitados.get("Peleadores", 0)
        equipo_entrenamiento = recursos_solicitados.get("Equipo de entrenamiento", 0)
        if peleadores <=0:
            return False, "Es obligatorio solicitar peleadores, la cantidad debe ser mayor que 0"
        if peleadores % 2 != 0:
            return False, "La cantidad de peleadores debe ser par para asegurar que todos tengan oponente"
        if equipo_entrenamiento < peleadores:
            return False, f"El equipo de entrenamiento debe ser almenos igual que el numero de peleadores. Se solicitaron {equipo_entrenamiento} equipos para {peleadores} peleadores"

        # 4. Árbitro debe venir con silbato (asumimos que el recurso \"Árbitros\" incluye silbato)
        arbitros = recursos_solicitados.get("Árbitros", 0)
        if arbitros <= 0:
            return False, "Debe haber al menos un árbitro con silbato en el evento."

        # 5. Protector Bucal obligatorio
        protector_bucal = recursos_solicitados.get("Protector Bucal", 0)
        if protector_bucal < peleadores:
            return False, f"El protector bucal es obligatorio. Se necesitan almenos {peleadores} protectores bucales para {peleadores} peleadores"

        # 6. Casco es opcional, no hay restricción
        
        return True, ""

    def _verificar_restriccion_espera(self, fecha_evento: datetime.date, recursos_solicitados: Dict[str, int]):
        # Recursos no reutilizables: Protector Bucal, Guantes, Vendas, Cascos
        recursos_no_reutilizables = ["Protector Bucal", "Guantes 16 oz", "Guantes 14 oz", "Vendas", "Cascos"]
        usa_no_reutilizables = any(recursos_solicitados.get(r, 0) > 0 for r in recursos_no_reutilizables)
        if usa_no_reutilizables and self.ultimo_evento_no_reutilizable_fecha:
            diferencia = (fecha_evento - self.ultimo_evento_no_reutilizable_fecha).days
            if diferencia < 30:
                dias_restantes = 30 - diferencia
                return False, (f"Debe esperar {dias_restantes} días para planificar un evento con recursos no reutilizables "
                               "para permitir la adquisición de nuevos recursos.")
        return True, ""

    def agregar_evento(self, fecha: datetime.date, hora_inicio: datetime.time, hora_fin: datetime.time,
                      recursos_solicitados: Dict[str, int]):
        #Validar restricciones personalizadas
        valido, mensaje = self._validar_restricciones(recursos_solicitados)
        if not valido:
            return False, mensaje
        
        #validador de restriccion de espera (30 dias)
        valido, mensaje = self._verificar_restriccion_espera(fecha, recursos_solicitados)
        if not valido:
            return False, mensaje
        
        #crear el evento
        nuevo_id = self.ultimo_id_evento + 1
        nuevo_evento = Evento(nuevo_id, fecha, hora_inicio, hora_fin, recursos_solicitados)

        #verificar conflictos de horario y recursos
        if self._hay_conflicto_horario(nuevo_evento):
            return False, "❌ Conflicto de horario o recursos con otro evento existente"
        
        #asignar recursos
        for recurso, cantidad in recursos_solicitados.items():
            self.recursos[recurso].asignar(cantidad)

        #añadir evento
        self.eventos.append(nuevo_evento)
        self.ultimo_id_evento = nuevo_id

        #actualizar fecha del ultimo evento con recursos no reutilizables
        recursos_no_reutilizables = ["Protector Bucal", "Guantes 16 oz", "Guantes 14 oz", "Vendas", "Cascos"]
        if any(recursos_solicitados.get(r, 0)> 0 for r in recursos_no_reutilizables):
            self.ultimo_evento_no_reutilizable_fecha = fecha
        return True, f"✅ Evento {nuevo_id} agregado exitosamente"
      

    def eliminar_evento(self, id_evento: int):
        evento_a_eliminar = None
        for evento in self.eventos:
            if evento.id_evento == id_evento:
                evento_a_eliminar = evento
                break
        if not evento_a_eliminar:
            return False, f"Evento con ID {id_evento} no encontrado."

        # Liberar recursos
        for recurso, cantidad in evento_a_eliminar.recursos_solicitados.items():
            if recurso in self.recursos:
                self.recursos[recurso].liberar(cantidad)

        self.eventos.remove(evento_a_eliminar)
        return True, f"Evento {id_evento} eliminado exitosamente."

    def ver_detalles_evento(self, id_evento: int) -> Optional[str]:
        for evento in self.eventos:
            if evento.id_evento == id_evento:
                detalles = f"Evento {evento.id_evento}\nFecha: {evento.fecha}\nHorario: {evento.hora_inicio.strftime('%H:%M')} - {evento.hora_fin.strftime('%H:%M')}\nRecursos asignados:\n"
                for recurso, cantidad in evento.recursos_solicitados.items():
                    detalles += f"  - {recurso}: {cantidad}\n"
                return detalles
        return None

    def sugerir_proximo_intervalo(self, duracion_horas: int, recursos_solicitados:Dict[str, int]= None) -> Optional[tuple]:
        #Sugiere el proximo intervalo disponible, considerando horarios, conflictos y disponibilidad de recursos
        if recursos_solicitados is None:
            recursos_solicitados = {}

        # Solo sábados de 6pm-8pm y 8pm-10pm
        hoy = datetime.date.today()
        duracion = datetime.timedelta(hours=duracion_horas)

        # Horarios posibles
        horarios = [
            (datetime.time(18, 0), datetime.time(20, 0)),
            (datetime.time(20, 0), datetime.time(22, 0))
        ]

        for dias_a_sumar in range(0, 365):  # Buscar hasta un año adelante
            dia = hoy + datetime.timedelta(days=dias_a_sumar)
            if dia.weekday() == 5:  # Sábado
                for inicio, fin in horarios:
                    if (datetime.datetime.combine(dia, fin) - datetime.datetime.combine(dia, inicio)) >= duracion:
                        # Crear evento temporal para verificar conflicto
                        evento_temp = Evento(-1, dia, inicio, fin, recursos_solicitados)

                        #Verificar si hay suficiente disponibilidad de recursos
                        recursos_disponibles = True
                        for recurso, cantidad in recursos_solicitados.items():
                            if recurso not in self.recursos:
                                recursos_disponibles = False
                                break
                            if self.recursos[recurso].disponible() < cantidad:
                                recursos_disponibles = False
                                break
                                  
                        if recursos_disponibles:
                            #verificar conflictos de horario y recursos
                            if not self._hay_conflicto_horario(evento_temp):
                                return (dia, inicio, fin)
        return None

    def guardar_estado(self, archivo: str):
        datos = {
            "recursos": {nombre: {
                "cantidad_total": recurso.cantidad_total,
                "cantidad_asignada": recurso.cantidad_asignada
            } for nombre, recurso in self.recursos.items()},
            "eventos": [{
                "id_evento": evento.id_evento,
                "fecha": evento.fecha.isoformat(),
                "hora_inicio": evento.hora_inicio.strftime('%H:%M'),
                "hora_fin": evento.hora_fin.strftime('%H:%M'),
                "recursos_solicitados": evento.recursos_solicitados
            } for evento in self.eventos],
            "ultimo_id_evento": self.ultimo_id_evento,
            "ultimo_evento_no_reutilizable_fecha": self.ultimo_evento_no_reutilizable_fecha.isoformat() if self.ultimo_evento_no_reutilizable_fecha else None
        }
        with open(archivo, 'w') as f:
            json.dump(datos, f, indent=4)

    def cargar_estado(self, archivo: str):
        with open(archivo, 'r') as f:
            datos = json.load(f)

        self.recursos = {}
        for nombre, info in datos.get("recursos", {}).items():
            recurso = Recurso(nombre, info["cantidad_total"])
            recurso.cantidad_asignada = info["cantidad_asignada"]
            self.recursos[nombre] = recurso

        self.eventos = []
        for evento_data in datos.get("eventos", []):
            fecha = datetime.date.fromisoformat(evento_data["fecha"])
            hora_inicio = datetime.datetime.strptime(evento_data["hora_inicio"], '%H:%M').time()
            hora_fin = datetime.datetime.strptime(evento_data["hora_fin"], '%H:%M').time()
            evento = Evento(
                evento_data["id_evento"], fecha, hora_inicio, hora_fin,
                evento_data["recursos_solicitados"]
            )
            self.eventos.append(evento)
        if self.eventos:
            max_id = max(evento.id_evento for evento in self.eventos)
            self.ultimo_id_evento = max(datos.get("ultimo_id_evento", 0), max_id)
        else:   
            self.ultimo_id_evento = datos.get("ultimo_id_evento", 0)
        fecha_ultimo = datos.get("ultimo_evento_no_reutilizable_fecha")
        self.ultimo_evento_no_reutilizable_fecha = datetime.date.fromisoformat(fecha_ultimo) if fecha_ultimo else None


def main():
    planificador = Planificador()
    # Definir recursos con cantidades
    planificador.agregar_recurso("Guantes 16 oz", 10)
    planificador.agregar_recurso("Guantes 14 oz", 10)
    planificador.agregar_recurso("Vendas", 20)
    planificador.agregar_recurso("Peleadores", 10)
    planificador.agregar_recurso("Equipo de entrenamiento", 10)
    planificador.agregar_recurso("Árbitros", 5)
    planificador.agregar_recurso("Cascos", 10)
    planificador.agregar_recurso("Protector Bucal", 20)

    archivo_datos = "planificador_eventos.json"

    while True:
        print("\n--- Planificador Inteligente de Eventos de Boxeo ---")
        print("1. Listar eventos")
        print("2. Agregar evento")
        print("3. Eliminar evento")
        print("4. Ver detalles de evento")
        print("5. Sugerir próximo intervalo disponible")
        print("6. Guardar estado")
        print("7. Cargar estado")
        print("0. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            if not planificador.eventos:
                print("No hay eventos planificados.")
            else:
                planificador.listar_eventos()

        elif opcion == "2":
            try:
                while True:
                    fecha_str = input("Ingrese fecha del evento (YYYY-MM-DD, solo sábados): ")
                    try:
                        fecha = datetime.date.fromisoformat(fecha_str)
                        if fecha.weekday() != 5:
                            print("❌ Error: La fecha debe ser un sábado.")
                            continue
                        hoy=datetime.date.today()
                        if fecha < hoy:
                            print(f"❌ Error: No se pueden crear eventos en fechas pasadas")
                            continue
                        break
                    except ValueError:
                        print("❌ Error: Formato de fecha invalido")
                while True:
                    print("Horarios disponibles:")
                    print("1. 18:00 - 20:00")
                    print("2. 20:00 - 22:00")
                    horario_op = input("Seleccione horario (1 o 2): ")
                    if horario_op == "1":
                        hora_inicio = datetime.time(18, 0)
                        hora_fin = datetime.time(20, 0)
                        break
                    elif horario_op == "2":
                        hora_inicio = datetime.time(20, 0)
                        hora_fin = datetime.time(22, 0)
                        break
                    else:
                        print("❌ Error: Horario inválido. Seleccione 1 o 2")
                hoy = datetime.date.today()
                if fecha == hoy:
                    ahora = datetime.datetime.now().time()
                    if hora_inicio < ahora:
                        print(f"❌ Error: La hora de inicio ya paso")
                        print("El evento no se pudo crear. Vuelva a intentarlo con otra fecha u horario")
                        continue

                print("\nIngrese recursos solicitados (cantidad numerica). Deje vacio o marca 0 para 0")
                print("⚠️-Recuerde las reglas:")
                print("   - No se pueden mezclar guantes 16 oz y 14 oz")
                print("   - Si hay guantes, debe haber vendas")
                print("   - Peleadores: cantidad par y mayor que 0")
                print("   - Equipo de entrenamiento >= peleadores")
                print("   - Arbitros: al menos 1")
                print("   - Protector Bucal: >= peleadores\n")
                recursos_solicitados = {}
                guantes_16 = 0
                guantes_14 = 0
                vendas = 0
                peleadores = 0
                equipo_de_entrenamiento = 0
                arbitros = 0
                protector_bucal = 0
                cascos = 0
                for recurso in planificador.recursos.keys():
                    while True:
                        cantidad_str = input(f"{recurso}: ")
                        try:
                            cantidad = int(cantidad_str) if cantidad_str.strip() else 0
                            if cantidad < 0:
                                print(f"❌ Error: La cantidad para '{recurso}' no puede ser negativa. Intente de nuevo")
                                continue
                            if cantidad > 0:
                                if planificador.recursos[recurso].disponible() < cantidad:
                                    print(f"❌ Error: no hay suficientes unidades para '{recurso}'. Disponible: {planificador.recursos[recurso].disponible()}")
                                    continue
                            # Validaciones en tiempo real segun el recurso
                            error = False

                            #1. Guantes
                            if recurso == "Guantes 16 oz":
                                if cantidad > 0 and guantes_14 > 0:
                                    print(f"❌ Error: No se pueden pedir ambos tipos de guantes. Debe ser parejo para todos")
                                    print(f"   Guantes 16 oz: {cantidad}, Guantes 14 oz: {guantes_14}")
                                    print("Debe elegir un solo tipo. Intente de nuevo")
                                    error = True
                                else:
                                    guantes_16 = cantidad

                            elif recurso =="Guantes 14 oz":
                                if cantidad > 0 and guantes_16 > 0:
                                    print(f"❌ Error: No se pueden pedir ambos tipos de guantes. Debe ser parejo para todos")
                                    print(f"   Guantes 16 oz: {cantidad}, Guantes 14 oz: {guantes_14}")
                                    print("Debe elegir un solo tipo. Intente de nuevo")
                                    error = True
                                else:
                                    guantes_14 = cantidad

                            #2. Vendas
                            elif recurso == "Vendas":
                                vendas = cantidad
                                if (guantes_16 > 0 or guantes_14 > 0) and vendas <= 0:
                                    print(f"❌ Error: Las vendas son obligatorias cuando se usan guantes. Intente de nuevo")
                                    error = True
                                #Validar que vendas >= guantes
                                if guantes_16 > 0 and vendas < guantes_16:
                                    print(f"❌ Error: Debe pedir tantas vendas como guantes")
                                    error = True
                                if guantes_14 > 0 and vendas < guantes_14:
                                    print(f"❌ Error: Debe pedir tantas vendas como guantes")
                                    error = True
                                else:   
                                    vendas = cantidad
                            
                            #3. Peleadores
                            elif recurso == "Peleadores":
                                if cantidad > guantes_14 + guantes_16:
                                    print(f"❌ Error: No es posible pedir mas peleadores que guantes")
                                    error = True
                                if cantidad <= 0:
                                    print(f"❌ Error: Es obligatorio solicitar peleadores, la cantidad debe ser mayor que 0")
                                    error = True
                                if cantidad % 2 != 0:
                                    print(f"❌ Error: La cantidad de peleadores debe ser par para asegurar que todos tengan oponente")
                                    error = True
                                else:
                                    peleadores = cantidad

                                #Validar equipo de entrenamiento si ya se ingreso
                                if equipo_de_entrenamiento > 0 and equipo_de_entrenamiento < peleadores:
                                    print(f"⚠️ Advertencia: El equipo de entrenamiento ({equipo_de_entrenamiento}) es menor que los peleadores ({peleadores}).")
                                    print("   Debe corregir el equipo de entrenamiento cuando llegue a ese recurso")

                            #4. Equipo de entrenamiento
                            elif recurso == "Equipo de entrenamiento":
                                if peleadores > 0 and cantidad < peleadores:
                                    print(f"❌ Error: El equipo de entrenamiento debe ser al menos igual que el numero de peleadores")
                                    error = True
                                else:
                                    equipo_de_entrenamiento = cantidad

                            #5. Arbitros
                            elif recurso == "Árbitros":
                                if cantidad <= 0:
                                    print(f"❌ Error: Debe haber al menos un arbitro en el evento")
                                    error = True
                                else:
                                    arbitros = cantidad

                            #6. Protector Bucal
                            elif recurso == "Protector Bucal":
                                if peleadores > 0 and cantidad < peleadores:
                                    print(f"❌ Error: El protector bucal debe ser al menos igual que el numero de peleadores")
                                    error = True
                                else:
                                    protector_bucal = cantidad

                            #7. Cascos
                            elif recurso == "Cascos":
                                cascos = cantidad

                            if error:
                                continue       
                            
                            recursos_solicitados[recurso] = cantidad
                            break
                        except ValueError:
                            print(f"❌ Error: Debe ingresar un numero entero valido para '{recurso}'. Intente de nuevo")
                exito, mensaje = planificador.agregar_evento(fecha, hora_inicio, hora_fin, recursos_solicitados)
                print(mensaje)
            except Exception as e:
                print(f"❌ Error al agregar evento: {e}")

        elif opcion == "3":
            try:
                id_str = input("Ingrese ID del evento a eliminar: ")
                id_evento = int(id_str)
                exito, mensaje = planificador.eliminar_evento(id_evento)
                print(mensaje)
            except Exception as e:
                print(f"Error al eliminar evento: {e}")

        elif opcion == "4":
            try:
                id_str = input("Ingrese ID del evento para ver detalles: ")
                id_evento = int(id_str)
                detalles = planificador.ver_detalles_evento(id_evento)
                if detalles:
                    print(detalles)
                else:
                    print(f"Evento con ID {id_evento} no encontrado.")
            except Exception as e:
                print(f"Error al ver detalles: {e}")

        elif opcion == "5":
            try:
                while True:
                    duracion_str = input("Ingrese duración en horas (1 o 2): ")
                    try:
                        duracion = int(duracion_str)
                        if duracion not in [1, 2]:
                            print("❌Error: Duración inválida. Solo 1 o 2 horas permitidas.")
                            continue
                        break
                    except ValueError:
                        print("❌Error: Debe ingresar un numero entero (1 o 2). Intente de nuevo")

                #Solicitar recursos para la sugerencia
                print("\nIngrese los recursos que necesitaria para el evento sugerido:")
                recursos_temp = {}
                for recurso in planificador.recursos.keys():
                    while True:
                        cantidad_str = input(f"{recurso} (0 no usar): ")
                        try:
                            cantidad = int(cantidad_str) if cantidad_str.strip() else 0
                            if cantidad < 0:
                                print("❌Error: Las cantidades no pueden ser negativas. Intente de nuevo")
                                continue
                            if cantidad > 0:
                                if planificador.recursos[recurso].disponible() < cantidad:
                                    print(f"❌Error: no hay suficientes unidades para '{recurso}'. Disponible: {planificador.recursos[recurso].disponible()}. Intente de nuevo")
                                    continue
                            recursos_temp[recurso] = cantidad
                            break
                        except ValueError:
                            print("❌Error: Debe ingresar un numero valido. Intente de nuevo")
                            
                sugerencia = planificador.sugerir_proximo_intervalo(duracion, recursos_temp)
                if sugerencia:
                    dia, inicio, fin = sugerencia
                    print(f"✅Próximo intervalo disponible: {dia} de {inicio.strftime('%H:%M')} a {fin.strftime('%H:%M')}")
                else:
                    print("❌No hay intervalos disponibles en el próximo año que cumplan con los recursos solicitados")
            except Exception as e:
                print(f"❌Error al sugerir intervalo: {e}")

        elif opcion == "6":
            try:
                planificador.guardar_estado(archivo_datos)
                print(f"Estado guardado en '{archivo_datos}'.")
            except Exception as e:
                print(f"Error al guardar estado: {e}")

        elif opcion == "7":
            try:
                planificador.cargar_estado(archivo_datos)
                print(f"Estado cargado desde '{archivo_datos}'.")
            except Exception as e:
                print(f"Error al cargar estado: {e}")

        elif opcion == "0":
            print("Saliendo...")
            break

        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    main()
