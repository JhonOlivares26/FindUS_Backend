import os
from azure.servicebus.management import ServiceBusAdministrationClient, SqlRuleFilter
from dotenv import load_dotenv

load_dotenv()
connection_str = os.getenv("AZURE_SERVICE_BUS_CONNECTION_STRING")
topic_name = "main"

# Lista de suscripciones y el filtro de propiedad que deben recibir
subscriptions = [
    "Paso1",
    "Paso2",
    "Paso3",
    "Coordinador",
    "Cache",
    "Reprocesados123"
]

# Crear cliente de administración
admin_client = ServiceBusAdministrationClient.from_connection_string(connection_str)

for subscription in subscriptions:
    print(f"🛠️ Configurando filtro para suscripción '{subscription}'...")

    # Eliminar la regla por defecto si existe
    rules = list(admin_client.list_rules(topic_name, subscription))  # Cambiado a list_rules
    for rule in rules:
        if rule.name == "$Default":
            admin_client.delete_rule(topic_name, subscription, "$Default")
            print(f"✅ Regla '$Default' eliminada de '{subscription}'")

    # Crear una nueva regla con filtro de sendTo
    filter_expression = f"sendTo = '{subscription}'"
    rule_name = f"sendTo_{subscription}"

    admin_client.create_rule(
        topic_name=topic_name,
        subscription_name=subscription,
        rule_name=rule_name,
        filter=SqlRuleFilter(filter_expression)
    )

    print(f"✅ Regla '{rule_name}' creada con filtro: {filter_expression}\n")

print("✅ Todos los filtros fueron configurados exitosamente.")