Carrera de pingüinos asíncronos con los módulos *threading* y *asyncio*: las diferentes aplicaciones de los sistemas distribuídos, el paso de mensajes y la asincronía

María García Fernández

2º ciencia e ingeniería de datos, Programación III

**Sistemas distribuidos**

“Un sistema distribuido es aquel  en el que componentes hardware o software ubicados en ordenadores conectados en red se comunican y coordinan sus acciones únicamente mediante el paso de mensajes”

Esto significa que los componentes (o nodos) se encuentran repartidos por el medio físico, no existe una memoria compartida, sino que se comunican mediante mensajes en red y, los fallos de cada nodo son independientes. 

En cada uno de los nodos de un sistema distribuido se ejecutan los procesos que lo componen, que se comunican y cooperan mediante mensajes en red. Estas características no sólo ofrecen a los sistemas distribuidos una alta tolerancia a fallos sino  además una fácil escalabilidad debido a que no comparten memoria.

En la ciencia de datos se usan los sistemas distribuidos para procesar grandes volúmenes de información , los cuales no podrían ser gestionados por una máquina de manera independiente. Al mismo tiempo, existen tecnologías y modelos como Apache Spark o Dask que se especializan en distribuir  operaciones entre diferentes máquinas con el fin de  facilitar ciertas tareas simples (limpieza de datos, visualización o entrenamiento de modelos). Los datos recolectados para un proyecto de Data Science pueden provenir de diferentes recursos; bases de datos, servicios externos, terceras partes, IoT…. Para conseguir una fácil integración en un sistema distribuido son necesarios mecanismos de sincronización, gestión de  las diferentes versiones, y control de los posibles conflictos internos.

**Programación asíncrona**

“La programación asíncrona es una técnica que permite a tu programa iniciar una tarea de larga duración y seguir respondiendo a otros eventos mientras esa tarea se ejecuta, en lugar de tener que esperar hasta que esa tarea haya terminado. Una vez que dicha tarea ha finalizado, tu programa presenta el resultado.”

Entendemos que no es necesario  tener que esperar a la finalización de una de las tareas para que otra pueda comenzar, la asincronía permite que el programa pueda gestionar varias tareas al mismo tiempo. Es posible que las tareas de entrada/salida(I/O), digamos consultas a bases de datos o comunicaciones en red, sean ejecutadas en un segundo plano para centrar el enfoque en otro tipo de acciones. Al implementar  este enfoque, se reducen los tiempos de espera y se mejora la eficiencia general del sistema.

Esta técnica resulta imprescindible en el procesamiento de grandes volúmenes de datos cuya información proviene de diversas fuentes, al poder ser analizados simultáneamente y unificarlo.Otra ventaja es conseguir el análisis en tiempo real (como en las plataformas de streaming). Las librerías asyncio, Dask y Ray permiten coordinar las tareas sin necesidad de bloquear otros recursos.Como resultado,  se consigue un aumento en la escalabilidad de los  sistemas y la mejora de respuesta.

**Paso de mensajes**

“El paso de mensajes es una forma de enviar y recibir datos y comandos entre subprocesos o procesos simultáneos utilizando un canal compartido o una cola. El emisor y el receptor no necesitan compartir ninguna memoria o estado, y no necesitan sincronizar su acceso al canal o la cola.” 

Permite desacoplar a los participantes de la comunicación, es decir, en una aplicación de procesamiento distribuido de grandes volúmenes de datos,  los nodos dividen las tareas y se comunican mediante mensajes para mantener la consistencia del procesamiento. En el caso de las arquitecturas basadas en agentes (en este caso multiagente), cada uno actúa autónomamente  a pesar de que comparte objetivos comunes con las demás. Sin embargo, cada proceso mantiene su propio espacio de memoria y se comunica con los demás exclusivamente mediante el envío de mensajes. El objetivo es conseguir un modelo más seguro y escalable, evitando condiciones de carrera y facilitando el diseño de aplicaciones concurrentes.

En ciencia de datos, se aplica el paso de mensajes en sistemas como Apache Kafka o Spark que se encargan de gestionar la comunicación de datos en procesos distribuidos. Las comunicaciones están basadas en colas o buffers para gestionar la recolección, transformación y análisis de los datos.

**Funcionalidad del código**

El proyecto consiste en la simulación de una carrera de pingüinos asíncronos donde cada uno debe ir avanzando con el fin de llegar a la meta. Existen multiagentes en forma de moscas que de manera independiente atacan a los pingüinos. Los elementos que lo configuran (pingüinos , pista y moscas) están representados en la consola mediante símbolos ASCII. El programa está desarrollado usando las librerías *threading* y *asyncio* para poder comparar ambos modelos y sus funcionalidades con respecto a la concurrencia. Los conceptos usados principalmente son los sistemas distribuidos, la programación asíncrona y el paso de mensajes, todos ellos aplicados a un entorno multiagente.

El servidor es la clase que se encarga de controlar el juego,  las posiciones de los pingüinos, el orden de llegada a la meta y decide si se puede avanzar o no. Los bots  preguntan al servidor si pueden avanzar, una vez que éste decide ,les responde. Aquí vemos representado un sistema distribuido centralizado. Se ha añadido una simulación de retardo para que no avancen inmediatamente al recibir el mensaje,  basándose en las redes como Internet(no es todo inmediato).

En esta clase se implementan los tres temas principales: el paso de mensajes, el sistema distribuido y la asincronía. Esta última permite , como se ha mencionado anteriormente, que cada tarea sea independiente a la hora de ejecutarse y que  avancen sin afectar al resto. En cuanto al paso de mensajes, va implícito, pero cada pingu ha de pedir permiso al servidor para poder  avanzar. Es una manera de comunicarse entre componentes, que  se envían información sin necesidad de modificar los datos. En definitiva,  pingüinos y moscas se definen  como hilos o tareas,  avanzando de manera independiente después de pedir permiso al servidor para hacerlo. 

**Código con *threading***

El código simula una carrera usando programación concurrente con *threads*. Cada pingüino y cada mosca se ejecutan en hilos independientes, lo que permite que avancen a la vez sin bloquearse entre sí. Para evitar conflictos cuando varios hilos acceden a recursos compartidos (como la posición o el orden de llegada), usamos un lock en el servidor para que los proteja y los sincronice.

No hay comunicación usando colas(Queue) ni sockets, sin embargo, los pingüinos interactúan con el servidor a través llamadas a métodos como *request_move()*, que funcionan como un sistema de mensajes centralizado. También usamos *sleep()* para simular los retrasos de las redes como Internet. Cada pingüino actúa autónomamente aunque la coordinación general la lleva el servidor, simulando el comportamiento de un sistema distribuido simple.

En este código tenemos las clases **Pingu** y **Fly** que representan a los diferentes elementos que participan en la carrera(los corredores y los atacantes):

La clase **Pingu** la conforma cada uno de los pingus heredando de *threading.Thread*, esto  implica que cada pingu se ejecuta en su hilo personal y corren todos en paralelo. Cuando lo lanzamos(*start()*) nuestros pingus entran en un bucle donde han de esperar y pedir permiso al server para avanzar. Se vuelve a utilizar la asincronía, el paso de mensajes y los sistemas distribuidos.

La clase **Fly** representa una mosca que se mueve por la pista y su cometido es derribar a un pingüino si lo alcanza. Obviamente, cada mosca actúa de forma independiente como un hilo. Al ser lanzada, elige una posición al azar dentro de la pista y a uno de los pingüinos, tiene la capacidad de moverse libremente siempre que siga activa(puede cambiar de objetivo o posición  en la pista). Cada vez que se mueve, su posición (y si cambia objetivo) se actualizan en la variable del servidor. Cuando se choca con un pingüino lo derriba, y hace que éste vuelva al inicio.

Ambas clases heredan de *threading.Threads* lo que implica que se ejecutan en su propio hilo de acuerdo a la concurrencia. Dependen de métodos como *start()* o *run()* para realizar sus tareas simultáneamente (entendiendo la real definición y funcionalidad de esto). 

Usamos candados(*self.Lock*) en el servidor para evitar condiciones de carrera y errores al acceder a los datos compartidos. Aseguramos así que solo un hilo pueda acceder, leer o modificar estructuras como las posiciones, el orden de llegada o la ubicación y objetivo de las moscas.

**Código con *asyncio***

El módulo *asyncio* está centrado principalmente en la escritura de código concurrente y asíncrono, permitiendo que múltiples tareas se ejecuten de manera ‘simultánea’ suspendiendo y reanudando su ejecución según sea necesario. Usa una sintaxis async/wait, define diferentes rutinas(corutinas) y crea bucles de eventos para coordinar la ejecución de tareas asíncronas. Este módulo se presenta como una alternativa más segura al multitasking preventivo usando hilos, reduciendo así la posibilidad de condiciones de carrera y otros errores que surgen con la concurrencia. A diferencia de los enfoques basados en hilos o procesos tradicionales, *asyncio* permite la gestión de múltiples tareas eficientemente dentro de un hilo exclusivo.

Una corutina es una función declarada con *async def* que puede pausar su ejecución y retomarla más tarde, es la unidad básica de trabajo asíncrono en Python. Una tarea, es una corutina que ha sido previamente programada para ejecutarse en el bucle de eventos, permite la ejecución en segundo plano de las corrutinas mientras otras continúan.

En el código con *asyncio*, encontramos que existe una única clase central que actúa como el servidor (clase **Server**). Es la encargada de mantener el estado global compartido, guarda y actualiza constantemente las posiciones de los pingüinos y las moscas, los objetivos de las moscas y aquellos que son derribados, y finalmente crea una instancia de *asyncio.Lock* para controlar los accesos.

Aunque solo haya una clase coordinadora, el código cuenta con dos entidades cuyo comportamiento se basa en las corutinas(*async def*). Estas funciones son las encargadas de que tanto las moscas como los pingüinos completen su objetivo. *run_pingu()*  representa a cada pingu que de manera continua solicita permiso al servidor para poder moverse (*request_move()*)  coopera con otras tareas usando await, de manera que no bloquea la ejecución global. Por otro lado, *start_mosca()* es una tarea que se lanza desde un método y va actualizando su posición moviéndose aleatoriamente.

La falta de colas de mensajes explícitas no supone un problema, pues el modelo simula el paso de mensajes de forma implícita igual que haría un sistema distribuido. Hace llamadas asíncronas a los métodos, el servidor actúa como punto central de sincronización y se incluyen *await()* para simular el tiempo de espera de red.

**Diferencias y similitudes entre ambos módulos**

- Aunque el resultado final de ambos módulos es aparentemente igual, hay grandes diferencias en su funcionalidad:

- Mientras que *threading* está basado en hilos del sistema operativo, *asyncio* funciona sobre un único hilo usando un bucle de eventos.

- El paralelismo sólo es real al usar *threading* gracias al uso de hilos preemptivos.

- En el código con hilos cada agente es una clase (o hilo) independiente mientras que en el código con *asyncio* son tareas asíncronas.

- Ambas hacen uso de candados(*Lock*) para proteger sus secciones críticas y evitar condiciones de carrera y colisiones entre las tareas.

- Del mismo modo, el paso de mensajes viene de manera implícita en ambas mediante llamadas a sus métodos o tareas.

- Las simulaciones del tiempo de espera de red son realizadas con el método *sleep()* en ambas ocasiones, aunque cada una con el módulo correspondiente

Podemos concluir que el uso de *asyncio* es ventajoso pues consta de menos código y de una estructura más simple, es más eficiente en términos de recursos(no se crean hilos reales) y todo ocurre dentro de un hilo cooperativo reduciendo así el riesgo de errores.

**Bibliografía**

How can you use message passing effectively in concurrent programming?, Linkedin

libro Using Asyncio in Python de Caleb Hattingh

El artículo Async IO in Python: A Complete Walkthrough de Real Python 

Introducing asynchronous JavaScript, mdn web docs

Data Distribution into Distributed Systems, Integration, and Advancing Machine Learning, Revista Española de Documentación Científica

Advanced guide to Python 3 programming, John Hunt

Modelización de la concurrencia en sistemas distribuidos multiagente, Carlos Herrero UPV

Concurrencia de los ITS y los sistemas multiagente, Universidad de Sevilla

Análisis automático de prestaciones de aplicaciones paralelas basadas en paso de mensajes, UAB

Asynchronous operations in distributed concurrency control, IEEE

Information consensus of asynchronous discrete-time multi-agent systems, IEEE

Temario de clase: concurrency

Y varios archivos en github y strackOverflow.
