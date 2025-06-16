# API Compras - Microservicio Multi-tenant para Inkafarma

Este microservicio maneja el registro y gestión de compras con soporte multi-tenant usando AWS Lambda, DynamoDB y autenticación JWT.

## Características

- ✅ Multi-tenancy (soporte para múltiples inquilinos)
- ✅ Serverless con AWS Lambda
- ✅ Protegido con autenticación JWT
- ✅ Registro de compras con múltiples productos
- ✅ Listado paginado de compras por usuario
- ✅ Búsqueda de compras por código
- ✅ Estadísticas de compras por usuario
- ✅ DynamoDB Streams habilitado para ingesta en tiempo real
- ✅ CORS habilitado
- ✅ Despliegue automatizado con Serverless Framework
- ✅ Manejo de decimales para cálculos monetarios precisos

## Estructura de Compras

Cada compra contiene:
- **tenant_id**: Identificador del inquilino (extraído del JWT)
- **codigo_compra**: Código único generado automáticamente (COM-timestamp-random)
- **email_usuario**: Email del usuario que realizó la compra
- **nombre_usuario**: Nombre del usuario
- **productos**: Array de productos comprados con código, nombre, precio, cantidad y subtotal
- **total_productos**: Cantidad total de productos
- **total_monto**: Monto total de la compra
- **fecha_compra**: Timestamp ISO de la compra
- **estado**: Estado de la compra (completada, pendiente, cancelada)
- **metodo_pago**: Método de pago utilizado
- **direccion_entrega**: Dirección de entrega (opcional)
- **observaciones**: Observaciones adicionales (opcional)

## Endpoints

### 1. Registrar Compra
- **URL**: `POST /compras/registrar`
- **Headers**: `Authorization: Bearer <token>`
- **Body**:
```json
{
  "productos": [
    {
      "codigo": "MED-ABC123-DEF456",
      "nombre": "Paracetamol 500mg",
      "precio": 12.50,
      "cantidad": 2
    },
    {
      "codigo": "MED-XYZ789-GHI012",
      "nombre": "Ibuprofeno 400mg",
      "precio": 18.00,
      "cantidad": 1
    }
  ],
  "metodo_pago": "tarjeta",
  "direccion_entrega": "Av. Siempre Viva 123, Lima",
  "observaciones": "Entregar en horario de oficina"
}
```
- **Respuesta**:
```json
{
  "message": "Compra registrada exitosamente",
  "compra": {
    "tenant_id": "inkafarma",
    "codigo_compra": "COM-1718123456-A7B9C2D4",
    "email_usuario": "usuario@email.com",
    "nombre_usuario": "Juan Pérez",
    "productos": [...],
    "total_productos": 3,
    "total_monto": 43.00,
    "fecha_compra": "2025-06-15T10:30:00.000Z",
    "estado": "completada",
    "metodo_pago": "tarjeta",
    "direccion_entrega": "Av. Siempre Viva 123, Lima",
    "observaciones": "Entregar en horario de oficina"
  }
}
```

### 2. Listar Compras del Usuario
- **URL**: `GET /compras/listar`
- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**:
  - `limit` (opcional): Número de compras por página (default: 20, máximo: 100)
  - `lastKey` (opcional): Clave para paginación (base64 encoded)
- **Respuesta**:
```json
{
  "compras": [...],
  "count": 20,
  "nextKey": "base64_encoded_key",
  "hasMore": true
}
```

### 3. Buscar Compra por Código
- **URL**: `GET /compras/buscar/{codigo}`
- **Headers**: `Authorization: Bearer <token>`
- **Respuesta**:
```json
{
  "compra": {
    "tenant_id": "inkafarma",
    "codigo_compra": "COM-1718123456-A7B9C2D4",
    "email_usuario": "usuario@email.com",
    "nombre_usuario": "Juan Pérez",
    "productos": [...],
    "total_productos": 3,
    "total_monto": 43.00,
    "fecha_compra": "2025-06-15T10:30:00.000Z",
    "estado": "completada",
    "metodo_pago": "tarjeta",
    "direccion_entrega": "Av. Siempre Viva 123, Lima"
  }
}
```

### 4. Estadísticas de Compras
- **URL**: `GET /compras/estadisticas`
- **Headers**: `Authorization: Bearer <token>`
- **Respuesta**:
```json
{
  "total_compras": 15,
  "total_gastado": 856.50,
  "total_productos_comprados": 45,
  "promedio_por_compra": 57.10,
  "primera_compra": "2025-05-01T08:15:00.000Z",
  "ultima_compra": "2025-06-15T10:30:00.000Z"
}
```

## Instalación y Despliegue

### Prerrequisitos
- Node.js 18+
- Python 3.11+
- AWS CLI configurado con credenciales válidas
- Serverless Framework (`npm install -g serverless`)
- Token JWT válido del microservicio de usuarios
- Permisos AWS para crear recursos (DynamoDB, Lambda, IAM)

### Variables de Entorno

El sistema utiliza las siguientes variables de entorno (configuradas automáticamente):

- `TABLE_NAME`: `{stage}-t_compras` (auto-generado por stage)
- `JWT_SECRET`: `mi-super-secreto-jwt-2025`

### Comandos de Despliegue

```bash
# Instalar dependencias
npm install

# Desplegar a desarrollo
npm run deploy-dev

# Desplegar a testing  
npm run deploy-test

# Desplegar a producción
npm run deploy-prod

# Eliminar despliegue
npm run remove-dev
npm run remove-test  
npm run remove-prod

# Ver información del despliegue
npm run info

# Ver logs en tiempo real
npm run logs-registrar
npm run logs-listar
npm run logs-buscar
npm run logs-estadisticas
```

## Estructura del Proyecto

```
api-compras/
├── compras.py          # Funciones Lambda principales
├── serverless.yml      # Configuración Serverless Framework
├── requirements.txt    # Dependencias Python
├── package.json       # Configuración del proyecto y scripts
└── README.md          # Documentación del proyecto
```

## Tabla DynamoDB

**Nombre**: `{stage}-t_compras`

**Schema**:
- **Partition Key**: `tenant_id` (String)
- **Sort Key**: `codigo_compra` (String)  
- **Streams**: Habilitado con NEW_AND_OLD_IMAGES
- **Billing**: PAY_PER_REQUEST

**Campos**:
- `tenant_id`: Identificador del inquilino (extraído del JWT)
- `codigo_compra`: Código único de la compra (auto-generado formato COM-timestamp-random)
- `email_usuario`: Email del usuario que realizó la compra
- `nombre_usuario`: Nombre del usuario
- `productos`: Array de productos con código, nombre, precio, cantidad y subtotal
- `total_productos`: Cantidad total de productos en la compra
- `total_monto`: Monto total de la compra (Decimal)
- `fecha_compra`: Timestamp ISO de la compra
- `estado`: Estado de la compra (String)
- `metodo_pago`: Método de pago utilizado
- `direccion_entrega`: Dirección de entrega (opcional)
- `observaciones`: Observaciones adicionales (opcional)

## Validaciones

### Estructura de Productos
Cada producto en la compra debe tener:
- `codigo`: Código del producto (requerido)
- `nombre`: Nombre del producto (requerido)
- `precio`: Precio unitario (requerido, mayor a 0)
- `cantidad`: Cantidad comprada (requerido, entero mayor a 0)

### Cálculos Automáticos
- `subtotal`: Se calcula automáticamente como precio × cantidad
- `total_productos`: Suma de todas las cantidades
- `total_monto`: Suma de todos los subtotales

### Validaciones de Datos
- Campos requeridos validados en registro
- Tipos de datos validados (números, enteros, strings)
- Precios y cantidades deben ser mayores a 0
- Código de compra validado en búsqueda
- Conversión automática de Decimal para compatibilidad JSON

## Seguridad

### Autenticación JWT
- Todos los endpoints requieren token JWT válido en header `Authorization: Bearer <token>`
- Soporte para header `authorization` (minúscula) como fallback
- Validación de expiración y firma del token
- Extracción automática de información del usuario desde payload JWT

### Multi-tenancy
- Aislamiento completo de datos por `tenant_id`
- Todas las operaciones filtradas automáticamente por tenant
- Usuarios solo pueden ver sus propias compras

### Filtros de Seguridad
- Usuarios solo pueden acceder a sus propias compras
- Validación de pertenencia en búsqueda por código
- Estadísticas calculadas solo con compras del usuario autenticado

### CORS y Headers
- CORS habilitado para todos los orígenes (`*`)
- Headers permitidos: `Content-Type`, `X-Amz-Date`, `Authorization`, `X-Api-Key`, `X-Amz-Security-Token`
- Métodos permitidos: `GET`, `POST`, `OPTIONS`

## Códigos de Estado HTTP

- **200**: Operación exitosa (GET)
- **201**: Compra registrada exitosamente (POST)
- **400**: Datos inválidos, faltantes o formato incorrecto
- **401**: Token inválido, expirado o faltante
- **404**: Compra no encontrada
- **500**: Error interno del servidor

## Generación de Códigos

Los códigos de compra se generan automáticamente con el formato:
```
COM-{timestamp}-{random_8_chars}
```

Ejemplo: `COM-1718123456-A7B9C2D4`

## Manejo de Errores

### Errores Comunes
- **Token JWT**: Validación de formato, expiración y firma
- **JSON malformado**: Validación de sintaxis en request body
- **Campos faltantes**: Validación de campos requeridos en productos
- **Tipos de datos**: Validación de números, enteros, strings
- **Lógica de negocio**: Precios y cantidades deben ser positivos
- **Paginación**: Validación de parámetros lastKey

### Logs
- Todos los errores se registran en CloudWatch Logs
- Información de debug disponible para troubleshooting
- Separación de logs por función Lambda

## DynamoDB Streams

El microservicio tiene habilitado DynamoDB Streams con vista `NEW_AND_OLD_IMAGES` para:
- Capturar cambios en tiempo real
- Integración con Lambda de ingesta para ciencia de datos
- Envío de datos a S3 en formato CSV/JSON
- Análisis con Athena y Glue