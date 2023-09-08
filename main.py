import requests
import discord
from discord import Intents
import asyncio
import json
import ranktier
from datetime import datetime, timedelta
from PIL import Image
from loguru import logger
from webserver import keep_alive
import os

# CONFIG
BEARER_TOKEN = my_secret = os.environ[
  'BEARER_TOKEN']  # Ключ к API откуда берутся матчи. Брать тут: https://stratz.com/api (My Tokens). Для REPL.IT создать Sercrets c этим именем и ключем
CHANNEL_ID = os.environ[
  'CHANNEL_ID']  # ID канала дикорда куда будем слать сообщения. Брать тут: https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID- Для REPL.IT создать Sercrets c этим именем и ключем
TOKEN = os.environ[
  'TOKEN']  # Токен бота дискорда который будет отправлять. Брать тут: https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token Для REPL.IT создать Sercrets c этим именем и ключем

# Список игроков кого будем чекать player_id можно взять из url dotabuff
PLAYERS = [{
  "PLAYER_ID": "35507228",
  "NICKNAME": "XuT"
}, {
  "PLAYER_ID": "93460388",
  "NICKNAME": "de.lsnk"
}, {
  "PLAYER_ID": "61624206",
  "NICKNAME": "Stealer"
}, {
  "PLAYER_ID": "107702115",
  "NICKNAME": "sparky"
}, {
  "PLAYER_ID": "95943488",
  "NICKNAME": "Ростовский"
}]

# Дальше не трогать

last_sent_matches = {}
logger.add("bot.log", rotation="1 day", retention="7 days", level="DEBUG")
MATCH_DATA_FILE = 'matches.json'
if os.path.exists(MATCH_DATA_FILE):
    try:
        with open(MATCH_DATA_FILE, 'r') as file:
            last_sent_matches = json.load(file)
    except json.JSONDecodeError:
        print(f"Error loading JSON data from {MATCH_DATA_FILE}. Initializing last_sent_matches as an empty dictionary.")
else:
    print(f"{MATCH_DATA_FILE} not found. Initializing last_sent_matches as an empty dictionary.")
intents = Intents.default()
intents.typing = False
intents.presences = False
client = discord.Client(intents=intents)
HERO_IDS = {
  1: "antimage",
  2: "axe",
  3: "bane",
  4: "bloodseeker",
  5: "crystal_maiden",
  6: "drow_ranger",
  7: "earthshaker",
  8: "juggernaut",
  9: "mirana",
  10: "morphling",
  11: "nevermore",
  12: "phantom_lancer",
  13: "puck",
  14: "pudge",
  15: "razor",
  16: "sand_king",
  17: "storm_spirit",
  18: "sven",
  19: "tiny",
  20: "vengefulspirit",
  21: "windrunner",
  22: "zuus",
  23: "kunkka",
  25: "lina",
  26: "lion",
  27: "shadow_shaman",
  28: "slardar",
  29: "tidehunter",
  30: "witch_doctor",
  31: "lich",
  32: "riki",
  33: "enigma",
  34: "tinker",
  35: "sniper",
  36: "necrolyte",
  37: "warlock",
  38: "beastmaster",
  39: "queenofpain",
  40: "venomancer",
  41: "faceless_void",
  42: "skeleton_king",
  43: "death_prophet",
  44: "phantom_assassin",
  45: "pugna",
  46: "templar_assassin",
  47: "viper",
  48: "luna",
  49: "dragon_knight",
  50: "dazzle",
  51: "rattletrap",
  52: "leshrac",
  53: "furion",
  54: "life_stealer",
  55: "dark_seer",
  56: "clinkz",
  57: "omniknight",
  58: "enchantress",
  59: "huskar",
  60: "night_stalker",
  61: "broodmother",
  62: "bounty_hunter",
  63: "weaver",
  64: "jakiro",
  65: "batrider",
  66: "chen",
  67: "spectre",
  69: "doom_bringer",
  68: "ancient_apparition",
  70: "ursa",
  71: "spirit_breaker",
  72: "gyrocopter",
  73: "alchemist",
  74: "invoker",
  75: "silencer",
  76: "obsidian_destroyer",
  77: "lycan",
  78: "brewmaster",
  79: "shadow_demon",
  80: "lone_druid",
  81: "chaos_knight",
  82: "meepo",
  83: "treant",
  84: "ogre_magi",
  85: "undying",
  86: "rubick",
  87: "disruptor",
  88: "nyx_assassin",
  89: "naga_siren",
  90: "keeper_of_the_light",
  91: "wisp",
  92: "visage",
  93: "slark",
  94: "medusa",
  95: "troll_warlord",
  96: "centaur",
  97: "magnataur",
  98: "shredder",
  99: "bristleback",
  100: "tusk",
  101: "skywrath_mage",
  102: "abaddon",
  103: "elder_titan",
  104: "legion_commander",
  105: "techies",
  106: "ember_spirit",
  107: "earth_spirit",
  108: "abyssal_underlord",
  109: "terrorblade",
  110: "phoenix",
  111: "oracle",
  112: "winter_wyvern",
  113: "arc_warden",
  114: "monkey_king",
  119: "dark_willow",
  120: "pangolier",
  121: "grimstroke",
  123: "hoodwink",
  126: "void_spirit",
  128: "snapfire",
  129: "mars",
  135: "dawnbreaker",
  136: "marci",
  137: "primal_beast",
  138: "muerta"
}


def get_matches(player_id):
  url = 'https://api.stratz.com/graphql'
  headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {BEARER_TOKEN}'
  }

  query = f"""
    query {{
        player(steamAccountId: {player_id}) {{
            matches(request: {{ isParsed: true, orderBy: DESC, take: 15 }}) {{
                id
                actualRank
                rank
                durationSeconds
                bottomLaneOutcome
                midLaneOutcome
                topLaneOutcome
                startDateTime
                players(steamAccountId: {player_id}) {{
                    isRadiant
                    lane
                    isVictory
                    heroId
                    kills
                    deaths
                    assists
                    heroDamage
                    goldPerMinute
                    position
                    intentionalFeeding
                    imp
                    award
                    item0Id
                    item1Id
                    item2Id
                    item3Id
                    item4Id
                    item5Id
                    backpack0Id
                    backpack1Id
                    backpack2Id
                    neutral0Id
                    steamAccount{{
                        avatar
                    }}
                }}
            }}
        }}
    }}
    """

  response = requests.post(url, headers=headers, json={'query': query})
  if response.status_code == 200:  # Проверяем успешность запроса
    data = response.json()
    if 'data' in data:  # Проверяем наличие ключа 'data' в ответе
      return data['data']
  return None


def format_duration(duration):
  minutes = duration // 60
  seconds = duration % 60
  return f"{minutes}:{seconds:02d}"


def get_hero_icon_url(hero_id):
  hero_name = HERO_IDS.get(hero_id)
  if hero_name:
    return f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/{hero_name}.png"
  else:
    return None


def get_win_loss_stats(matches_data):
  win_count = 0
  loss_count = 0

  current_time = datetime.now()
  current_timestamp = current_time.timestamp()
  one_day_ago = current_time - timedelta(days=1)
  one_day_ago_timestamp = one_day_ago.timestamp()

  for match in matches_data["player"]["matches"]:
    start_timestamp = match["startDateTime"]
    is_victory = match["players"][0]["isVictory"]

    if start_timestamp >= one_day_ago_timestamp and start_timestamp <= current_timestamp:
      if is_victory:
        win_count += 1
      else:
        loss_count += 1

  return win_count, loss_count


async def send_latest_match_result(channel):
    for player in PLAYERS:
        player_id = player["PLAYER_ID"]
        player_nickname = player["NICKNAME"]
        matches_data = get_matches(player_id)

        if matches_data is None:
            continue  # Если данные о матчах равны None, пропустите итерацию

        # Получите ID последнего матча
        latest_match_id = matches_data["player"]["matches"][0]["id"]

        # Проверьте, был ли этот матч уже отправлен
        if last_sent_matches.get(player_id) == latest_match_id:
            continue  # Если этот матч уже был отправлен, пропустите его

        # Если этот матч не был отправлен, сохраните его ID
        last_sent_matches[player_id] = latest_match_id
        with open(MATCH_DATA_FILE, 'w') as file:
            json.dump(last_sent_matches, file)
        win_count, loss_count = get_win_loss_stats(matches_data)
        logger.info(f"Новый матч {player_nickname}: {latest_match_id}")
        match = matches_data["player"]["matches"][0]
        player_data = match["players"][0]
        outcome = None

        last_5_matches = matches_data["player"]["matches"][:5]  # Получить последние 5 матчей
        player_is_radiant = player_data["isRadiant"]
        player_lane = player_data["lane"]

        LANE_OUTCOME_MAP = {
            True: {
                "SAFE_LANE": "bottomLaneOutcome",
                "MID_LANE": "midLaneOutcome",
                "OFF_LANE": "topLaneOutcome",
            },
            False: {
                "SAFE_LANE": "topLaneOutcome",
                "MID_LANE": "midLaneOutcome",
                "OFF_LANE": "bottomLaneOutcome",
            }
        }

        OUTCOME_NAME_MAP ={
        True: {
            "TIE": "Ровно",
            "RADIANT_VICTORY": "Разьебал",
            "RADIANT_STOMP": "Жестко разъебал",
            "DIRE_VICTORY": "Высосал",
            "DIRE_STOMP": "Пиздец высосал",
        },
        False: {
            "TIE": "Ровно",
            "RADIANT_VICTORY": "Высосал",
            "RADIANT_STOMP": "Пиздец высосал",
            "DIRE_VICTORY": "Разьебал",
            "DIRE_STOMP": "Жестко разъебал",
        }
        }

        outcome = LANE_OUTCOME_MAP[player_is_radiant][player_lane]
        outcome_name = OUTCOME_NAME_MAP[player_is_radiant][match[outcome]]

        match_result_images = []  # Список для хранения изображений результатов матчей

        for match in last_5_matches[::-1]:
            player_data = match["players"][0]
            is_victory = player_data["isVictory"]  # Получить значение победы из данных игрока

            color_matches = 0x00ff00 if is_victory else 0xff0000  # Определить цвет в зависимости от значения победы

            if color_matches == 0x00ff00:
                image = ":green_square:"  # Замените на URL зеленого изображения
            else:
                image = ":red_square:"  # Замените на URL красного изображения

            match_result_images.append(image)  # Добавить изображение в список
        hero_id = player_data["heroId"]
        hero_icon_url = get_hero_icon_url(hero_id)
        victory = player_data["isVictory"]
        if victory:
            color = 0x00ff00  # Зеленый цвет
        else:
            color = 0xff0000  # Красный цвет
        avatar = player_data["steamAccount"]["avatar"]
        nickname = player["NICKNAME"]
        kills = player_data["kills"]
        deaths = player_data["deaths"]
        assists = player_data["assists"]
        rank = ranktier.Rank(str(match["rank"]))
        position = player_data.get("position")
        if position is not None:
            position = position.split("_")[-1]
        else:
            position = "Unknown"
        imp = player_data["imp"]
        award = player_data["award"]

        embed = discord.Embed(description=" ".join(match_result_images[::-1]) if match_result_images else "None", color=color)
        embed.set_thumbnail(url=hero_icon_url)
        embed.add_field(name="Время", value=format_duration(match["durationSeconds"]))
        embed.add_field(name="KDA", value=f"{kills}/{deaths}/{assists}")
        embed.add_field(name="Аверага", value=f"{rank}")

        if award != "NONE":
            embed.add_field(name="Матч", value=f"Позиция: {position}\nImp: `{imp}\n`Лайн: {outcome_name}\nНаграда: `{award}` :medal:\n")
        else:
            embed.add_field(name="Матч", value=f"Позиция: {position}\nImp: `{imp}\n`Лайн: {outcome_name}\n")

        match_id = match["id"]
        embed.add_field(name="Статистика:", value=f"Сегодня: {win_count}/{loss_count}")

        embed.set_author(name=f"{nickname}", url=f"https://stratz.com/matches/{match_id}", icon_url=f"{avatar}")
        embed.set_footer(text="")

        # Генерация изображений
        item_ids = [
            player_data.get('item0Id'),
            player_data.get('item1Id'),
            player_data.get('item2Id'),
            player_data.get('item3Id'),
            player_data.get('item4Id'),
            player_data.get('item5Id')
        ]

        item_images = []
        image_directory = "assets/items/"

        for item_id in item_ids:
            item_image_path = f"{image_directory}{item_id}.png"
            try:
                item_image = Image.open(item_image_path)
                item_images.append(item_image)
            except FileNotFoundError:
                print(f"Изображение для item_id {item_id} не найдено.")

        image_width = sum(image.width for image in item_images[:3])
        image_height = 60

        result_image = Image.new("RGBA", (image_width, image_height))

        x_offset = 0
        y_offset = 0
        for item_image in item_images:
            result_image.paste(item_image, (x_offset, y_offset))
            x_offset += item_image.width
            if x_offset >= image_width:
                x_offset = 0
                y_offset += item_image.height

        try:
            image_filename = f"{player_id}_items.png"  # Имя файла для сохранения изображения
            result_image.save(image_filename)
            file = discord.File(image_filename)
            embed.set_image(url=f"attachment://{image_filename}")
        except Exception as e:
            print(f"Ошибка при сохранении изображения: {e}")

        await channel.send(embed=embed, file=file)

        match_id = match["id"]


@client.event
@client.event
async def on_ready():
    channel = client.get_channel(int(CHANNEL_ID))
    if channel:
        while True:
            await send_latest_match_result(channel)  # Вызов функции для отправки сообщения о последнем матче
            logger.info("Спим...")
            await asyncio.sleep(300)  # Задержка в секундах перед повторным выполнением функции
    else:
        print("Не удалось найти указанный канал:")


client.run(TOKEN)
