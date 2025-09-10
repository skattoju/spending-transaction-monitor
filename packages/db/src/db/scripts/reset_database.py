"""
Reset database script - Delete all rows from all tables
"""

import asyncio
import os
import sys

from sqlalchemy import text

# Add the parent directory to sys.path to make imports work
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from db.database import SessionLocal


async def reset_database() -> None:
    """
    Reset database by deleting all rows from all tables.
    Deletes in order to respect foreign key constraints.
    """
    print('🔄 Starting database reset...')

    async with SessionLocal() as session:
        try:
            # Delete in reverse dependency order to avoid foreign key violations
            # Even though we have CASCADE, it's safer to be explicit

            print('📋 Deleting alert_notifications...')
            await session.execute(text('DELETE FROM alert_notifications'))

            print('⚠️  Deleting alert_rules...')
            await session.execute(text('DELETE FROM alert_rules'))

            print('💳 Deleting transactions...')
            await session.execute(text('DELETE FROM transactions'))

            print('🏦 Deleting credit_cards...')
            await session.execute(text('DELETE FROM credit_cards'))

            print('👤 Deleting users...')
            await session.execute(text('DELETE FROM users'))

            # Commit all deletions
            await session.commit()

            # Verify tables are empty
            print('\n📊 Verifying reset...')
            tables = [
                'users',
                'credit_cards',
                'transactions',
                'alert_rules',
                'alert_notifications',
            ]

            for table in tables:
                result = await session.execute(text(f'SELECT COUNT(*) FROM {table}'))
                count = result.scalar()
                print(f'  {table}: {count} rows')

            print('\n✅ Database reset completed successfully!')

        except Exception as e:
            print(f'❌ Error during database reset: {e}')
            await session.rollback()
            raise
        finally:
            await session.close()


if __name__ == '__main__':
    asyncio.run(reset_database())
