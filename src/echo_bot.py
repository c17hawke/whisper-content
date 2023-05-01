"""
This is a echo bot.
It echoes any incoming text messages.
"""
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
import os
from pathlib import Path
import openai
import subprocess
import json
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
API_TOKEN = os.getenv("TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
storage = MemoryStorage()
dp = Dispatcher(bot)#, storage=storage)



def oga_to_wav(oga_file_path, wav_file_path):
    # Load the .oga file
    subprocess.call(["./ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe", "-i", 
                     oga_file_path, wav_file_path, "-y"])
    print(f"successfully exported at: {wav_file_path}")
    logging.info(f"successfully exported at: {wav_file_path}")


@dp.message_handler(content_types=['voice'])
async def handle_audio(message: types.Message):

    file = await bot.get_file(message.voice.file_id)
    file_path = file.file_path
    print(file_path)
    _ = await bot.download_file(file_path, destination_dir="artifacts")
    audio_input_filepath = Path(f"./artifacts/{file_path}")
    oga_to_wav(oga_file_path=audio_input_filepath, wav_file_path="output.wav")
    wav_file_path = "output.wav"
    import requests

    headers = {
        'Authorization': 'Bearer {}'.format(os.getenv("OPENAI_API")),
    }

    files = {
        'file': open(wav_file_path, "rb"),
        'model': (None, 'whisper-1'),
    }
    response = requests.post('https://api.openai.com/v1/audio/transcriptions', 
                             headers=headers, files=files)
    print(response.text)
    send_response = json.loads(response.text)['text']
    
    await message.reply(send_response)

if __name__ == '__main__':
    executor.start_polling(dp)

