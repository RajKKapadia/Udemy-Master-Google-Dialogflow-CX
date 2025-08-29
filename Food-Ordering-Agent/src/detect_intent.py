from typing import Dict, Any

from google.cloud import dialogflowcx_v3 as dialogflow
from google.oauth2 import service_account

from src import logging
from src import config

logger = logging.getLogger(__name__)


async def detect_intent_async(
    session_id: str,
    text_input: str,
    project_id: str = config.PROJECT_ID,
    location: str = config.LOCATION,
    agent_id: str = config.AGENT_ID,
    language_code: str = "en",
) -> Dict[str, Any]:
    """
    Detects intent from text input using Dialogflow CX agent asynchronously.

    Args:
        project_id: Google Cloud project ID
        location: Location of the agent (e.g., 'us-central1')
        agent_id: Dialogflow CX agent ID
        session_id: Unique session ID for the conversation
        text_input: Text input from user
        language_code: Language code (default: 'en')

    Returns:
        Dictionary containing intent detection results
    """

    try:
        # Set up credentials
        credentials = service_account.Credentials.from_service_account_info(
            config.SERVICE_ACCOUNT_JSON
        )

        # Create the client with credentials
        client = dialogflow.SessionsAsyncClient(credentials=credentials)

        # Build the session path
        session_path = client.session_path(
            project=project_id, location=location, agent=agent_id, session=session_id
        )

        # Create text input
        text_input_obj = dialogflow.TextInput(text=text_input)
        query_input = dialogflow.QueryInput(
            text=text_input_obj, language_code=language_code
        )

        # Create the request
        request = dialogflow.DetectIntentRequest(
            session=session_path, query_input=query_input
        )

        # Make the async call
        response = await client.detect_intent(request=request)

        logger.info(response.query_result.response_messages)

        response_messages = []

        for rm in response.query_result.response_messages:
            response_messages.append(rm.text.text[0])
        return {"status": True, "messages": response_messages}

    except Exception as e:
        logger.error(f"Error at detect_intent_async: {e}")
        return {"status": False, "messages": []}
