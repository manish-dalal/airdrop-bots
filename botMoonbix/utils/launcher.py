import os
import glob
import asyncio
import argparse
import sys
from pathlib import Path

import requests
from itertools import cycle

from pyrogram import Client
from better_proxy import Proxy

from botMoonbix.config import settings
from botMoonbix.utils import logger
from botMoonbix.core.tapper import run_tapper
from botMoonbix.core.tapperNoThread import run_tapper_no_thread
from botMoonbix.core.registrator import register_sessions

curr_version = "2.5.0"

version = requests.get("https://raw.githubusercontent.com/vanhbakaa/moonbix-bot/refs/heads/main/version")
version_ = version.text.strip()
if curr_version == version_:
    logger.info("<cyan>Your version is up to date!</cyan>")
else:
    logger.warning(f"<yellow>New version detected {version_} please update the bot!</yellow>")
    sys.exit()
start_text = f"""

Version: {curr_version} 
By: https://github.com/vanhbakaa                                                                                                                                                                                         
Select an action:

    1. Create session
    2. Run clicker 
    3. Run clicker with multi-thread (Need proxy) | Just work with one account if you dont have proxy !
"""

global tg_clients

def get_session_names(username) -> list[str]:
	session_path = Path('sessions')
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


async def get_tg_clients(username) -> list[Client]:
    global tg_clients

    session_names = get_session_names(username)

    if not session_names:
        raise FileNotFoundError("Not found session files")

    if not settings.API_ID or not settings.API_HASH:
        raise ValueError("API_ID and API_HASH not found in the .env file.")

    tg_clients = [
        Client(
            name=session_name,
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
            workdir="sessions/",
            plugins=dict(root="bot/plugins"),
        )
        for session_name in session_names
    ]

    return tg_clients


async def process() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', type=int, help='Action to perform')

    parser.add_argument('-u', '--user')
    username = parser.parse_args().user
    logger.info(f"username== {username}")
    logger.info(f"Detected {len(get_session_names(username))} sessions | {len(get_proxies())} proxies")

    action = parser.parse_args().action

    if not action:

        print(start_text)

        while True:
            action = input("> ")

            if not action.isdigit():
                logger.warning("Action must be number")
            elif action not in ["1", "2", "3"]:
                logger.warning("Action must be 1, 2 or 3")
            else:
                action = int(action)
                break

    if action == 1:
        await register_sessions()
    elif action == 2:
        tg_clients = await get_tg_clients(username)
        proxies = get_proxies()
        await run_tapper_no_thread(tg_clients=tg_clients, proxies=proxies)


    elif action == 3:
        tg_clients = await get_tg_clients()


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

