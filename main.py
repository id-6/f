# Requier Modules 
from pyrogram import Client, types, filters, enums, raw
import pyromod

from pyrogram.errors import (
    PhoneNumberInvalid, PhoneCodeInvalid, SessionPasswordNeeded, PasswordHashInvalid, PhoneCodeExpired
)
import asyncio

# Bot Config
class config:
    API_KEY = "5870809786:AAFxbB6M9p1BgABJbFuxyQOHN5dgiESszvs"
    API_HASH = "9cf3a6feb6dfcc7c02c69eb2c286830e"
    API_ID = 18421930

# start Pyrogram App 
app = Client(
    name="rad", 
    bot_token=config.API_KEY, 
    api_hash=config.API_HASH, 
    api_id=config.API_ID
)



@app.on_message(filters.private & filters.regex('^/start$'))
async def ON_START_BOT(app: Client, message: types.Message):
    await app.send_message(
        chat_id=message.chat.id ,text="Welcome To Delete Telegram Account Bot.", 
        reply_markup=types.InlineKeyboardMarkup([
            [
                types.InlineKeyboardButton(text='Delete Account', callback_data="DELETACCOUNT")
            ]
        ])
    )

SESSSIONS = None
PASSWORD = None

@app.on_callback_query(filters.regex('^DELETACCOUNT$'))
async def DELET_ACCOUNT(app: Client, query: types.CallbackQuery):
    global SESSSIONS
    await app.edit_message_text(
        chat_id=query.message.chat.id, message_id=query.message.id , 
        text='Send Me Phone Number', reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton('BACK', 'BACK')]])
    )

    # On Listen Phone Number 
    data = await app.listen(chat_id=query.from_user.id, filters=filters.text & filters.private)

    # Check PHone and start Client 
    PhoneNumber = data.text
    message_data = await app.send_message(
        chat_id=query.message.chat.id, 
        text='With Check data .'
    )
    
    session_client = Client(
        name=":memory:",
        api_hash=config.API_HASH, api_id=config.API_ID, in_memory=True
    )
    try:
        await session_client.connect()
        phon_code_data = await session_client.send_code(
            phone_number=PhoneNumber
        )

    except PhoneNumberInvalid as Err:
        await app.edit_message_text(
            chat_id=query.message.chat.id, message_id=message_data.id, 
            text="Phone NUmber Invalid", reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton('BACK', 'BACK')]])
        )
        await session_client.disconnect()
        return  
      
    await app.edit_message_text(
        chat_id=query.message.chat.id, message_id=message_data.id, 
        text='Send Phone Code ', reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton('BACK', 'BACK')]])
    )

    # On Listen Ver Code 
    data = await app.listen(chat_id=query.from_user.id, filters=filters.text & filters.private)

    
    message_data = await app.send_message(
        chat_id=query.message.chat.id, 
        text='With Check data .'
    )

    # Check COde
    try: 
        VerCode = int(data.text)
    except:
        await session_client.disconnect()
        await app.edit_message_text(
            chat_id=query.message.chat.id, message_id=message_data.id, 
            text='Phone Code Error', reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton('BACK', 'BACK')]])
        )
        return

    # Start Logins Session
    try:
        await session_client.sign_in(
            phone_code=str(VerCode), 
            phone_code_hash=phon_code_data.phone_code_hash, 
            phone_number=PhoneNumber
        )

    except (PhoneCodeInvalid ,PhoneCodeExpired) as Err:
        await session_client.disconnect()
        await app.edit_message_text(
            chat_id=query.message.chat.id, message_id=message_data.id, 
            text='Phone Code Invalid' ,reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton('BACK', 'BACK')]])
        )
        return
    
    
    except SessionPasswordNeeded as Err:
        await app.edit_message_text(
            chat_id=query.message.chat.id, message_id=message_data.id, 
            text='Send Me Account Password ', reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton('BACK', 'BACK')]])
        )
        
        # On Listen Password 
        data = await app.listen(chat_id=query.from_user.id, filters=filters.text & filters.private)

        
        Password = data.text
        PASSWORD = Password
        message_data = await app.send_message(
            chat_id=query.message.chat.id, 
            text='With Check Data'
            )

        # CHcek Password 
        try: 
            await session_client.check_password(Password)
         
        except PasswordHashInvalid as Err:
            await app.edit_message_text(
                    chat_id=query.message.chat.id, message_id=message_data.id, 
                    text='Password Invalid ', reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton('BACK', 'BACK')]])
            )
            await session_client.disconnect()
            return
        
    #  ADD Session Data 
    session_String = await session_client.export_session_string()
    SESSSIONS = session_String
    await session_client.disconnect()


    await app.edit_message_text(
        chat_id=query.message.chat.id, message_id=message_data.id, 
        text="Are you sure you want to delete the account?", reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text="Yes Delete", callback_data='OnDelete')]])
    )



@app.on_callback_query(filters.regex('^OnDelete$'))
async def DELET_ACCOUNT(app: Client, query: types.CallbackQuery):
    async with Client(':memory:', api_hash="", api_id="",  session_string=SESSSIONS) as session_client:
        await session_client.invoke(raw.functions.account.DeleteAccount(
            reason="not"))

    await app.edit_message_text(
        chat_id=query.message.chat.id, message_id=query.message.id, 
        text="The account was deleted successfully"
    )




asyncio.run(app.run())

