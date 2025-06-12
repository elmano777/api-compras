# API Compras - Microservicio Multi-tenant (Medicinas)

Este microservicio maneja el registro y gestión de compras de productos farmacéuticos con soporte multi-tenant usando AWS Lambda, DynamoDB y autenticación JWT.

## Características

- ✅ Multi-tenancy (soporte para múltiples inquilinos)
- ✅ Serverless con AWS Lambda (Python 3.9)
- ✅ Protección con tokens JWT
- ✅ Registro completo de compras con múltiples productos
- ✅ Listado de compras del usuario con paginación
- ✅ Detalle de compras individuales
- ✅ Estadísticas de compras del usuario
- ✅ DynamoDB Streams habilitado para CDC
- ✅ CORS habilitado
- ✅ Despliegue automatizado con Serverless Framework

## Endpoints

### 1. Registrar Compra
- **URL**: `POST /compras`
- **Headers**: `Authorization: Bearer <token>`
- **Body**:
```json
{
  "productos": [
    {
      "codigo": "MED-ABC123",
      "nombre": "Paracetamol 500mg",
      "descripcion": "Analgésico y antipirético",
      "categoria": "Analgésicos",
      "laboratorio": "Bayer",
      "precio": 15.50,
      "cantidad": 2
    },
    {
      "codigo": "MED-DEF456",
      "nombre": "Ibuprofeno 400mg",
      "descripcion": "Antiinflamatorio",
      "categoria": "Antiinflamatorios",
      "laboratorio": "Pfizer",
      "precio": 12.00,
      "cantidad": 1
    }
  ],
  "metodo_pago": "TARJETA",
  "direccion_envio": "Av. Lima 123, Breña",
  "telefono_contacto": "987654321",
  "notas": "Entregar en horario de oficina",
  "moneda": "PEN"
}
```
- **Respuesta**:
```json
{
  "message": "Compra registrada exitosamente",
  "compra": {
    "codigo_compra": "COMP-1234567890-ABC12345",
    "total_compra": 43.00,
    "total_productos": 2,
    "total_cantidad": 3,
    "estado": "COMPLETADA",
    "fecha_compra": "2025-06-12T10:30:00Z"
  }
}
```

### 2. Listar Compras del Usuario
- **URL**: `GET /compras`
- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**:
  - `limit`: Número de compras por página (default: 20)
  - `lastKey`: Clave para paginación
- **Respuesta**:
```json
{
  "compras": [...],
  "count": 5,
  "lastEvaluatedKey": "encoded_key_for_next_page"
}
```

### 3. Obtener Detalle de Compra
- **URL**: `GET /compras/{codigo_compra}`
- **Headers**: `Authorization: Bearer <token>`
- **Ejemplo**: `GET /compras/COMP-1234567890-ABC12345`

### 4. Estadísticas de Compras
- **URL**: `GET /compras/estadisticas`
- **Headers**: `Authorization: Bearer <token>`
- **Respuesta**:
```json
{
  "total_compras": 15,
  "total_gastado": 450.75,
  "total_productos_comprados": 42,
  "compra_promedio": 30.05,
  "ultima_compra": {
    "codigo": "COMP-1234567890-ABC12345",
    "fecha": "2025-06-12T10:30:00Z",
    "total": 43.00
  },
  "categorias_favoritas": [
    {"categoria": "Analgésicos", "cantidad": 15},
    {"categoria": "Vitaminas", "cantidad": 12}
  ],
  "laboratorios_favoritos": [
    {"laboratorio": "Bayer", "cantidad": 18},
    {"laboratorio": "Pfizer", "cantidad": 10}
  ]
}
```

## Estructura de Datos - Compras

### Campos de la Compra
- `tenant_id`: Identificador del inquilino
- `codigo_compra`: Código único de la compra (auto-generado)
- `usuario_id`: ID del usuario que realizó la compra
- `productos`: Array de productos comprados con detalles
- `total_productos`: Cantidad de tipos de productos diferentes
- `total_cantidad`: Cantidad total de productos (suma de cantidades)
- `total_compra`: Monto total de la compra
- `moneda`: Moneda de la transacción (default: PEN)
- `estado`: Estado de la compra (COMPLETADA, PENDIENTE, CANCELADA)
- `metodo_pago`: Método de pago utilizado
- `direccion_envio`: Dirección de entrega
- `telefono_contacto`: Teléfono de contacto
- `notas`: Notas adicionales de la compra
- `fecha_compra`: Timestamp de la compra
- `fecha_creacion`: Timestamp de creación del registro
- `fecha_actualizacion`: Timestamp de última actualización
- `activo`: Estado del registro

### Estructura de Producto en Compra
```json
{
  "codigo": "MED-ABC123",
  "nombre": "Paracetamol 500mg",
  "descripcion": "Analgésico y antipirético",
  "categoria": "Analgésicos",
  "laboratorio": "Bayer",
  "precio": 15.50,
  "cantidad": 2,
  "subtotal": 31.00
}
```

## Instalación y Despliegue

### Prerrequisitos
- Python 3.9+
- AWS CLI configurado
- Serverless Framework
- pip (Python package manager)

### Comandos de Despliegue

```bash
# Instalar dependencias Python
pip install -r requirements.txt

# Instalar Serverless (si no está instalado)
npm install -g serverless

# Desplegar a desarrollo
npm run deploy-dev

# Desplegar a testing
npm run deploy-test

# Desplegar a producción
npm run deploy-prod

# Ver información del despliegue
npm run info

# Ver logs de una función específica
npm run logs registrar-compra
```

## Estructura del Proyecto

```
api-compras/
├── main.py             # Funciones Lambda
├── serverless.yml      # Configuración Serverless
├── requirements.txt    # Dependencias Python
├── package.json       # Scripts de despliegue
└── README.md          # Documentación
```

## Variables de Entorno

- `TABLE_NAME`: Nombre de la tabla DynamoDB (auto-generado por stage)
- `JWT_SECRET`: Secreto para validar tokens JWT (debe coincidir con api-usuarios)

## Tabla DynamoDB

**Nombre**: `{stage}-t_compras`

**Schema**:
- **Partition Key**: `tenant_id` (String)
- **Sort Key**: `codigo_compra` (String)

**Características**:
- DynamoDB Streams habilitado (NEW_AND_OLD_IMAGES)
- Global Secondary Indexes:
  - `usuario_id-fecha_compra-index`: Para consultas por usuario
  - `tenant_id-fecha_compra-index`: Para consultas por tenant
- Billing Mode: PAY_PER_REQUEST

## Seguridad

- Todos los endpoints requieren token JWT válido
- Validación de tenant_id desde el token
- Aislamiento de datos por tenant y usuario
- Los usuarios solo pueden ver sus propias compras
- CORS configurado para frontend

## Ejemplos de Uso

### Registrar una Compra
```bash
curl -X POST https://tu-api-url/compras \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "productos": [
      {
        "codigo": "MED-ABC123",
        "nombre": "Paracetamol 500mg",
        "descripcion": "Analgésico",
        "categoria": "Analgésicos",
        "laboratorio": "Bayer",
        "precio": 15.50,
        "cantidad": 2
      }
    ],
    "metodo_pago": "EFECTIVO",
    "direccion_envio": "Av. Lima 123",
    "telefono_contacto": "987654321"
  }'
```

### Listar Compras
```bash
curl -X GET "https://tu-api-url/compras?limit=10" \
  -H "Authorization: Bearer <token>"
```

### Obtener Detalle de Compra
```bash
curl -X GET https://tu-api-url/compras/COMP-1234567890-ABC12345 \
  -H "Authorization: Bearer <token>"
```

### Obtener Estadísticas
```bash
curl -X GET https://tu-api-url/compras/estadisticas \
  -H "Authorization: Bearer <token>"
```

## Integración con DynamoDB Streams

La tabla tiene DynamoDB Streams habilitado para:
- Sincronización con S3 para análisis de datos
- Generación de archivos CSV/JSON para Athena
- Auditoría de transacciones
- Integración con sistemas de facturación

## Métodos de Pago Soportados

- EFECTIVO
- TARJETA
- TRANSFERENCIA
- YAPE
- PLIN
- PAYPAL

## Estados de Compra

- **COMPLETADA**: Compra exitosa y confirmada
- **PENDIENTE**: Compra registrada pero pendiente de confirmación
- **CANCELADA**: Compra cancelada por el usuario o sistema

## Validaciones Implementadas

- Validación de token JWT en todos los endpoints
- Verificación de campos requeridos en productos
- Validación de tipos de datos (precios, cantidades)
- Cálculo automático de subtotales y total
- Verificación de permisos por usuario y tenant
- Validación de formato de códigos de producto

## Consideraciones para Producción

- Implementar validación de stock en tiempo real
- Integrar con sistema de pagos real
- Añadir notificaciones por email/SMS
- Implementar sistema de reembolsos
- Añadir seguimiento de envíos
- Implementar límites de compra por usuario