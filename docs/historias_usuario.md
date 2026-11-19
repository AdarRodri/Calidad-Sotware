# Historias de Usuario - MediCitas

## HU-01 - Registro de paciente

**Como:** paciente

**Quiero:** registrarme en MediCitas

**Para:** poder gestionar mis citas médicas.

### Criterios de aceptación

- El nombre es obligatorio.
- El apellido es obligatorio.
- El correo es obligatorio.
- La contraseña es obligatoria.
- El correo debe ser único.
- La contraseña debe almacenarse utilizando hash seguro.
- El usuario registrado públicamente tendrá rol paciente.

### BDD

```gherkin
Dado que un usuario no está registrado
Cuando envía sus datos de registro válidos
Entonces el sistema crea su cuenta
Y asigna el rol paciente
Y responde HTTP 201
```


## HU-02 - Registro de la atención médica (historia clínica)

**Como:** médico tratante

**Quiero:** registrar el diagnóstico, la evolución y las observaciones médicas de la cita atendida

**Para:** llevar un expediente clínico digital y actualizado de cada paciente.

### Criterios de aceptación

- Solo el médico asignado a la cita puede registrar su atención.
- El diagnóstico es obligatorio; la evolución y las observaciones son opcionales.
- Cada texto admite hasta 4000 caracteres.
- La atención solo se puede registrar desde el día de la cita en adelante.
- No se puede registrar la atención de una cita cancelada.
- Una cita tiene como máximo una historia clínica.
- Al guardar la historia, la cita pasa a estado "atendida".
- El médico puede editar las historias que registró.
- El médico consulta el expediente de sus pacientes, agrupado por paciente.
- Solo el médico autor accede a la historia: ni el administrador ni otros médicos.
- No se puede eliminar un médico que tiene historias clínicas registradas.

### BDD

```gherkin
Dado que un médico tiene una cita confirmada del día de hoy
Cuando registra el diagnóstico, la evolución y las observaciones
Entonces el sistema guarda la historia clínica
Y marca la cita como atendida
Y responde HTTP 201
```

```gherkin
Dado que un médico intenta registrar la atención de una cita de otro médico
Cuando envía la historia clínica
Entonces el sistema responde HTTP 403
```


## HU-03 - Recordatorios automáticos de citas

**Como:** sistema de gestión

**Quiero:** enviar recordatorios automáticos al paciente antes de su cita médica

**Para:** disminuir el ausentismo (inasistencias) a las consultas programadas.

### Criterios de aceptación

- Se genera un recordatorio para las citas programadas o confirmadas que ocurren dentro de las próximas 24 horas (configurable con `RECORDATORIO_HORAS`).
- Cada cita recibe un único recordatorio, aunque el proceso se ejecute varias veces.
- No se generan recordatorios para citas canceladas, atendidas o ya vencidas.
- El paciente ve sus recordatorios vigentes en su panel.
- El proceso se ejecuta automáticamente cada hora mediante una tarea programada protegida con una clave (`CRON_TOKEN`), y también cuando el paciente abre su panel.
- El administrador puede ejecutar el proceso manualmente.
- Si está configurado el servicio de correo, el recordatorio también se envía al correo del paciente.
- Un fallo en el envío del correo no impide que el recordatorio se registre.

### BDD

```gherkin
Dado que un paciente tiene una cita confirmada dentro de 20 horas
Cuando se ejecuta el proceso de recordatorios
Entonces el sistema crea un recordatorio para esa cita
Y el paciente lo ve en su panel
```

```gherkin
Dado que una cita ya tiene recordatorio
Cuando se ejecuta nuevamente el proceso de recordatorios
Entonces el sistema no crea un recordatorio duplicado
```


## HU-04 - Panel de métricas y reportes de citas

**Como:** administrador del sistema

**Quiero:** visualizar un panel con métricas y reportes sobre el estado de las citas (atendidas, canceladas, pendientes)

**Para:** evaluar el flujo de atención de la clínica.

### Criterios de aceptación

- Solo el administrador accede al panel y a los reportes.
- Muestra el total de citas y su distribución en atendidas, canceladas y pendientes (programadas más confirmadas).
- Muestra las citas vencidas sin atender y las tasas de atención y de cancelación.
- Muestra el detalle por médico y la evolución por mes.
- Se puede filtrar por rango de fechas.
- Se puede descargar el reporte de citas en formato CSV.
- Los textos del CSV se neutralizan para evitar la inyección de fórmulas en Excel.

### BDD

```gherkin
Dado que el administrador inició sesión
Cuando abre el panel de métricas
Entonces el sistema muestra las citas atendidas, canceladas y pendientes
```

```gherkin
Dado que un paciente inició sesión
Cuando intenta consultar los reportes
Entonces el sistema responde HTTP 403
```
