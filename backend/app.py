import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('IncidentesUTEC')

def crear_incidente(event, context):
    """Crear nuevo incidente - POST /incidentes"""
    try:
        body = json.loads(event['body'])
        
        # Validación
        if not body.get('tipo') or not body.get('descripcion'):
            return response(400, {'error': 'Faltan campos requeridos: tipo, descripcion'})
        
        incident_id = f"inc_{uuid.uuid4()}"
        fecha_actual = datetime.utcnow().isoformat()
        
        incidente = {
            'id': incident_id,
            'tipo': body['tipo'],
            'ubicacion': body.get('ubicacion', 'No especificada'),
            'descripcion': body['descripcion'],
            'urgencia': body.get('urgencia', 'media'),
            'estado': 'pendiente',
            'fecha': fecha_actual,
            'usuario': 'anonymous'
        }
        
        table.put_item(Item=incidente)
        
        return response(201, {
            'message': 'Incidente creado exitosamente',
            'id': incident_id,
            'incidente': incidente
        })
        
    except Exception as e:
        return response(500, {'error': str(e)})

def listar_incidentes(event, context):
    """Listar todos los incidentes - GET /incidentes"""
    try:
        result = table.scan()
        incidentes = result.get('Items', [])
        
        # Ordenar por fecha (más recientes primero)
        incidentes.sort(key=lambda x: x.get('fecha', ''), reverse=True)
        
        return response(200, {
            'incidentes': incidentes,
            'total': len(incidentes)
        })
        
    except Exception as e:
        return response(500, {'error': str(e)})

def obtener_incidente(event, context):
    """Obtener incidente específico - GET /incidentes/{id}"""
    try:
        incident_id = event['pathParameters']['id']
        
        result = table.get_item(Key={'id': incident_id})
        
        if 'Item' not in result:
            return response(404, {'error': 'Incidente no encontrado'})
        
        return response(200, {'incidente': result['Item']})
        
    except Exception as e:
        return response(500, {'error': str(e)})

def actualizar_incidente(event, context):
    """Actualizar estado de incidente - PUT /incidentes/{id}"""
    try:
        incident_id = event['pathParameters']['id']
        body = json.loads(event['body'])
        
        # Verificar que existe
        existing = table.get_item(Key={'id': incident_id})
        if 'Item' not in existing:
            return response(404, {'error': 'Incidente no encontrado'})
        
        # Campos permitidos para actualización
        update_expression = "SET "
        expression_values = {}
        
        allowed_fields = ['estado', 'urgencia', 'descripcion', 'ubicacion']
        updates = []
        
        for field in allowed_fields:
            if field in body:
                updates.append(f"{field} = :{field}")
                expression_values[f":{field}"] = body[field]
        
        if not updates:
            return response(400, {'error': 'No hay campos válidos para actualizar'})
        
        update_expression += ", ".join(updates)
        
        # Actualizar en DynamoDB
        result = table.update_item(
            Key={'id': incident_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues='ALL_NEW'
        )
        
        return response(200, {
            'message': 'Incidente actualizado',
            'incidente': result['Attributes']
        })
        
    except Exception as e:
        return response(500, {'error': str(e)})

def response(status_code, body):
    """Helper para respuestas HTTP"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': json.dumps(body)
    }