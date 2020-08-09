# Main app begins app
# references rootBot to hand off skills to other bots

# unused rn
# import for async functionality
import asyncio

# system imports
import sys
import traceback
from datetime import datetime
from http import HTTPStatus

# Core imports
from aiohttp import web
from aiohttp.web import Request, Response
from aiohttp.web_response import json_response
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    ConversationState,
    MemoryStorage,
    TurnContext,
    UserState
    # BotFrameworkAdapter, # using adapter with errors instead
)

# Imports for integration
from botbuilder.core.integration import (
    aiohttp_channel_service_routes,
    aiohttp_error_middleware
)

# Imports for bot skill hand off
from botbuilder.core.skills import SkillHandler
from botbuilder.integration.aiohttp.skills import SkillHttpClient
from botbuilder.schema import Activity  #, ActivityTypes
from botframework.connector.auth import (
    AuthenticationConfiguration,
    SimpleCredentialProvider
)
from bots.skill_conversation_id_factory import SkillConversationIdFactory
from bots.authentication import AllowedSkillsClaimsValidator
from config import DefaultConfig, SkillConfiguration
from adapters.adapter_with_error_handler import AdapterWithErrorHandler

# ---- Import Bots ----
from bots.root_bot import RootBot

# ---- Import Dialog ----
from dialogs import MainDialog

# # Import Bots
# from bots import RootBot  # rootBot to call other skills
# attachmentBot
# authBot
# dialogBot
# proactiveBot
# teamsFileBot
# sharepointBot
# msGraphBot
# telegramBot
# helpdeskBot

# ---- CONFIGURATION ----
# config.py
CONFIG = DefaultConfig()
SKILL_CONFIG = SkillConfiguration()

# Whitelist skills from skill_config - skills allowed to be called
ALLOWED_CALLER_IDS = {s.app_id for s in [*SKILL_CONFIG.SKILLS.values()]}
CLAIMS_VALIDATOR = AllowedSkillsClaimsValidator(ALLOWED_CALLER_IDS)
AUTH_CONFIG = AuthenticationConfiguration(
    claims_validator=CLAIMS_VALIDATOR.validate_claims
)

# ---- ADAPTER ----
# adapter settings
SETTINGS = BotFrameworkAdapterSettings(
    app_id=CONFIG.APP_ID,
    app_password=CONFIG.APP_PASSWORD,
    auth_configuration=AUTH_CONFIG
)

# Conversation storage & state
MEMORY = MemoryStorage()
USER_STATE = UserState()
# TODO: CosmosDB
CONVERSATION_STATE = ConversationState(MEMORY)

# Conversation ID & credentials
ID_FACTORY = SkillConversationIdFactory(MEMORY)
CREDENTIAL_PROVIDER = SimpleCredentialProvider(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
CLIENT = SkillHttpClient(CREDENTIAL_PROVIDER, ID_FACTORY)

# adapter w/ error handling
ADAPTER = AdapterWithErrorHandler(
    SETTINGS, CONFIG, CONVERSATION_STATE, CLIENT, SKILL_CONFIG
)

# ---- Create Dialog ----
DIALOG = MainDialog()

# ---- Create bot ----
""" Uses root bot for a multi skill functionality """
BOT = RootBot(CONVERSATION_STATE, SKILL_CONFIG, CLIENT, CONFIG, DIALOG)


SKILL_HANDLER = SkillHandler(
    ADAPTER, BOT, ID_FACTORY, CREDENTIAL_PROVIDER, AuthenticationConfiguration()
)

# Listen for incoming responses on /api/messages
async def messages(req: Request) -> Response:
    # Main bot message handler
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    invoke_response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if invoke_response:
        return json_response(data=invoke_response.body, status=invoke_response.status)
    return Response(status=HTTPStatus.OK)


APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)
APP.router.add_routes(aiohttp_channel_service_routes(SKILL_HANDLER, "/api/skills"))


if __name__ == "__main__":
    try:
        web.run_app(APP, host="localhost", port=CONFIG.PORT)  # TODO: Change host to Azure / deploy from Raspberry Pi
    except Exception as error:
        raise error
