import json

def serve_swagger_ui(event, context):
    """Sirve la interfaz de Swagger UI"""
    try:
        # Obtener la URL base de la API desde el evento
        headers = event.get('headers', {})
        host = headers.get('Host') or headers.get('host', 'localhost')
        stage = event.get('requestContext', {}).get('stage', 'dev')
        swagger_json_url = f"https://{host}/{stage}/swagger.json"
        
        html = f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Swagger UI - API Compras</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.10.3/swagger-ui.css" />
  <style>
    .swagger-ui .topbar {{ display: none; }}
    .swagger-ui .info {{ margin: 50px 0; }}
    .swagger-ui .info .title {{ color: #3b4151; }}
    .swagger-ui .scheme-container {{ background: #fff; }}
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5.10.3/swagger-ui-bundle.js"></script>
  <script>
    window.onload = function() {{
      const ui = SwaggerUIBundle({{
        url: '{swagger_json_url}',
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIBundle.presets.standalone
        ],
        plugins: [
          SwaggerUIBundle.plugins.DownloadUrl
        ],
        layout: "BaseLayout",
        defaultModelsExpandDepth: 1,
        defaultModelExpandDepth: 1,
        docExpansion: "list",
        operationsSorter: "alpha",
        tagsSorter: "alpha",
        filter: true,
        supportedSubmitMethods: ['get', 'post', 'put', 'delete', 'patch'],
        requestInterceptor: function(request) {{
          const token = localStorage.getItem('authToken');
          if (token) {{
            request.headers['Authorization'] = 'Bearer ' + token;
          }}
          return request;
        }},
        responseInterceptor: function(response) {{
          console.log('Response intercepted:', response);
          return response;
        }},
        onComplete: function() {{
          console.log('Swagger UI loaded successfully');
          
          // Configurar autorización si existe token
          const savedToken = localStorage.getItem('authToken');
          if (savedToken) {{
            ui.preauthorizeApiKey('bearerAuth', 'Bearer ' + savedToken);
          }}
        }},
        onFailure: function(error) {{
          console.error('Error loading Swagger UI:', error);
        }}
      }});
      
      window.ui = ui;
      
      window.setAuthToken = function(token) {{
        if (!token || token.trim() === '') {{
          alert('Por favor ingresa un token válido');
          return;
        }}
        
        localStorage.setItem('authToken', token);
        ui.preauthorizeApiKey('bearerAuth', 'Bearer ' + token);
        
        // Actualizar el campo de entrada
        const tokenInput = document.getElementById('jwtToken');
        if (tokenInput) {{
          tokenInput.value = token;
        }}
        
        alert('Token de autorización establecido correctamente');
      }};
      
      window.clearAuthToken = function() {{
        localStorage.removeItem('authToken');
        
        // Limpiar el campo de entrada
        const tokenInput = document.getElementById('jwtToken');
        if (tokenInput) {{
          tokenInput.value = '';
        }}
        
        // Recargar la página para limpiar la autorización
        location.reload();
      }};
      
      // Agregar la sección de configuración de token después de que se cargue
      setTimeout(function() {{
        const infoDiv = document.querySelector('.info');
        if (infoDiv && !document.getElementById('token-config')) {{
          const savedToken = localStorage.getItem('authToken');
          const tokenDiv = document.createElement('div');
          tokenDiv.id = 'token-config';
          tokenDiv.innerHTML = `
            <div style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 6px; border-left: 4px solid #007bff;">
              <h4 style="margin: 0 0 10px 0; color: #007bff;">🔐 Configuración de Token JWT</h4>
              <p style="margin: 0 0 10px 0; color: #6c757d; font-size: 14px;">
                Para probar los endpoints protegidos, establece tu token JWT:
              </p>
              <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                <input 
                  type="text" 
                  id="jwtToken" 
                  placeholder="Ingresa tu token JWT aquí..." 
                  value="${{savedToken || ''}}"
                  style="flex: 1; min-width: 300px; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;"
                >
                <button 
                  onclick="setAuthToken(document.getElementById('jwtToken').value)" 
                  style="padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; white-space: nowrap;"
                >
                  Establecer Token
                </button>
                <button 
                  onclick="clearAuthToken()" 
                  style="padding: 8px 16px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; white-space: nowrap;"
                >
                  Limpiar
                </button>
              </div>
              <div style="margin-top: 10px; font-size: 12px; color: #6c757d;">
                <strong>Estado:</strong> <span id="token-status">${{savedToken ? 'Token configurado ✅' : 'Sin token configurado ❌'}}</span>
              </div>
            </div>
          `;
          infoDiv.appendChild(tokenDiv);
        }}
      }}, 1500);
    }};
  </script>
</body>
</html>'''
        
        # Formato de respuesta para lambda-proxy
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,OPTIONS',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            },
            'body': html,
            'isBase64Encoded': False
        }
        
        return response
        
    except Exception as e:
        print(f"Error sirviendo Swagger UI: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_response = {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Error interno del servidor',
                'message': str(e)
            }),
            'isBase64Encoded': False
        }
        
        return error_response

def get_swagger_json(event, context):
    """Retorna la especificación OpenAPI/Swagger en formato JSON"""
    try:
        # Obtener la URL base de la API
        headers = event.get('headers', {})
        host = headers.get('Host') or headers.get('host', 'localhost')
        stage = event.get('requestContext', {}).get('stage', 'dev')
        base_url = f"https://{host}/{stage}"
        
        # Especificación OpenAPI 3.0.0 - Corregida y simplificada
        swagger_spec = {
            "openapi": "3.1.0",
            "info": {
                "swagger": "2.0",
                "title": "API Compras - Microservicio Multi-tenant",
                "version": "1.0.0",
                "description": "Microservicio para gestión de compras con soporte multi-tenant usando AWS Lambda y DynamoDB."
            },
            "servers": [
                {
                    "url": base_url,
                    "description": "Servidor de desarrollo"
                }
            ],
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                },
                "schemas": {
                    "Producto": {
                        "type": "object",
                        "required": ["codigo", "nombre", "precio", "cantidad"],
                        "properties": {
                            "codigo": {
                                "type": "string",
                                "description": "Código del producto",
                                "example": "MED-ABC123-DEF456"
                            },
                            "nombre": {
                                "type": "string",
                                "description": "Nombre del producto",
                                "example": "Paracetamol 500mg"
                            },
                            "precio": {
                                "type": "number",
                                "format": "float",
                                "description": "Precio unitario",
                                "example": 12.50
                            },
                            "cantidad": {
                                "type": "integer",
                                "description": "Cantidad comprada",
                                "example": 2
                            }
                        }
                    },
                    "CompraRequest": {
                        "type": "object",
                        "required": ["productos"],
                        "properties": {
                            "productos": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/components/schemas/Producto"
                                }
                            },
                            "metodo_pago": {
                                "type": "string",
                                "description": "Método de pago utilizado",
                                "example": "tarjeta"
                            },
                            "direccion_entrega": {
                                "type": "string",
                                "description": "Dirección de entrega",
                                "example": "Av. Siempre Viva 123, Lima"
                            },
                            "observaciones": {
                                "type": "string",
                                "description": "Observaciones adicionales",
                                "example": "Entregar en horario de oficina"
                            }
                        }
                    },
                    "Compra": {
                        "type": "object",
                        "properties": {
                            "tenant_id": {
                                "type": "string",
                                "description": "ID del tenant"
                            },
                            "codigo_compra": {
                                "type": "string",
                                "description": "Código único de la compra",
                                "example": "COM-1718123456-A7B9C2D4"
                            },
                            "email_usuario": {
                                "type": "string",
                                "format": "email",
                                "description": "Email del usuario"
                            },
                            "nombre_usuario": {
                                "type": "string",
                                "description": "Nombre del usuario"
                            },
                            "productos": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/components/schemas/Producto"
                                }
                            },
                            "total_productos": {
                                "type": "integer",
                                "description": "Total de productos comprados"
                            },
                            "total_monto": {
                                "type": "number",
                                "format": "float",
                                "description": "Monto total de la compra"
                            },
                            "fecha_compra": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Fecha y hora de la compra"
                            },
                            "estado": {
                                "type": "string",
                                "enum": ["completada", "pendiente", "cancelada"],
                                "description": "Estado actual de la compra"
                            },
                            "metodo_pago": {
                                "type": "string",
                                "description": "Método de pago utilizado"
                            },
                            "direccion_entrega": {
                                "type": "string",
                                "description": "Dirección de entrega"
                            },
                            "observaciones": {
                                "type": "string",
                                "description": "Observaciones adicionales"
                            }
                        }
                    },
                    "CompraResponse": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "example": "Compra registrada exitosamente"
                            },
                            "compra": {
                                "$ref": "#/components/schemas/Compra"
                            }
                        }
                    },
                    "ListaComprasResponse": {
                        "type": "object",
                        "properties": {
                            "compras": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/components/schemas/Compra"
                                }
                            },
                            "count": {
                                "type": "integer",
                                "description": "Número de compras devueltas"
                            },
                            "hasMore": {
                                "type": "boolean",
                                "description": "Indica si hay más resultados"
                            }
                        }
                    },
                    "EstadisticasResponse": {
                        "type": "object",
                        "properties": {
                            "total_compras": {
                                "type": "integer",
                                "description": "Total de compras realizadas"
                            },
                            "total_gastado": {
                                "type": "number",
                                "format": "float",
                                "description": "Total gastado en compras"
                            },
                            "total_productos_comprados": {
                                "type": "integer",
                                "description": "Total de productos comprados"
                            },
                            "promedio_por_compra": {
                                "type": "number",
                                "format": "float",
                                "description": "Promedio gastado por compra"
                            },
                            "primera_compra": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Fecha de la primera compra"
                            },
                            "ultima_compra": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Fecha de la última compra"
                            }
                        }
                    },
                    "ErrorResponse": {
                        "type": "object",
                        "properties": {
                            "error": {
                                "type": "string",
                                "description": "Mensaje de error"
                            },
                            "message": {
                                "type": "string",
                                "description": "Descripción detallada del error"
                            }
                        }
                    }
                }
            },
            "security": [
                {
                    "bearerAuth": []
                }
            ],
            "paths": {
                "/compras/registrar": {
                    "post": {
                        "summary": "Registrar nueva compra",
                        "description": "Registra una nueva compra con múltiples productos",
                        "tags": ["Compras"],
                        "security": [{"bearerAuth": []}],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/CompraRequest"
                                    },
                                    "example": {
                                        "productos": [
                                            {
                                                "codigo": "MED-ABC123-DEF456",
                                                "nombre": "Paracetamol 500mg",
                                                "precio": 12.50,
                                                "cantidad": 2
                                            }
                                        ],
                                        "metodo_pago": "tarjeta",
                                        "direccion_entrega": "Av. Siempre Viva 123, Lima",
                                        "observaciones": "Entregar en horario de oficina"
                                    }
                                }
                            }
                        },
                        "responses": {
                            "201": {
                                "description": "Compra registrada exitosamente",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/CompraResponse"
                                        }
                                    }
                                }
                            },
                            "400": {
                                "description": "Datos inválidos",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/ErrorResponse"
                                        }
                                    }
                                }
                            },
                            "401": {
                                "description": "Token inválido o faltante",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/ErrorResponse"
                                        }
                                    }
                                }
                            },
                            "500": {
                                "description": "Error interno del servidor",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/ErrorResponse"
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/compras/listar": {
                    "get": {
                        "summary": "Listar compras del usuario",
                        "description": "Obtiene lista paginada de compras del usuario autenticado",
                        "tags": ["Compras"],
                        "security": [{"bearerAuth": []}],
                        "parameters": [
                            {
                                "name": "limit",
                                "in": "query",
                                "description": "Número de compras por página",
                                "required": False,
                                "schema": {
                                    "type": "integer",
                                    "default": 10
                                }
                            },
                            {
                                "name": "tenant_id",
                                "in": "query",
                                "description": "ID del tenant",
                                "required": False,
                                "schema": {
                                    "type": "string"
                                }
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Lista de compras obtenida exitosamente",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/ListaComprasResponse"
                                        }
                                    }
                                }
                            },
                            "401": {
                                "description": "Token inválido o faltante",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/ErrorResponse"
                                        }
                                    }
                                }
                            },
                            "500": {
                                "description": "Error interno del servidor",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/ErrorResponse"
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/compras/buscar/{codigo}": {
                    "get": {
                        "summary": "Buscar compra por código",
                        "description": "Busca una compra específica por su código único",
                        "tags": ["Compras"],
                        "security": [{"bearerAuth": []}],
                        "parameters": [
                            {
                                "name": "codigo",
                                "in": "path",
                                "description": "Código único de la compra",
                                "required": True,
                                "schema": {
                                    "type": "string",
                                    "example": "COM-1718123456-A7B9C2D4"
                                }
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Compra encontrada",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "compra": {
                                                    "$ref": "#/components/schemas/Compra"
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            "404": {
                                "description": "Compra no encontrada",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/ErrorResponse"
                                        }
                                    }
                                }
                            },
                            "401": {
                                "description": "Token inválido o faltante",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/ErrorResponse"
                                        }
                                    }
                                }
                            },
                            "500": {
                                "description": "Error interno del servidor",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/ErrorResponse"
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/compras/estadisticas": {
                    "get": {
                        "summary": "Obtener estadísticas de compras",
                        "description": "Obtiene estadísticas completas de compras del usuario autenticado",
                        "tags": ["Compras"],
                        "security": [{"bearerAuth": []}],
                        "responses": {
                            "200": {
                                "description": "Estadísticas obtenidas exitosamente",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/EstadisticasResponse"
                                        }
                                    }
                                }
                            },
                            "401": {
                                "description": "Token inválido o faltante",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/ErrorResponse"
                                        }
                                    }
                                }
                            },
                            "500": {
                                "description": "Error interno del servidor",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/ErrorResponse"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "tags": [
                {
                    "name": "Compras",
                    "description": "Operaciones relacionadas con la gestión de compras"
                }
            ]
        }
        
        # Convertir a JSON con manejo de errores
        try:
            json_response = json.dumps(swagger_spec, ensure_ascii=False, separators=(',', ':'))
        except Exception as json_error:
            print(f"Error al convertir a JSON: {str(json_error)}")
            # Fallback a especificación mínima
            minimal_spec = {
                "openapi": "3.0.0",
                "info": {
                    "title": "API Compras",
                    "version": "1.0.0"
                },
                "paths": {}
            }
            json_response = json.dumps(minimal_spec, ensure_ascii=False)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json; charset=utf-8',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            'body': json_response,
            'isBase64Encoded': False
        }
        
    except Exception as e:
        print(f"Error generando Swagger JSON: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Respuesta de error mínima pero válida
        error_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "API Compras - Error",
                "version": "1.0.0",
                "description": f"Error generando especificación: {str(e)}"
            },
            "paths": {}
        }
        
        return {
            'statusCode': 200,  # Cambiado a 200 para que Swagger UI pueda mostrar el error
            'headers': {
                'Content-Type': 'application/json; charset=utf-8',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(error_spec, ensure_ascii=False),
            'isBase64Encoded': False
        }