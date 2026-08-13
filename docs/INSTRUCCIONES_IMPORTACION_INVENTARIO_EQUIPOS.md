# Plantilla de importacion de inventario de equipos

Archivo para cargar: `output/templates/plantilla_importacion_inventario_equipos.csv`

## Reglas importantes

- No cambie, traduzca, reordene ni elimine los encabezados de la fila 1.
- El archivo CSV debe conservar el separador coma.
- Cada fila representa un equipo.
- Elimine filas completamente vacias antes de importar.
- Diligencie las once columnas. Para marca, modelo, serie o ubicacion desconocidos, escriba `SIN DATO` en lugar de dejar la celda vacia. No use `N/A` ni `NA` porque pandas puede interpretarlos como valores vacios.
- `codigo_inventario` debe ser unico en toda la plataforma. El importador lo guarda como Codigo ID del equipo.
- `empresa` debe coincidir con el nombre registrado en el modulo Empresas.
- `sede` debe coincidir con el nombre registrado en el modulo Sedes y pertenecer a la empresa indicada.
- `categoria` debe coincidir exactamente con uno de los cuatro nombres permitidos.
- La carga masiva actual no importa los campos INVIMA, Inventario adicional ni la hoja de vida tecnica. Esos datos se completan posteriormente en la plataforma.

## Columnas

| Columna | Obligatoria | Contenido | Ejemplo |
| --- | --- | --- | --- |
| `codigo_inventario` | Si | Codigo unico del equipo | `EQ-0001` |
| `nombre` | Si | Nombre o descripcion corta | `Bomba centrifuga 1` |
| `empresa` | Si | Nombre exacto de la empresa | `Empresa Ejemplo SAS` |
| `sede` | Si | Nombre exacto de la sede | `Sede Principal` |
| `categoria` | Si | Categoria canonica | `Equipos Industriales` |
| `marca` | Si en la plantilla | Marca o `SIN DATO` | `Siemens` |
| `modelo` | Si en la plantilla | Modelo o `SIN DATO` | `XYZ-100` |
| `serie` | Si en la plantilla | Serie o `SIN DATO` | `SN123456` |
| `ubicacion` | Si en la plantilla | Ubicacion interna o `SIN DATO` | `Cuarto de bombas` |
| `estado` | Si | Estado permitido en mayusculas | `OPERATIVO` |
| `criticidad` | Si | Criticidad permitida en mayusculas | `MEDIA` |

## Categorias permitidas

- `Equipos Industriales`
- `Aires Acondicionados`
- `Cámaras de Seguridad`
- `Sistemas de Protección Contra Incendios`

Copie los nombres directamente desde el modulo Categorias para garantizar la coincidencia exacta, especialmente cuando contienen tildes.

## Estados permitidos

- `OPERATIVO`
- `EN_MANTENIMIENTO`
- `FUERA_DE_SERVICIO`
- `BAJA`

## Criticidades permitidas

- `BAJA`
- `MEDIA`
- `ALTA`
- `CRITICA`

## Procedimiento

1. Abra la plantilla en Excel.
2. Agregue un equipo por fila desde la fila 2.
3. No agregue titulos ni notas encima de la fila de encabezados.
4. Guarde como `CSV UTF-8 (delimitado por comas)`.
5. En SGA SaaS, entre en Administracion > Equipos > Importar inventario.
6. Seleccione el archivo y ejecute la importacion.
7. Revise el resumen de creados y los errores por numero de fila.
