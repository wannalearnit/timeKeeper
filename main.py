import logging
import sqlite3
import time


from statdraw import drawdailyshit
from aiogram import Bot, Dispatcher, executor, types
import asyncio

API_TOKEN = '5451160025:AAGFakoc_h0rKWuWyqPFlJ9EdjV_wj6xK48'
base = sqlite3.connect('TimeBase.db')
cur = base.cursor()


logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    with open("list_of_commands.txt", "r") as file:
        list_of_commands = file.read()
    await message.reply(list_of_commands)


@dp.message_handler(commands=['set'])
async def set_timer(message: types.Message):
    amp = cur.execute("SELECT timestamp FROM users_calls WHERE (user_id = ?)", [message.from_user.id]).fetchall()
    if bool(amp):
        am = amp[0][0] - int(time.time())

        await message.answer('Таймер уже установлен, задача закончится через %d мин. и %d сек. '
                             '\nНе отвлекайтесь!!!' % (am // 60,  am % 60))
    else:
        line = message.text[5:]
        if line.isdigit() and int(line) <= 120:
            vrem = int(time.time()) + int(line) * 60
            cur.execute("INSERT INTO users_calls VALUES (?, ?, ?)", [message.from_user.id, vrem, int(line)])
            base.commit()
            await message.answer('таймер на ' + line + ' минут установлен')
        else:
            await message.answer('Syntax.Error')


@dp.message_handler(commands=['stat'])
async def stat(message: types.Message):
    drawdailyshit(message.from_user.id)
    photo = open(str(message.from_user.id) + '.png', 'rb')
    await message.answer_photo(photo=photo)


async def spammer(timer):
    while True:
        kp = cur.execute("SELECT * FROM users_calls ORDER BY timestamp")
        for row in kp:
            user_id = row[0]
            tstamp = row[1]
            dur = row[2]
            if tstamp < int(time.time()):
                await bot.send_message(user_id, 'time is gone')
                cur.execute('''INSERT INTO all_sets VALUES (?, ?, ?)''', [user_id, tstamp, dur])
                cur.execute("DELETE FROM users_calls WHERE (user_id = ?) AND (timestamp = ?)", [user_id, tstamp])
                base.commit()
            else:
                break
        await asyncio.sleep(timer)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(spammer(1))
    executor.start_polling(dp, skip_updates=True)
