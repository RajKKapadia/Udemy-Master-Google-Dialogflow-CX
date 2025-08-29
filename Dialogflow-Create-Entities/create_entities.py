import json
from typing import Any, Dict

from google.cloud import dialogflowcx_v3
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials


def load_service_account_credentials(credentials_path: str) -> Credentials:
    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        return credentials
    except Exception as e:
        print(f"Error loading service account credentials: {e}")
        return None


def load_entities_from_json(entities_file_path: str) -> Dict[str, Any] | None:
    try:
        with open(entities_file_path, "r") as file:
            entities_data = json.load(file)
        return entities_data
    except Exception as e:
        print(f"Error loading entities from JSON file: {e}")
        return None


def create_entity_type(
    client: dialogflowcx_v3.EntityTypesClient,
    parent: str,
    entity_name: str,
    kind="KIND_MAP",
) -> dialogflowcx_v3.EntityType | None:
    try:
        entity_type = dialogflowcx_v3.EntityType()
        entity_type.display_name = entity_name
        entity_type.kind = dialogflowcx_v3.EntityType.Kind[kind]
        entity_type.auto_expansion_mode = (
            dialogflowcx_v3.EntityType.AutoExpansionMode.AUTO_EXPANSION_MODE_DEFAULT
        )
        response = client.create_entity_type(parent=parent, entity_type=entity_type)
        print(f"Created entity type: {entity_name}")
        return response
    except Exception as e:
        print(f"Error creating entity type {entity_name}: {e}")
        return None


def add_entity_values(
    client: dialogflowcx_v3.EntityTypesClient,
    entity_type: dialogflowcx_v3.EntityType,
    entities_data: Dict[str, Any],
) -> dialogflowcx_v3.EntityType:
    try:
        entity_values = []
        for value, synonyms in entities_data.items():
            entity_values.append(
                dialogflowcx_v3.EntityType.Entity(value=value, synonyms=synonyms)
            )
        entity_type.entities = entity_values
        update_mask = {"paths": ["entities"]}
        response = client.update_entity_type(
            entity_type=entity_type, update_mask=update_mask
        )
        print(
            f"Added {len(entity_values)} values to entity type: {entity_type.display_name}"
        )
        return response
    except Exception as e:
        print(f"Error adding entity values to {entity_type.display_name}: {e}")
        return None


PROJECT_ID = "youtube-dialogflow-cx"
LOCATION = "global"
AGENT_ID = "fc07ebab-fef6-4e0e-b487-4f615a11b3df"

SERVICE_ACCOUNT_FILE_PATH = "service_account.json"
ENTITIES_JSON_FILE_PATH = "entities.json"


def main():
    credentials = load_service_account_credentials(
        credentials_path=SERVICE_ACCOUNT_FILE_PATH
    )
    if not credentials:
        return

    entities_data = load_entities_from_json(entities_file_path=ENTITIES_JSON_FILE_PATH)
    if not entities_data:
        return

    client_options = {"api_endpoint": f"{LOCATION}-dialogflow.googleapis.com"}
    client = dialogflowcx_v3.EntityTypesClient(
        credentials=credentials, client_options=client_options
    )

    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}"

    for entity_name, entity_values in entities_data.items():
        entity_type = create_entity_type(
            client=client, parent=parent, entity_name=entity_name
        )
        if entity_type:
            add_entity_values(
                client=client, entity_type=entity_type, entities_data=entity_values
            )


if __name__ == "__main__":
    main()
