# Certificado de Compliance

**Proyecto:** EP3 — Implementación de Automatización de Red con Compliance Auditado
**Asignatura:** DRY7122 — Programación y Redes Virtualizadas (SDN-NFV)
**Alumno:** Maldonado Bustamante Nicolas Gabriel — Código: 001V-08
**Cliente:** Servicios Financieros SA
**Dispositivo auditado:** Router CSR1kv (hostname inicial) → RTR-SERFIN (hostname corporativo)
**Fecha de auditoría:** 23 de junio de 2026

---

## 1. Alcance de la auditoria

Se certifica que el router corporativo fue aprovisionado mediante automatizacion
(Ansible) y que la configuracion aplicada fue verificada de forma independiente
mediante tres metodos distintos:

1. Comparacion de snapshots de estado (Genie / pyATS) - baseline vs estado final
2. Validacion vía NETCONF (XML, puerto 830)
3. Validacion vía RESTCONF (JSON, HTTPS)

## 2. Criterios verificados

| # | Criterio                  | Valor esperado                              | Conforme |
|---|----------------------------|----------------------------------------------|----------|
| 1 | Hostname corporativo       | RTR-SERFIN                                   | ✅ Si    |
| 2 | IP de Loopback de gestion  | 10.1.8.1 / 255.255.255.0                     | ✅ Si    |
| 3 | Descripcion interfaz WAN   | Enlace-WAN-Puerto-Montt                      | ✅ Si    |
| 4 | Servidor NTP               | 208.67.222.222                               | ✅ Si    |
| 5 | Banner de acceso           | ACCESO RESTRINGIDO - SERFIN                  | ✅ Si    |
| 6 | NETCONF habilitado y operativo | netconf-yang activo, puerto 830          | ✅ Si    |
| 7 | RESTCONF habilitado y operativo | restconf activo, HTTPS                  | ✅ Si    |

## 3. Resultado de las validaciones independientes

| Metodo de validacion | Resultado            |
|------------------------|---------------------|
| Diff Genie (baseline vs final) | Cambios esperados confirmados (interface, routing) |
| NETCONF (validacion_netconf.py) | 5/5 criterios conformes — **CONFORME** |
| RESTCONF (validacion_restconf.py) | 5/5 criterios conformes — **CONFORME** |

## 4. Declaracion

En base a la evidencia recolectada en las Fases 1 a 4 de este proyecto
(snapshots Genie, ejecuciones Ansible idempotentes, validaciones NETCONF y
RESTCONF), se declara que el router **RTR-SERFIN** cumple con la
configuracion corporativa exigida por **Servicios Financieros SA**, y que
dicha configuracion fue verificada por al menos dos canales independientes
de gestion (NETCONF y RESTCONF), ademas de la comparacion estructural de
estado (Genie diff).

**RESULTADO FINAL DE LA AUDITORIA: CONFORME**

---

*Documento generado como parte del entregable academico EP3 - DRY7122,
Escuela de Informatica y Telecomunicaciones, DUOC UC.*
