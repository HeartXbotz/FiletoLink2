"""import datetime
import motor.motor_asyncio
from utils import send_log


class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups

    def new_user(self, id):
        return dict(
            id=id,
            join_date=datetime.date.today().isoformat(),
            shortner_api=None,
            shortner_url=None,
            caption=None,
        )

    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)

    async def hs_add_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.new_user(u.id)
            await self.col.insert_one(user)
            await send_log(b, u)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def total_chat_count(self):
        count = await self.grp.count_documents({})
        return count

    async def get_user(self, id):
        return await self.col.find_one({"id": id})

    async def add_user_pass(self, id, ag_pass):
        await self.add_user(int(id))
        await self.col.update_one({"id": int(id)}, {"$set": {"ag_p": ag_pass}})

    async def get_user_pass(self, id):
        user_pass = await self.col.find_one({"id": int(id)})
        return user_pass.get("ag_p", None) if user_pass else None

    async def is_user_exist(self, id):
        user = await self.col.find_one({"id": int(id)})
        return bool(user)

    async def get_all_users(self):
        return self.col.find({})

    async def get_all_chats(self):
        return self.grp.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({"id": int(user_id)})

    async def set_caption(self, id, caption):
        await self.col.update_one({"id": int(id)}, {"$set": {"caption": caption}})

    async def get_caption(self, id):
        user = await self.col.find_one({"id": int(id)})
        return user.get("caption", None)

    async def update_user_info(self, user_id, value: dict, tag="$set"):
        user_id = int(user_id)
        myquery = {"id": user_id}
        newvalues = {tag: value}
        await self.col.update_one(myquery, newvalues)
"""

import datetime
import motor.motor_asyncio
from utils import send_log


class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups

    async def initialize(self):
        """Create necessary indexes for optimized queries."""
        await self.col.create_index("id", unique=True)
        await self.grp.create_index("id", unique=True)

    def new_user(self, id):
        """Create a default user dictionary."""
        return {
            "id": id,
            "join_date": datetime.date.today().isoformat(),
            "shortner_api": None,
            "shortner_url": None,
            "caption": None,
            "ag_p": None,  # Placeholder for additional data (e.g., passwords)
        }

    async def add_user(self, id):
        """Add a new user if not already in the database."""
        if not await self.is_user_exist(id):
            user = self.new_user(id)
            await self.col.insert_one(user)

    async def hs_add_user(self, bot, message):
        """Handle user addition and log new users."""
        user = message.from_user
        if not await self.is_user_exist(user.id):
            await self.add_user(user.id)
            await send_log(bot, user)

    async def total_users_count(self):
        """Return the total number of users."""
        return await self.col.count_documents({})

    async def total_chat_count(self):
        """Return the total number of groups/chats."""
        return await self.grp.count_documents({})

    async def get_user(self, id):
        """Fetch user data by ID."""
        return await self.col.find_one({"id": int(id)})

    async def add_user_pass(self, id, ag_pass):
        """Set a user's password field."""
        if not await self.is_user_exist(id):
            await self.add_user(id)
        await self.col.update_one({"id": int(id)}, {"$set": {"ag_p": ag_pass}})

    async def get_user_pass(self, id):
        """Retrieve the stored password for a user."""
        user = await self.col.find_one({"id": int(id)})
        return user.get("ag_p") if user else None

    async def is_user_exist(self, id):
        """Check if a user exists in the database."""
        try:
            return bool(await self.col.find_one({"id": int(id)}))
        except Exception as e:
            print(f"[DB ERROR] Failed to check user existence: {e}")
            return False

    async def get_all_users(self):
        """Retrieve all users."""
        return self.col.find({})

    async def get_all_chats(self):
        """Retrieve all groups."""
        return self.grp.find({})

    async def delete_user(self, user_id):
        """Delete a user from the database."""
        await self.col.delete_many({"id": int(user_id)})

    async def set_caption(self, id, caption):
        """Update caption for a specific user."""
        await self.col.update_one({"id": int(id)}, {"$set": {"caption": caption}})

    async def get_caption(self, id):
        """Retrieve the stored caption for a user."""
        user = await self.col.find_one({"id": int(id)})
        return user["caption"] if user and "caption" in user else None

    async def update_user_info(self, user_id, value: dict, tag="$set"):
        """Update user information using MongoDB operators."""
        try:
            await self.col.update_one({"id": int(user_id)}, {tag: value})
            return True
        except Exception as e:
            print(f"[DB ERROR] Failed to update user info: {e}")
            return False

    async def update_group_info(self, chat_id, value: dict, tag="$set"):
        """Update group settings using MongoDB operators."""
        try:
            await self.grp.update_one({"id": int(chat_id)}, {tag: value}, upsert=True)
            return True
        except Exception as e:
            print(f"[DB ERROR] Failed to update group info: {e}")
            return False

    async def get_group_info(self, chat_id):
        """Retrieve group settings."""
        return await self.grp.find_one({"id": int(chat_id)})

    async def delete_group(self, chat_id):
        """Delete a group from the database."""
        await self.grp.delete_many({"id": int(chat_id)})
