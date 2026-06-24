# EP3 — Automatización de Red con Compliance Auditado

**Alumno:** Maldonado Bustamante Nicolas Gabriel — Código: 001V-08
**Asignatura:** DRY7122 — Programación y Redes Virtualizadas (SDN-NFV)
**Cliente:** Servicios Financieros SA
**Repositorio:** ep3-automatizacion-001V-08

---

## 1. Objetivo

Incorporar un nuevo router (CSR1kv) a la infraestructura de red corporativa
de Servicios Financieros SA, automatizando su aprovisionamiento mediante
Ansible y verificando, de manera independiente y auditable, que la
configuración aplicada cumple con los estándares exigidos por la empresa.
Todo el proceso queda documentado con evidencia trazable en este
repositorio, desde el estado inicial del dispositivo hasta la certificación
final de compliance.

## 2. Alcance

El proyecto cubre el ciclo completo de incorporación de un dispositivo de
red a un entorno gestionado:

- Captura del estado inicial del router (baseline) antes de cualquier cambio.
- Aprovisionamiento automatizado de la configuración corporativa vía Ansible.
- Verificación de idempotencia de dicho aprovisionamiento.
- Validación independiente de la configuración aplicada por dos protocolos
  de gestión de red distintos: NETCONF y RESTCONF.
- Comparación estructurada (diff) entre el estado inicial y el estado final.
- Emisión de un certificado de compliance que resume los hallazgos.

No se cubre en este proyecto la configuración de protocolos de enrutamiento
dinámico, políticas de seguridad perimetral, ni integración con sistemas de
monitoreo externos — el alcance se limita a la incorporación base del
dispositivo y su compliance de configuración.

## 3. Infraestructura utilizada

- **DEVASC VM** (Cisco Networking Academy / Emerging Technologies Workshop):
  máquina virtual desde donde se ejecutan todos los comandos, scripts y
  playbooks del proyecto.
- **Router CSR1kv** (Cisco Cloud Services Router 1000V, IOS-XE 16.9.5):
  dispositivo de red objetivo de la automatización, accesible por SSH,
  NETCONF (puerto 830) y RESTCONF (HTTPS).
- Conectividad de red privada entre la VM y el router (192.168.56.101).

## 4. Tecnologías empleadas

| Tecnología   | Uso en el proyecto                                              |
|--------------|-------------------------------------------------------------------|
| pyATS / Genie | Captura de snapshots (baseline y final) y comparación (diff)     |
| Ansible 2.9   | Aprovisionamiento idempotente de la configuración corporativa    |
| NETCONF (ncclient) | Validación independiente vía XML (modelo Cisco-IOS-XE-native) |
| RESTCONF (requests) | Validación independiente vía JSON (HTTPS)                    |
| Git / GitHub  | Control de versiones y trazabilidad de todo el proceso            |
| YAML          | Centralización de variables del proyecto (vars_001V-08.yaml)      |

## 5. Configuración aplicada

A través del playbook de Ansible (`fase2_aprovisionamiento/playbook_001V-08.yaml`),
se aplicaron los siguientes cambios sobre el router, partiendo de un respaldo
previo de la configuración original:

- Habilitación de NETCONF (`netconf-yang`) y RESTCONF (`restconf` + `ip http secure-server`).
- Cambio de hostname: `CSR1kv` → **RTR-SERFIN**.
- Banner de acceso: **ACCESO RESTRINGIDO - SERFIN**.
- Servidor NTP: **208.67.222.222**.
- Descripción de la interfaz WAN (GigabitEthernet1): **Enlace-WAN-Puerto-Montt**.
- Creación de interfaz de gestión Loopback10 con IP **10.1.8.1/24**.

Todos los valores anteriores se gestionan desde un único archivo de
variables (`vars/vars_001V-08.yaml`), sin valores hardcodeados en el
playbook ni en los scripts de validación.

## 6. Resultados de validación

| Validación                                  | Resultado      |
|----------------------------------------------|----------------|
| Primera ejecución del playbook                | 5 tareas `changed`, 0 `failed` |
| Segunda ejecución del playbook (idempotencia) | 10 tareas `ok`, 0 `changed`, 0 `failed` |
| Validación NETCONF (5 criterios)              | 5/5 — **CONFORME** |
| Validación RESTCONF (5 criterios)             | 5/5 — **CONFORME** |
| Diff Genie (baseline vs. estado final)        | Cambios esperados confirmados en `interface` y `routing` (nueva Loopback10, descripción WAN actualizada, rutas conectadas) |

El detalle completo de cada validación se encuentra en las carpetas
`fase3_validacion_netconf/`, `fase4_validacion_restconf/` y
`fase5_reporte/evidencias/diff_001V-08/`. El certificado formal de
compliance se genera mediante el script `fase5_reporte/generar_certificado.py`
y queda disponible en `fase5_reporte/evidencias/certificado_compliance_001V-08.txt`.

## 7. Conclusiones

El proceso de automatización permitió incorporar el router CSR1kv a la red
corporativa de Servicios Financieros SA de forma controlada, repetible y
auditable. La idempotencia del playbook de Ansible se verificó
empíricamente (segunda ejecución sin cambios), y la configuración aplicada
fue confirmada por dos canales de gestión completamente independientes del
proceso de aprovisionamiento (NETCONF y RESTCONF), reduciendo el riesgo de
que un error en una sola herramienta pase inadvertido.

Durante el desarrollo se identificaron y resolvieron varios desafíos
técnicos propios de un entorno de laboratorio (parseo de puertos SSH en
pyATS, manejo de banners MOTD en Ansible, y diferencias de namespace YANG
entre NETCONF y RESTCONF para el bloque NTP), documentados como parte del
proceso de aprendizaje y depuración de este proyecto. El resultado final
demuestra que la automatización de redes, combinada con validación
independiente multicanal, es una estrategia robusta para garantizar el
compliance de configuración en entornos de infraestructura crítica como el
de una entidad financiera.

---

## Estructura del repositorio

```
ep3-automatizacion-001V-08/
├── README.md
├── vars/
│   └── vars_001V-08.yaml
├── fase1_baseline/
│   ├── testbed_001V-08.yaml
│   └── evidencias/
├── fase2_aprovisionamiento/
│   ├── inventario.ini
│   ├── playbook_001V-08.yaml
│   ├── respaldo/
│   └── evidencias/
├── fase3_validacion_netconf/
│   ├── validacion_netconf.py
│   └── evidencias/
├── fase4_validacion_restconf/
│   ├── validacion_restconf.py
│   └── evidencias/
│       └── responses/
└── fase5_reporte/
    ├── testbed_001V-08.yaml
    ├── certificado_compliance.md
    └── evidencias/
```
