import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timedelta

# Add the parent directory to sys.path to make imports work when run as script
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from db.database import SessionLocal
from db.models import CreditCard, Transaction, User


async def seed() -> None:
    """Seed database with transactions from the last hour with dynamic timestamps"""

    print('🔄 Starting transactions_last_hour seeding...')

    # --- Load fixture ---
    script_dir = os.path.dirname(__file__)
    fixture_path = os.path.join(script_dir, 'json', 'transaction_last_hour.json')

    print(f'📂 Loading fixture from: {fixture_path}')
    with open(fixture_path) as f:
        fixture = json.load(f)

    # --- Database setup with AsyncSession ---
    async with SessionLocal() as session:
        try:
            # --- Insert Users ---
            for user_data in fixture['users']:
                # Convert string timestamps to datetime objects
                user_data_copy = user_data.copy()
                for field in [
                    'created_at',
                    'updated_at',
                    'last_app_location_timestamp',
                    'last_transaction_timestamp',
                ]:
                    if user_data_copy.get(field):
                        # Remove Z and parse ISO format
                        timestamp_str = user_data_copy[field].replace('Z', '+00:00')
                        user_data_copy[field] = datetime.fromisoformat(timestamp_str)

                user = User(**user_data_copy)
                await session.merge(user)  # AsyncSession requires await
                print(f'👤 Seeded User: {user.first_name} {user.last_name}')

            # --- Insert Credit Cards ---
            for card_data in fixture['credit_cards']:
                # Convert string timestamps to datetime objects
                card_data_copy = card_data.copy()
                for field in ['created_at', 'updated_at']:
                    if card_data_copy.get(field):
                        # Remove Z and parse ISO format
                        timestamp_str = card_data_copy[field].replace('Z', '+00:00')
                        card_data_copy[field] = datetime.fromisoformat(timestamp_str)

                card = CreditCard(**card_data_copy)
                await session.merge(card)
                print(f'💳 Seeded Credit Card: ****{card.card_number[-4:]}')

            # --- Insert Transactions (dynamic dates within last hour) ---
            now = datetime.now()
            print(f'⏰ Current time: {now}')
            print(f'📊 Processing {len(fixture["transactions"])} transactions...')

            for i, txn_data in enumerate(fixture['transactions']):
                # Create a copy to avoid modifying the original fixture
                txn_data_copy = txn_data.copy()

                # Generate new UUID and dynamic timestamps within the last hour
                txn_data_copy['id'] = str(uuid.uuid4())
                txn_data_copy['transaction_date'] = now - timedelta(
                    minutes=5 * i
                )  # Spread over last hour
                txn_data_copy['created_at'] = txn_data_copy['transaction_date']
                txn_data_copy['updated_at'] = txn_data_copy['transaction_date']

                # Convert any remaining string timestamps to datetime objects
                for field in ['transaction_date', 'created_at', 'updated_at']:
                    if isinstance(txn_data_copy.get(field), str):
                        # Remove Z and parse ISO format
                        timestamp_str = txn_data_copy[field].replace('Z', '+00:00')
                        txn_data_copy[field] = datetime.fromisoformat(timestamp_str)

                txn = Transaction(**txn_data_copy)
                await session.merge(txn)
                print(
                    f'💰 Seeded Transaction: {txn.trans_num} - ${txn.amount} at {txn.merchant_name} ({txn.transaction_date})'
                )

            # Commit all changes
            await session.commit()
            print('✅ All data committed to database')

            # Verify insertion
            from sqlalchemy import func, select

            user_count = await session.scalar(select(func.count(User.id)))
            card_count = await session.scalar(select(func.count(CreditCard.id)))
            txn_count = await session.scalar(select(func.count(Transaction.id)))

            print(
                f'📈 Final counts - Users: {user_count}, Cards: {card_count}, Transactions: {txn_count}'
            )
            print('✅ Seeding completed successfully!')

        except Exception as e:
            print(f'❌ Error during seeding: {e}')
            await session.rollback()
            raise


if __name__ == '__main__':
    asyncio.run(seed())
