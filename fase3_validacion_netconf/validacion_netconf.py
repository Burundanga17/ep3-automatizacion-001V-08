#!/usr/bin/env python3
"""
fase3_validacion_netconf/validacion_netconf.py

Valida, de forma independiente a Ansible, que la configuracion corporativa
fue aplicada correctamente en el router CSR1kv usando NETCONF (puerto 830).
Solo lectura - no modifica nada en el dispositivo.
"""

import sys
import socket
from datetime import datetime

import yaml
from ncclient import manager
from ncclient.xml_ import to_ele

# ---------------------------------------------------------------------------
# Metadatos de ejecucion
# ---------------------------------------------------------------------------
print("=" * 60)
print("Script         : validacion_netconf.py")
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

# ---------------------------------------------------------------------------
# Filtro XML para el modelo Cisco-IOS-XE-native
# ---------------------------------------------------------------------------
FILTRO = """
<filter>
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <hostname/>
    <interface>
      <Loopback/>
      <GigabitEthernet/>
    </interface>
    <ntp/>
  </native>
</filter>
"""

# ---------------------------------------------------------------------------
# Conexion NETCONF
# ---------------------------------------------------------------------------
print(f"Conectando a {router_ip} via NETCONF (puerto 830)...")

try:
    with manager.connect(
        host=router_ip,
        port=830,
        username=router_user,
        password=router_pass,
        hostkey_verify=False,
        allow_agent=False,
        look_for_keys=False,
        device_params={"name": "iosxe"},
        timeout=30,
    ) as m:
        print("Conexion NETCONF establecida correctamente.")
        print()

        respuesta = m.get_config(source="running", filter=FILTRO)

        # Guardar el XML crudo de la respuesta (incluye message-id urn:uuid:...)
        with open("evidencias/rpc_reply_raw.xml", "w") as f:
            f.write(respuesta.xml)
        print("XML crudo guardado en evidencias/rpc_reply_raw.xml")
        print()

        root = to_ele(respuesta.xml)

        ns = {
            "nc": "urn:ietf:params:xml:ns:netconf:base:1.0",
            "native": "http://cisco.com/ns/yang/Cisco-IOS-XE-native",
            "ntp": "http://cisco.com/ns/yang/Cisco-IOS-XE-ntp",
        }

        def buscar_texto(xpath):
            el = root.find(xpath, ns)
            return el.text.strip() if el is not None and el.text else None

        hostname_actual = buscar_texto(".//native:native/native:hostname")

        loopback_ip_actual = None
        loopback_mask_actual = None
        for lb in root.findall(".//native:native/native:interface/native:Loopback", ns):
            num_el = lb.find("native:name", ns)
            if num_el is not None and num_el.text == str(loopback_id):
                addr = lb.find("native:ip/native:address/native:primary", ns)
                if addr is not None:
                    ip_el = addr.find("native:address", ns)
                    mask_el = addr.find("native:mask", ns)
                    loopback_ip_actual = ip_el.text if ip_el is not None else None
                    loopback_mask_actual = mask_el.text if mask_el is not None else None

        descripcion_wan_actual = None
        for gi in root.findall(".//native:native/native:interface/native:GigabitEthernet", ns):
            num_el = gi.find("native:name", ns)
            if num_el is not None and num_el.text == "1":
                desc_el = gi.find("native:description", ns)
                descripcion_wan_actual = desc_el.text if desc_el is not None else None

        ntp_server_actual = None
        for srv in root.findall(".//native:native/native:ntp/ntp:server/ntp:server-list", ns):
            ip_el = srv.find("ntp:ip-address", ns)
            if ip_el is not None:
                ntp_server_actual = ip_el.text
                break

except Exception as e:
    print(f"[ERROR] No fue posible completar la validacion NETCONF: {e}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Comparacion contra valores esperados
# ---------------------------------------------------------------------------
print("Resultado de validacion NETCONF")
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
