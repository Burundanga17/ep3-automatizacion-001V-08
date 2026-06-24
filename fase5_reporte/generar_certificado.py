#!/usr/bin/env python3
"""
fase5_reporte/generar_certificado.py

Genera el certificado de compliance del proyecto EP3 (001V-08), leyendo:
- El directorio de diff de Genie (evidencias/diff_001V-08/)
- El output de la validacion NETCONF (Fase 3)
- El output de la validacion RESTCONF (Fase 4)

Determina el resultado global (CONFORME / NO CONFORME) en base a esas
tres fuentes y escribe el certificado final en texto plano.
"""

import os
import sys
from datetime import datetime

CODIGO = "001V-08"
NOMBRE = "Maldonado Bustamante Nicolas Gabriel"
CLIENTE = "Servicios Financieros SA"
HOSTNAME_CORPORATIVO = "RTR-SERFIN"

DIFF_DIR = "evidencias/diff_001V-08"
NETCONF_OUTPUT = "../fase3_validacion_netconf/evidencias/output_fase3.txt"
RESTCONF_OUTPUT = "../fase4_validacion_restconf/evidencias/output_fase4.txt"
SALIDA = f"evidencias/certificado_compliance_{CODIGO}.txt"


def leer_diff(diff_dir):
    """Lee todos los archivos de diff del directorio y reporta si hubo
    cambios detectados (lo cual es el resultado esperado: el aprovisionamiento
    si modifico la configuracion del router)."""
    if not os.path.isdir(diff_dir):
        return False, "Directorio de diff no encontrado."

    archivos = [f for f in os.listdir(diff_dir) if f.endswith(".txt")]
    if not archivos:
        return False, "Directorio de diff vacio - no hay evidencia de cambios."

    resumen = []
    for archivo in sorted(archivos):
        ruta = os.path.join(diff_dir, archivo)
        with open(ruta, "r") as f:
            contenido = f.read()
        lineas_cambio = [l for l in contenido.splitlines() if l.startswith("+") or l.startswith("-")]
        resumen.append(f"  - {archivo}: {len(lineas_cambio)} lineas modificadas")

    return True, "\n".join(resumen)


def leer_resultado_validacion(path_output):
    """Busca la linea 'RESULTADO GLOBAL: CONFORME/NO CONFORME' dentro
    del archivo de output de una validacion (NETCONF o RESTCONF)."""
    if not os.path.isfile(path_output):
        return False, "Archivo de validacion no encontrado."

    with open(path_output, "r") as f:
        contenido = f.read()

    if "RESULTADO GLOBAL: CONFORME" in contenido:
        return True, "CONFORME"
    elif "RESULTADO GLOBAL: NO CONFORME" in contenido:
        return False, "NO CONFORME"
    else:
        return False, "Resultado no encontrado en el archivo."


def main():
    print("=" * 60)
    print("Script         : generar_certificado.py")
    print(f"Fecha/Hora     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    # ----- 1. Leer diff de Genie -----
    diff_ok, diff_detalle = leer_diff(DIFF_DIR)
    print(f"[{'OK' if diff_ok else 'FAIL'}] Diff de Genie ({DIFF_DIR})")
    print(diff_detalle)
    print()

    # ----- 2. Leer resultado NETCONF -----
    netconf_ok, netconf_resultado = leer_resultado_validacion(NETCONF_OUTPUT)
    print(f"[{'OK' if netconf_ok else 'FAIL'}] Validacion NETCONF: {netconf_resultado}")

    # ----- 3. Leer resultado RESTCONF -----
    restconf_ok, restconf_resultado = leer_resultado_validacion(RESTCONF_OUTPUT)
    print(f"[{'OK' if restconf_ok else 'FAIL'}] Validacion RESTCONF: {restconf_resultado}")
    print()

    # ----- 4. Determinar resultado global -----
    resultado_global = "CONFORME" if (diff_ok and netconf_ok and restconf_ok) else "NO CONFORME"

    # ----- 5. Generar el certificado -----
    lineas = []
    lineas.append("=" * 60)
    lineas.append("CERTIFICADO DE COMPLIANCE")
    lineas.append("=" * 60)
    lineas.append(f"Proyecto      : EP3 - Automatizacion de Red con Compliance Auditado")
    lineas.append(f"Asignatura    : DRY7122 - Programacion y Redes Virtualizadas (SDN-NFV)")
    lineas.append(f"Alumno        : {NOMBRE}")
    lineas.append(f"Codigo alumno : {CODIGO}")
    lineas.append(f"Cliente       : {CLIENTE}")
    lineas.append(f"Hostname      : {HOSTNAME_CORPORATIVO}")
    lineas.append(f"Generado el   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lineas.append("=" * 60)
    lineas.append("")
    lineas.append("Fuentes de verificacion analizadas:")
    lineas.append(f"  1. Diff de Genie (baseline vs estado final)  : {'OK' if diff_ok else 'FAIL'}")
    lineas.append(f"  2. Validacion NETCONF (Fase 3)                : {netconf_resultado}")
    lineas.append(f"  3. Validacion RESTCONF (Fase 4)               : {restconf_resultado}")
    lineas.append("")
    lineas.append("-" * 60)
    lineas.append(f"RESULTADO FINAL DE LA AUDITORIA: {resultado_global}")
    lineas.append("-" * 60)

    contenido_certificado = "\n".join(lineas) + "\n"

    with open(SALIDA, "w") as f:
        f.write(contenido_certificado)

    print(contenido_certificado)
    print(f"Certificado guardado en: {SALIDA}")

    sys.exit(0 if resultado_global == "CONFORME" else 1)


if __name__ == "__main__":
    main()
