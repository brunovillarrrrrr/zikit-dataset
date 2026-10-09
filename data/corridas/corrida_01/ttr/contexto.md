# Contexto — ttr

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
