import asyncio
import sys
import os

# Ensure we can import from the app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import update, select
from database import async_session
from models.user import User

async def promote(email: str):
    async with async_session() as session:
        # Check if user exists
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user:
            # Promote to admin
            await session.execute(update(User).where(User.email == email).values(role='admin'))
            await session.commit()
            print(f"✅ Success: User '{email}' has been successfully promoted to Admin!")
            print("Please refresh your browser or log out and log back in to see the admin features.")
        else:
            print(f"❌ Error: No user found with email '{email}'.")
            print("Please make sure you have registered first at http://localhost:3000/register.html")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python promote_to_admin.py <your_email@example.com>")
    else:
        asyncio.run(promote(sys.argv[1]))
