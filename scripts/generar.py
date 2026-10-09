#!/usr/bin/env python3
"""Genera un dataset sintetico de telemetria TI para 3 PyMEs (tenants).

Por tenant escribe en data/<tenant>/:
  - contexto.md : giro, empleados, horario, sistemas criticos
  - metricas.csv: 120 filas (1 por minuto): cpu, ram, disco, latencia_ms, errores
  - logs.md     : ~20 lineas por fuente (servidor, firewall, app) con incidentes
                  que se anticipan en las metricas

Semilla fija: ejecutar de nuevo produce exactamente los mismos archivos.
Uso: python3 scripts/generar.py
"""
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

SEMILLA = 42
MINUTOS = 120
LINEAS_LOG_POR_FUENTE = 20
FECHA = "2026-10-08"
RAIZ = Path(__file__).resolve().parent.parent

TENANTS = {
    "gracko": {
        "inicio": "08:00",
        "base": {"cpu": 26.0, "ram": 54.0, "disco": 58.0, "latencia": 40.0, "errores": 0.3},
        "ruido": {"cpu": 2.5, "ram": 1.2, "disco": 0.15, "latencia": 5.0},
        # Disco de /data crece sin parar: el respaldo termina fallando.
        "incidentes": [
            {"nombre": "disco_lleno", "inicio": 58, "pico": 97, "reinicio": None,
             "delta": {"disco": 39.0, "latencia": 25.0, "errores": 3.0}},
        ],
        "eventos": [
            (60, "servidor", "INFO", "crecimiento inusual de /data: +1.8 GB en la ultima hora"),
            (80, "servidor", "WARN", "disco /data al {disco:.0f}% (umbral 80%)"),
            (92, "servidor", "WARN", "disco /data al {disco:.0f}% (umbral 90%)"),
            (97, "servidor", "ERROR", "job respaldo-nocturno abortado: no space left on device"),
            (97, "app", "ERROR", "exportacion de cierre mensual fallida: escritura en /data sin espacio"),
        ],
        "contexto": """# Contexto — gracko

- **Giro:** despacho contable y fiscal (nomina, declaraciones y cierres mensuales de clientes).
- **Empleados:** 12, en una sola oficina.
- **Horario:** lunes a viernes 08:00–18:00; sabados 09:00–13:00.

## Sistemas criticos

| Sistema | Descripcion | Ventana critica |
|---|---|---|
| fs-01 (Windows Server 2019) | Servidor de archivos; volumen `/data` con expedientes de clientes | Todo el horario |
| ERP contable (web) | Captura de polizas, nomina y cierres; corre en fs-01 | Cierre mensual (dias 1-5) |
| fw-01 (firewall perimetral) | Acceso a internet, VPN para socio y contador externo | Todo el horario |
| Respaldo nocturno | Copia de /data a NAS, 23:00 | Diario |

## Notas
- Telemetria: CPU, RAM, disco de /data, latencia del ERP y errores por minuto.
- Riesgo conocido: /data sin alerta de capacidad desde hace 3 meses.
""",
    },
    "gramo": {
        "inicio": "07:00",
        "base": {"cpu": 31.0, "ram": 55.0, "disco": 47.0, "latencia": 60.0, "errores": 0.5},
        "ruido": {"cpu": 2.8, "ram": 1.0, "disco": 0.1, "latencia": 6.0},
        # Dos incidentes: fuga de memoria en el worker de pedidos y flood al firewall.
        "incidentes": [
            {"nombre": "fuga_memoria", "inicio": 30, "pico": 52, "reinicio": 54,
             "delta": {"cpu": 8.0, "ram": 40.0, "latencia": 180.0, "errores": 12.0}},
            {"nombre": "flood_firewall", "inicio": 100, "pico": 104, "reinicio": 112,
             "delta": {"cpu": 22.0, "latencia": 90.0, "errores": 4.0}},
        ],
        "eventos": [
            (47, "servidor", "WARN", "memoria RAM al {ram:.0f}% (umbral 85%) en app-01"),
            (52, "app", "ERROR", "OutOfMemoryError en pedidos-worker (pid 4117); 3 pedidos abortados"),
            (53, "app", "ERROR", "API /pedidos responde en {latencia:.0f} ms; 504 en 9 peticiones"),
            (54, "servidor", "INFO", "supervisor reinicio el servicio pedidos-worker"),
            (99, "firewall", "WARN", "480 conn/s desde 198.51.100.23 hacia 443/tcp (posible SYN flood)"),
            (104, "firewall", "INFO", "rate-limit aplicado a 198.51.100.0/24"),
            (112, "firewall", "INFO", "rate-limit retirado tras 8 min sin trafico anomalo"),
        ],
        "contexto": """# Contexto — gramo

- **Giro:** distribuidora de alimentos a restaurantes y comercios (pedidos, inventario, reparto).
- **Empleados:** 25 (oficina, almacen y reparto).
- **Horario:** lunes a sabado 07:00–16:00; pedidos en linea 24/7.

## Sistemas criticos

| Sistema | Descripcion | Ventana critica |
|---|---|---|
| app-01 (VM Linux, Ubuntu 22.04) | API de pedidos y proceso worker `pedidos-worker` | 07:00–16:00 |
| Servidor de inventario | Base de datos de existencias y lotes (caducidad) | Todo el horario |
| fw-01 (firewall perimetral) | Publicacion de la API y acceso de clientes por HTTPS | 24/7 |
| Portal de clientes | Pedidos en linea, consume la API de app-01 | 24/7 |

## Notas
- Telemetria: CPU, RAM, disco y latencia de app-01, y errores por minuto.
- Pico de pedidos a las 07:30 y a las 13:00 (reposicion de restaurantes).
""",
    },
    "ttr": {
        "inicio": "06:00",
        "base": {"cpu": 34.0, "ram": 61.0, "disco": 39.0, "latencia": 85.0, "errores": 0.4},
        "ruido": {"cpu": 2.2, "ram": 1.1, "disco": 0.1, "latencia": 8.0},
        # Saturacion del optimizador de rutas al cargar la planeacion de la manana.
        "incidentes": [
            {"nombre": "saturacion_optimizador", "inicio": 70, "pico": 86, "reinicio": 100,
             "delta": {"cpu": 58.0, "ram": 12.0, "latencia": 150.0, "errores": 7.0}},
        ],
        "eventos": [
            (76, "servidor", "WARN", "cpu del optimizador de rutas al {cpu:.0f}% y en aumento"),
            (84, "app", "WARN", "cola de calculo de rutas con 210 tareas pendientes"),
            (88, "app", "ERROR", "timeout consultando rutas (>5 s) para 14 unidades"),
            (100, "app", "INFO", "proceso optimizador de rutas reiniciado por operador"),
        ],
        "contexto": """# Contexto — ttr

- **Giro:** transportes y logistica de ultima milla (rutas, rastreo de unidades, entregas).
- **Empleados:** 40 (choferes, despacho y oficina).
- **Horario:** lunes a sabado 06:00–20:00; planeacion de rutas de 06:00 a 08:00.

## Sistemas criticos

| Sistema | Descripcion | Ventana critica |
|---|---|---|
| TMS / optimizador de rutas (srv-tms-01) | Calcula rutas diarias por unidad | 06:00–08:00 |
| Servidor de rastreo GPS | Recibe posiciones de 32 unidades cada 30 s | 06:00–20:00 |
| fw-01 (firewall) + VPN | Acceso de choferes a la app movil y al TMS | 06:00–20:00 |
| App movil de choferes | Recibe ruta, firma entregas y reporta incidencias | 06:00–20:00 |

## Notas
- Telemetria: CPU, RAM, disco y latencia de srv-tms-01, y errores por minuto.
- El optimizador comparte servidor con el rastreo GPS.
""",
    },
}


def efecto(cfg, minuto, metrica):
    """Suma el efecto de los incidentes activos sobre una metrica en un minuto."""
    total = 0.0
    for inc in cfg["incidentes"]:
        if minuto < inc["inicio"]:
            continue
        if inc["reinicio"] is not None and minuto >= inc["reinicio"]:
            continue
        frac = min(1.0, (minuto - inc["inicio"]) / (inc["pico"] - inc["inicio"]))
        total += inc["delta"].get(metrica, 0.0) * frac
    return total


def poisson(rng, lam):
    """Muestrea una Poisson(lam) con el generador del tenant (sin numpy)."""
    limite = math.exp(-lam)
    k, p = 0, 1.0
    while True:
        p *= rng.random()
        if p <= limite:
            return k
        k += 1


def generar_metricas(rng, cfg, inicio):
    filas = []
    for m in range(MINUTOS):
        def valor(k, lo, hi):
            v = cfg["base"][k] + rng.gauss(0, cfg["ruido"][k]) + efecto(cfg, m, k)
            return min(max(v, lo), hi)

        filas.append({
            "timestamp": (inicio + timedelta(minutes=m)).strftime("%Y-%m-%dT%H:%M:%S"),
            "cpu": valor("cpu", 0, 100),
            "ram": valor("ram", 0, 100),
            "disco": valor("disco", 0, 100),
            "latencia": valor("latencia", 1, 10000),
            "errores": poisson(rng, cfg["base"]["errores"] + efecto(cfg, m, "errores")),
        })
    return filas


PLANTILLAS = {
    "servidor": [
        ("INFO", "rotacion de logs completada ({n} archivos)"),
        ("INFO", "sesion abierta por admin desde 10.0.0.{ip}"),
        ("DEBUG", "ntp: offset {off} s respecto a time.google.com"),
        ("INFO", "snapshot programado completado en {ms} ms"),
    ],
    "firewall": [
        ("INFO", "permitido 10.0.1.{ip} -> 8.8.8.8:53/udp"),
        ("INFO", "bloqueado 185.220.101.{ip} -> 22/tcp (intento SSH)"),
        ("INFO", "VPN: usuario vpn{ip} conectado desde 189.201.12.{ip}"),
        ("INFO", "sesion TLS establecida 10.0.2.{ip} -> 443/tcp"),
    ],
    "app": [
        ("INFO", "GET /api/v1/clientes 200 en {ms} ms"),
        ("INFO", "login correcto del usuario u{ip}"),
        ("INFO", "lote completado: {n} registros procesados"),
        ("DEBUG", "cache hit ratio {pct}%"),
    ],
}


def generar_logs(rng, cfg, filas, inicio):
    """Devuelve {fuente: [(timestamp, nivel, mensaje), ...]} con ~20 lineas por fuente."""
    por_fuente = {f: [] for f in PLANTILLAS}

    for minuto, fuente, nivel, plantilla in cfg["eventos"]:
        ts = inicio + timedelta(minutes=minuto, seconds=rng.randint(0, 59))
        msg = plantilla.format(**filas[minuto])
        por_fuente[fuente].append((ts, nivel, msg))

    for fuente, eventos in por_fuente.items():
        relleno = LINEAS_LOG_POR_FUENTE - len(eventos)
        for _ in range(relleno):
            minuto = rng.randrange(MINUTOS)
            ts = inicio + timedelta(minutes=minuto, seconds=rng.randint(0, 59))
            nivel, plantilla = rng.choice(PLANTILLAS[fuente])
            msg = plantilla.format(
                n=rng.randint(10, 900), ip=rng.randint(2, 250), off=f"{rng.uniform(-0.01, 0.01):.4f}",
                ms=rng.randint(12, 480), pct=rng.randint(85, 99),
            )
            eventos.append((ts, nivel, msg))
        eventos.sort(key=lambda e: e[0])
    return por_fuente


def escribir_metricas(ruta, filas):
    with ruta.open("w", encoding="utf-8") as f:
        f.write("timestamp,cpu,ram,disco,latencia_ms,errores\n")
        for r in filas:
            f.write(f"{r['timestamp']},{r['cpu']:.1f},{r['ram']:.1f},{r['disco']:.1f},"
                    f"{r['latencia']:.0f},{r['errores']}\n")


def escribir_logs(ruta, nombre, inicio, fin, por_fuente):
    partes = [
        f"# Logs — {nombre}\n",
        f"Ventana: {FECHA} {inicio:%H:%M}–{fin:%H:%M} (sintetico). "
        "Formato: `timestamp nivel mensaje`.\n",
    ]
    for fuente in ("servidor", "firewall", "app"):
        lineas = "\n".join(
            f"{ts:%Y-%m-%dT%H:%M:%S} {nivel} {msg}" for ts, nivel, msg in por_fuente[fuente]
        )
        partes.append(f"## {fuente}\n\n```text\n{lineas}\n```\n")
    ruta.write_text("\n".join(partes), encoding="utf-8")


def main():
    for indice, (nombre, cfg) in enumerate(TENANTS.items()):
        rng = random.Random(f"{SEMILLA}-{nombre}")
        inicio = datetime.strptime(f"{FECHA} {cfg['inicio']}", "%Y-%m-%d %H:%M")
        fin = inicio + timedelta(minutes=MINUTOS)

        carpeta = RAIZ / "data" / nombre
        carpeta.mkdir(parents=True, exist_ok=True)

        filas = generar_metricas(rng, cfg, inicio)
        por_fuente = generar_logs(rng, cfg, filas, inicio)

        (carpeta / "contexto.md").write_text(cfg["contexto"], encoding="utf-8")
        escribir_metricas(carpeta / "metricas.csv", filas)
        escribir_logs(carpeta / "logs.md", nombre, inicio, fin, por_fuente)
        print(f"{nombre}: {len(filas)} filas de metricas, "
              f"{sum(len(v) for v in por_fuente.values())} lineas de log -> {carpeta}")


if __name__ == "__main__":
    main()
