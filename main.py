from os import getenv
from openai import OpenAI
from dotenv import load_dotenv
import discord
from discord.ext import commands

#load up environment variables
load_dotenv()
OPENAI_API_KEY = getenv("OPENAI_API_KEY")
DISCORD_TOKEN = getenv("DISCORD_TOKEN")
DISCORD_APP_ID = getenv("DISCORD_APP_ID")
client = OpenAI(api_key=OPENAI_API_KEY)

#set the intents and settings for the bot
intents = discord.Intents.default()
intents.message_content = True #needed to read user messages
bot = commands.Bot(command_prefix="!", intents=intents)

messages = []
SYSTEM_PROMPT = (
    "You are a friendly computer science tutor for the UCM ACM discord server."
    "You should be able to answer simple computer science and data structures questions that users might have."
    "Should be able to answer students and tell them what errors they're getting mean, what they're doing wrong in a code segement, how to fix it, etc. Stuff along that nature"
)

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
    messages.append(
        {"role": "user", "content": message.content}
    )

    print(messages)
    #respond when @ or via !tutor
    if bot.user and (bot.user.mentioned_in(message) or message.content.startswith("!tutor")):
        user_input = message.content.replace(bot.user.mention, "").strip()
        try:
            #ask open ai for a reply
            response = client.responses.create(
                model="gpt-5-mini",
                instructions=SYSTEM_PROMPT,
                input= message.content
            )

            await message.reply(response.output_text)
            print(response.output_text)
        except Exception as e:
            print(f"Error: {e}")
            await message.reply("i forgor \U0001F480")

bot.run(DISCORD_TOKEN)