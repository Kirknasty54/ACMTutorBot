import asyncio
from os import getenv
from openai import OpenAI, api_key
from dotenv import load_dotenv
import discord
from discord.ext import commands
from pymongo import MongoClient
from memori import Memori
from datetime import datetime
#load up environment variables
load_dotenv()
MONGODB_USER = getenv("MONGODB_USER")
MONGODB_PASSWORD = getenv("MONGODB_PASSWORD")
OPENAI_API_KEY = getenv("OPENAI_API_KEY")
DISCORD_TOKEN = getenv("DISCORD_TOKEN")
DISCORD_APP_ID = getenv("DISCORD_APP_ID")
client = OpenAI(api_key=OPENAI_API_KEY)
memori = Memori()
memori.openai = client
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

#mongodb setup
MONGODB_URI = getenv("MONGODB_URI")
DB_Name = getenv("DB_NAME")
mongo_client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))

try:
    mongo_client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    db = mongo_client[DB_Name]
    db.client.admin.command('ping')
    db.acm_discord.find_one()
    print("Pinged the db")
    print("Testing MongoDB connection...")
    print(f"Collections: {db.list_collection_names()}")
    print(f"Document count: {db.acm_discord.count_documents({})}")
    result = db.acm_discord.find_one()
    query= {"user": "test_user1"}
    result2 = list(db.acm_discord.find(query))

    print(f"Sample document: {result}")
    print(f"Sample document2: {result2}")
except Exception as e:
    print(e)

#set the intents and settings for the bot
intents = discord.Intents.default()
intents.message_content = True #needed to read user messages
bot = commands.Bot(command_prefix="!", intents=intents)

messages = []
SYSTEM_PROMPT = (
    "You are a friendly computer science tutor for the UCM ACM discord server."
    "You should be able to answer simple computer science and data structures questions that users might have."
    "Should be able to answer students and tell them what errors they're getting mean, what they're doing wrong in a code segement, how to fix it, etc. Stuff along that nature."
    "Make sure to have your responses be concise and under 2000 characters otherwise it won't allow to send via discord"
)

#memory functionality

#what will display when the bot is online
@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready to help CS students!")

#what will happen when a user sends a message mentioning the bot or via !tutor
@bot.event
async def on_message(message):

    #ignore self messages
    if message.author == bot.user:
        return
    #respond when @ or via !tutor
    if bot.user and (bot.user.mentioned_in(message) or message.content.startswith("!tutor")):
        user_input = message.content.replace(bot.user.mention, "").strip()
        print(user_input)

        try:
            #store user message in mongodb
            user_message_doc = {
                "user": str(message.author),
                "user_id": str(message.author.id),
                "message": user_input,
                "timestamp": datetime.now(),
                "channel_id": str(message.channel.id),
                "message_type": "user"
            }
            db.acm_discord.insert_one(user_message_doc)

            #ask open ai for a reply
            response = client.responses.create(
                model="gpt-5-mini",
                instructions=SYSTEM_PROMPT,
                input= message.content
            )

            #store openai model response in mongodb
            bot_message_doc = {
                "user": str(bot.user),
                "user_id": str(bot.user.id),
                "message": response.output_text,
                "timestamp": datetime.now(),
                "channel_id": str(message.channel.id),
                "message_type": "bot",
                "reply_to_user": str(message.author)
            }
            db.acm_discord.insert_one(bot_message_doc)


            #gives it realistic typing speed, improving user experience knowing the bot is at least responding
            wpm = 150
            seconds_per_word = 60 / wpm
            max_typing_time = 6
            typing_time = min(len(response.output_text) * seconds_per_word, max_typing_time)
            async with message.channel.typing():
                await asyncio.sleep(typing_time)

            await message.reply(response.output_text)
            print(response.output_text)
        except Exception as e:
            print(f"Error: {e}")
            await message.reply("i forgor \U0001F480")

bot.run(DISCORD_TOKEN)