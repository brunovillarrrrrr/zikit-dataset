# Logs — ttr

Ventana: 2026-10-08 06:00–08:00 (sintetico). Formato: `timestamp nivel mensaje`.

## servidor

```text
2026-10-08T06:01:56 DEBUG ntp: offset -0.0073 s respecto a time.google.com
2026-10-08T06:16:56 INFO rotacion de logs completada (398 archivos)
2026-10-08T06:41:44 INFO sesion abierta por admin desde 10.0.0.24
2026-10-08T06:43:13 INFO snapshot programado completado en 69 ms
2026-10-08T06:44:58 DEBUG ntp: offset 0.0100 s respecto a time.google.com
2026-10-08T06:49:40 DEBUG ntp: offset 0.0095 s respecto a time.google.com
2026-10-08T06:51:32 INFO rotacion de logs completada (41 archivos)
2026-10-08T06:53:12 INFO sesion abierta por admin desde 10.0.0.114
2026-10-08T06:53:33 INFO sesion abierta por admin desde 10.0.0.228
2026-10-08T07:00:52 INFO rotacion de logs completada (728 archivos)
2026-10-08T07:03:50 DEBUG ntp: offset 0.0034 s respecto a time.google.com
2026-10-08T07:04:14 INFO snapshot programado completado en 54 ms
2026-10-08T07:08:05 INFO sesion abierta por admin desde 10.0.0.126
2026-10-08T07:16:31 WARN cpu del optimizador de rutas al 58% y en aumento
2026-10-08T07:17:10 INFO sesion abierta por admin desde 10.0.0.21
2026-10-08T07:21:28 INFO snapshot programado completado en 223 ms
2026-10-08T07:22:39 INFO snapshot programado completado en 394 ms
2026-10-08T07:27:09 INFO rotacion de logs completada (128 archivos)
2026-10-08T07:28:50 DEBUG ntp: offset 0.0031 s respecto a time.google.com
2026-10-08T07:36:38 INFO snapshot programado completado en 132 ms
```

## firewall

```text
2026-10-08T06:08:20 INFO permitido 10.0.1.113 -> 8.8.8.8:53/udp
2026-10-08T06:10:16 INFO bloqueado 185.220.101.218 -> 22/tcp (intento SSH)
2026-10-08T06:20:16 INFO sesion TLS establecida 10.0.2.72 -> 443/tcp
2026-10-08T06:25:21 INFO bloqueado 185.220.101.136 -> 22/tcp (intento SSH)
2026-10-08T06:28:33 INFO sesion TLS establecida 10.0.2.162 -> 443/tcp
2026-10-08T06:41:40 INFO sesion TLS establecida 10.0.2.101 -> 443/tcp
2026-10-08T06:44:30 INFO VPN: usuario vpn20 conectado desde 189.201.12.20
2026-10-08T06:44:36 INFO VPN: usuario vpn53 conectado desde 189.201.12.53
2026-10-08T06:58:33 INFO VPN: usuario vpn61 conectado desde 189.201.12.61
2026-10-08T07:07:08 INFO sesion TLS establecida 10.0.2.68 -> 443/tcp
2026-10-08T07:12:20 INFO VPN: usuario vpn54 conectado desde 189.201.12.54
2026-10-08T07:14:29 INFO bloqueado 185.220.101.32 -> 22/tcp (intento SSH)
2026-10-08T07:16:10 INFO sesion TLS establecida 10.0.2.216 -> 443/tcp
2026-10-08T07:25:57 INFO permitido 10.0.1.174 -> 8.8.8.8:53/udp
2026-10-08T07:26:13 INFO bloqueado 185.220.101.121 -> 22/tcp (intento SSH)
2026-10-08T07:29:06 INFO bloqueado 185.220.101.109 -> 22/tcp (intento SSH)
2026-10-08T07:30:03 INFO sesion TLS establecida 10.0.2.46 -> 443/tcp
2026-10-08T07:30:28 INFO permitido 10.0.1.239 -> 8.8.8.8:53/udp
2026-10-08T07:30:45 INFO VPN: usuario vpn220 conectado desde 189.201.12.220
2026-10-08T07:51:08 INFO VPN: usuario vpn20 conectado desde 189.201.12.20
```

## app

```text
2026-10-08T06:03:31 INFO GET /api/v1/clientes 200 en 320 ms
2026-10-08T06:03:37 DEBUG cache hit ratio 94%
2026-10-08T06:26:01 DEBUG cache hit ratio 98%
2026-10-08T06:29:14 INFO login correcto del usuario u122
2026-10-08T06:35:27 INFO GET /api/v1/clientes 200 en 235 ms
2026-10-08T06:36:08 DEBUG cache hit ratio 98%
2026-10-08T06:42:28 INFO lote completado: 280 registros procesados
2026-10-08T06:48:21 INFO login correcto del usuario u38
2026-10-08T06:56:52 DEBUG cache hit ratio 93%
2026-10-08T07:04:13 INFO lote completado: 267 registros procesados
2026-10-08T07:14:25 INFO lote completado: 292 registros procesados
2026-10-08T07:24:38 WARN cola de calculo de rutas con 210 tareas pendientes
2026-10-08T07:28:06 ERROR timeout consultando rutas (>5 s) para 14 unidades
2026-10-08T07:30:52 INFO GET /api/v1/clientes 200 en 471 ms
2026-10-08T07:32:21 INFO GET /api/v1/clientes 200 en 407 ms
2026-10-08T07:32:47 DEBUG cache hit ratio 98%
2026-10-08T07:35:26 DEBUG cache hit ratio 98%
2026-10-08T07:40:10 INFO GET /api/v1/clientes 200 en 265 ms
2026-10-08T07:40:17 INFO proceso optimizador de rutas reiniciado por operador
2026-10-08T07:42:01 INFO GET /api/v1/clientes 200 en 118 ms
```
