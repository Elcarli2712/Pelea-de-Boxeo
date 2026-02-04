El proyecto consiste en un planificador de eventos en el cual se asignarán una fecha determinada y los recursos (en cantidades limitadas) para gestionar combates de boxeo. Su objetivo consiste en permitir al usuario añadir,listar y eliminar eventos, respetando una cierta lógica diseñada por el creador.

# Dominio: En el dominio utilizado se diseñaron restricciones entre diversos elementos

Fecha: Los eventos solo tendrán lugar los sábados (como las peleas estelares de la UFC) y en el horario nocturno: dígase de 18.00h a 20.00h y de 20.00h a 22.00h. Fuera de ese horario no se permitirá crear el evento

Recursos: Esta sección presenta diversos tipos de restricciones, como son la exclusión e inclusión entre los diversos elementos que se van a solicitar

Guantes(16oz o 14oz): Entre estos dos recursos existe una restricción de exclusión mutua, dado que no es lógico que exista diferencia de peso entre los guantes de los peleadores, y además ningún peleador usará dos tipos de guantes distintos al mismo tiempo, eso hace las cosas más parejas en la pelea, dado que los guantes de 16oz, aunque más lentos para maniobrar, hacen del golpe algo más pesado y potente, mientras que los de 14oz ayudan con la ligereza del golpe

Vendas: Las vendas presentan una restricción de inclusión con los guantes seleccionados, es decir, se deben pedir tantas vendas como guantes se hallan solicitado anteriormente, debido a que las vendas sirven para proteger las manos mientras se usan los guantes, para evitar lesiones en muñecas y dedos.

Peleadores y equipo de entrenamiento: Estos presentan inclusión también, pues cada peleador debe disponer de su esquina que supervise su combate y lo atienda en sus necesidades, y se deben pedir los peleadores en cantidades pares para asegurar que cada uno tenga un oponente, mas que no se admiten cantidades inferiores o iguales a 0 (tiene q haber participantes obligatoriamente)

Árbitro: No presenta restricción de inclusión ni exclusión, pero es obligatorio pedir almenos uno, para tener quien dirija los combates

Cascos: Son totalmente opcionales, dado que aumentan la defensa pero reducen la visibilidad de los peleadores

Protector Bucal: Es estrictamente obligatorio, dado que protege a los peleadores y sus dentaduras

# Estructura:
Todo se halla estructurado en el archivo proyecto.py, donde están ubicadas todas las frases y funciones que dan vida al proyecto
