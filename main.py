import time
from config import Config
from pyrogram import Client, filters
from database.repository.user import UserRepository

app = Client(
    "my_account",
    api_id = Config.API_ID,
    api_hash = Config.API_HASH
)


@app.on_message(filters.command("getall") & filters.group & filters.user(Config.OWNER))
def get_all_chat_members(client, message):
    chat = message.chat.id
    for member in app.iter_chat_members(chat):
        if member.user.username is not None:
            user_id = member.user.id
            user_username = '@'+member.user.username
            user = UserRepository().getById(user_id)
            default_count_warn = 0
            if user:
                print("User {}, {} exists on the database".format(user_username, user_id))
                data = [(user_username,user_id)]
                UserRepository().update(data)
            else:
                print("The {}, {} user has been saved to the database".format(user_username, user_id))
                data = [(user_id,user_username,default_count_warn)]
                UserRepository().add(data)
            data_mtm = [(user_id, chat, default_count_warn)]
            UserRepository().add_into_mtm(data_mtm)

@app.on_message(filters.command("start") & filters.private)
def start_command(client, message):
    message.reply_text("I am a Userbot created by @squirrelnetwork in support of @nebuladevbot")

@app.on_message(filters.command("checkusername") & filters.group & filters.user(Config.OWNER))
def check_user_username(client, message):
    chat = message.chat.id
    for member in app.iter_chat_members(chat):
        if member.user.username is None:
            msg = "The TEST user was kicked by the automatic system because he doesn't have a username"
            client.send_message(chat_id=message.chat.id, text=msg)
            app.kick_chat_member(chat, member.user.id, until_date=int(time.time()+30))
        else:
            print("User {} have a username".format(member.user.id))


app.run()