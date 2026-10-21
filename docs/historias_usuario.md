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