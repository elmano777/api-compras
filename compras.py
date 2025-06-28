import json
import boto3
import jwt
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal

# Clientes AWS
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
jwt_secret = os.environ['JWT_SECRET']
table = dynamodb.Table(table_name)

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
        'body': json.dumps(body, default=str, ensure_ascii=False)
    }

def extract_user_from_token(event):
    """Extrae información del usuario desde el token JWT"""
    try:
        auth_header = event.get('headers', {}).get('Authorization') or event.get('headers', {}).get('authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None, 'Token requerido'
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, 'Token expirado'
        except jwt.InvalidTokenError:
            return None, 'Token inválido'
            
    except Exception as e:
        print(f"Error extrayendo usuario del token: {str(e)}")
        return None, 'Error procesando token'

def generar_codigo_compra():
    """Genera un código único para la compra"""
    timestamp = int(datetime.now().timestamp())
    random_part = str(uuid.uuid4()).replace('-', '')[:8].upper()
    return f"COM-{timestamp}-{random_part}"

def decimal_to_float(obj):
    """Convierte Decimal a float para serialización JSON"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_float(item) for item in obj]
    return obj

def registrar_compra(event, context):
    """Función para registrar una nueva compra"""
    try:
        # Validar token y extraer usuario
        usuario, error = extract_user_from_token(event)
        if error:
            return lambda_response(401, {'error': error})
        
        # Parsear body
        body = event.get('body')
        if isinstance(body, str):
            body = json.loads(body)
        
        # Validar campos requeridos
        if 'productos' not in body or not body['productos']:
            return lambda_response(400, {'error': 'Lista de productos requerida'})
        
        productos = body['productos']
        
        # Validar estructura de productos
        for i, producto in enumerate(productos):
            required_fields = ['codigo', 'nombre', 'precio', 'cantidad']
            for field in required_fields:
                if field not in producto or producto[field] is None:
                    return lambda_response(400, {
                        'error': f'Campo requerido en producto {i+1}: {field}'
                    })
            
            # Validar tipos de datos
            try:
                if not isinstance(producto['cantidad'], int) or producto['cantidad'] <= 0:
                    return lambda_response(400, {
                        'error': f'Cantidad debe ser un número entero mayor a 0 en producto {i+1}'
                    })
                
                precio = float(producto['precio'])
                if precio <= 0:
                    return lambda_response(400, {
                        'error': f'Precio debe ser mayor a 0 en producto {i+1}'
                    })
                
                # Convertir a Decimal para DynamoDB
                producto['precio'] = Decimal(str(precio))
                producto['subtotal'] = Decimal(str(precio * producto['cantidad']))
                
            except (ValueError, TypeError):
                return lambda_response(400, {
                    'error': f'Precio inválido en producto {i+1}'
                })
        
        # Calcular totales
        total_productos = sum(p['cantidad'] for p in productos)
        total_monto = sum(p['subtotal'] for p in productos)
        
        # Generar código de compra
        codigo_compra = generar_codigo_compra()
        
        # Crear item de compra
        compra_item = {
            'tenant_id': usuario['tenant_id'],
            'codigo_compra': codigo_compra,
            'email_usuario': usuario['email'],
            'nombre_usuario': usuario['nombre'],
            'productos': productos,
            'total_productos': total_productos,
            'total_monto': total_monto,
            'fecha_compra': datetime.now().isoformat(),
            'estado': 'completada',
            'metodo_pago': body.get('metodo_pago', 'online'),
            'direccion_entrega': body.get('direccion_entrega', ''),
            'observaciones': body.get('observaciones', '')
        }
        
        # Guardar en DynamoDB
        table.put_item(Item=compra_item)
        
        # Preparar respuesta (convertir Decimals a float)
        compra_respuesta = decimal_to_float(compra_item)
        
        return lambda_response(201, {
            'message': 'Compra registrada exitosamente',
            'compra': compra_respuesta
        })
        
    except json.JSONDecodeError:
        return lambda_response(400, {'error': 'JSON inválido'})
    except Exception as e:
        print(f"Error registrando compra: {str(e)}")
        return lambda_response(500, {'error': 'Error interno del servidor'})

def listar_compras(event, context):
    """
    Lista las compras con soporte para limit, offset y filtros
    """
    try:
        # Obtener parámetros de query
        query_params = event.get('queryStringParameters') or {}
        
        # Parámetros de paginación
        limit = int(query_params.get('limit', 10))  # Default 10 items
        last_key = query_params.get('lastKey')  # Para paginación
        
        # Parámetros de filtro (opcionales)
        tenant_id = query_params.get('tenant_id')
        fecha_desde = query_params.get('fecha_desde')
        fecha_hasta = query_params.get('fecha_hasta')
        
        # CORRECCIÓN: Usar el limit directamente en el scan
        scan_params = {
            'Limit': limit  # ← AQUÍ ESTABA EL PROBLEMA: era limit * 10
        }
        
        # Si hay lastKey para paginación
        if last_key:
            try:
                import base64
                decoded_key = json.loads(base64.b64decode(last_key).decode('utf-8'))
                scan_params['ExclusiveStartKey'] = decoded_key
            except:
                pass
        
        # Si hay filtros, necesitamos usar FilterExpression de DynamoDB
        filter_expressions = []
        expression_values = {}
        
        if tenant_id:
            filter_expressions.append('tenant_id = :tenant_id')
            expression_values[':tenant_id'] = tenant_id
        
        if fecha_desde:
            filter_expressions.append('fecha_compra >= :fecha_desde')
            expression_values[':fecha_desde'] = fecha_desde
            
        if fecha_hasta:
            filter_expressions.append('fecha_compra <= :fecha_hasta')
            expression_values[':fecha_hasta'] = fecha_hasta
        
        # Aplicar filtros si existen
        if filter_expressions:
            scan_params['FilterExpression'] = ' AND '.join(filter_expressions)
            scan_params['ExpressionAttributeValues'] = expression_values
        
        # Realizar el scan
        response = table.scan(**scan_params)
        
        # Procesar resultados
        items = response.get('Items', [])
        
        # Convertir Decimal a float para JSON
        items = decimal_to_float(items)
        
        # Preparar respuesta
        result = {
            'compras': items,
            'count': len(items),
            'scannedCount': response.get('ScannedCount', 0)
        }
        
        # Agregar lastKey para paginación si existe
        if 'LastEvaluatedKey' in response:
            import base64
            last_key_encoded = base64.b64encode(
                json.dumps(response['LastEvaluatedKey'], default=str).encode('utf-8')
            ).decode('utf-8')
            result['lastKey'] = last_key_encoded
            result['hasMore'] = True
        else:
            result['hasMore'] = False
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            'body': json.dumps(result, ensure_ascii=False)
        }
        
    except ValueError as e:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Parámetros inválidos',
                'message': str(e)
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        print(f"Error en listar_compras: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Error interno del servidor',
                'message': str(e)
            }, ensure_ascii=False)
        }

def buscar_compra(event, context):
    """Función para buscar una compra específica por código"""
    print('Evento completo:', json.dumps(event, indent=2, default=str))  # Debug
    
    try:
        # Validar token y extraer usuario
        usuario, error = extract_user_from_token(event)
        if error:
            return lambda_response(401, {'error': error})
        
        # CORRECCIÓN: Múltiples formas de obtener el código
        codigo_compra = None
        
        # Opción 1: Desde pathParameters (estructura estándar de API Gateway)
        if event.get('pathParameters') and event['pathParameters'].get('codigo'):
            codigo_compra = event['pathParameters']['codigo']
        
        # Opción 2: Desde path como objeto (ESTE ES TU CASO)
        elif event.get('path') and isinstance(event['path'], dict) and event['path'].get('codigo'):
            codigo_compra = event['path']['codigo']
        
        # Opción 3: Desde queryStringParameters (fallback)
        elif event.get('queryStringParameters') and event['queryStringParameters'].get('codigo'):
            codigo_compra = event['queryStringParameters']['codigo']
        
        # Opción 4: Desde resource path parsing (backup)
        elif event.get('resource'):
            import re
            matches = re.search(r'/compras/buscar/([^/]+)', event['resource'])
            if matches:
                codigo_compra = matches.group(1)
        
        # Opción 5: Desde requestPath parsing
        elif event.get('requestPath'):
            import re
            matches = re.search(r'/compras/buscar/([^/]+)', event['requestPath'])
            if matches:
                codigo_compra = matches.group(1)
        
        # Opción 6: Desde requestContext (otro fallback)
        elif event.get('requestContext') and event['requestContext'].get('resourcePath'):
            import re
            matches = re.search(r'/compras/buscar/([^/]+)', event['requestContext']['resourcePath'])
            if matches:
                codigo_compra = matches.group(1)
        
        # Opción 7: Parsing manual del path como string
        elif event.get('path') and isinstance(event['path'], str):
            import re
            matches = re.search(r'/compras/buscar/([^/]+)', str(event['path']))
            if matches:
                codigo_compra = matches.group(1)
        
        print(f'Código extraído: {codigo_compra}')  # Debug
        
        if not codigo_compra:
            print('PathParameters:', event.get('pathParameters'))
            print('Path:', event.get('path'))
            print('Resource:', event.get('resource'))
            print('RequestPath:', event.get('requestPath'))
            print('RequestContext:', event.get('requestContext'))
            return lambda_response(400, {
                'error': 'Código de compra requerido',
                'debug': {
                    'pathParameters': event.get('pathParameters'),
                    'path': str(event.get('path')),
                    'resource': event.get('resource'),
                    'requestPath': event.get('requestPath')
                }
            })
        
        # Buscar compra
        try:
            print(f'Buscando compra con tenant_id: {usuario["tenant_id"]}, codigo_compra: {codigo_compra}')  # Debug
            
            response = table.get_item(
                Key={
                    'tenant_id': usuario['tenant_id'],
                    'codigo_compra': codigo_compra
                }
            )
            
            if 'Item' not in response:
                return lambda_response(404, {'error': 'Compra no encontrada'})
            
            compra = response['Item']
            
            # Verificar que la compra pertenece al usuario
            if compra.get('email_usuario') != usuario['email']:
                return lambda_response(404, {'error': 'Compra no encontrada'})
            
            # Convertir Decimals y responder
            compra_respuesta = decimal_to_float(compra)
            
            return lambda_response(200, {
                'compra': compra_respuesta
            })
            
        except Exception as e:
            print(f"Error buscando compra en DynamoDB: {str(e)}")
            return lambda_response(500, {'error': 'Error interno del servidor'})
        
    except Exception as e:
        print(f"Error en buscar_compra: {str(e)}")
        return lambda_response(500, {'error': 'Error interno del servidor'})

def obtener_estadisticas_compras(event, context):
    """Función para obtener estadísticas de compras del usuario"""
    try:
        # Validar token y extraer usuario
        usuario, error = extract_user_from_token(event)
        if error:
            return lambda_response(401, {'error': error})
        
        # Consultar todas las compras del usuario
        response = table.query(
            KeyConditionExpression='tenant_id = :tenant_id',
            FilterExpression='email_usuario = :email',
            ExpressionAttributeValues={
                ':tenant_id': usuario['tenant_id'],
                ':email': usuario['email']
            }
        )
        
        compras = response.get('Items', [])
        
        if not compras:
            return lambda_response(200, {
                'total_compras': 0,
                'total_gastado': 0,
                'total_productos_comprados': 0,
                'promedio_por_compra': 0,
                'primera_compra': None,
                'ultima_compra': None
            })
        
        # Calcular estadísticas
        total_compras = len(compras)
        total_gastado = sum(float(compra.get('total_monto', 0)) for compra in compras)
        total_productos = sum(compra.get('total_productos', 0) for compra in compras)
        promedio_por_compra = total_gastado / total_compras if total_compras > 0 else 0
        
        # Ordenar por fecha para obtener primera y última compra
        compras_ordenadas = sorted(compras, key=lambda x: x.get('fecha_compra', ''))
        primera_compra = compras_ordenadas[0].get('fecha_compra') if compras_ordenadas else None
        ultima_compra = compras_ordenadas[-1].get('fecha_compra') if compras_ordenadas else None
        
        return lambda_response(200, {
            'total_compras': total_compras,
            'total_gastado': round(total_gastado, 2),
            'total_productos_comprados': total_productos,
            'promedio_por_compra': round(promedio_por_compra, 2),
            'primera_compra': primera_compra,
            'ultima_compra': ultima_compra
        })
        
    except Exception as e:
        print(f"Error obteniendo estadísticas: {str(e)}")
        return lambda_response(500, {'error': 'Error interno del servidor'})