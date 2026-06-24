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
                 hora_fin: datetime.time, recursos_solicitados: Dict[str, int], recurrente: bool = False):
        self.id_evento = id_evento
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.recursos_solicitados = recursos_solicitados  # {nombre_recurso: cantidad}
        self.recurrente = recurrente

    def intervalo(self):
        inicio = datetime.datetime.combine(self.fecha, self.hora_inicio)
        fin = datetime.datetime.combine(self.fecha, self.hora_fin)
        return (inicio, fin)

    def __repr__(self):
        return (f"Evento {self.id_evento} - {self.fecha} {self.hora_inicio.strftime('%H:%M')} a \n"
                f"{self.hora_fin.strftime('%H:%M')} - Recursos: {self.recursos_solicitados} - \n"
                f"{'Recurrente' if self.recurrente else 'Único'}")

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
        for evento in self.eventos:
            inicio, fin = evento.intervalo()
            # Verificar si hay solapamiento de horarios
            if (nuevo_inicio < fin and nuevo_fin > inicio):
                # Verificar si hay conflicto en recursos
                for recurso, cantidad in nuevo_evento.recursos_solicitados.items():
                    if recurso in evento.recursos_solicitados:
                        # Si la suma de cantidades excede la disponible, hay conflicto
                        total_usado = cantidad + evento.recursos_solicitados[recurso]
                        if total_usado > self.recursos[recurso].cantidad_total:
                            return True
        return False

    def _validar_restricciones(self, recursos_solicitados: Dict[str, int]):
        # Restricciones personalizadas:
        # 1. Solo un tipo de guantes por peleador (16 oz o 14 oz)
        guantes_16 = recursos_solicitados.get("Guantes 16 oz", 0)
        guantes_14 = recursos_solicitados.get("Guantes 14 oz", 0)
        if guantes_16 > 0 and guantes_14 > 0:
            return False, "No se pueden pedir ambos tipos de guantes para un mismo evento. Y las cantidades deben ser no negati"

        # 2. Vendas obligatorias si hay guantes
        if (guantes_16 > 0 or guantes_14 > 0) and recursos_solicitados.get("Vendas", 0) == 0:
            return False, "Las vendas son obligatorias cuando se usan guantes."

        # 3. Es obligado pedir peleadores y equipo de entrenamiento
        peleadores = recursos_solicitados.get("Peleadores", 0)
        equipo_entrenamiento = recursos_solicitados.get("Equipo de entrenamiento", 0)
        if peleadores <= 0 or equipo_entrenamiento <= peleadores:
            if peleadores %2!=0:
                return False, "Es obligatorio que se pidan peleadores (en pares) y equipo de entrenamiento. Dichos equipos deben ser almenos la misma cantidad que hay de peladores "

        # 4. Árbitro debe venir con silbato (asumimos que el recurso \"Árbitros\" incluye silbato)
        arbitros = recursos_solicitados.get("Árbitros", 0)
        if arbitros <= 0:
            return False, "Debe haber al menos un árbitro con silbato en el evento."

        # 5. Protector Bucal obligatorio
        protector_bucal = recursos_solicitados.get("Protector Bucal", 0)
        if protector_bucal < peleadores:
            return False, "El protector bucal es obligatorio para el evento y debes pedir almenos uno para cada peleador"

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
                      recursos_solicitados: Dict[str, int], recurrente: bool = False):
        nuevo_id = self.ultimo_id_evento + 1
        nuevo_evento = Evento(nuevo_id, fecha, hora_inicio, hora_fin, recursos_solicitados, recurrente)

        # Validar restricciones personalizadas
        valido, mensaje = self._validar_restricciones(recursos_solicitados)
        if not valido:
            return False, mensaje

        # Validar restricción de espera para recursos no reutilizables
        valido, mensaje = self._verificar_restriccion_espera(fecha, recursos_solicitados)
        if not valido:
            return False, mensaje

        # Validar conflictos de recursos y horarios
        if self._hay_conflicto_horario(nuevo_evento):
            return False, "Conflicto de recursos o horario con otro evento existente."

        # Asignar recursos
        for recurso, cantidad in recursos_solicitados.items():
            if recurso not in self.recursos:
                return False, f"Recurso '{recurso}' no existe en el sistema."
            if self.recursos[recurso].disponible() < cantidad:
                return False, f"No hay suficientes unidades disponibles para el recurso '{recurso}'."

        # Si todo está bien, asignar recursos
        for recurso, cantidad in recursos_solicitados.items():
            self.recursos[recurso].asignar(cantidad)

        self.eventos.append(nuevo_evento)
        self.ultimo_id_evento = nuevo_id

        # Actualizar fecha del último evento con recursos no reutilizables
        recursos_no_reutilizables = ["Protector Bucal", "Guantes 16 oz", "Guantes 14 oz", "Vendas", "Cascos"]
        if any(recursos_solicitados.get(r, 0) > 0 for r in recursos_no_reutilizables):
            self.ultimo_evento_no_reutilizable_fecha = fecha

        return True, f"Evento {nuevo_id} agregado exitosamente."

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
                detalles += f"Recurrente: {'Sí' if evento.recurrente else 'No'}"
                return detalles
        return None

    def sugerir_proximo_intervalo(self, duracion_horas: int) -> Optional[tuple]:
        # Solo sábados de 6pm-8pm y 8pm-10pm
        # Buscar el próximo sábado disponible sin conflictos
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
                        evento_temp = Evento(-1, dia, inicio, fin, {})
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
                "recursos_solicitados": evento.recursos_solicitados,
                "recurrente": evento.recurrente
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
                evento_data["recursos_solicitados"], evento_data["recurrente"]
            )
            self.eventos.append(evento)

        self.ultimo_id_evento = datos.get("ultimo_id_evento", 0)
        fecha_ultimo = datos.get("ultimo_evento_no_reutilizable_fecha")
        self.ultimo_evento_no_reutilizable_fecha = datetime.date.fromisoformat(fecha_ultimo) if fecha_ultimo else None


def main():
    planificador = Planificador()
    # Definir recursos con cantidades
    planificador.agregar_recurso("Guantes 16 oz", 10)
    planificador.agregar_recurso("Guantes 14 oz", 10)
    planificador.agregar_recurso("Vendas", 20)
    planificador.agregar_recurso("Peleadores", 20)
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
                fecha_str = input("Ingrese fecha del evento (YYYY-MM-DD, solo sábados): ")
                fecha = datetime.date.fromisoformat(fecha_str)
                if fecha.weekday() != 5:
                    print("La fecha debe ser un sábado.")
                    continue

                print("Horarios disponibles:")
                print("1. 18:00 - 20:00")
                print("2. 20:00 - 22:00")
                horario_op = input("Seleccione horario (1 o 2): ")
                if horario_op == "1":
                    hora_inicio = datetime.time(18, 0)
                    hora_fin = datetime.time(20, 0)
                elif horario_op == "2":
                    hora_inicio = datetime.time(20, 0)
                    hora_fin = datetime.time(22, 0)
                else:
                    print("Horario inválido.")
                    continue

                print("Ingrese recursos solicitados (cantidad numérica). Deje vacío para 0.")
                recursos_solicitados = {}
                for recurso in planificador.recursos.keys():
                    cantidad_str = input(f"{recurso}: ")
                    cantidad = int(cantidad_str) if cantidad_str.strip() else 0
                    recursos_solicitados[recurso] = cantidad

                recurrente_str = input("¿Evento recurrente? (s/n): ").lower()
                recurrente = recurrente_str == 's'

                exito, mensaje = planificador.agregar_evento(fecha, hora_inicio, hora_fin, recursos_solicitados, recurrente)
                print(mensaje)
            except Exception as e:
                print(f"Error al agregar evento: {e}")

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
                duracion_str = input("Ingrese duración en horas (1 o 2): ")
                duracion = int(duracion_str)
                if duracion not in [1, 2]:
                    print("Duración inválida. Solo 1 o 2 horas permitidas.")
                    continue
                sugerencia = planificador.sugerir_proximo_intervalo(duracion)
                if sugerencia:
                    dia, inicio, fin = sugerencia
                    print(f"Próximo intervalo disponible: {dia} de {inicio.strftime('%H:%M')} a {fin.strftime('%H:%M')}")
                else:
                    print("No hay intervalos disponibles en el próximo año.")
            except Exception as e:
                print(f"Error al sugerir intervalo: {e}")

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
