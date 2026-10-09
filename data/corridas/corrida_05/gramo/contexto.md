# Contexto — gramo

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
