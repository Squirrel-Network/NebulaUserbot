#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright SquirrelNetwork

import re
import time
import datetime
from config import Config
from pyrogram import Client, filters
from pyrogram.types.messages_and_media import message
from database.repository.user import UserRepository
from database.repository.superban import SuperbanRepository
from pyrogram.handlers import MessageHandler

app = Client(
    "my_account",
    api_id = Config.API_ID,
    api_hash = Config.API_HASH
)

@app.on_message(filters.command("getall") & filters.group & filters.user(Config.OWNER))
def get_all_chat_members(client,message):
    chat = message.chat.id
    for member in app.iter_chat_members(chat):
        current_time = datetime.datetime.utcnow().isoformat()
        if member.user.username is not None:
            user_id = member.user.id
            user_username = '@'+member.user.username
            user = UserRepository().getById(user_id)
            default_count_warn = 0
            if user:
                print("User {}, {} exists on the database".format(user_username, user_id))
                data = [(user_username,current_time,user_id)]
                UserRepository().update(data)
            else:
                print("The {}, {} user has been saved to the database".format(user_username, user_id))
                data = [(user_id,user_username,current_time,current_time)]
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
            user_id = member.user.id
            msg = "The {} user was kicked by the automatic system because he doesn't have a username".format(user_id)
            client.send_message(chat_id=message.chat.id, text=msg)
            app.kick_chat_member(chat, member.user.id, until_date=int(time.time()+30))
        else:
            print("User {} have a username".format(member.user.id))

@app.on_message(filters.command("checksuperban") & filters.group & filters.user(Config.OWNER))
def check_superban(client, message):
    chat = message.chat.id
    for member in app.iter_chat_members(chat):
        user_id = member.user.id
        row = SuperbanRepository().getById(user_id)
        if row:
            msg = "User {} was kicked out of chat because he is blacklisted\nMore information on https://squirrel-network.online/knowhere/".format(user_id)
            client.send_message(chat_id=message.chat.id, text=msg)
            app.kick_chat_member(chat, member.user.id)

@app.on_message(filters.chat("cas_feed"))
def from_cas(client, message):
    a_string = message.text
    numeric_filter = filter(str.isdigit, a_string)
    user_id = "".join(numeric_filter)
    row = SuperbanRepository().getById(int(user_id))
    if row:
        print("{} Exists on the database".format(user_id))
    else:
        motivation_text = "CASBAN CHANNEL IMPORT"
        id_operator = 1065189838
        user_date = datetime.datetime.utcnow().isoformat()
        data = [(int(user_id),motivation_text,user_date,id_operator)]
        SuperbanRepository().add(data)
        print("Correct Insert {} into Database".format(user_id))



app.add_handler(MessageHandler(get_all_chat_members))
app.add_handler(MessageHandler(from_cas))
app.run()