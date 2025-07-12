import json

def get_swagger_json(event, context):
    # Obtener la URL base de la API desde el evento
    headers = event.get('headers', {})
    host = headers.get('Host') or headers.get('host', 'localhost')
    stage = event.get('requestContext', {}).get('stage', 'dev')
    base_url = f"https://{host}/{stage}"
    
    swagger_spec = {
        "openapi": "3.0.1",
        "info": {
            "title": "API Compras",
            "version": "1.0.0",
            "description": "Documentación de la API de compras (Swagger UI)"
        },
        "servers": [
            {"url": base_url}
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
                        "codigo": {"type": "string", "example": "PROD001"},
                        "nombre": {"type": "string", "example": "Laptop Dell"},
                        "precio": {"type": "number", "example": 999.99},
                        "cantidad": {"type": "integer", "example": 1},
                        "subtotal": {"type": "number", "example": 999.99}
                    }
                },
                "RegistrarCompraRequest": {
                    "type": "object",
                    "required": ["productos"],
                    "properties": {
                        "productos": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Producto"}
                        },
                        "metodo_pago": {"type": "string", "example": "online"},
                        "direccion_entrega": {"type": "string", "example": "Av. Principal 123"},
                        "observaciones": {"type": "string", "example": "Entregar en la mañana"}
                    }
                },
                "Compra": {
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string", "example": "tenant123"},
                        "codigo_compra": {"type": "string", "example": "COM-1641234567-ABC123"},
                        "email_usuario": {"type": "string", "example": "usuario@example.com"},
                        "nombre_usuario": {"type": "string", "example": "Juan Pérez"},
                        "productos": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Producto"}
                        },
                        "total_productos": {"type": "integer", "example": 2},
                        "total_monto": {"type": "number", "example": 1999.98},
                        "fecha_compra": {"type": "string", "format": "date-time", "example": "2025-01-15T10:30:00Z"},
                        "estado": {"type": "string", "example": "completada"},
                        "metodo_pago": {"type": "string", "example": "online"},
                        "direccion_entrega": {"type": "string", "example": "Av. Principal 123"},
                        "observaciones": {"type": "string", "example": "Entregar en la mañana"}
                    }
                },
                "Estadisticas": {
                    "type": "object",
                    "properties": {
                        "total_compras": {"type": "integer", "example": 5},
                        "total_gastado": {"type": "number", "example": 2500.75},
                        "total_productos_comprados": {"type": "integer", "example": 8},
                        "promedio_por_compra": {"type": "number", "example": 500.15},
                        "primera_compra": {"type": "string", "format": "date-time", "nullable": True, "example": "2025-01-01T10:00:00Z"},
                        "ultima_compra": {"type": "string", "format": "date-time", "nullable": True, "example": "2025-01-15T10:30:00Z"}
                    }
                },
                "Error": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Mensaje de error"}
                    }
                }
            }
        },
        "security": [
            {"bearerAuth": []}
        ],
        "paths": {
            "/compras/registrar": {
                "post": {
                    "summary": "Registrar compra",
                    "description": "Registra una nueva compra en el sistema",
                    "tags": ["Compras"],
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/RegistrarCompraRequest"},
                                "example": {
                                    "productos": [
                                        {
                                            "codigo": "PROD001",
                                            "nombre": "Laptop Dell",
                                            "precio": 999.99,
                                            "cantidad": 1
                                        }
                                    ],
                                    "metodo_pago": "online",
                                    "direccion_entrega": "Av. Principal 123",
                                    "observaciones": "Entregar en la mañana"
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
                                        "type": "object",
                                        "properties": {
                                            "message": {"type": "string", "example": "Compra registrada exitosamente"},
                                            "compra": {"$ref": "#/components/schemas/Compra"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Error en la solicitud",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        },
                        "401": {
                            "description": "Token inválido o faltante",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/compras/listar": {
                "get": {
                    "summary": "Listar compras",
                    "description": "Obtiene una lista de compras con filtros y paginación",
                    "tags": ["Compras"],
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "description": "Cantidad máxima de compras a devolver",
                            "required": False,
                            "schema": {"type": "integer", "default": 10, "minimum": 1, "maximum": 100}
                        },
                        {
                            "name": "tenant_id",
                            "in": "query",
                            "description": "Filtrar por tenant_id",
                            "required": False,
                            "schema": {"type": "string"}
                        },
                        {
                            "name": "fecha_desde",
                            "in": "query",
                            "description": "Filtrar desde esta fecha (formato ISO 8601)",
                            "required": False,
                            "schema": {"type": "string", "format": "date-time"}
                        },
                        {
                            "name": "fecha_hasta",
                            "in": "query",
                            "description": "Filtrar hasta esta fecha (formato ISO 8601)",
                            "required": False,
                            "schema": {"type": "string", "format": "date-time"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Lista de compras",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "compras": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/Compra"}
                                            },
                                            "count": {"type": "integer", "example": 5},
                                            "hasMore": {"type": "boolean", "example": False}
                                        }
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
                    "description": "Busca una compra específica por su código",
                    "tags": ["Compras"],
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "name": "codigo",
                            "in": "path",
                            "required": True,
                            "description": "Código de la compra",
                            "schema": {"type": "string"},
                            "example": "COM-1641234567-ABC123"
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
                                            "compra": {"$ref": "#/components/schemas/Compra"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Compra no encontrada",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        },
                        "401": {
                            "description": "Token inválido o faltante",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/compras/estadisticas": {
                "get": {
                    "summary": "Obtener estadísticas de compras",
                    "description": "Devuelve estadísticas de compras del usuario autenticado",
                    "tags": ["Estadísticas"],
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Estadísticas de compras",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Estadisticas"}
                                }
                            }
                        },
                        "401": {
                            "description": "Token inválido o faltante",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        },
        'body': json.dumps(swagger_spec, ensure_ascii=False)
    }

def serve_swagger_ui(event, context):
    # Obtener la URL base de la API desde el evento
    headers = event.get('headers', {})
    host = headers.get('Host') or headers.get('host', 'localhost')
    stage = event.get('requestContext', {}).get('stage', 'dev')
    swagger_json_url = f"https://{host}/{stage}/swagger.json"
    
    html = f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8">
      <title>Swagger UI - API Compras</title>
      <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
      <style>
        .swagger-ui .topbar {{ display: none; }}
        .swagger-ui .info {{ margin: 50px 0; }}
        .swagger-ui .info .title {{ color: #3b4151; }}
      </style>
    </head>
    <body>
      <div id="swagger-ui"></div>
      <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
      <script>
        window.onload = function() {{
          const ui = SwaggerUIBundle({{
            url: '{swagger_json_url}',
            dom_id: '#swagger-ui',
            deepLinking: true,
            presets: [
              SwaggerUIBundle.presets.apis,
              SwaggerUIBundle.SwaggerUIStandalonePreset
            ],
            plugins: [
              SwaggerUIBundle.plugins.DownloadUrl
            ],
            layout: "StandaloneLayout",
            defaultModelsExpandDepth: 1,
            defaultModelExpandDepth: 1,
            docExpansion: "list",
            operationsSorter: "alpha",
            tagsSorter: "alpha",
            filter: true,
            requestInterceptor: function(request) {{
              // Agregar automáticamente el token si existe en localStorage
              const token = localStorage.getItem('authToken');
              if (token) {{
                request.headers['Authorization'] = 'Bearer ' + token;
              }}
              return request;
            }},
            onComplete: function() {{
              console.log('Swagger UI loaded successfully');
            }}
          }});
          
          // Función para establecer el token de autorización
          window.setAuthToken = function(token) {{
            localStorage.setItem('authToken', token);
            ui.preauthorizeApiKey('bearerAuth', 'Bearer ' + token);
            alert('Token de autorización establecido');
          }};
          
          // Función para limpiar el token
          window.clearAuthToken = function() {{
            localStorage.removeItem('authToken');
            alert('Token de autorización eliminado');
          }};
          
          // Agregar botones de utilidad
          setTimeout(function() {{
            const infoDiv = document.querySelector('.info');
            if (infoDiv) {{
              const tokenDiv = document.createElement('div');
              tokenDiv.innerHTML = `
                <div style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 4px; border-left: 4px solid #007bff;">
                  <h4 style="margin: 0 0 10px 0; color: #007bff;">🔐 Configuración de Token JWT</h4>
                  <p style="margin: 0 0 10px 0; color: #6c757d;">Para probar los endpoints protegidos, establece tu token JWT:</p>
                  <div style="display: flex; gap: 10px; align-items: center;">
                    <input type="text" id="jwtToken" placeholder="Ingresa tu token JWT aquí..." style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                    <button onclick="setAuthToken(document.getElementById('jwtToken').value)" style="padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">Establecer Token</button>
                    <button onclick="clearAuthToken()" style="padding: 8px 16px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;">Limpiar</button>
                  </div>
                </div>
              `;
              infoDiv.appendChild(tokenDiv);
            }}
          }}, 1000);
        }};
      </script>
    </body>
    </html>
    '''
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html; charset=utf-8',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        },
        'body': html
    }