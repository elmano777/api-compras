import json

def get_swagger_json(event, context):
    swagger_spec = {
        "openapi": "3.0.1",
        "info": {
            "title": "API Compras",
            "version": "1.0.0",
            "description": "Documentación de la API de compras (Swagger UI)"
        },
        "servers": [
            {"url": "https://tu-api-url"}
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
                    "properties": {
                        "codigo": {"type": "string"},
                        "nombre": {"type": "string"},
                        "precio": {"type": "number"},
                        "cantidad": {"type": "integer"},
                        "subtotal": {"type": "number"}
                    }
                },
                "Compra": {
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "codigo_compra": {"type": "string"},
                        "email_usuario": {"type": "string"},
                        "nombre_usuario": {"type": "string"},
                        "productos": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Producto"}
                        },
                        "total_productos": {"type": "integer"},
                        "total_monto": {"type": "number"},
                        "fecha_compra": {"type": "string"},
                        "estado": {"type": "string"},
                        "metodo_pago": {"type": "string"},
                        "direccion_entrega": {"type": "string"},
                        "observaciones": {"type": "string"}
                    }
                },
                "Estadisticas": {
                    "type": "object",
                    "properties": {
                        "total_compras": {"type": "integer"},
                        "total_gastado": {"type": "number"},
                        "total_productos_comprados": {"type": "integer"},
                        "promedio_por_compra": {"type": "number"},
                        "primera_compra": {"type": "string", "nullable": True},
                        "ultima_compra": {"type": "string", "nullable": True}
                    }
                }
            }
        },
        "paths": {
            "/compras/registrar": {
                "post": {
                    "summary": "Registrar compra",
                    "description": "Registra una nueva compra",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "productos": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/Producto"}
                                        },
                                        "metodo_pago": {"type": "string"},
                                        "direccion_entrega": {"type": "string"},
                                        "observaciones": {"type": "string"}
                                    },
                                    "required": ["productos"]
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
                                            "message": {"type": "string"},
                                            "compra": {"$ref": "#/components/schemas/Compra"}
                                        }
                                    }
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
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "description": "Cantidad máxima de compras a devolver",
                            "required": False,
                            "schema": {"type": "integer", "default": 10}
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
                            "description": "Filtrar desde esta fecha (ISO)",
                            "required": False,
                            "schema": {"type": "string", "format": "date-time"}
                        },
                        {
                            "name": "fecha_hasta",
                            "in": "query",
                            "description": "Filtrar hasta esta fecha (ISO)",
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
                                            "count": {"type": "integer"},
                                            "hasMore": {"type": "boolean"}
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
                    "parameters": [
                        {
                            "name": "codigo",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
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
                        "404": {"description": "Compra no encontrada"}
                    }
                }
            },
            "/compras/estadisticas": {
                "get": {
                    "summary": "Obtener estadísticas de compras",
                    "description": "Devuelve estadísticas de compras del usuario autenticado",
                    "responses": {
                        "200": {
                            "description": "Estadísticas de compras",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Estadisticas"}
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
    html = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8">
      <title>Swagger UI - API Compras</title>
      <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css" />
    </head>
    <body>
      <div id="swagger-ui"></div>
      <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
      <script>
        window.onload = function() {
          window.ui = SwaggerUIBundle({
            url: '/swagger.json',
            dom_id: '#swagger-ui',
            presets: [
              SwaggerUIBundle.presets.apis,
              SwaggerUIBundle.SwaggerUIStandalonePreset
            ],
            layout: "BaseLayout",
            docExpansion: "none",
            operationsSorter: "alpha"
          });
        };
      </script>
    </body>
    </html>
    '''
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        },
        'body': html
    } 