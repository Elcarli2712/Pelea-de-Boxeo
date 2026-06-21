Planificador Inteligente de Eventos de Boxeo

1. Introducción

El proyecto consiste en un Planificador Inteligente de Eventos de Boxeo, una aplicación de software diseñada para gestionar de manera eficiente la organización de combates de boxeo profesionales y amateurs. El sistema permite a los usuarios añadir, listar, eliminar y consultar eventos, respetando un conjunto complejo de restricciones tanto temporales como de recursos.

La aplicación ha sido desarrollada en Python 3, siguiendo un enfoque orientado a objetos que facilita la comprensión, mantenimiento y extensión del código. La interfaz de usuario se implementa mediante línea de comandos (CLI), ofreciendo una experiencia interactiva y accesible para el usuario final.

---

2. Dominio del Problema

2.1 Contexto del Boxeo y su Gestión

El boxeo es un deporte de combate que requiere una logística meticulosa para la organización de eventos. Cada evento implica la coordinación de múltiples elementos: peleadores, equipos de entrenamiento, árbitros, equipamiento de protección y espacio físico. La complejidad aumenta cuando se consideran las restricciones de tiempo (los eventos solo pueden realizarse en días y horarios específicos) y las limitaciones en la disponibilidad de recursos.

2.2 Selección del Dominio

Se ha elegido el dominio del boxeo por varias razones fundamentales:

· Riqueza de restricciones: El boxeo ofrece un conjunto natural de reglas y dependencias entre recursos que permiten implementar restricciones de inclusión y exclusión mutua de manera significativa.
· Relevancia cultural: Los eventos de boxeo tienen un alto valor de entretenimiento y una estructura organizativa bien definida.
· Complejidad manejable: El dominio presenta la cantidad adecuada de complejidad para demostrar las capacidades del sistema sin ser abrumador.

---

3. Restricciones Temporales

3.1 Restricción de Día y Horario

El sistema implementa una restricción temporal fundamental: los eventos solo pueden tener lugar los sábados, en horario nocturno, específicamente entre las 18:00-20:00 o 20:00-22:00. Esta decisión de diseño refleja la realidad de la industria del boxeo, donde los eventos principales suelen programarse en fines de semana para maximizar la audiencia. Los horarios nocturnos son tradicionales en este deporte, creando un ambiente de espectáculo que caracteriza a las veladas de boxeo.

3.2 Validación de Fechas Pasadas y Hora Futura

El sistema incorpora validaciones adicionales para garantizar que los eventos se planifiquen correctamente:

· Fechas pasadas: No se permiten eventos en fechas anteriores al día actual. Esta regla evita que los organizadores intenten registrar eventos que ya deberían haber ocurrido, manteniendo la integridad del calendario.
· Hora futura: Si la fecha del evento es hoy, la hora de inicio debe ser posterior a la hora actual. Esto garantiza que no se creen eventos que ya deberían haber comenzado, lo cual sería ilógico y generaría confusión en la planificación.

3.3 Restricción de Espera para Recursos No Reutilizables

El sistema implementa una restricción innovadora: 30 días de espera entre eventos que utilizan recursos no reutilizables como guantes, vendas, cascos y protectores bucales. Esta regla refleja la realidad logística del deporte, donde el equipamiento requiere tiempo para ser reemplazado, mantenido o adquirido. Un período de espera garantiza que los organizadores puedan reponer sus inventarios adecuadamente y que el equipamiento esté en condiciones óptimas para cada evento.

---

4. Restricciones de Recursos

4.1 Gestión de Recursos como Pools

A diferencia de un sistema de recursos únicos donde cada recurso es un elemento individual, este proyecto implementa recursos con cantidades. Cada recurso tiene una cantidad total disponible y una cantidad actualmente asignada a eventos activos. Esta arquitectura permite una gestión más realista de los inventarios, donde múltiples eventos pueden compartir recursos del mismo tipo siempre que no excedan la capacidad total.

4.2 Guantes (16 oz y 14 oz)

Entre estos dos recursos existe una restricción de exclusión mutua, dado que no es lógico que exista diferencia de peso entre los guantes de los peleadores. Ningún peleador usará dos tipos de guantes distintos al mismo tiempo, lo que hace las cosas más parejas en la pelea. Los guantes de 16 oz, aunque más lentos para maniobrar, hacen del golpe algo más pesado y potente, mientras que los de 14 oz ayudan con la ligereza del golpe. Permitir ambos tipos en el mismo evento rompería la equidad competitiva, otorgando ventajas injustas a unos peleadores sobre otros.

4.3 Vendas

Las vendas presentan una restricción de inclusión con los guantes seleccionados. Se deben pedir tantas vendas como guantes se hayan solicitado anteriormente, debido a que las vendas sirven para proteger las manos mientras se usan los guantes, evitando lesiones en muñecas y dedos. Sin vendas, el uso de guantes sería insuficiente para garantizar la seguridad de los atletas, ya que las vendas son el primer nivel de protección para las manos de los peleadores. Antes de colocarse los guantes, los boxeadores envuelven sus manos y muñecas con vendas para prevenir lesiones en los huesos metacarpianos, tendones y articulaciones.

4.4 Peleadores y Equipo de Entrenamiento

Estos elementos presentan inclusión también. Cada peleador debe disponer de su esquina que supervise su combate y lo atienda en sus necesidades. Se deben pedir los peleadores en cantidades pares para asegurar que cada uno tenga un oponente, y no se admiten cantidades inferiores o iguales a cero, ya que debe haber participantes obligatoriamente. Esta restricción refleja la estructura organizativa de un evento de boxeo: cada peleador necesita su propio equipo de esquina (entrenador, asistente, médico, etc.) que lo supervise durante el combate y lo atienda en caso de necesidad.

4.5 Árbitro

El árbitro no presenta restricción de inclusión ni exclusión, pero es obligatorio pedir al menos uno, para tener quien dirija los combates. Su papel es fundamental en la dirección del combate, la aplicación de las reglas y la seguridad de los peleadores. La decisión de no imponer más restricciones sobre los árbitros es pragmática: aunque son esenciales, su número no está directamente vinculado a otros recursos del evento.

4.6 Cascos

Los cascos son totalmente opcionales, dado que aumentan la defensa pero reducen la visibilidad de los peleadores. Esta decisión refleja la realidad del boxeo profesional, donde el uso de cascos varía según el nivel de la competición, las regulaciones locales y las preferencias de los organizadores y peleadores. En el boxeo amateur, los cascos son obligatorios, mientras que en el boxeo profesional su uso está prohibido en combates oficiales. Al hacerlos opcionales, el sistema ofrece flexibilidad para adaptarse a diferentes tipos de eventos.

4.7 Protector Bucal

Es estrictamente obligatorio, dado que protege a los peleadores y sus dentaduras. El sistema exige al menos uno por cada peleador. Esta restricción es de vital importancia por razones médicas: los protectores bucales previenen lesiones dentales graves, reducen el riesgo de conmociones cerebrales al amortiguar los impactos y protegen la mandíbula de fracturas. En el boxeo, donde los golpes directos al rostro son la norma, el protector bucal es un elemento de seguridad irrenunciable.

---

5. Validación en Tiempo Real en la Interfaz de Usuario

Una de las características más destacadas del proyecto es la validación en tiempo real durante la entrada de datos. Cuando el usuario ingresa recursos, el sistema verifica inmediatamente las restricciones y muestra errores específicos sin esperar a que se complete todo el proceso.

5.1 Validación de Exclusión de Guantes en Tiempo Real

Si el usuario intenta ingresar ambos tipos de guantes, el sistema detecta inmediatamente el conflicto y muestra un mensaje claro indicando que no se pueden pedir ambos tipos. El usuario solo debe corregir el recurso que falló, sin tener que reiniciar todo el proceso de ingreso.

5.2 Validación de Vendas en Tiempo Real

Cuando el usuario ingresa la cantidad de vendas, el sistema verifica inmediatamente si hay guantes solicitados y si la cantidad de vendas es suficiente. Si las vendas son insuficientes o no se solicitaron, se muestra un error específico y el usuario puede corregirlo en el momento.

5.3 Validación de Peleadores en Tiempo Real

El sistema valida que los peleadores sean en cantidad par y mayor que cero inmediatamente después de ingresar el valor. Si el usuario ingresa un número impar, se le informa que debe ser par para asegurar que todos tengan oponente.

5.4 Ventajas de la Validación en Tiempo Real

· Corrección inmediata: El usuario sabe el error en el momento en que ocurre.
· Sin reinicio: Solo corrige el recurso que falló, no todo el proceso.
· Mensajes claros: Muestra qué está mal y cómo corregirlo.
· Mejor experiencia: El usuario no se frustra teniendo que empezar de nuevo.

---

6. Gestión de Conflictos de Horario y Recursos

6.1 Detección de Conflictos

El sistema implementa un algoritmo robusto para detectar conflictos de horario y recursos:

1. Identificación de eventos solapados: Encuentra todos los eventos existentes que se solapan en horario con el nuevo evento que se quiere crear.
2. Suma de recursos usados: Para cada recurso solicitado, calcula cuántas unidades de ese recurso ya están usadas en todos los eventos que se solapan.
3. Verificación de capacidad: Si la cantidad solicitada sumada a la cantidad ya usada excede la capacidad total del recurso, se detecta un conflicto.

Este algoritmo es especialmente robusto porque detecta conflictos incluso cuando tres o más eventos se solapan en el tiempo y comparten recursos, algo que un sistema de verificación simple por pares no podría detectar.

6.2 Liberación de Recursos al Eliminar

Cuando se elimina un evento, el sistema libera automáticamente todos los recursos que estaban asignados a ese evento, actualizando el inventario para que estén disponibles para futuros eventos.

---

7. Búsqueda Automática de Horarios

7.1 Funcionamiento del Método

El sistema incluye una función inteligente que, dado un evento y los recursos que necesita, analiza el calendario y sugiere el próximo intervalo de tiempo disponible donde se pueda realizar sin conflictos ni violaciones de restricciones. La búsqueda se realiza considerando:

· Los días deben ser sábados.
· Los horarios permitidos: 18:00-20:00 o 20:00-22:00.
· La disponibilidad de recursos solicitados.
· Los conflictos con eventos existentes.

7.2 Casos de Uso

Esta funcionalidad es especialmente útil para:

· Organizadores que necesitan planificar con anticipación.
· Usuarios que no están seguros de qué fechas están disponibles.
· Eventos que requieren fechas consistentes.

---

8. Gestión de Eventos

8.1 Creación de Eventos

El usuario puede crear un nuevo evento proporcionando:

· Fecha (validada como sábado, no pasada, con hora futura si es hoy).
· Horario (18:00-20:00 o 20:00-22:00).
· Cantidades de cada recurso (con validación en tiempo real).
· Confirmación para guardar el evento.

8.2 Listado de Eventos

El usuario puede listar todos los eventos planificados, mostrando su ID, fecha, horario y recursos solicitados.

8.3 Eliminación de Eventos

El usuario puede eliminar un evento existente por su ID, liberando automáticamente los recursos asignados.

8.4 Visualización de Detalles

El usuario puede ver información detallada de un evento específico: fecha, horario completo y todos los recursos asignados con sus cantidades.

---

9. Persistencia de Datos

9.1 Estructura del Archivo JSON

El sistema guarda el estado completo en un archivo JSON con la siguiente información:

· Recursos con sus cantidades totales y asignadas.
· Eventos con fecha, horario y recursos solicitados.
· Último ID de evento asignado.
· Fecha del último evento con recursos no reutilizables (para la restricción de 30 días).

9.2 Ventajas de la Persistencia

· Continuidad: Los eventos persisten entre sesiones de uso.
· Portabilidad: El archivo puede transferirse entre sistemas.
· Respaldo: Los datos pueden respaldarse fácilmente.
· Auditoría: El archivo JSON es legible por humanos.

---

10. Interfaz de Usuario y Experiencia de Uso

10.1 Estructura del Menú

La aplicación presenta un menú interactivo con 8 opciones:

1. Listar eventos: Muestra todos los eventos planificados.
2. Agregar evento: Solicita fecha, horario y recursos.
3. Eliminar evento: Elimina un evento por ID y libera recursos.
4. Ver detalles: Muestra información completa de un evento específico.
5. Sugerir intervalo: Encuentra el próximo espacio disponible.
6. Guardar estado: Persiste el estado en un archivo JSON.
7. Cargar estado: Restaura un estado previamente guardado.
8. Salir: Termina la ejecución.

10.2 Mensajes de Error y Éxito

El sistema utiliza emojis para mejorar la claridad de los mensajes:

· ❌ Error: Indica que algo salió mal y requiere corrección.
· ✅ Éxito: Confirma que una operación se completó correctamente.
· ⚠️ Advertencia: Señala un problema potencial pero no bloquea la operación.

---

11. Conclusiones

11.1 Resumen de Logros

El Planificador Inteligente de Eventos de Boxeo cumple con todos los requisitos establecidos:

1. Dominio bien definido: Eventos de boxeo con restricciones realistas.
2. Restricciones completas: Inclusión, exclusión y obligatoriedad.
3. Validación robusta: En tiempo real en la interfaz de usuario.
4. Detección de conflictos: Horarios y recursos con pools de cantidades.
5. Búsqueda automática: Sugerencia de próximos intervalos disponibles.
6. Persistencia: Guardado y carga de estado en JSON.
7. Interfaz amigable: Menú con mensajes claros y emojis.

11.2 Fortalezas Técnicas

1. Arquitectura orientada a objetos: Clases bien definidas con responsabilidades claras.
2. Validación progresiva: Validación en tiempo real en la interfaz de usuario y validación final en el planificador.
3. Gestión de conflictos avanzada: Detecta conflictos con múltiples eventos solapados.
4. Recursos con cantidades: Gestión de inventarios como pools, no como elementos individuales.
5. Manejo de errores robusto: Mensajes claros y específicos para cada situación.

11.3 Reflexión Final

El proyecto demuestra cómo un software bien diseñado puede resolver problemas logísticos complejos en un dominio específico. La combinación de restricciones temporales, de recursos y de espera refleja un profundo entendimiento del deporte del boxeo y sus necesidades operativas. El código es limpio, bien comentado y sigue las convenciones de Python, lo que facilita su mantenimiento y extensión. El sistema resultante es una herramienta práctica que podría ser adoptada por organizadores de boxeo reales para gestionar sus eventos de manera eficiente.
