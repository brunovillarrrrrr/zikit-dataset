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

## Notas
- Telemetria: CPU, RAM, disco y latencia de srv-bd-01, y errores por minuto.
- Riesgo conocido: sin limite de conexiones por cliente en el checkout.
