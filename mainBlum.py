import asyncio
from botBlum.core import launcher
from botBlum.utils.logger import log

async def main():
	await launcher.start()


if __name__ == '__main__':
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		log.info("Bot stopped by user")