#!/usr/bin/env python3
"""Genera un dataset sintetico de telemetria TI para 4 PyMEs (tenants).

Por tenant escribe en <salida>/<tenant>/:
  - contexto.md : giro, empleados, horario, sistemas criticos, eventos de negocio
  - metricas.csv: 9200 filas (1 por minuto): cpu, ram, disco, latencia_ms, errores.
                  Algunas celdas vacias (faltantes) y apagones cortos del agente.
  - logs.md     : ~400 lineas por fuente (servidor, firewall, app). Las pistas de
                  incidentes son escasas y hay senuelos con ERROR/WARN enganosos.

Por tenant escribe la respuesta oculta en <salida>/_solucion/<tenant>/etiquetas.csv
  - inicio_incidente,tipo,es_real : inicio_incidente es el minuto del impacto para
    incidentes reales y el minuto de inicio para senuelos (es_real = false).

Modelo: ruido AR(1), estacionalidad diaria y semanal, incidentes con precursores
graduales (lineal, exponencial, escalon, intermitente) y retrasos por metrica,
senuelos (pulsos benignos) y eventos recurrentes (respaldos).

Semilla fija: ejecutar de nuevo produce exactamente los mismos archivos.
Uso: python3 scripts/generar.py [semilla] [carpeta_salida]
     (por defecto: semilla 42, carpeta data/)
"""
import math
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

SEMILLA = int(sys.argv[1]) if len(sys.argv) > 1 else 42
MINUTOS = 9200
LINEAS_LOG_POR_FUENTE = 400
FORMATO_FECHA = "%Y-%m-%d %H:%M"
METRICAS = ("cpu", "ram", "disco", "latencia", "errores")
LIMITES = {"cpu": (0, 100), "ram": (0, 100), "disco": (0, 100), "latencia": (1, 10000)}
PROB_CELDA_FALTANTE = 0.006   # celda vacia por metrica y minuto
PROB_APAGON = 1 / 2500        # inicio de un apagon del agente (3 a 25 min sin datos)
RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / (sys.argv[2] if len(sys.argv) > 2 else "data")


def t(texto):
    return datetime.strptime(texto, FORMATO_FECHA)


def minuto(inicio, texto):
    """Minuto (entero) de una fecha 'AAAA-MM-DD HH:MM' dentro de la serie."""
    return int((t(texto) - inicio).total_seconds() // 60)


TENANTS = {
    "gracko": {
        "inicio": "2026-10-08 08:00",
        "base": {"cpu": 26.0, "ram": 54.0, "disco": 58.0, "latencia": 40.0, "errores": 0.3},
        "ruido": {"cpu": 3.0, "ram": 1.6, "disco": 0.25, "latencia": 7.0},
        "estacional": {"cpu": 5.0, "ram": 2.0, "disco": 0.2, "latencia": 10.0, "errores": 0.3},
        # Lun-vie 08-18, sabado medio dia, domingo cerrado.
        "perfil": {"picos": [(11.0, 2.5, 0.42), (15.0, 2.5, 0.42)],
                   "dias": [1, 1, 1, 1, 1, 0.55, 0.05]},
        "incidentes": [
            # Deriva lenta de /data: crecimiento exponencial desde el viernes; el respaldo aborta.
            {"tipo": "deriva_disco", "forma": "exponencial",
             "inicio": "2026-10-09 06:00", "impacto": "2026-10-11 23:00", "fin": "2026-10-12 00:30",
             "delta": {"disco": 39.0, "latencia": 14.0, "errores": 0.6},
             "retraso": {"latencia": 600, "errores": 900},
             "logs": [
                 ("2026-10-09 07:12", "servidor", "INFO", "archivo nuevo en /data/tmp/exportaciones: 1.2 GB"),
                 ("2026-10-10 04:30", "servidor", "DEBUG", "volumen /data: {disco:.0f}% usado"),
                 ("2026-10-10 13:05", "app", "INFO", "exportacion masiva de expedientes en /data/tmp (en curso)"),
                 ("2026-10-11 09:02", "servidor", "WARN", "disco /data al {disco:.0f}% (umbral 80%)"),
                 ("2026-10-11 23:00", "servidor", "ERROR", "job respaldo-nocturno abortado: no space left on device"),
                 ("2026-10-11 23:01", "app", "ERROR", "exportacion de cierre mensual fallida: escritura en /data sin espacio"),
                 ("2026-10-12 00:30", "servidor", "INFO", "limpieza manual de /data liberó 31 GB"),
             ]},
            # ERP lento y con cpu en rafagas que crecen; la captura de polizas agota el tiempo de espera.
            {"tipo": "cpu_intermitente_erp", "forma": "intermitente",
             "inicio": "2026-10-13 19:00", "impacto": "2026-10-14 09:20", "fin": "2026-10-14 10:05",
             "delta": {"cpu": 24.0, "latencia": 110.0, "errores": 2.2},
             "retraso": {"latencia": 60, "errores": 240},
             "logs": [
                 ("2026-10-13 22:14", "app", "DEBUG", "consulta de polizas tardo {latencia:.0f} ms"),
                 ("2026-10-14 05:30", "app", "WARN", "ERP: consultas de polizas por encima de 3 s en la ultima hora"),
                 ("2026-10-14 09:20", "app", "ERROR", "ERP: timeout al capturar poliza (>30 s), sesion cerrada"),
                 ("2026-10-14 09:21", "servidor", "WARN", "cpu de fs-01 al {cpu:.0f}% sostenido"),
                 ("2026-10-14 10:05", "servidor", "INFO", "servicio del ERP reiniciado por operador"),
             ]},
            # Intentos de acceso a la VPN con cuentas del ERP: pocas pistas, aviso corto.
            {"tipo": "acceso_masivo_vpn", "forma": "lineal",
             "inicio": "2026-10-12 21:00", "impacto": "2026-10-13 00:30", "fin": "2026-10-13 02:00",
             "delta": {"errores": 1.2, "cpu": 3.0},
             "logs": [
                 ("2026-10-12 21:40", "firewall", "INFO", "VPN: usuario vpn17 fallo la autenticacion"),
                 ("2026-10-12 23:58", "firewall", "INFO", "VPN: 9 intentos fallidos en 10 min (usuario contador)"),
                 ("2026-10-13 00:31", "app", "ERROR", "ERP: 37 cuentas bloqueadas por intentos fallidos de acceso"),
                 ("2026-10-13 00:33", "firewall", "WARN", "VPN: 212 intentos fallidos desde 203.0.113.0/24"),
                 ("2026-10-13 02:00", "firewall", "INFO", "VPN: 203.0.113.0/24 bloqueada manualmente"),
             ]},
        ],
        "senuelos": [
            # Carga masiva de declaraciones: sube el disco y se limpia al terminar.
            {"tipo": "carga_masiva_declaraciones", "inicio": "2026-10-09 17:00",
             "fin": "2026-10-09 19:30", "rampa": 10,
             "delta": {"disco": 7.0, "cpu": 6.0},
             "logs": [
                 ("2026-10-09 17:05", "servidor", "INFO", "carga masiva de declaraciones en /data/declaraciones (3.1 GB)"),
                 ("2026-10-09 18:10", "servidor", "WARN", "disco /data al {disco:.0f}% (crecimiento de 9 GB desde las 17:00)"),
                 ("2026-10-09 19:35", "servidor", "INFO", "limpieza de temporales liberó 9.8 GB"),
             ]},
            # Cierre de nomina quincenal: carga alta y errores de timeout que se resuelven solos.
            {"tipo": "cierre_nomina", "inicio": "2026-10-12 10:00",
             "fin": "2026-10-12 14:00", "rampa": 15,
             "delta": {"cpu": 18.0, "latencia": 90.0, "errores": 2.0},
             "logs": [
                 ("2026-10-12 10:00", "app", "INFO", "cierre de nomina quincenal iniciado: 12 empresas"),
                 ("2026-10-12 11:15", "app", "WARN", "ERP: respuesta lenta en captura de nomina"),
                 ("2026-10-12 12:20", "app", "ERROR", "ERP: 2 polizas rechazadas por timeout durante el cierre de nomina"),
                 ("2026-10-12 14:05", "servidor", "INFO", "cierre de nomina finalizado; carga normal"),
             ]},
        ],
        "recurrentes": [
            # Respaldo nocturno a NAS; a veces reintenta y termina bien.
            {"tipo": "respaldo_nocturno", "hora": "23:00", "duracion": 40,
             "delta": {"cpu": 14.0, "latencia": 25.0}, "rampa": 5, "p_falso": 0.35,
             "log_falso": ("servidor", "WARN", "respaldo-nocturno: timeout de NAS en intento 1/3"),
             "log_ok": ("servidor", "INFO", "respaldo-nocturno completado (reintento 2/3)")},
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

## Eventos de negocio

- **Viernes 9 de octubre:** carga masiva de declaraciones del cliente de mayor volumen (17:00–19:30).
- **Lunes 12 de octubre:** cierre de nomina quincenal, 10:00–14:00 (carga alta en el ERP).

## Notas
- Telemetria: CPU, RAM, disco de /data, latencia del ERP y errores por minuto.
- Riesgo conocido: /data sin alerta de capacidad desde hace 3 meses.
""",
    },
    "gramo": {
        "inicio": "2026-10-08 07:00",
        "base": {"cpu": 31.0, "ram": 55.0, "disco": 47.0, "latencia": 60.0, "errores": 0.5},
        "ruido": {"cpu": 3.4, "ram": 1.8, "disco": 0.2, "latencia": 9.0},
        "estacional": {"cpu": 6.0, "ram": 2.5, "disco": 0.3, "latencia": 14.0, "errores": 0.4},
        # Picos de pedidos 07:30 y 13:00; portal 24/7 con actividad nocturna baja.
        "perfil": {"picos": [(7.5, 0.7, 0.45), (13.0, 0.7, 0.45), (19.0, 2.5, 0.25)],
                   "dias": [1, 1, 1, 1, 1, 0.9, 0.7]},
        "incidentes": [
            # Fuga de memoria en el worker: crece de noche y muere al abrir el pico de pedidos.
            {"tipo": "fuga_memoria_worker", "forma": "exponencial",
             "inicio": "2026-10-12 19:00", "impacto": "2026-10-13 07:35", "fin": "2026-10-13 07:45",
             "delta": {"ram": 36.0, "latencia": 40.0, "errores": 3.0},
             "retraso": {"latencia": 240, "errores": 300},
             "logs": [
                 ("2026-10-12 23:14", "app", "DEBUG", "pedidos-worker: heap al {ram:.0f}% tras lote nocturno"),
                 ("2026-10-13 03:50", "app", "INFO", "pedidos-worker: pausa de GC de 1.9 s (lote de sincronizacion)"),
                 ("2026-10-13 06:20", "servidor", "WARN", "app-01: memoria RAM con tendencia ascendente desde la madrugada"),
                 ("2026-10-13 07:35", "app", "ERROR", "OutOfMemoryError en pedidos-worker (pid 4117); 3 pedidos abortados"),
                 ("2026-10-13 07:36", "app", "ERROR", "API /pedidos responde en {latencia:.0f} ms; 504 en 9 peticiones"),
                 ("2026-10-13 07:45", "servidor", "INFO", "supervisor reinicio el servicio pedidos-worker"),
             ]},
            # Trafico hostil de baja intensidad hacia 443: la latencia sube media jornada antes.
            {"tipo": "trafico_hostil_lento", "forma": "lineal",
             "inicio": "2026-10-09 06:30", "impacto": "2026-10-09 13:05", "fin": "2026-10-09 14:10",
             "delta": {"latencia": 85.0, "cpu": 7.0, "errores": 2.5},
             "retraso": {"errores": 150},
             "logs": [
                 ("2026-10-09 07:52", "firewall", "INFO", "conexiones 443/tcp por encima de lo habitual desde 198.51.100.0/24 (sin bloqueo)"),
                 ("2026-10-09 13:05", "firewall", "WARN", "480 conn/s desde 198.51.100.23 hacia 443/tcp (posible SYN flood)"),
                 ("2026-10-09 13:40", "firewall", "INFO", "rate-limit aplicado a 198.51.100.0/24"),
                 ("2026-10-09 14:10", "firewall", "INFO", "rate-limit retirado: trafico normal desde las 13:40"),
             ]},
            # Pool de conexiones a inventario que se agota en escalones.
            {"tipo": "agotamiento_pool_inventario", "forma": "escalon",
             "inicio": "2026-10-14 05:20", "impacto": "2026-10-14 07:20", "fin": "2026-10-14 09:10",
             "delta": {"latencia": 160.0, "errores": 5.0, "cpu": 4.0},
             "logs": [
                 ("2026-10-14 06:10", "app", "WARN", "pool de conexiones a inventario al 85%"),
                 ("2026-10-14 07:21", "app", "ERROR", "API /pedidos 504: timeout consultando inventario (>10 s)"),
                 ("2026-10-14 09:10", "app", "INFO", "pool de inventario reconfigurado por operador"),
             ]},
        ],
        "senuelos": [
            # Promocion 2x1 para restaurantes: pico real de trafico que se ve como alarma.
            {"tipo": "promo_2x1", "inicio": "2026-10-09 10:00", "fin": "2026-10-09 12:00", "rampa": 10,
             "delta": {"latencia": 130.0, "cpu": 16.0, "errores": 4.0, "ram": 4.0},
             "logs": [
                 ("2026-10-09 09:55", "app", "INFO", "promocion 2x1 en restaurantes activa"),
                 ("2026-10-09 10:32", "app", "ERROR", "API /pedidos responde en {latencia:.0f} ms; 504 en 4 peticiones (pico de promocion)"),
                 ("2026-10-09 12:10", "app", "INFO", "promocion 2x1 finalizada; pedidos del periodo: 412"),
             ]},
            # Snapshot semanal de inventario del sabado: tarda mas de lo normal.
            {"tipo": "snapshot_inventario", "inicio": "2026-10-10 03:00", "fin": "2026-10-10 04:30", "rampa": 5,
             "delta": {"cpu": 22.0, "disco": 2.0, "latencia": 15.0},
             "logs": [
                 ("2026-10-10 03:00", "servidor", "INFO", "snapshot semanal de inventario iniciado"),
                 ("2026-10-10 04:40", "servidor", "WARN", "snapshot de inventario tardo 100 min (umbral 60 min)"),
             ]},
        ],
        "recurrentes": [
            # Reporte de rutas de reparto de madrugada.
            {"tipo": "reporte_rutas_nocturno", "hora": "02:00", "duracion": 20,
             "delta": {"cpu": 10.0, "ram": 6.0}, "rampa": 3, "p_falso": 0.0},
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

## Eventos de negocio

- **Viernes 9 de octubre, 10:00–12:00:** promocion 2x1 para restaurantes (se espera mas trafico de lo normal).
- **Sabados:** snapshot semanal del inventario, 03:00–04:30 (copia completa; mas lento en temporada alta).

## Notas
- Telemetria: CPU, RAM, disco y latencia de app-01, y errores por minuto.
- Pico de pedidos a las 07:30 y a las 13:00 (reposicion de restaurantes).
""",
    },
    "kaiku": {
        "inicio": "2026-10-08 09:00",
        "base": {"cpu": 30.0, "ram": 48.0, "disco": 44.0, "latencia": 60.0, "errores": 0.5},
        "ruido": {"cpu": 3.0, "ram": 2.0, "disco": 0.2, "latencia": 9.0},
        "estacional": {"cpu": 6.0, "ram": 2.0, "disco": 0.2, "latencia": 12.0, "errores": 0.4},
        # Tienda 24/7: pico de tarde y noche; fines de semana mas trafico.
        "perfil": {"picos": [(13.0, 3.0, 0.3), (21.0, 2.0, 0.55)],
                   "dias": [0.85, 0.85, 0.85, 0.85, 0.9, 1.05, 1.1]},
        "incidentes": [
            # Saturacion gradual de srv-bd-01: pendiente suave el fin de semana, golpe el domingo.
            {"tipo": "saturacion_bd_gradual", "forma": "exponencial",
             "inicio": "2026-10-10 09:00", "impacto": "2026-10-11 20:30", "fin": "2026-10-11 21:40",
             "delta": {"cpu": 24.0, "ram": 8.0, "latencia": 170.0, "errores": 5.0},
             "retraso": {"latencia": 240, "errores": 720},
             "logs": [
                 ("2026-10-10 13:20", "app", "INFO", "consultas lentas registradas en srv-bd-01: 14 (>1 s) en la ultima hora"),
                 ("2026-10-11 09:00", "app", "WARN", "pool de conexiones a la base de datos al 85%"),
                 ("2026-10-11 19:20", "servidor", "WARN", "cpu de srv-bd-01 al {cpu:.0f}% sostenido"),
                 ("2026-10-11 20:31", "app", "ERROR", "timeout en checkout de la tienda en linea (>8 s)"),
                 ("2026-10-11 20:35", "app", "ERROR", "timeout en checkout de la tienda en linea (>8 s), 14 peticiones"),
                 ("2026-10-11 21:40", "servidor", "INFO", "servicio de base de datos reiniciado por operador"),
             ]},
            # Fuga de conexiones en el checkout: el pool se llena de noche y se agota el lunes.
            {"tipo": "fuga_conexiones_checkout", "forma": "lineal",
             "inicio": "2026-10-11 22:00", "impacto": "2026-10-12 14:00", "fin": "2026-10-12 14:12",
             "delta": {"ram": 10.0, "errores": 1.6, "latencia": 35.0},
             "retraso": {"errores": 600, "latencia": 360},
             "logs": [
                 ("2026-10-11 22:10", "app", "DEBUG", "pool checkout: 41 conexiones abiertas (max 100)"),
                 ("2026-10-12 06:30", "app", "DEBUG", "pool checkout: 67 conexiones abiertas (max 100)"),
                 ("2026-10-12 09:45", "app", "WARN", "pool de conexiones a la base de datos al 85%"),
                 ("2026-10-12 14:00", "app", "ERROR", "checkout: 503 en 17 peticiones (pool agotado)"),
                 ("2026-10-12 14:12", "app", "INFO", "app-checkout reiniciado por operador"),
             ]},
            # Rafaga de trafico tipo bot sobre el checkout: aviso de menos de una hora.
            {"tipo": "rafaga_bot_checkout", "forma": "escalon",
             "inicio": "2026-10-13 19:20", "impacto": "2026-10-13 20:00", "fin": "2026-10-13 20:50",
             "delta": {"cpu": 30.0, "latencia": 220.0, "errores": 8.0},
             "logs": [
                 ("2026-10-13 19:24", "firewall", "WARN", "pico de conexiones entrantes a 443/tcp (x3 lo normal)"),
                 ("2026-10-13 20:01", "app", "ERROR", "timeout en checkout de la tienda en linea (>8 s)"),
                 ("2026-10-13 20:12", "firewall", "INFO", "WAF: 3 rangos bloqueados por tasa de peticion"),
                 ("2026-10-13 20:50", "servidor", "INFO", "trafico normalizado en 443/tcp"),
             ]},
        ],
        "senuelos": [
            # Campana de correo masivo: pico de trafico benigno con timeouts transitorios.
            {"tipo": "campana_correo", "inicio": "2026-10-09 12:00", "fin": "2026-10-09 13:30", "rampa": 10,
             "delta": {"cpu": 9.0, "latencia": 110.0, "errores": 4.0, "ram": 3.0},
             "logs": [
                 ("2026-10-09 11:55", "app", "INFO", "campana 'Otono de cafe': envio de correo masivo a 48000 contactos"),
                 ("2026-10-09 12:06", "firewall", "WARN", "pico de conexiones entrantes a 443/tcp (campana de correo)"),
                 ("2026-10-09 12:20", "app", "ERROR", "timeout en checkout de la tienda en linea (>8 s) en 6 peticiones"),
                 ("2026-10-09 13:40", "app", "INFO", "campana finalizada: 2.1 % de clics, 311 pedidos"),
             ]},
            # Reindexado dominical del catalogo: deadlocks que se reintentan solos.
            {"tipo": "reindexado_catalogo", "inicio": "2026-10-11 04:00", "fin": "2026-10-11 05:30", "rampa": 10,
             "delta": {"cpu": 25.0, "latencia": 90.0, "errores": 2.0},
             "logs": [
                 ("2026-10-11 04:22", "app", "ERROR", "deadlock detectado en tabla productos (transaccion reintentada)"),
                 ("2026-10-11 05:35", "app", "INFO", "reindexado del catalogo completado"),
             ]},
        ],
        "recurrentes": [
            # Respaldo diario mysqldump; a veces se queja de bloqueos y sigue bien.
            {"tipo": "mysqldump_diario", "hora": "03:00", "duracion": 30,
             "delta": {"cpu": 12.0, "latencia": 30.0, "disco": 1.0}, "rampa": 4, "p_falso": 0.3,
             "log_falso": ("servidor", "WARN", "mysqldump: espera de bloqueo de 8 s en tabla pedidos"),
             "log_ok": ("servidor", "INFO", "respaldo diario de base de datos completado")},
        ],
        "contexto": """# Contexto — kaiku

- **Giro:** comercio electronico de cafe y accesorios (tienda en linea y envios).
- **Empleados:** 18 (atencion, bodega y marketing).
- **Horario:** tienda en linea 24/7; soporte lunes a sabado 09:00–19:00.

## Sistemas criticos

| Sistema | Descripcion | Ventana critica |
|---|---|---|
| srv-bd-01 | Base de datos de pedidos e inventario | 24/7 |
| Tienda en linea | Catalogo, carrito y checkout | Campanas y fines de semana |
| fw-01 (firewall) | Proteccion perimetral y WAF basico | 24/7 |

## Eventos de negocio

- **Viernes 9 de octubre, 12:00:** envio de la campana de correo «Otono de cafe» (48 000 contactos); se espera un pico de trafico de unas 2 h.
- **Domingos 04:00:** reindexado del catalogo (unos 90 min).
- **Diario 03:00:** respaldo de la base de datos (30 min).

## Notas
- Telemetria: CPU, RAM, disco y latencia de srv-bd-01, y errores por minuto.
- Riesgo conocido: sin limite de conexiones por cliente en el checkout.
""",
    },
    "ttr": {
        "inicio": "2026-10-08 06:00",
        "base": {"cpu": 34.0, "ram": 61.0, "disco": 39.0, "latencia": 85.0, "errores": 0.4},
        "ruido": {"cpu": 3.0, "ram": 1.5, "disco": 0.2, "latencia": 12.0},
        "estacional": {"cpu": 7.0, "ram": 2.0, "disco": 0.2, "latencia": 15.0, "errores": 0.3},
        # Planeacion de rutas 06:00–08:00 a diario, lun-sab; domingo cerrado.
        "perfil": {"picos": [(7.0, 1.2, 0.6), (12.5, 3.0, 0.2), (17.0, 2.0, 0.2)],
                   "dias": [1, 1, 1, 1, 1, 1, 0.05]},
        "incidentes": [
            # Cache de posiciones GPS que crece el domingo; el optimizador se satura al planear el lunes.
            {"tipo": "crecimiento_cache_gps", "forma": "exponencial",
             "inicio": "2026-10-11 06:00", "impacto": "2026-10-12 07:00", "fin": "2026-10-12 07:50",
             "delta": {"ram": 14.0, "cpu": 30.0, "latencia": 180.0, "errores": 5.0},
             "retraso": {"ram": 0, "latencia": 300, "errores": 360},
             "logs": [
                 ("2026-10-11 08:14", "servidor", "DEBUG", "cache de posiciones GPS en 1.8 GB (ttl 24 h)"),
                 ("2026-10-12 03:10", "servidor", "DEBUG", "cache de posiciones GPS en 3.6 GB (ttl 24 h)"),
                 ("2026-10-12 06:30", "servidor", "WARN", "cpu del optimizador de rutas al {cpu:.0f}% y en aumento"),
                 ("2026-10-12 06:44", "app", "WARN", "cola de calculo de rutas con 210 tareas pendientes"),
                 ("2026-10-12 07:02", "app", "ERROR", "timeout consultando rutas (>5 s) para 14 unidades"),
                 ("2026-10-12 07:50", "servidor", "INFO", "proceso optimizador de rutas reiniciado por operador"),
             ]},
            # Enlace GPS intermitente: la latencia y los errores suben en rafagas durante la tarde.
            {"tipo": "red_gps_intermitente", "forma": "intermitente",
             "inicio": "2026-10-09 11:00", "impacto": "2026-10-09 15:00", "fin": "2026-10-09 15:40",
             "delta": {"latencia": 60.0, "errores": 3.0},
             "retraso": {"errores": 30},
             "logs": [
                 ("2026-10-09 11:20", "app", "INFO", "reconexion de 3 unidades al rastreo GPS"),
                 ("2026-10-09 12:40", "app", "WARN", "posiciones de 9 unidades sin datos >5 min"),
                 ("2026-10-09 15:02", "app", "ERROR", "app movil: 14 unidades sin posicion >10 min"),
                 ("2026-10-09 15:40", "servidor", "INFO", "enlace GPS restablecido (proveedor)"),
             ]},
            # Bloqueos en la base de rutas al arrancar la planeacion del miercoles.
            {"tipo": "bloqueo_base_rutas", "forma": "escalon",
             "inicio": "2026-10-14 04:00", "impacto": "2026-10-14 06:30", "fin": "2026-10-14 07:20",
             "delta": {"latencia": 380.0, "errores": 7.0, "cpu": 12.0},
             "logs": [
                 ("2026-10-14 04:50", "servidor", "DEBUG", "bd de rutas: espera de bloqueo de 120 ms (p99)"),
                 ("2026-10-14 06:12", "app", "WARN", "cola de calculo de rutas con 60 tareas pendientes"),
                 ("2026-10-14 06:31", "app", "ERROR", "timeout consultando rutas (>5 s) para 14 unidades"),
                 ("2026-10-14 07:20", "servidor", "INFO", "bloqueos liberados; optimizador reiniciado por operador"),
             ]},
        ],
        "senuelos": [
            # Mantenimiento de red programado: latencia alta sin incidente.
            {"tipo": "mantenimiento_red", "inicio": "2026-10-10 22:00", "fin": "2026-10-10 23:00", "rampa": 5,
             "delta": {"latencia": 90.0, "errores": 2.5},
             "logs": [
                 ("2026-10-10 21:55", "servidor", "INFO", "ventana de mantenimiento de red en la sede (programada)"),
                 ("2026-10-10 22:20", "servidor", "WARN", "latencia de red elevada durante el mantenimiento (esperado)"),
                 ("2026-10-10 23:05", "servidor", "INFO", "mantenimiento de red finalizado"),
             ]},
            # Pedido urgente de tres clientes: planeacion extra; no aparece en el contexto.
            {"tipo": "pedido_urgente", "inicio": "2026-10-13 06:00", "fin": "2026-10-13 09:00", "rampa": 15,
             "delta": {"cpu": 20.0, "latencia": 60.0},
             "logs": [
                 ("2026-10-13 06:40", "app", "WARN", "cola de calculo de rutas con 150 tareas pendientes"),
                 ("2026-10-13 08:40", "app", "INFO", "planeacion extra completada: 26 rutas"),
             ]},
        ],
        "recurrentes": [
            # Respaldo nocturno de la base de rutas; a veces omite una tabla y la reintenta.
            {"tipo": "respaldo_bd_nocturno", "hora": "01:00", "duracion": 45,
             "delta": {"cpu": 10.0, "latencia": 25.0, "disco": 0.5}, "rampa": 5, "p_falso": 0.3,
             "log_falso": ("servidor", "WARN", "respaldo de BD: 1 tabla omitida por bloqueo (reintentada)"),
             "log_ok": ("servidor", "INFO", "respaldo de BD completado")},
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

## Eventos de negocio

- **Sabado 10 de octubre, 22:00–23:00:** mantenimiento programado de red en la sede.

## Notas
- Telemetria: CPU, RAM, disco y latencia de srv-tms-01, y errores por minuto.
- El optimizador comparte servidor con el rastreo GPS.
""",
    },
}


def actividad(cfg, ts):
    """Nivel de actividad en [0, 1] segun hora del dia y dia de la semana."""
    h = ts.hour + ts.minute / 60
    pico = sum(a * math.exp(-((h - c) ** 2) / (2 * w * w)) for c, w, a in cfg["perfil"]["picos"])
    return min(1.0, 0.15 + cfg["perfil"]["dias"][ts.weekday()] * pico)


def fraccion(ev, m, k):
    """Peso (0 a 1) del efecto del evento ev sobre la metrica k en el minuto m."""
    inicio = ev["m_inicio"] + ev["retraso"].get(k, 0)
    fin = ev["m_fin"]
    if m < inicio or m >= fin:
        return 0.0
    if ev["pulso"]:
        r = ev["rampa"]
        return max(0.0, min(1.0, (m - inicio) / r, (fin - m) / r))
    dt = m - inicio
    total = ev["m_impacto"] - inicio
    if dt >= total:
        return 1.0                       # impacto: efecto completo hasta el fin
    p = dt / total
    forma = ev["forma"]
    if forma == "lineal":
        return p
    if forma == "exponencial":           # arranque lento, cola rapida
        return (math.exp(3 * p) - 1) / (math.exp(3) - 1)
    if forma == "escalon":               # cuatro escalones antes del impacto
        return math.floor(p * 4) / 4
    if forma == "intermitente":          # rafagas cada 90 min, cada vez mas largas
        ciclo = 90
        return 1.0 if dt % ciclo < ciclo * (0.05 + 0.95 * p) else 0.0
    raise ValueError(forma)


def efecto_total(efectos, m, k):
    total = 0.0
    for ev in efectos:
        d = ev["delta"].get(k)
        if d:
            total += d * fraccion(ev, m, k)
    return total


def construir_efectos(cfg, inicio, rng):
    """Une incidentes reales, senuelos y eventos recurrentes en una sola lista de efectos."""
    fin_serie = inicio + timedelta(minutes=MINUTOS)
    efectos = []

    def logs_de(lista):
        return [(t(f) + timedelta(seconds=rng.randint(0, 59)), fuente, nivel, plantilla)
                for f, fuente, nivel, plantilla in lista]

    for inc in cfg["incidentes"]:
        efectos.append({
            "tipo": inc["tipo"], "es_real": True, "pulso": False, "forma": inc["forma"],
            "m_inicio": minuto(inicio, inc["inicio"]), "m_impacto": minuto(inicio, inc["impacto"]),
            "m_fin": minuto(inicio, inc["fin"]), "delta": inc["delta"],
            "retraso": inc.get("retraso", {}), "logs": logs_de(inc["logs"]),
            "etiqueta": t(inc["impacto"]),
        })
    for sen in cfg["senuelos"]:
        m0 = minuto(inicio, sen["inicio"])
        efectos.append({
            "tipo": sen["tipo"], "es_real": False, "pulso": True, "forma": None,
            "m_inicio": m0, "m_fin": minuto(inicio, sen["fin"]), "rampa": sen["rampa"],
            "delta": sen["delta"], "retraso": {}, "logs": logs_de(sen["logs"]),
            "etiqueta": t(sen["inicio"]),
        })

    reales = [e for e in efectos if e["es_real"]]
    for rec in cfg["recurrentes"]:
        hora = datetime.strptime(rec["hora"], "%H:%M").time()
        for dia in range(-1, 9):
            comienzo = datetime.combine(inicio.date() + timedelta(days=dia), hora)
            if not (inicio <= comienzo < fin_serie):
                continue
            m0 = minuto(inicio, f"{comienzo:%Y-%m-%d %H:%M}")
            logs = []
            solapa = any(r["m_inicio"] - 60 <= m0 < r["m_fin"] for r in reales)
            if "log_falso" in rec and not solapa and rng.random() < rec["p_falso"]:
                fuente, nivel, msg = rec["log_falso"]
                logs.append((comienzo + timedelta(minutes=8, seconds=rng.randint(0, 59)), fuente, nivel, msg))
                fuente, nivel, msg = rec["log_ok"]
                logs.append((comienzo + timedelta(minutes=rec["duracion"] - 3), fuente, nivel, msg))
            efectos.append({
                "tipo": rec["tipo"], "es_real": False, "pulso": True, "forma": None,
                "m_inicio": m0, "m_fin": m0 + rec["duracion"], "rampa": rec["rampa"],
                "delta": rec["delta"], "retraso": {}, "logs": logs,
                "etiqueta": comienzo,
            })
    return efectos


def poisson(rng, lam):
    """Muestrea una Poisson(lam) con el generador del tenant (sin numpy)."""
    limite = math.exp(-lam)
    k, p = 0, 1.0
    while True:
        p *= rng.random()
        if p <= limite:
            return k
        k += 1


def generar_metricas(rng, cfg, inicio, efectos):
    """Devuelve la lista de filas (valores completos, sin faltantes)."""
    filas = []
    estado = {k: 0.0 for k in ("cpu", "ram", "disco", "latencia")}
    phi = 0.75                                # ruido AR(1): suave, con deriva posible
    for m in range(MINUTOS):
        ts = inicio + timedelta(minutes=m)
        act = actividad(cfg, ts) - 0.5
        fila = {"timestamp": ts}
        for k in ("cpu", "ram", "disco", "latencia"):
            sd = cfg["ruido"][k]
            estado[k] = phi * estado[k] + math.sqrt(1 - phi * phi) * rng.gauss(0, sd)
            v = cfg["base"][k] + cfg["estacional"][k] * act + estado[k] + efecto_total(efectos, m, k)
            lo, hi = LIMITES[k]
            fila[k] = min(max(v, lo), hi)
        lam = max(0.05, cfg["base"]["errores"] + cfg["estacional"]["errores"] * act
                  + efecto_total(efectos, m, "errores"))
        fila["errores"] = poisson(rng, lam)
        filas.append(fila)
    return filas


def generar_faltantes(rng):
    """Por minuto, el conjunto de metricas sin valor (celdas vacias y apagones del agente)."""
    faltan = [set() for _ in range(MINUTOS)]
    m = 0
    while m < MINUTOS:
        if rng.random() < PROB_APAGON:
            dur = rng.randint(3, 25)
            for j in range(m, min(MINUTOS, m + dur)):
                faltan[j].update(METRICAS)
            m += dur
        else:
            m += 1
    for j in range(MINUTOS):
        for k in METRICAS:
            if rng.random() < PROB_CELDA_FALTANTE:
                faltan[j].add(k)
    return faltan


PLANTILLAS = {
    "servidor": [
        ("INFO", "rotacion de logs completada ({n} archivos)"),
        ("INFO", "sesion abierta por admin desde 10.0.0.{ip}"),
        ("DEBUG", "ntp: offset {off} s respecto a time.google.com"),
        ("INFO", "snapshot programado completado en {ms} ms"),
        ("INFO", "actualizacion de seguridad instalada (KB{n})"),
        ("DEBUG", "conexion SMB desde 10.0.0.{ip} cerrada por inactividad"),
        ("INFO", "tarea programada 'limpieza_temp' finalizada en {ms} ms"),
        ("WARN", "servicio de impresion: cola con {n} trabajos pendientes"),
        ("ERROR", "tarea programada 'sync_contactos' sin respuesta (reintento {n} s)"),
    ],
    "firewall": [
        ("INFO", "permitido 10.0.1.{ip} -> 8.8.8.8:53/udp"),
        ("INFO", "bloqueado 185.220.101.{ip} -> 22/tcp (intento SSH)"),
        ("INFO", "VPN: usuario vpn{ip} conectado desde 189.201.12.{ip}"),
        ("INFO", "sesion TLS establecida 10.0.2.{ip} -> 443/tcp"),
        ("INFO", "VPN: usuario vpn{ip} desconectado (inactivo)"),
        ("DEBUG", "regla {n} aplicada a 10.0.3.{ip}"),
        ("WARN", "bloqueado 45.146.164.{ip} -> 3389/tcp (escaneo de puertos)"),
        ("INFO", "conexion 443/tcp desde 10.0.2.{ip} cerrada ({ms} ms)"),
    ],
    "app": [
        ("INFO", "GET /api/v1/clientes 200 en {ms} ms"),
        ("INFO", "login correcto del usuario u{ip}"),
        ("INFO", "lote completado: {n} registros procesados"),
        ("DEBUG", "cache hit ratio {pct}%"),
        ("INFO", "GET /api/v1/reportes 200 en {ms} ms"),
        ("INFO", "sincronizacion de catalogo finalizada: {n} cambios"),
        ("WARN", "reintento de envio de correo ({n} pendientes)"),
        ("ERROR", "webhook de notificacion sin respuesta (reintento programado)"),
    ],
}


def generar_logs(rng, cfg, filas, inicio, eventos):
    """Devuelve {fuente: [(timestamp, nivel, mensaje), ...]} con LINEAS_LOG_POR_FUENTE lineas."""
    por_fuente = {f: [] for f in PLANTILLAS}
    for ts, fuente, nivel, plantilla in eventos:
        m = int((ts - inicio).total_seconds() // 60)
        por_fuente[fuente].append((ts, nivel, plantilla.format(**filas[m])))

    for fuente, lista in por_fuente.items():
        relleno = LINEAS_LOG_POR_FUENTE - len(lista)
        while relleno > 0:
            m = rng.randrange(MINUTOS)
            # Mas ruido en horario de actividad; menos de madrugada.
            if rng.random() > 0.25 + 0.75 * actividad(cfg, inicio + timedelta(minutes=m)):
                continue
            ts = inicio + timedelta(minutes=m, seconds=rng.randint(0, 59))
            # Relleno: casi todo INFO/DEBUG; alertas benignas solo ~4 % de las lineas.
            alertas = [p for p in PLANTILLAS[fuente] if p[0] in ("WARN", "ERROR")]
            rutina = [p for p in PLANTILLAS[fuente] if p[0] not in ("WARN", "ERROR")]
            nivel, plantilla = rng.choice(alertas if rng.random() < 0.04 else rutina)
            msg = plantilla.format(
                n=rng.randint(10, 900), ip=rng.randint(2, 250), off=f"{rng.uniform(-0.01, 0.01):.4f}",
                ms=rng.randint(12, 480), pct=rng.randint(85, 99),
            )
            lista.append((ts, nivel, msg))
            relleno -= 1
        lista.sort(key=lambda e: e[0])
    return por_fuente


def formato_fila(tenant, r, faltan):
    celdas = []
    for k in METRICAS:
        if k in faltan:
            celdas.append("")
        elif k == "errores":
            celdas.append(str(r[k]))
        elif k == "latencia":
            celdas.append(f"{r[k]:.0f}")
        else:
            celdas.append(f"{r[k]:.1f}")
    return ",".join(celdas)


def escribir_metricas(ruta, filas, faltantes):
    with ruta.open("w", encoding="utf-8") as f:
        f.write("timestamp,cpu,ram,disco,latencia_ms,errores\n")
        for r, falt in zip(filas, faltantes):
            f.write(f"{r['timestamp']:%Y-%m-%dT%H:%M:%S},{formato_fila(None, r, falt)}\n")


def escribir_logs(ruta, nombre, inicio, fin, por_fuente):
    partes = [
        f"# Logs — {nombre}\n",
        f"Ventana: {inicio:%Y-%m-%d %H:%M} a {fin:%Y-%m-%d %H:%M} (sintetico). "
        "Formato: `timestamp nivel mensaje`.\n",
    ]
    for fuente in ("servidor", "firewall", "app"):
        lineas = "\n".join(
            f"{ts:%Y-%m-%dT%H:%M:%S} {nivel} {msg}" for ts, nivel, msg in por_fuente[fuente]
        )
        partes.append(f"## {fuente}\n\n```text\n{lineas}\n```\n")
    ruta.write_text("\n".join(partes), encoding="utf-8")


def escribir_etiquetas(ruta, efectos):
    filas = sorted(efectos, key=lambda e: e["etiqueta"])
    with ruta.open("w", encoding="utf-8") as f:
        f.write("inicio_incidente,tipo,es_real\n")
        for ev in filas:
            f.write(f"{ev['etiqueta']:%Y-%m-%dT%H:%M:%S},{ev['tipo']},"
                    f"{'true' if ev['es_real'] else 'false'}\n")


def main():
    combinado = []
    for nombre, cfg in TENANTS.items():
        rng = random.Random(f"{SEMILLA}-{nombre}")
        inicio = t(cfg["inicio"])
        fin = inicio + timedelta(minutes=MINUTOS)

        efectos = construir_efectos(cfg, inicio, rng)
        filas = generar_metricas(rng, cfg, inicio, efectos)
        faltantes = generar_faltantes(rng)
        eventos = [e for ev in efectos for e in ev["logs"]]
        por_fuente = generar_logs(rng, cfg, filas, inicio, eventos)

        carpeta = SALIDA / nombre
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / "contexto.md").write_text(cfg["contexto"], encoding="utf-8")
        escribir_metricas(carpeta / "metricas.csv", filas, faltantes)
        escribir_logs(carpeta / "logs.md", nombre, inicio, fin, por_fuente)

        solucion = SALIDA / "_solucion" / nombre
        solucion.mkdir(parents=True, exist_ok=True)
        escribir_etiquetas(solucion / "etiquetas.csv", efectos)

        combinado.extend((nombre, r, f) for r, f in zip(filas, faltantes))
        print(f"{nombre}: {len(filas)} filas de metricas, "
              f"{sum(len(v) for v in por_fuente.values())} lineas de log, "
              f"{sum(1 for e in efectos if e['es_real'])} incidentes reales -> {carpeta}")

    ruta = SALIDA / "todos_metricas.csv"
    combinado.sort(key=lambda x: (x[1]["timestamp"], x[0]))
    with ruta.open("w", encoding="utf-8") as f:
        f.write("tenant,timestamp,cpu,ram,disco,latencia_ms,errores\n")
        for n, r, falt in combinado:
            f.write(f"{n},{r['timestamp']:%Y-%m-%dT%H:%M:%S},{formato_fila(n, r, falt)}\n")
    print(f"combinado: {len(combinado)} filas -> {ruta}")


if __name__ == "__main__":
    main()
