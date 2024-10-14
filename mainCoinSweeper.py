import asyncio
from contextlib import suppress

from botCoinSweeper.utils.launcher import process


async def main():
    await process()


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
