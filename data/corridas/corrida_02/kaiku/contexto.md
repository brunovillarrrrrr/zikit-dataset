# Contexto — kaiku

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
