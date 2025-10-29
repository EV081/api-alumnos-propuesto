import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # Entrada (json)
    tenant_id = event['body']['tenant_id']
    alumno_id = event['body']['alumno_id']

    # Proceso
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_alumnos')

    try:
        response = table.delete_item(
            Key={
                'tenant_id': tenant_id,
                'alumno_id': alumno_id
            },
            ConditionExpression="attribute_exists(tenant_id) AND attribute_exists(alumno_id)",
            ReturnValues="ALL_OLD"
        )

        # Si ReturnValues="ALL_OLD" regresa vacío, no existía (pero con la condición ya habría fallado)
        eliminado = response.get('Attributes', {})

        # Salida (json)
        return {
            'statusCode': 200,
            'message': 'Alumno eliminado correctamente',
            'alumno_eliminado': eliminado
        }

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                'statusCode': 404,
                'message': 'Alumno no existe para eliminar',
                'tenant_id': tenant_id,
                'alumno_id': alumno_id
            }
        else:
            return {
                'statusCode': 500,
                'message': 'Error al eliminar alumno',
                'error': str(e)
            }
