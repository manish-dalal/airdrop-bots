import os
import glob
import asyncio
import argparse
from pathlib import Path
from itertools import cycle

from pyrogram import Client, compose
from better_proxy import Proxy

from botYesCoin.config import settings
from botYesCoin.utils import logger
from botYesCoin.core.tapper import run_tapper
from botYesCoin.core.registrator import register_sessions


start_text = """

░█  ░█ █▀▀ █▀▀ ░█▀▀█ █▀▀█  ▀  █▀▀▄ ░█▀▀█ █▀▀█ ▀▀█▀▀ 
░█▄▄▄█ █▀▀ ▀▀█ ░█    █  █ ▀█▀ █  █ ░█▀▀▄ █  █   █   
  ░█   ▀▀▀ ▀▀▀ ░█▄▄█ ▀▀▀▀ ▀▀▀ ▀  ▀ ░█▄▄█ ▀▀▀▀   ▀  

Select an action:

    1. Create session
    2. Run clicker
    3. Run via Telegram (Beta)
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
    parser.add_argument('-sd', '--sessionDir')
    parser.add_argument('-u', '--user')
    username = parser.parse_args().user
    logger.info(f"username== {username}")

    sessionDir = parser.parse_args().sessionDir or ''
    print('sessionDir', sessionDir)

    logger.info(f"Detected {len(get_session_names(sessionDir, username))} sessions | {len(get_proxies())} proxies")

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
        tg_clients = await get_tg_clients(sessionDir, username)

        await run_tasks(tg_clients=tg_clients)
    elif action == 3:
        tg_clients = await get_tg_clients(sessionDir, username)

        logger.info("Send /help command in Saved Messages\n")

        await compose(tg_clients)


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
