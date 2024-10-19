import asyncio
import random
import sys
from itertools import cycle
from urllib.parse import unquote

import aiohttp
import requests
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from botNotPixel.core.agents import generate_random_user_agent
from botNotPixel.config import settings
from datetime import datetime, timedelta
from tzlocal import get_localzone
import time as time_module

from botNotPixel.utils import logger
from botNotPixel.exceptions import InvalidSession
from .headers import headers
from random import randint
import os
from PIL import Image
import io
import traceback
from botNotPixel.core.image_checker import get_cords_and_color, template_to_join, inform
import urllib3
import json

from ..utils.ps import check_base_url

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_GAME_ENDPOINT = "https://notpx.app/api/v1"
class Tapper:
    def __init__(self, query: str, session_name, multi_thread):
        self.query = query
        self.session_name = session_name
        self.first_name = ''
        self.last_name = ''
        self.user_id = ''
        self.auth_token = ""
        self.last_claim = None
        self.last_checkin = None
        self.balace = 0
        self.maxtime = 0
        self.fromstart = 0
        self.checked = [False] * 9
        self.balance = 0
        self.color_list = ["#FFD635", "#7EED56", "#00CCC0", "#51E9F4", "#94B3FF", "#000000", "#898D90", "#E46E6E",
                           "#E4ABFF", "#FF99AA", "#FFB470", "#FFFFFF", "#BE0039", "#FF9600", "#00CC78", "#009EAA",
                           "#3690EA", "#6A5CFF", "#B44AC0", "#FF3881", "#9C6926", "#6D001A", "#BF4300", "#00A368",
                           "#00756F", "#2450A4", "#493AC1", "#811E9F", "#A00357", "#6D482F"]
        self.multi_thread = multi_thread
        self.my_ref = "f6624523270"
        self.socket = None
        self.default_template = {
            'x': 244,
            'y': 244,
            'image_size': 510,
            'image': None
        }
        self.template_id = None
        self.cache = os.path.join(os.getcwd(), "cache")

        self.template_to_join = 0


    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy):
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5), )
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
            return True
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")
            return False

    def login(self, session: requests.Session):
        response = session.get(f"{API_GAME_ENDPOINT}/users/me", headers=headers, verify=False)
        if response.status_code == 200:
            logger.success(f"{self.session_name} | <green>Logged in.</green>")
            return True
        else:
            print(response.json())
            logger.warning("{self.session_name} | <red>Failed to login</red>")
            return False

    def get_user_data(self, session: requests.Session):
        response = session.get(f"{API_GAME_ENDPOINT}/mining/status", headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            print(response.json())
            return None

    def generate_random_color(self, color):
        a = random.choice(self.color_list)
        while a == color:
            a = random.choice(self.color_list)
        return a

    def generate_random_pos(self):
        return randint(1, 1000000)

    def repaintV2(self, session: requests.Session, chance_left, i, data):
        if i % 2 == 0:
            payload = {
                "newColor": data[0],
                "pixelId": data[1]
            }

        else:
            data1 = [str(self.generate_random_color(data[0])), int(self.generate_random_pos())]
            payload = {
                "newColor": data1[0],
                "pixelId": data[1]
            }
        response = session.post(f"{API_GAME_ENDPOINT}/repaint/start", headers=headers, json=payload, verify=False)
        if response.status_code == 200:
            if i % 2 == 0:
                logger.success(
                    f"{self.session_name} | <green>Painted <cyan>{data[1]}</cyan> successfully new color: <cyan>{data[0]}</cyan> | Earned <light-blue>{int(response.json()['balance']) - self.balance}</light-blue> | Balace: <light-blue>{response.json()['balance']}</light-blue> | Repaint left: <yellow>{chance_left}</yellow></green>")
                self.balance = int(response.json()['balance'])

            else:
                logger.success(
                    f"{self.session_name} | <green>Painted <cyan>{data[1]}</cyan> successfully new color: <cyan>{data1[0]}</cyan> | Earned <light-blue>{int(response.json()['balance']) - self.balance}</light-blue> | Balace: <light-blue>{response.json()['balance']}</light-blue> | Repaint left: <yellow>{chance_left}</yellow></green>")
                self.balance = int(response.json()['balance'])
        else:
            print(response.text)
            logger.warning(f"{self.session_name} | Faled to repaint: {response.status_code}")

    async def auto_upgrade_paint(self, session: requests.Session):
        res = session.get(f"{API_GAME_ENDPOINT}/mining/boost/check/paintReward", headers=headers, verify=False)
        if res.status_code == 200:
            logger.success(f"{self.session_name} | <green>Upgrade paint reward successfully!</green>")
        await asyncio.sleep(random.uniform(2, 4))

    async def auto_upgrade_recharge_speed(self, session: requests.Session):
        res = session.get(f"{API_GAME_ENDPOINT}/mining/boost/check/reChargeSpeed", headers=headers, verify=False)
        if res.status_code == 200:
            logger.success(f"{self.session_name} | <green>Upgrade recharging speed successfully!</green>")
        await asyncio.sleep(random.uniform(2, 4))

    async def auto_upgrade_energy_limit(self, session: requests.Session):
        res = session.get(f"{API_GAME_ENDPOINT}/mining/boost/check/energyLimit", headers=headers, verify=False)
        if res.status_code == 200:
            logger.success(f"{self.session_name} | <green>Upgrade energy limit successfully!</green>")

    def claimpx(self, session: requests.Session):
        res = session.get(f"{API_GAME_ENDPOINT}/mining/claim", headers=headers, verify=False)
        if res.status_code == 200:
            logger.success(
                f"{self.session_name} | Successfully claimed <cyan>{res.json()['claimed']}</cyan> px from mining!")
            self.balance += res.json()['claimed']

        else:
            logger.warning(f"{self.session_name} | Failed to claim px from mining: {res.json()}")

    async def subscribe_template(self, session: requests.Session, template_id: int):
        for attempt in range(3):
            try:

                resp = session.put(f'{API_GAME_ENDPOINT}/image/template/subscribe/{template_id}', headers=headers,
                                   verify=False)

                if resp.status_code == 200 or resp.status_code == 204:
                    logger.success(
                        f"{self.session_name} | <green>Started using template: <cyan>{template_id}</cyan></green>")
                    return True
                else:
                    print(resp.text)
                    return False
            except Exception as e:
                if resp.status_code == 504:
                    logger.warning(f"{self.session_name} | Attempt {attempt}: Connection timeout, retry after 3-5s...")
                    await asyncio.sleep(random.randint(3, 5))
                else:
                    logger.error(
                        f"{self.session_name} | <red>Unknown error while subscribing to template {template_id}: <light-yellow>{e}</light-yellow> </red>")

    async def get_template(self, session: requests.Session):
        for attempts in range(3):
            try:
                res = session.get(f'{API_GAME_ENDPOINT}/image/template/my', headers=headers, verify=False)

                if res.status_code == 200:
                    return res.json()
                else:
                    return None
            except Exception as e:
                if res.status_code == 504:
                    logger.warning(f"{self.session_name} | Attempt {attempts}: Connection timeout, retry after 3-5s...")
                    await asyncio.sleep(random.randint(3, 5))
                else:
                    logger.error(
                        f"{self.session_name} | <red>Unknown error while getting template info: <light-yellow>{e}</light-yellow></red>")
                    return None
        return None

    async def get_template_info(self, session: requests.Session, template_id: int):
        for attempts in range(3):
            try:
                res = session.get(f'{API_GAME_ENDPOINT}/image/template/{template_id}',
                                  headers=headers,
                                  verify=False)
                data = res.json()

                return data
            except Exception as e:
                if res.status_code == 504:
                    logger.warning(f"{self.session_name} | Attempt {attempts}: Connection timeout, retry after 3-5s...")
                    await asyncio.sleep(random.randint(3, 5))
                    continue
                else:
                    logger.error(
                        f"{self.session_name} | <red>Unknown error while getting template info: <light-yellow>{e}</light-yellow></red>")
                    break

    async def notpx_template(self, session):
        try:
            stats_req = session.get(f'{API_GAME_ENDPOINT}/image/template/my', headers=headers)
            stats_req.raise_for_status()
            cur_template = stats_req.json()
            return cur_template.get("id")
        except Exception as error:
            return 0

    async def need_join_template(self, session):
        try:
            tmpl = await self.notpx_template(session)
            self.template_to_join = template_to_join(tmpl)
            return str(tmpl) != self.template_to_join
        except Exception as error:
            logger.error(f"Failed to determine template join requirement: {error}")
            return False

    async def join_template(self, session, template_id):
        try:
            resp = session.put(f"{API_GAME_ENDPOINT}/image/template/subscribe/{template_id}", headers=headers)
            resp.raise_for_status()
            return resp.status_code == 204
        except Exception as error:
            logger.error(f"Error joining template: {error}")
            return False

    async def make_paint_request(self, session, yx, color, delay_start, delay_end):
        try:
            paint_request = session.post(f'{API_GAME_ENDPOINT}/repaint/start',
                                         json={"pixelId": int(yx), "newColor": color}, headers=headers)
            paint_request.raise_for_status()
            paint_request_json = paint_request.json()
            cur_balance = paint_request_json.get("balance", self.balance)
            change = max(0, cur_balance - self.balance)
            self.balance = cur_balance
            logger.success(
                f"{self.session_name} | Painted <cyan>{yx}</cyan> with color: <cyan>{color}</cyan> | Earned +<red>{change}</red> px | Balance: <cyan>{self.balance}</cyan> px")

            await asyncio.sleep(delay=randint(delay_start, delay_end))
        except requests.RequestException as e:
            logger.error(f"Failed to paint due to network error: {e}")
            await asyncio.sleep(5)
            return False

    async def paint(self, session, retries=20):
        try:
            stats_json = self.get_user_data(session)
            charges = stats_json.get('charges', 24)
            self.balance = stats_json.get('userBalance', 0)
            max_charges = stats_json.get('maxCharges', 24)
            logger.info(f"{self.session_name} | Charges: <yellow>{charges}/{max_charges}</yellow>")

            if await self.need_join_template(session):
                result = await self.join_template(session, self.template_to_join)
                if result:
                    logger.success(
                        f"{self.session_name} | <green>Successfully joined template <cyan>{self.template_to_join}</cyan></green>")

            for _ in range(charges):
                try:
                    q = get_cords_and_color(user_id=self.user_id, template=self.template_to_join)
                    coords = q["coords"]
                    color = q["color"]
                    yx = coords
                    await self.make_paint_request(session, yx, color, 5, 10)
                except Exception as error:
                    logger.warning(
                        f"{self.session_name} | <yellow>No pixels to paint or error occurred: {error}</yellow>")
                    return

        except requests.RequestException as error:
            logger.error(f"Error during painting: {error}")
            if retries > 0:
                await asyncio.sleep(10)
                await self.paint(session, retries=retries - 1)

    def paintv2(self, session: requests.Session, x, y, color, chance_left):
        pxId = y * 1000 + x + 1
        payload = {
            "pixelId": pxId,
            "newColor": color
        }

        res = session.post(f"{API_GAME_ENDPOINT}/repaint/start", headers=headers,
                           json=payload, verify=False)
        if res.status_code == 200:
            logger.success(
                f"{self.session_name} | <green>Painted <cyan>{pxId}</cyan> successfully new color: <cyan>{color}</cyan> | Earned <light-blue>{round(int(res.json()['balance']) - self.balance)}</light-blue> | Balace: <light-blue>{res.json()['balance']}</light-blue> | Repaint left: <yellow>{chance_left}</yellow></green>")
            self.balance = int(res.json()['balance'])
            return True
        else:
            logger.warning(f"{self.session_name} | Faled to repaint: {res.status_code}")
            return False

    async def repaintV5(self, session: requests.Session, template_info):
        try:
            if not template_info:
                return None

            curr_image = template_info.get('image', None)
            curr_start_x = template_info.get('x', 0)
            curr_start_y = template_info.get('y', 0)
            curr_image_size = template_info.get('image_size', 128)

            if not curr_image:
                return None

            user_data = self.get_user_data(session)

            if user_data is None:
                return None

            Total_attempt = user_data['charges']

            self.balance = user_data['userBalance']

            if Total_attempt > 0:
                logger.info(f"{self.session_name} | Starting to paint...")
            else:
                logger.info(f"{self.session_name} | No energy left...")
                return None

            tries = 2

            while Total_attempt > 0:
                try:
                    x = randint(0, curr_image_size - 5)
                    y = randint(0, curr_image_size - 5)
                    if Total_attempt == 0:
                        return
                    image_pixel = curr_image.getpixel((x, y))
                    image_hex_color = '#{:02x}{:02x}{:02x}'.format(*image_pixel)
                    Total_attempt -= 1
                    if self.paintv2(session, curr_start_x + x, curr_start_y + y, image_hex_color.upper(),
                                    Total_attempt) is False:
                        return
                    await asyncio.sleep(delay=random.randint(4, 10))
                except Exception as e:
                    if 'Gateway Timeout' in str(e):
                        status_data = self.get_user_data(session)

                        if status_data:
                            charges = status_data['charges']
                            self.balance = status_data['userBalance']

                        if tries > 0 and charges > 0:
                            logger.warning(
                                f"{self.session_name} | server is not response. Retrying..")
                            tries = tries - 1
                            sleep_time = random.randint(10, 20)
                            logger.info(f"{self.session_name} | Restart drawing in {round(sleep_time)} seconds...")
                            await asyncio.sleep(delay=sleep_time)
                            continue
                        else:
                            logger.warning(
                                f"{self.session_name} | server is not response. Go to sleep..")
                            break
                    elif "Bad Request" in str(e):
                        logger.warning(
                            f" Go to sleep..")
                        break
                    else:
                        logger.error(
                            f"{self.session_name} | <red>Unknown error while painting: <light-yellow>{e}</light-yellow></red>")
                        break

        except Exception as e:
            if 'Gateway Timeout' in str(e):
                logger.warning(f"{self.session_name} | <yellow>Server is not response.</yellow>")
            else:
                logger.error(
                    f"{self.session_name} | <red>Unknown error while painting: <light-yellow>{e}</light-yellow></red>")
            await asyncio.sleep(random.randint(2, 5))

    async def get_image(self, session: requests.Session, url, image_headers):
        image_filename = os.path.join(self.cache, url.split("/")[-1])

        try:
            if os.path.exists(image_filename):
                logger.info(f"{self.session_name} | Loading image from cache...")
                img = Image.open(image_filename)
                img.load()
                return img
        except Exception as e:
            logger.error(
                f"{self.session_name} | <red>Failed to load image from file: {image_filename} | Error: {e} <red>")

        try:
            logger.info(f"{self.session_name} | Downloading image from server...")
            res = session.get(url, headers=image_headers)

            if res.status_code == 200:
                img_data = res.content
                img = Image.open(io.BytesIO(img_data))

                img.save(image_filename)
                return img
            else:
                print(res.text)
                raise Exception(f"Failed to download image from {url}, status: {res.status_code}")
        except Exception as e:
            # traceback.print_exc()
            logger.error(f"{self.session_name} | Error while loading image from url: {url} | Error: {e}")
            return None

    async def run(self, proxy: str | None) -> None:
        access_token_created_time = 0
        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        headers["User-Agent"] = generate_random_user_agent(device_type='android', browser_type='chrome')
        http_client = CloudflareScraper(headers=headers, connector=proxy_conn)

        session = requests.Session()

        if proxy:
            proxy_check = await self.check_proxy(http_client=http_client, proxy=proxy)
            if proxy_check:
                proxy_type = proxy.split(':')[0]
                proxies = {
                    proxy_type: proxy
                }
                session.proxies.update(proxies)
                logger.info(f"{self.session_name} | bind with proxy ip: {proxy}")

        token_live_time = randint(1000, 1500)
        while True:
            try:
                if time_module.time() - access_token_created_time >= token_live_time:
                    if check_base_url() is False:
                        sys.exit(
                            "Detected api change! Stoped the bot for safety. Contact me here to update the bot: https://t.me/vanhbakaaa")

                    tg_web_data = self.query
                    headers['Authorization'] = f"initData {tg_web_data}"
                    tgencode = unquote(tg_web_data)
                    tgjson = tgencode.split('user=')[1].split('&chat_instance')[0]
                    user_data = json.loads(tgjson)
                    self.user_id = user_data['id']
                    self.balance = 0
                    access_token_created_time = time_module.time()
                    token_live_time = randint(1000, 1500)

                local_timezone = get_localzone()
                current_time = datetime.now(local_timezone)
                start_time = current_time.replace(hour=settings.SLEEP_TIME[0], minute=0, second=0, microsecond=0)
                end_time = current_time.replace(hour=settings.SLEEP_TIME[1], minute=0, second=0, microsecond=0)

                if end_time < start_time:
                    end_time += timedelta(days=1)

                if settings.NIGHT_MODE and (start_time <= current_time <= end_time):
                    time_to_sleep = (end_time - current_time).total_seconds()
                    logger.info(f"{self.session_name} | Sleeping for {time_to_sleep} seconds until {end_time}.")
                    await asyncio.sleep(time_to_sleep)

                elif self.login(session):
                    user = self.get_user_data(session)

                    if user:
                        self.maxtime = user['maxMiningTime']
                        self.fromstart = user['fromStart']
                        self.balance = int(user['userBalance'])
                        repaints = int(user['repaintsTotal'])
                        user_league = user['league']
                        logger.info(
                            f"{self.session_name} | Pixel Balance: <light-blue>{int(user['userBalance'])}</light-blue> | Pixel available to paint: <cyan>{user['charges']}</cyan> | User league: <yellow>{user_league}</yellow>")

                        if user['charges'] > 0:
                            if settings.USE_RANDOM_TEMPLATES:
                                self.template_id = random.choice(settings.RANDOM_TEMPLATES_ID)
                            elif settings.USE_CUSTOM_TEMPLATE:
                                self.template_id = settings.CUSTOM_TEMPLATE_ID

                            if settings.USE_NEW_PAINT_METHOD:
                                logger.info(f"{self.session_name} | Using the new painting method.")
                                inform(self.user_id, self.balance)
                                await self.paint(session)
                            else:

                                curr_template = await self.get_template(session)

                                await asyncio.sleep(randint(2, 5))
                                subcribed = True
                                if not curr_template or curr_template.get('id', 0) != self.template_id:
                                    subcribed = await self.subscribe_template(session, self.template_id)
                                    if subcribed:
                                        logger.success(
                                            f"{self.session_name} | <green>Successfully subscribed to the template | ID: <cyan>{self.template_id}</cyan></green>")
                                    await asyncio.sleep(random.randint(2, 5))

                                if subcribed:
                                    template_info = await self.get_template_info(session, self.template_id)
                                    if template_info:
                                        url = template_info['url']
                                        img_headers = dict()
                                        img_headers['Host'] = 'static.notpx.app'
                                        template_image = await self.get_image(session, url, image_headers=img_headers)
                                        self.default_template = {
                                            'x': template_info['x'],
                                            'y': template_info['y'],
                                            'image_size': template_info['imageSize'],
                                            'image': template_image,
                                        }
                                if not self.default_template['image']:
                                    image_url = 'https://app.notpx.app/assets/durovoriginal-CqJYkgok.png'
                                    image_headers = headers.copy()
                                    image_headers['Referer'] = 'https://app.notpx.app/'
                                    self.default_template['image'] = await self.get_image(session, image_url,
                                                                                          image_headers=image_headers)
                                    await asyncio.sleep(random.randint(2, 5))

                                logger.info(f"{self.session_name} | Using the old painting method.")
                                await self.repaintV5(session, template_info=self.default_template)

                                await asyncio.sleep(random.randint(2, 5))

                        r = random.uniform(2, 4)
                        if float(self.fromstart) >= self.maxtime / r:
                            self.claimpx(session)
                            await asyncio.sleep(random.uniform(2, 5))
                        if settings.AUTO_TASK:
                            res = session.get(f"{API_GAME_ENDPOINT}/mining/task/check/x?name=notpixel", headers=headers,
                                              verify=False)
                            if res.status_code == 200 and res.json()['x:notpixel'] and self.checked[1] is False:
                                self.checked[1] = True
                                logger.success("<green>Task Not pixel on x completed!</green>")
                            res = session.get(f"{API_GAME_ENDPOINT}/mining/task/check/x?name=notcoin", headers=headers,
                                              verify=False)
                            if res.status_code == 200 and res.json()['x:notcoin'] and self.checked[2] is False:
                                self.checked[2] = True
                                logger.success("<green>Task Not coin on x completed!</green>")
                            res = session.get(f"{API_GAME_ENDPOINT}/mining/task/check/paint20pixels", headers=headers,
                                              verify=False)
                            if res.status_code == 200 and res.json()['paint20pixels'] and self.checked[3] is False:
                                self.checked[3] = True
                                logger.success("<green>Task paint 20 pixels completed!</green>")

                            if repaints >= 2049:
                                res = session.get(f"{API_GAME_ENDPOINT}/mining/task/check/leagueBonusPlatinum",
                                                  headers=headers, verify=False)
                                if res.status_code == 200 and res.json()['leagueBonusPlatinum'] and self.checked[
                                    8] is False:
                                    self.checked[8] = True
                                    logger.success("<green>Upgraded to Plantium league!</green>")
                            if repaints >= 129:
                                res = session.get(f"{API_GAME_ENDPOINT}/mining/task/check/leagueBonusGold",
                                                  headers=headers, verify=False)
                                if res.status_code == 200 and res.json()['leagueBonusGold'] and self.checked[
                                    7] is False:
                                    self.checked[7] = True
                                    logger.success("<green>Upgraded to Gold league!</green>")
                            if repaints >= 9:
                                res = session.get(f"{API_GAME_ENDPOINT}/mining/task/check/leagueBonusSilver",
                                                  headers=headers, verify=False)
                                if res.status_code == 200 and res.json()['leagueBonusSilver'] and self.checked[
                                    6] is False:
                                    self.checked[6] = True
                                    logger.success("<green>Upgraded to Silver league!</green>")

                            res = session.get(f"{API_GAME_ENDPOINT}/mining/task/check/leagueBonusBronze",
                                              headers=headers, verify=False)
                            if res.status_code == 200 and res.json()['leagueBonusBronze'] and self.checked[5] is False:
                                self.checked[5] = True
                                logger.success(f"{self.session_name} | <green>Upgraded to Bronze league!</green>")

                        if settings.AUTO_UPGRADE_PAINT_REWARD:
                            await self.auto_upgrade_paint(session)
                        if settings.AUTO_UPGRADE_RECHARGE_SPEED:
                            await self.auto_upgrade_recharge_speed(session)
                        if settings.AUTO_UPGRADE_RECHARGE_ENERGY:
                            await self.auto_upgrade_energy_limit(session)

                    else:
                        logger.warning(f"{self.session_name} | <yellow>Failed to get user data!</yellow>")
                if self.multi_thread:
                    sleep_ = randint(settings.SLEEP_TIME_BETWEEN_EACH_ROUND[0],
                                     settings.SLEEP_TIME_BETWEEN_EACH_ROUND[1])
                    logger.info(f"{self.session_name} | Sleep {sleep_}s...")
                    await asyncio.sleep(sleep_)
                else:
                    await http_client.close()
                    session.close()
                    break
            except InvalidSession as error:
                raise error

            except Exception as error:
                traceback.print_exc()
                logger.error(f"{self.session_name} | Unknown error: {error}")
                await asyncio.sleep(delay=randint(60, 120))


async def run_query_tapper(query: str, name: str, proxy: str | None):
    try:
        sleep_ = randint(1, 15)
        logger.info(f" start after {sleep_}s")
        # await asyncio.sleep(sleep_)
        await Tapper(query=query, session_name=name, multi_thread=True).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"Invalid Query: {query}")

async def run_query_tapper1(querys: list[str], proxies):
    proxies_cycle = cycle(proxies) if proxies else None
    name = "Account"

    while True:
        i = 0
        for query in querys:
            try:
                await Tapper(query=query,session_name=f"{name} {i}",multi_thread=False).run(next(proxies_cycle) if proxies_cycle else None)
            except InvalidSession:
                logger.error(f"Invalid Query: {query}")

            sleep_ = randint(settings.DELAY_EACH_ACCOUNT[0], settings.DELAY_EACH_ACCOUNT[1])
            logger.info(f"Sleep {sleep_}s...")
            await asyncio.sleep(sleep_)

        sleep_ = randint(settings.SLEEP_TIME_BETWEEN_EACH_ROUND[0], settings.SLEEP_TIME_BETWEEN_EACH_ROUND[1])
        logger.info(f"<red>Sleep {sleep_}s...</red>")
        await asyncio.sleep(sleep_)
