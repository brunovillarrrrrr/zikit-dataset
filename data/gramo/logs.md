# Logs — gramo

Ventana: 2026-10-08 07:00–09:00 (sintetico). Formato: `timestamp nivel mensaje`.

## servidor

```text
2026-10-08T07:01:46 DEBUG ntp: offset -0.0067 s respecto a time.google.com
2026-10-08T07:07:04 INFO snapshot programado completado en 406 ms
2026-10-08T07:07:12 INFO snapshot programado completado en 210 ms
2026-10-08T07:11:22 INFO snapshot programado completado en 120 ms
2026-10-08T07:18:48 INFO sesion abierta por admin desde 10.0.0.196
2026-10-08T07:26:21 INFO sesion abierta por admin desde 10.0.0.54
2026-10-08T07:29:59 INFO sesion abierta por admin desde 10.0.0.98
2026-10-08T07:46:14 DEBUG ntp: offset 0.0036 s respecto a time.google.com
2026-10-08T07:46:40 DEBUG ntp: offset -0.0074 s respecto a time.google.com
2026-10-08T07:47:21 WARN memoria RAM al 84% (umbral 85%) en app-01
2026-10-08T07:48:31 INFO rotacion de logs completada (81 archivos)
2026-10-08T07:54:27 INFO supervisor reinicio el servicio pedidos-worker
2026-10-08T08:01:17 INFO sesion abierta por admin desde 10.0.0.95
2026-10-08T08:08:30 INFO sesion abierta por admin desde 10.0.0.19
2026-10-08T08:19:28 DEBUG ntp: offset 0.0090 s respecto a time.google.com
2026-10-08T08:27:13 DEBUG ntp: offset -0.0079 s respecto a time.google.com
2026-10-08T08:33:24 INFO snapshot programado completado en 107 ms
2026-10-08T08:39:10 DEBUG ntp: offset -0.0051 s respecto a time.google.com
2026-10-08T08:53:27 INFO rotacion de logs completada (63 archivos)
2026-10-08T08:54:50 INFO sesion abierta por admin desde 10.0.0.56
```

## firewall

```text
2026-10-08T07:01:48 INFO VPN: usuario vpn147 conectado desde 189.201.12.147
2026-10-08T07:02:04 INFO sesion TLS establecida 10.0.2.197 -> 443/tcp
2026-10-08T07:06:56 INFO VPN: usuario vpn50 conectado desde 189.201.12.50
2026-10-08T07:24:55 INFO sesion TLS establecida 10.0.2.9 -> 443/tcp
2026-10-08T07:33:54 INFO bloqueado 185.220.101.244 -> 22/tcp (intento SSH)
2026-10-08T07:38:30 INFO bloqueado 185.220.101.41 -> 22/tcp (intento SSH)
2026-10-08T07:39:34 INFO bloqueado 185.220.101.199 -> 22/tcp (intento SSH)
2026-10-08T07:54:43 INFO sesion TLS establecida 10.0.2.212 -> 443/tcp
2026-10-08T07:55:13 INFO permitido 10.0.1.242 -> 8.8.8.8:53/udp
2026-10-08T07:57:12 INFO sesion TLS establecida 10.0.2.208 -> 443/tcp
2026-10-08T07:57:55 INFO permitido 10.0.1.93 -> 8.8.8.8:53/udp
2026-10-08T08:11:47 INFO bloqueado 185.220.101.151 -> 22/tcp (intento SSH)
2026-10-08T08:13:26 INFO bloqueado 185.220.101.36 -> 22/tcp (intento SSH)
2026-10-08T08:39:55 WARN 480 conn/s desde 198.51.100.23 hacia 443/tcp (posible SYN flood)
2026-10-08T08:44:08 INFO rate-limit aplicado a 198.51.100.0/24
2026-10-08T08:44:19 INFO sesion TLS establecida 10.0.2.50 -> 443/tcp
2026-10-08T08:50:51 INFO VPN: usuario vpn249 conectado desde 189.201.12.249
2026-10-08T08:52:22 INFO rate-limit retirado tras 8 min sin trafico anomalo
2026-10-08T08:53:38 INFO permitido 10.0.1.211 -> 8.8.8.8:53/udp
2026-10-08T08:57:16 INFO sesion TLS establecida 10.0.2.248 -> 443/tcp
```

## app

```text
2026-10-08T07:04:20 INFO login correcto del usuario u93
2026-10-08T07:04:59 INFO lote completado: 204 registros procesados
2026-10-08T07:05:38 INFO lote completado: 57 registros procesados
2026-10-08T07:09:18 INFO GET /api/v1/clientes 200 en 27 ms
2026-10-08T07:11:19 INFO login correcto del usuario u137
2026-10-08T07:11:23 INFO lote completado: 295 registros procesados
2026-10-08T07:28:26 INFO login correcto del usuario u210
2026-10-08T07:37:05 INFO GET /api/v1/clientes 200 en 423 ms
2026-10-08T07:46:00 DEBUG cache hit ratio 85%
2026-10-08T07:46:31 INFO login correcto del usuario u213
2026-10-08T07:52:17 ERROR OutOfMemoryError en pedidos-worker (pid 4117); 3 pedidos abortados
2026-10-08T07:53:54 ERROR API /pedidos responde en 233 ms; 504 en 9 peticiones
2026-10-08T08:08:08 INFO lote completado: 161 registros procesados
2026-10-08T08:11:14 INFO login correcto del usuario u216
2026-10-08T08:11:17 INFO GET /api/v1/clientes 200 en 111 ms
2026-10-08T08:16:10 INFO GET /api/v1/clientes 200 en 371 ms
2026-10-08T08:46:01 INFO login correcto del usuario u217
2026-10-08T08:49:46 INFO login correcto del usuario u102
2026-10-08T08:49:58 INFO GET /api/v1/clientes 200 en 111 ms
2026-10-08T08:51:00 INFO lote completado: 513 registros procesados
```
