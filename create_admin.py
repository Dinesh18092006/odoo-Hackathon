import asyncio
import sys
import os

# Ensure we can import from the app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import update, select
from database import AsyncSessionLocal as async_session
from models.user import User
from auth.password_handler import hash_password

async def create_demo_admin():
    async with async_session() as session:
        email = "admin@assetflow.com"
        # Check if user exists
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            # Create the user
            user = User(
                email=email,
                full_name="Demo Admin",
                hashed_password=hash_password("admin1234"),
                role="admin",
                status="active"
            )
            session.add(user)
            await session.commit()
            print(f"Created user {email} as admin.")
        else:
            # Promote to admin if already exists
            user.role = "admin"
            user.hashed_password = hash_password("admin1234")
            await session.commit()
            print(f"Updated user {email} to admin.")

if __name__ == "__main__":
    asyncio.run(create_demo_admin())
