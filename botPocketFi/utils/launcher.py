import os
import glob
import asyncio
import argparse
from pathlib import Path
from itertools import cycle

from pyrogram import Client
from better_proxy import Proxy

from botPocketFi.config import settings
from botPocketFi.utils import logger
from botPocketFi.core.tapper import run_tapper
from botPocketFi.core.registrator import register_sessions
from .ps import check_base_url
import sys


start_text = """

                                                                                                                                             
Select an action:

    1. Run clicker
    2. Create session
"""

global tg_clients

def get_session_names(sessionDir, username) -> list[str]:
	session_path = Path(sessionDir or 'sessions')
	finalUser = (username or '*') + '.session'
	session_files = session_path.glob(finalUser)
	session_names = sorted([file.stem for file in session_files])
	return session_names


def get_proxies() -> list[Proxy]:
    if settings.USE_PROXY_FROM_FILE:
        with open(file="bot/config/proxies.txt", encoding="utf-8-sig") as file:
            proxies = [Proxy.from_str(proxy=row.strip()).as_url for row in file]
    else:
        proxies = []

    return proxies


async def get_tg_clients(sessionDir, username) -> list[Client]:
    global tg_clients

    session_names = get_session_names(sessionDir, username)

    if not session_names:
        raise FileNotFoundError("Not found session files")

    if not settings.API_ID or not settings.API_HASH:
        raise ValueError("API_ID and API_HASH not found in the .env file.")

    tempDir = sessionDir or 'sessions'
    sdir = tempDir + '/'
    tg_clients = [
        Client(
            name=session_name,
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
            workdir=sdir,
            plugins=dict(root="bot/plugins"),
        )
        for session_name in session_names
    ]

    return tg_clients


async def process() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", type=int, help="Action to perform")
    parser.add_argument('-u', '--user')
    parser.add_argument('-sd', '--sessionDir')
    if check_base_url() is False:
        sys.exit(
            "Detected api change! Stoped the bot for safety. Contact me here to update the bot: https://t.me/vanhbakaaa")

    username = parser.parse_args().user
    logger.info(f"username== {username}")
    sessionDir = parser.parse_args().sessionDir or ''
    logger.info(f"Detected {len(get_session_names(sessionDir, username))} sessions | {len(get_proxies())} proxies")

    action = parser.parse_args().action

    if not action:
        print(start_text)

        while True:
            action = input("> ")

            if not action.isdigit():
                logger.warning("Action must be number")
            elif action not in ["1", "2"]:
                logger.warning("Action must be 1 or 2")
            else:
                action = int(action)
                break

    if action == 2:
        await register_sessions()
    elif action == 1:
        tg_clients = await get_tg_clients(sessionDir, username)

        await run_tasks(tg_clients=tg_clients)


async def run_tasks(tg_clients: list[Client]):
    proxies = get_proxies()
    proxies_cycle = cycle(proxies) if proxies else None
    tasks = [
        asyncio.create_task(
            run_tapper(
                tg_client=tg_client,
                proxy=next(proxies_cycle) if proxies_cycle else None,
            )
        )
        for tg_client in tg_clients
    ]

    await asyncio.gather(*tasks)
