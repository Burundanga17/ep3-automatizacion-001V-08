#!/usr/bin/env python3
"""
fase4_validacion_restconf/validacion_restconf.py

Valida, de forma independiente a Ansible y a NETCONF, que la configuracion
corporativa fue aplicada correctamente en el router CSR1kv usando RESTCONF
(HTTPS, formato JSON). Solo lectura - no modifica nada en el dispositivo.
"""

import sys
import json
import socket
from datetime import datetime

import yaml
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------------------------
# Metadatos de ejecucion
# ---------------------------------------------------------------------------
print("=" * 60)
print("Script         : validacion_restconf.py")
print(f"Fecha/Hora     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Hostname VM    : {socket.gethostname()}")
print("=" * 60)
print()

# ---------------------------------------------------------------------------
# Cargar variables esperadas desde vars_001V-08.yaml
# ---------------------------------------------------------------------------
VARS_PATH = "../vars/vars_001V-08.yaml"

with open(VARS_PATH, "r") as f:
    cfg = yaml.safe_load(f)

esperado = {
    "hostname": cfg["cliente"]["hostname"],
    "loopback_ip": cfg["router"]["loopback_ip"],
    "loopback_mask": cfg["router"]["loopback_mask"],
    "descripcion_wan": cfg["router"]["descripcion_wan"],
    "ntp_server": cfg["router"]["ntp_server"],
}

router_ip = cfg["router"]["ip"]
router_user = cfg["router"]["usuario"]
router_pass = cfg["router"]["password"]
loopback_id = cfg["router"]["loopback_id"]

BASE_URL = f"https://{router_ip}/restconf/data/Cisco-IOS-XE-native:native"
HEADERS = {"Accept": "application/yang-data+json"}
AUTH = (router_user, router_pass)

print(f"Conectando a {router_ip} via RESTCONF (HTTPS)...")

try:
    resp = requests.get(
        BASE_URL,
        auth=AUTH,
        headers=HEADERS,
        verify=False,
        timeout=30,
    )
    resp.raise_for_status()
    print(f"Conexion RESTCONF establecida correctamente (HTTP {resp.status_code}).")
    print()

    data = resp.json()

    # Guardar la respuesta JSON cruda
    with open("evidencias/responses/restconf_response_raw.json", "w") as f:
        json.dump(data, f, indent=2)
    print("JSON crudo guardado en evidencias/responses/restconf_response_raw.json")
    print()

    native = data.get("Cisco-IOS-XE-native:native", {})

    # ----- Hostname -----
    hostname_actual = native.get("hostname")

    # ----- Loopback -----
    loopback_ip_actual = None
    loopback_mask_actual = None
    loopbacks = native.get("interface", {}).get("Loopback", [])
    for lb in loopbacks:
        if str(lb.get("name")) == str(loopback_id):
            primary = lb.get("ip", {}).get("address", {}).get("primary", {})
            loopback_ip_actual = primary.get("address")
            loopback_mask_actual = primary.get("mask")
            break

    # ----- Descripcion WAN (GigabitEthernet1) -----
    descripcion_wan_actual = None
    gigs = native.get("interface", {}).get("GigabitEthernet", [])
    for gi in gigs:
        if str(gi.get("name")) == "1":
            descripcion_wan_actual = gi.get("description")
            break

    # ----- NTP -----
    ntp_server_actual = None
    ntp_block = native.get("ntp", {})
    servers = ntp_block.get("Cisco-IOS-XE-ntp:server", {}).get("server-list", [])
    if servers:
        ntp_server_actual = servers[0].get("ip-address")

except Exception as e:
    print(f"[ERROR] No fue posible completar la validacion RESTCONF: {e}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Comparacion contra valores esperados
# ---------------------------------------------------------------------------
print("Resultado de validacion RESTCONF")
print("-" * 60)

criterios = [
    ("Hostname", esperado["hostname"], hostname_actual),
    ("IP Loopback", esperado["loopback_ip"], loopback_ip_actual),
    ("Mascara Loopback", esperado["loopback_mask"], loopback_mask_actual),
    ("Descripcion WAN", esperado["descripcion_wan"], descripcion_wan_actual),
    ("Servidor NTP", esperado["ntp_server"], ntp_server_actual),
]

ok_count = 0
for nombre, esp, act in criterios:
    estado = "[OK]" if esp == act else "[FAIL]"
    if esp == act:
        ok_count += 1
    print(f"{estado:7} {nombre:20} esperado='{esp}'  obtenido='{act}'")

print("-" * 60)
print(f"Criterios conformes: {ok_count}/{len(criterios)}")

if ok_count == len(criterios):
    print()
    print("RESULTADO GLOBAL: CONFORME")
    sys.exit(0)
else:
    print()
    print("RESULTADO GLOBAL: NO CONFORME")
    sys.exit(1)
