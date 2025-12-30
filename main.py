import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# ================= CONFIG =================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("SESSION_STRING")

# Log group (forum-enabled supergroup)
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID"))

# ================= USERBOT =================

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# ================= MEMORY =================
# user_id -> message_thread_id
USER_TOPICS = {}

# ================= FUNCTIONS =================

async def get_or_create_topic(client: Client, user):
    uid = user.id

    # Reuse existing topic (runtime)
    if uid in USER_TOPICS:
        return USER_TOPICS[uid]

    title = f"{user.first_name or 'User'} | {uid}"

    try:
        topic = await client.create_forum_topic(
            chat_id=LOG_GROUP_ID,
            title=title
        )
        USER_TOPICS[uid] = topic.message_thread_id
        print(f"✅ Topic created for {uid}: {topic.message_thread_id}")
        return topic.message_thread_id

    except Exception as e:
        print(f"❌ Topic creation failed for {uid}: {e}")
        return None

# ================= HANDLER =================

@app.on_message(filters.private & filters.incoming)
async def log_private_messages(client: Client, message: Message):
    if not message.from_user:
        return

    user = message.from_user
    topic_id = await get_or_create_topic(client, user)

    text = (
        f"👤 User: {user.mention}\n"
        f"🆔 ID: `{user.id}`\n\n"
    )

    if message.text:
        text += f"💬 Message:\n{message.text}"
    else:
        text += "📎 Media received"

    if topic_id:
        await client.send_message(
            chat_id=LOG_GROUP_ID,
            message_thread_id=topic_id,
            text=text
        )
    else:
        # fallback (should not happen)
        await client.send_message(
            chat_id=LOG_GROUP_ID,
            text="❌ Topic create failed\n\n" + text
        )

# ================= START =================

async def main():
    await app.start()
    print("🚀 Userbot started")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
