import json
import boto3
import jwt
import os
from datetime import datetime, timezone
from decimal import Decimal
import uuid
from botocore.exceptions import ClientError

# Cliente DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)
jwt_secret = os.environ['JWT_SECRET']

class DecimalEncoder(json.JSONEncoder):
    """Encoder personalizado para manejar Decimal de DynamoDB"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_response(status_code, body):
    """Función helper para respuestas consistentes"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }

def validar_token(auth_header):
    """Función para validar token JWT"""
    try:
        if not auth_header or not auth_header.startswith('Bearer '):
            raise Exception('Token no proporcionado')
        
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        return payload
    except Exception as e:
        raise Exception('Token inválido o expirado')

def generar_codigo_compra():
    """Función para generar código único de compra"""
    timestamp = str(int(datetime.now().timestamp()))
    unique_id = str(uuid.uuid4())[:8]
    return f"COMP-{timestamp}-{unique_id}".upper()

def registrar_compra(event, context):
    """REGISTRAR COMPRA"""
    try:
        # Validar token
        auth_header = event.get('headers', {}).get('Authorization') or event.get('headers', {}).get('authorization')
        usuario = validar_token(auth_header)
        
        tenant_id = usuario['tenant_id']
        usuario_id = usuario['usuario_id']
        body = json.loads(event['body'])
        
        # Validar campos requeridos
        if not body.get('productos') or not isinstance(body['productos'], list):
            return lambda_response(400, {'error': 'Lista de productos requerida'})
        
        if not body['productos']:
            return lambda_response(400, {'error': 'La compra debe tener al menos un producto'})
        
        # Validar estructura de productos
        total_compra = Decimal('0')
        productos_procesados = []
        
        for producto in body['productos']:
            if not all(key in producto for key in ['codigo', 'nombre', 'precio', 'cantidad']):
                return lambda_response(400, {'error': 'Cada producto debe tener: codigo, nombre, precio, cantidad'})
            
            cantidad = int(producto['cantidad'])
            precio = Decimal(str(producto['precio']))
            subtotal = precio * cantidad
            
            producto_procesado = {
                'codigo': producto['codigo'],
                'nombre': producto['nombre'],
                'precio': precio,
                'cantidad': cantidad,
                'subtotal': subtotal,
                'categoria': producto.get('categoria', ''),
                'laboratorio': producto.get('laboratorio', ''),
                'descripcion': producto.get('descripcion', '')
            }
            
            productos_procesados.append(producto_procesado)
            total_compra += subtotal
        
        codigo_compra = generar_codigo_compra()
        fecha_actual = datetime.now(timezone.utc).isoformat()
        
        # Crear objeto compra
        compra = {
            'tenant_id': tenant_id,
            'codigo_compra': codigo_compra,
            'usuario_id': usuario_id,
            'productos': productos_procesados,
            'total_productos': len(productos_procesados),
            'total_cantidad': sum(p['cantidad'] for p in productos_procesados),
            'total_compra': total_compra,
            'moneda': body.get('moneda', 'PEN'),
            'estado': 'COMPLETADA',
            'metodo_pago': body.get('metodo_pago', 'EFECTIVO'),
            'direccion_envio': body.get('direccion_envio', ''),
            'telefono_contacto': body.get('telefono_contacto', ''),
            'notas': body.get('notas', ''),
            'fecha_compra': fecha_actual,
            'fecha_creacion': fecha_actual,
            'fecha_actualizacion': fecha_actual,
            'activo': True
        }
        
        # Guardar en DynamoDB
        table.put_item(Item=compra)
        
        return lambda_response(201, {
            'message': 'Compra registrada exitosamente',
            'compra': compra
        })
        
    except ValueError as e:
        return lambda_response(400, {'error': f'Error en formato de datos: {str(e)}'})
    except Exception as e:
        print(f'Error registrando compra: {str(e)}')
        if 'Token inválido' in str(e):
            return lambda_response(401, {'error': str(e)})
        return lambda_response(500, {'error': 'Error interno del servidor'})

def listar_compras_usuario(event, context):
    """LISTAR TODAS LAS COMPRAS DE UN USUARIO"""
    try:
        # Validar token
        auth_header = event.get('headers', {}).get('Authorization') or event.get('headers', {}).get('authorization')
        usuario = validar_token(auth_header)
        
        tenant_id = usuario['tenant_id']
        usuario_id = usuario['usuario_id']
        
        # Parámetros de paginación
        limit = int(event.get('queryStringParameters', {}).get('limit', 20))
        last_key = event.get('queryStringParameters', {}).get('lastKey')
        
        # Construir parámetros de consulta
        scan_kwargs = {
            'FilterExpression': boto3.dynamodb.conditions.Attr('tenant_id').eq(tenant_id) & 
                              boto3.dynamodb.conditions.Attr('usuario_id').eq(usuario_id) &
                              boto3.dynamodb.conditions.Attr('activo').eq(True),
            'Limit': limit
        }
        
        if last_key:
            try:
                last_evaluated_key = json.loads(last_key)
                scan_kwargs['ExclusiveStartKey'] = last_evaluated_key
            except:
                pass
        
        # Ejecutar consulta
        response = table.scan(**scan_kwargs)
        
        # Ordenar por fecha de compra (más reciente primero)
        compras = sorted(response['Items'], key=lambda x: x['fecha_compra'], reverse=True)
        
        # Preparar respuesta
        resultado = {
            'compras': compras,
            'count': len(compras),
            'lastEvaluatedKey': json.dumps(response.get('LastEvaluatedKey')) if response.get('LastEvaluatedKey') else None
        }
        
        return lambda_response(200, resultado)
        
    except Exception as e:
        print(f'Error listando compras: {str(e)}')
        if 'Token inválido' in str(e):
            return lambda_response(401, {'error': str(e)})
        return lambda_response(500, {'error': 'Error interno del servidor'})

def obtener_compra(event, context):
    """OBTENER DETALLE DE UNA COMPRA ESPECÍFICA"""
    try:
        # Validar token
        auth_header = event.get('headers', {}).get('Authorization') or event.get('headers', {}).get('authorization')
        usuario = validar_token(auth_header)
        
        tenant_id = usuario['tenant_id']
        usuario_id = usuario['usuario_id']
        codigo_compra = event.get('pathParameters', {}).get('codigo')
        
        if not codigo_compra:
            return lambda_response(400, {'error': 'Código de compra requerido'})
        
        # Buscar compra
        try:
            response = table.get_item(
                Key={
                    'tenant_id': tenant_id,
                    'codigo_compra': codigo_compra
                }
            )
            
            if 'Item' not in response:
                return lambda_response(404, {'error': 'Compra no encontrada'})
            
            compra = response['Item']
            
            # Verificar que la compra pertenece al usuario
            if compra['usuario_id'] != usuario_id:
                return lambda_response(403, {'error': 'No tiene permisos para ver esta compra'})
            
            if not compra.get('activo', True):
                return lambda_response(404, {'error': 'Compra no disponible'})
            
            return lambda_response(200, {'compra': compra})
            
        except ClientError as e:
            print(f'Error de DynamoDB: {str(e)}')
            return lambda_response(500, {'error': 'Error accediendo a la base de datos'})
        
    except Exception as e:
        print(f'Error obteniendo compra: {str(e)}')
        if 'Token inválido' in str(e):
            return lambda_response(401, {'error': str(e)})
        return lambda_response(500, {'error': 'Error interno del servidor'})

def obtener_estadisticas_compras(event, context):
    """OBTENER ESTADÍSTICAS DE COMPRAS DEL USUARIO"""
    try:
        # Validar token
        auth_header = event.get('headers', {}).get('Authorization') or event.get('headers', {}).get('authorization')
        usuario = validar_token(auth_header)
        
        tenant_id = usuario['tenant_id']
        usuario_id = usuario['usuario_id']
        
        # Obtener todas las compras del usuario
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('tenant_id').eq(tenant_id) & 
                           boto3.dynamodb.conditions.Attr('usuario_id').eq(usuario_id) &
                           boto3.dynamodb.conditions.Attr('activo').eq(True)
        )
        
        compras = response['Items']
        
        if not compras:
            return lambda_response(200, {
                'total_compras': 0,
                'total_gastado': 0,
                'total_productos_comprados': 0,
                'compra_promedio': 0,
                'ultima_compra': None,
                'categorias_favoritas': [],
                'laboratorios_favoritos': []
            })
        
        # Calcular estadísticas
        total_compras = len(compras)
        total_gastado = sum(float(compra['total_compra']) for compra in compras)
        total_productos = sum(compra['total_cantidad'] for compra in compras)
        compra_promedio = total_gastado / total_compras if total_compras > 0 else 0
        
        # Encontrar última compra
        ultima_compra = max(compras, key=lambda x: x['fecha_compra'])
        
        # Analizar categorías y laboratorios favoritos
        categorias = {}
        laboratorios = {}
        
        for compra in compras:
            for producto in compra['productos']:
                categoria = producto.get('categoria', 'Sin categoría')
                laboratorio = producto.get('laboratorio', 'Sin laboratorio')
                
                categorias[categoria] = categorias.get(categoria, 0) + producto['cantidad']
                laboratorios[laboratorio] = laboratorios.get(laboratorio, 0) + producto['cantidad']
        
        # Top 5 categorías y laboratorios
        categorias_favoritas = sorted(categorias.items(), key=lambda x: x[1], reverse=True)[:5]
        laboratorios_favoritos = sorted(laboratorios.items(), key=lambda x: x[1], reverse=True)[:5]
        
        estadisticas = {
            'total_compras': total_compras,
            'total_gastado': round(total_gastado, 2),
            'total_productos_comprados': total_productos,
            'compra_promedio': round(compra_promedio, 2),
            'ultima_compra': {
                'codigo': ultima_compra['codigo_compra'],
                'fecha': ultima_compra['fecha_compra'],
                'total': float(ultima_compra['total_compra'])
            },
            'categorias_favoritas': [{'categoria': cat, 'cantidad': cant} for cat, cant in categorias_favoritas],
            'laboratorios_favoritos': [{'laboratorio': lab, 'cantidad': cant} for lab, cant in laboratorios_favoritos]
        }
        
        return lambda_response(200, estadisticas)
        
    except Exception as e:
        print(f'Error obteniendo estadísticas: {str(e)}')
        if 'Token inválido' in str(e):
            return lambda_response(401, {'error': str(e)})
        return lambda_response(500, {'error': 'Error interno del servidor'})