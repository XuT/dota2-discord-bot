# dota2-discord-bot
Бот чекает нужных вам игроков и показывает результаты их последних матчей в Discord

![Screenshot_10](https://github.com/XuT/dota2-discord-bot/assets/7423848/c6486cfb-be0b-4a73-a6fd-c74d5545a88c)


# Установка:
Replit позволяет бесплатно разместить бота.
1. Регистрируйтесь на https://replit.com
	Create Repl - import from github - https://github.com/XuT/dota2-discord-bot
2. После ипорта репозитория в Tools - Secrets - New secrets создаем 3 ключа:
	BEARER_TOKEN - Ключ к API откуда берутся матчи. Брать тут: https://stratz.com/api (My Tokens)
	CHANNEL_ID - ID канала дикорда куда будем слать сообщения. Брать тут: https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-
	TOKEN - Токен бота дискорда который будет отправлять сообщения. Брать тут: https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token
![Screenshot_7](https://github.com/XuT/dota2-discord-bot/assets/7423848/08681e36-9916-4724-b0f2-6f1711d05bd1)

4. В файле main.py в PLAYERS вписываем PLAYER_ID и никнейм кого будем трекать. PLAYER_ID можно взять из url dotabuff. После этого бот уже можно запускать.
5. Repl.it если закрыть вкладку с сайтом остановит скрипт через какое-то время если к нему нет запросов, по этому мы будем дергать его с помощью сервиса https://uptimerobot.com/.
   Регистрируемся, жмем Add new monitor, Friendly Name любое, Monitoring Interval: 5 min, URL (or IP) берем в replit.com в окне webview.
7. ![Screenshot_9](https://github.com/XuT/dota2-discord-bot/assets/7423848/a062d815-bd42-4632-99a4-d9718b8e2aa4)
