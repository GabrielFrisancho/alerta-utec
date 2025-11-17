from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import boto3
import json
from botocore.exceptions import ClientError

default_args = {
    'owner': 'alerta-utec',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def procesar_incidentes_pendientes():
    """
    Procesa incidentes pendientes y los clasifica automáticamente
    """
    print("🔄 Iniciando procesamiento de incidentes...")
    
    # Configurar cliente de DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('IncidentesUTEC')
    
    try:
        # Obtener incidentes pendientes
        response = table.scan(
            FilterExpression='estado = :estado',
            ExpressionAttributeValues={':estado': 'pendiente'}
        )
        
        incidentes_pendientes = response.get('Items', [])
        print(f"📊 Encontrados {len(incidentes_pendientes)} incidentes pendientes")
        
        # Procesar cada incidente
        for incidente in incidentes_pendientes:
            clasificar_y_notificar_incidente(incidente, table)
            
    except ClientError as e:
        print(f"❌ Error accediendo a DynamoDB: {e}")

def clasificar_y_notificar_incidente(incidente, table):
    """
    Clasifica un incidente y envía notificaciones si es necesario
    """
    incidente_id = incidente['id']
    descripcion = incidente['descripcion'].lower()
    tipo = incidente['tipo'].lower()
    urgencia_actual = incidente['urgencia']
    
    print(f"🔍 Procesando incidente: {incidente_id}")
    
    # Lógica de clasificación automática
    nueva_urgencia = clasificar_urgencia_automatica(descripcion, tipo, urgencia_actual)
    
    # Si cambió la urgencia, actualizar
    if nueva_urgencia != urgencia_actual:
        print(f"🔄 Actualizando urgencia de {urgencia_actual} a {nueva_urgencia}")
        actualizar_urgencia_incidente(table, incidente_id, nueva_urgencia)
    
    # Notificar si es urgente o crítica
    if nueva_urgencia in ['alta', 'critica']:
        print(f"🚨 Notificando incidente {nueva_urgencia.upper()}: {incidente_id}")
        # Aquí podrías integrar con SNS para notificaciones reales
        generar_alerta_administrativa(incidente, nueva_urgencia)

def clasificar_urgencia_automatica(descripcion, tipo, urgencia_actual):
    """
    Clasifica automáticamente la urgencia basado en palabras clave
    """
    # Palabras clave para cada nivel de urgencia
    palabras_criticas = [
        'emergencia', 'sangre', 'incendio', 'accidente', 'desmayo', 
        'convulsión', 'ataque', 'peligro inminente', 'amenaza'
    ]
    
    palabras_altas = [
        'grave', 'urgente', 'peligro', 'fuga', 'inundación', 
        'corto circuito', 'electricidad', 'estructural'
    ]
    
    # Verificar palabras críticas
    if any(palabra in descripcion for palabra in palabras_criticas):
        return 'critica'
    
    # Verificar palabras altas
    if any(palabra in descripcion for palabra in palabras_altas):
        return 'alta'
    
    # Tipos de incidente que son automáticamente altos
    if tipo in ['seguridad', 'salud', 'incendio']:
        return 'alta'
    
    # Si no hay cambios, mantener la urgencia actual
    return urgencia_actual

def actualizar_urgencia_incidente(table, incidente_id, nueva_urgencia):
    """
    Actualiza la urgencia de un incidente en DynamoDB
    """
    try:
        table.update_item(
            Key={'id': incidente_id},
            UpdateExpression='SET urgencia = :urgencia, procesado_por_airflow = :procesado',
            ExpressionAttributeValues={
                ':urgencia': nueva_urgencia,
                ':procesado': True
            }
        )
        print(f"✅ Incidente {incidente_id} actualizado a urgencia: {nueva_urgencia}")
    except ClientError as e:
        print(f"❌ Error actualizando incidente {incidente_id}: {e}")

def generar_alerta_administrativa(incidente, urgencia):
    """
    Genera una alerta para el equipo administrativo
    """
    alerta = f"""
    🚨 ALERTA {urgencia.upper()} - ALERTA UTEC
    
    Incidente ID: {incidente['id']}
    Tipo: {incidente['tipo']}
    Ubicación: {incidente['ubicacion']}
    Urgencia: {urgencia}
    Descripción: {incidente['descripcion']}
    Fecha: {incidente['fecha']}
    
    **Por favor atender inmediatamente**
    """
    
    print(alerta)
    # En producción, aquí enviarías email/SMS via SNS

def generar_reporte_diario():
    """
    Genera un reporte diario de incidentes
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('IncidentesUTEC')
    
    # Obtener incidentes de las últimas 24 horas
    fecha_limite = (datetime.utcnow() - timedelta(hours=24)).isoformat()
    
    try:
        response = table.scan(
            FilterExpression='fecha >= :fecha_limite',
            ExpressionAttributeValues={':fecha_limite': fecha_limite}
        )
        
        incidentes_recientes = response.get('Items', [])
        
        # Generar estadísticas
        total_incidentes = len(incidentes_recientes)
        por_estado = {}
        por_urgencia = {}
        
        for incidente in incidentes_recientes:
            estado = incidente['estado']
            urgencia = incidente['urgencia']
            
            por_estado[estado] = por_estado.get(estado, 0) + 1
            por_urgencia[urgencia] = por_urgencia.get(urgencia, 0) + 1
        
        reporte = f"""
        📊 REPORTE DIARIO - ALERTA UTEC
        Fecha: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}
        
        ESTADÍSTICAS:
        - Total incidentes (24h): {total_incidentes}
        - Por estado: {por_estado}
        - Por urgencia: {por_urgencia}
        
        INCIDENTES RECIENTES:
        """
        
        for incidente in incidentes_recientes[:5]:  # Mostrar solo los 5 más recientes
            reporte += f"\n- {incidente['tipo']} ({incidente['urgencia']}) - {incidente['estado']}"
        
        print(reporte)
        
    except ClientError as e:
        print(f"❌ Error generando reporte: {e}")

# Definir el DAG
with DAG(
    'alerta_utec_processor',
    default_args=default_args,
    description='DAG para procesamiento automático de incidentes UTEC',
    schedule_interval=timedelta(minutes=10),  # Ejecutar cada 10 minutos
    catchup=False,
    tags=['utec', 'incidentes', 'alerta']
) as dag:
    
    # Tarea 1: Procesar incidentes pendientes
    procesar_incidentes = PythonOperator(
        task_id='procesar_incidentes_pendientes',
        python_callable=procesar_incidentes_pendientes
    )
    
    # Tarea 2: Generar reporte diario (ejecutar una vez al día)
    reporte_diario = PythonOperator(
        task_id='generar_reporte_diario',
        python_callable=generar_reporte_diario
    )
    
    procesar_incidentes >> reporte_diario
