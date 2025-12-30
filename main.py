import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# ================= ENV =================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID"))

if not STRING_SESSION:
    raise RuntimeError("STRING_SESSION is missing")

# ================= USERBOT =================

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION
)

# ================= MEMORY =================
# user_id -> message_thread_id
USER_TOPICS = {}

# ================= TOPIC FUNCTION =================
# 🔥 YE WAHI FUNCTION HAI JO TUMNE POOCHA

async def get_or_create_topic(client, user):
    uid = user.id

    if uid in USER_TOPICS:
        return USER_TOPICS[uid]

    try:
        topic = await client.create_forum_topic(
            chat_id=LOG_GROUP_ID,
            title=f"{user.first_name or 'User'} | {uid}"
        )
        USER_TOPICS[uid] = topic.message_thread_id
        print(f"✅ Topic created for {uid}")
        return topic.message_thread_id

    except Exception as e:
        print(f"❌ Topic creation failed: {e}")
        return None

# ================= HANDLER =================

@app.on_message(filters.private & filters.incoming)
async def log_private_messages(client: Client, message: Message):
    if not message.from_user:
        return

    user = message.from_user
    topic_id = await get_or_create_topic(client, user)

    # ❌ AGAR TOPIC NA BANE TO GENERAL ME MAT BHEJO
    if not topic_id:
        print("❌ No topic id, message skipped")
        return

    text = (
        f"👤 User: {user.mention}\n"
        f"🆔 ID: `{user.id}`\n\n"
    )

    if message.text:
        text += f"💬 Message:\n{message.text}"
    else:
        text += "📎 Media received"

    await client.send_message(
        chat_id=LOG_GROUP_ID,
        message_thread_id=topic_id,
        text=text
    )

# ================= START =================

async def main():
    await app.start()
    print("🚀 Userbot started")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
