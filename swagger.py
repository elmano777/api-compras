import json

def serve_swagger_ui(event, context):
    # Obtener la URL base de la API desde el evento
    headers = event.get('headers', {})
    host = headers.get('Host') or headers.get('host', 'localhost')
    stage = event.get('requestContext', {}).get('stage', 'dev')
    swagger_json_url = f"https://{host}/{stage}/swagger.json"
    
    html = f'''<!DOCTYPE html>
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
      
      window.setAuthToken = function(token) {{
        localStorage.setItem('authToken', token);
        ui.preauthorizeApiKey('bearerAuth', 'Bearer ' + token);
        alert('Token de autorización establecido');
      }};
      
      window.clearAuthToken = function() {{
        localStorage.removeItem('authToken');
        alert('Token de autorización eliminado');
      }};
      
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
</html>'''
    
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