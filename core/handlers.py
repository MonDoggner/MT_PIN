from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart

import sqlite3
from core.config import GREETING
from core.config import TOKEN
import core.keyboards as k

import datetime
import requests
from bs4 import BeautifulSoup
from core.config import PINSAVER_URL

bot = Bot(token=TOKEN)
router = Router()

def create_or_update_database():
    # Connect to the database
    conn = sqlite3.connect('PIN_DATA.db')
    c = conn.cursor()

    # Create the users table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, telegram_id TEXT UNIQUE, username TEXT, free_uses INTEGER)''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

@router.message(CommandStart())
async def cmd_start(message: Message):
    # Create or update the database
    create_or_update_database()

    # Get user data
    user_id = message.from_user.id
    username = message.from_user.username

    # Connect to the database
    conn = sqlite3.connect('PIN_DATA.db')
    c = conn.cursor()

    # Insert user data into the database
    c.execute("INSERT OR IGNORE INTO users (telegram_id, username, free_uses) VALUES (?, ?, ?)", (user_id, username, 3))
    conn.commit()
    conn.close()

    await message.answer(GREETING, reply_markup=k.dev_keyboard)

async def save(url):

    data = {
        'url': url
    }

    response = requests.post(
        url=PINSAVER_URL, 
        data=data
    )    
    
    try:
        soup = BeautifulSoup(response.text, 'lxml')

        video = soup.find('video')
        video_src = video['src']

        return video_src        

    except Exception as e:
        print(f'{datetime.datetime.now()} Что-то пошло не так: {e}') 
    
@router.message(F.text)
async def start(message: Message):
    user_id = message.from_user.id

    # Connect to the database
    conn = sqlite3.connect('PIN_DATA.db')
    c = conn.cursor()

    if message.text and message.text[0:5] == 'https':
        # Get the user's current free_uses value
        c.execute("SELECT free_uses FROM users WHERE telegram_id = ?", (user_id,))
        free_uses = c.fetchone()[0]

        if free_uses > 0:
            await message.answer('Ваше видео уже скачивается...')
            video_src = await save(message.text)
            if video_src:
                await message.answer_video(video_src)
                await message.answer('Готово')

                # Decrement the user's free_uses value
                free_uses -= 1
                c.execute("UPDATE users SET free_uses = ? WHERE telegram_id = ?", (free_uses, user_id))
                conn.commit()
        elif free_uses == 0:
            await message.answer('Мы рады, что вам понравился наш продукт.')
            #Место для монетизации
            free_uses += 3
            c.execute("UPDATE users SET free_uses = ? WHERE telegram_id = ?", (free_uses, user_id))
            conn.commit()
            await message.answer('Для продолжения работы отправьте ссылку повторно')
    else:
        await message.answer('Ошибка. Ссылка введена некорректно.')

    conn.close()
    