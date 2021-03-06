#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from typing import Dict
from botbuilder.core.skills import BotFrameworkSkill


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3980
    APP_ID = os.environ.get(
        "MicrosoftAppId", "87880ec8-6989-4b4f-b13b-cba69dc2b82b"
        # Kirin-TeamsBot
    )
    APP_PASSWORD = os.environ.get(
        "MicrosoftAppPassword", "V88ZT~_rOnsEEy.59b7qg_MYW8JiZD2ja4"
        # Kirin-TeamsBot
    )
    SKILL_HOST_ENDPOINT = "http://127.0.0.1:3980/api/skills"
    SKILLS = [
        {
            "id": "EchoSkillBot",
            "app_id": "fddbb187-b979-43a7-aa9a-4630c931184c",
            "skill_endpoint": "http://localhost:39783/api/messages",
        },
        {
            "id": "TeamsFileBot",
            "app_id": "cb8fe097-cb7c-4e1c-bf47-7afab84fdd0a",
            "skill_endpoint": "https://teamsfilebot.troykirin.io/api/messages"
        },
        {
            "id": "AttachmentBot",
            "app_id": "2d4dc6c8-2b32-46c2-aa5a-363625f93e1e",
            "skill_endpoint": "https://teams.troykirin.io/api/messages"
        }
    ]

    # Callers to only those specified, '*' allows any caller.
    # Example: os.environ.get("AllowedCallers", ["54d3bb6a-3b6d-4ccd-bbfd-cad5c72fb53a"])
    ALLOWED_CALLERS = os.environ.get("AllowedCallers", ["*"])


class SkillConfiguration:
    SKILL_HOST_ENDPOINT = DefaultConfig.SKILL_HOST_ENDPOINT
    SKILLS: Dict[str, BotFrameworkSkill] = {
        skill["id"]: BotFrameworkSkill(**skill) for skill in DefaultConfig.SKILLS
    }
