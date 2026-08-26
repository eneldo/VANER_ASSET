# Alta de un cliente VANER ASSET

1. Crear un `.env` fuera de Git con `APP_NAME`, `CLIENT_CODE`, `CLIENT_NAME` y `APP_DOMAIN`.
2. Crear la empresa tenant y sus sedes.
3. Crear usuarios y asignar roles minimos.
4. Configurar identidad visual y datos de soporte.
5. Definir modulos habilitados.
6. Configurar almacenamiento, correo e integraciones.
7. Importar inventario autorizado o iniciar vacio.
8. Ejecutar pruebas de aislamiento, permisos y reportes.
9. Registrar fecha, responsable y version desplegada.

Ejemplo no sensible:

```dotenv
APP_NAME="VANER ASSET"
CLIENT_CODE=empresa_xyz
CLIENT_NAME="Empresa XYZ S.A.S."
APP_DOMAIN=asset.empresaxyz.com
```

Nunca copie bases de datos, evidencias, usuarios, secretos o archivos desde SGAHolding hacia un nuevo cliente.
