# Logs — gracko

Ventana: 2026-10-08 08:00–10:00 (sintetico). Formato: `timestamp nivel mensaje`.

## servidor

```text
2026-10-08T08:04:49 DEBUG ntp: offset 0.0032 s respecto a time.google.com
2026-10-08T08:29:07 DEBUG ntp: offset -0.0076 s respecto a time.google.com
2026-10-08T08:29:15 INFO sesion abierta por admin desde 10.0.0.112
2026-10-08T08:47:08 INFO sesion abierta por admin desde 10.0.0.158
2026-10-08T08:55:42 DEBUG ntp: offset -0.0006 s respecto a time.google.com
2026-10-08T09:00:02 INFO snapshot programado completado en 239 ms
2026-10-08T09:00:13 INFO crecimiento inusual de /data: +1.8 GB en la ultima hora
2026-10-08T09:05:28 INFO snapshot programado completado en 16 ms
2026-10-08T09:06:31 INFO snapshot programado completado en 24 ms
2026-10-08T09:06:37 INFO rotacion de logs completada (264 archivos)
2026-10-08T09:13:53 INFO sesion abierta por admin desde 10.0.0.165
2026-10-08T09:20:58 WARN disco /data al 80% (umbral 80%)
2026-10-08T09:28:07 INFO snapshot programado completado en 350 ms
2026-10-08T09:32:43 WARN disco /data al 92% (umbral 90%)
2026-10-08T09:33:03 INFO sesion abierta por admin desde 10.0.0.245
2026-10-08T09:37:12 ERROR job respaldo-nocturno abortado: no space left on device
2026-10-08T09:42:11 INFO sesion abierta por admin desde 10.0.0.229
2026-10-08T09:46:22 DEBUG ntp: offset 0.0030 s respecto a time.google.com
2026-10-08T09:47:23 INFO rotacion de logs completada (852 archivos)
2026-10-08T09:55:02 INFO snapshot programado completado en 160 ms
```

## firewall

```text
2026-10-08T08:14:09 INFO VPN: usuario vpn7 conectado desde 189.201.12.7
2026-10-08T08:14:42 INFO VPN: usuario vpn56 conectado desde 189.201.12.56
2026-10-08T08:24:56 INFO permitido 10.0.1.48 -> 8.8.8.8:53/udp
2026-10-08T08:26:22 INFO sesion TLS establecida 10.0.2.33 -> 443/tcp
2026-10-08T08:33:50 INFO permitido 10.0.1.161 -> 8.8.8.8:53/udp
2026-10-08T08:36:09 INFO sesion TLS establecida 10.0.2.205 -> 443/tcp
2026-10-08T08:46:17 INFO sesion TLS establecida 10.0.2.131 -> 443/tcp
2026-10-08T08:54:36 INFO permitido 10.0.1.108 -> 8.8.8.8:53/udp
2026-10-08T08:57:18 INFO permitido 10.0.1.167 -> 8.8.8.8:53/udp
2026-10-08T09:06:06 INFO bloqueado 185.220.101.31 -> 22/tcp (intento SSH)
2026-10-08T09:08:35 INFO sesion TLS establecida 10.0.2.109 -> 443/tcp
2026-10-08T09:09:28 INFO sesion TLS establecida 10.0.2.171 -> 443/tcp
2026-10-08T09:22:03 INFO permitido 10.0.1.126 -> 8.8.8.8:53/udp
2026-10-08T09:23:58 INFO bloqueado 185.220.101.244 -> 22/tcp (intento SSH)
2026-10-08T09:26:33 INFO bloqueado 185.220.101.142 -> 22/tcp (intento SSH)
2026-10-08T09:30:55 INFO VPN: usuario vpn170 conectado desde 189.201.12.170
2026-10-08T09:31:59 INFO sesion TLS establecida 10.0.2.118 -> 443/tcp
2026-10-08T09:38:58 INFO bloqueado 185.220.101.80 -> 22/tcp (intento SSH)
2026-10-08T09:43:37 INFO VPN: usuario vpn206 conectado desde 189.201.12.206
2026-10-08T09:50:47 INFO permitido 10.0.1.166 -> 8.8.8.8:53/udp
```

## app

```text
2026-10-08T08:14:53 INFO lote completado: 296 registros procesados
2026-10-08T08:19:41 DEBUG cache hit ratio 94%
2026-10-08T08:24:51 DEBUG cache hit ratio 93%
2026-10-08T08:35:12 DEBUG cache hit ratio 88%
2026-10-08T08:40:29 INFO lote completado: 754 registros procesados
2026-10-08T08:45:32 DEBUG cache hit ratio 96%
2026-10-08T08:58:28 INFO GET /api/v1/clientes 200 en 340 ms
2026-10-08T09:02:07 INFO GET /api/v1/clientes 200 en 425 ms
2026-10-08T09:03:03 INFO login correcto del usuario u8
2026-10-08T09:04:01 DEBUG cache hit ratio 85%
2026-10-08T09:04:43 INFO GET /api/v1/clientes 200 en 112 ms
2026-10-08T09:11:22 DEBUG cache hit ratio 91%
2026-10-08T09:11:49 INFO login correcto del usuario u145
2026-10-08T09:13:40 DEBUG cache hit ratio 93%
2026-10-08T09:15:11 DEBUG cache hit ratio 89%
2026-10-08T09:18:44 DEBUG cache hit ratio 86%
2026-10-08T09:23:22 DEBUG cache hit ratio 85%
2026-10-08T09:26:54 INFO lote completado: 802 registros procesados
2026-10-08T09:30:29 INFO GET /api/v1/clientes 200 en 432 ms
2026-10-08T09:37:24 ERROR exportacion de cierre mensual fallida: escritura en /data sin espacio
```
