import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # Entrada (json)
    tenant_id = event['body']['tenant_id']
    alumno_id = event['body']['alumno_id']
    alumno_datos = event['body']['alumno_datos']  # dict con los nuevos datos

    # Proceso
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_alumnos')

    try:
        response = table.update_item(
            Key={
                'tenant_id': tenant_id,
                'alumno_id': alumno_id
            },
            UpdateExpression="""
                SET alumno_datos = :datos,
                    fecha_actualizacion = :ts
            """,
            ExpressionAttributeValues={
                ':datos': alumno_datos,
                ':ts': int(__import__('time').time())
            },
            ConditionExpression="attribute_exists(tenant_id) AND attribute_exists(alumno_id)",
            ReturnValues="ALL_NEW"
        )

        # Salida (json)
        return {
            'statusCode': 200,
            'message': 'Alumno modificado correctamente',
            'alumno': response.get('Attributes', {})
        }

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                'statusCode': 404,
                'message': 'Alumno no existe para modificar',
                'tenant_id': tenant_id,
                'alumno_id': alumno_id
            }
        else:
            return {
                'statusCode': 500,
                'message': 'Error al modificar alumno',
                'error': str(e)
            }
