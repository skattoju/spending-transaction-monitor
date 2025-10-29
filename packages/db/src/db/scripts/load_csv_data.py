#!/usr/bin/env python3
"""Load sample data from CSV files into the database (SYNC version for migrations)"""

import csv
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import create_engine, delete, text
from sqlalchemy.orm import sessionmaker

from db.config import settings
from db.models import AlertNotification, AlertRule, CreditCard, Transaction, User


def parse_datetime(date_str: str) -> datetime:
    """Parse datetime string in ISO format"""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        # Fallback for different formats
        return datetime.fromisoformat(date_str)


def clear_existing_data(session) -> None:
    """Clear all existing data from tables to ensure fresh load"""
    print('🗑️  Clearing existing data from all tables...')

    try:
        # Delete in order to respect foreign key constraints
        # Child tables first, then parent tables

        # Clear cached recommendations (has foreign keys to users)
        print('   Clearing cached recommendations...')
        result = session.execute(text('DELETE FROM cached_recommendations'))
        cached_recommendations_count = result.rowcount
        print(f'   Deleted {cached_recommendations_count} cached recommendations')

        # Clear alert notifications (has foreign keys to alert rules)
        print('   Clearing alert notifications...')
        result = session.execute(delete(AlertNotification))
        alert_notification_count = result.rowcount
        print(f'   Deleted {alert_notification_count} alert notifications')

        # Clear alert rules (has foreign keys to users)
        print('   Clearing alert notifications...')
        result = session.execute(delete(AlertRule))
        alert_count = result.rowcount
        print(f'   Deleted {alert_count} alert rules')

        # Clear transactions (has foreign keys to users and credit cards)
        print('   Clearing transactions...')
        result = session.execute(delete(Transaction))
        transaction_count = result.rowcount
        print(f'   Deleted {transaction_count} transactions')

        # Clear credit cards (has foreign keys to users)
        print('   Clearing credit cards...')
        result = session.execute(delete(CreditCard))
        card_count = result.rowcount
        print(f'   Deleted {card_count} credit cards')

        # Clear users (parent table, no foreign keys from other tables at this point)
        print('   Clearing users...')
        result = session.execute(delete(User))
        user_count = result.rowcount
        print(f'   Deleted {user_count} users')

        session.commit()

        total_deleted = transaction_count + alert_count + card_count + user_count
        print(f'✅ Successfully cleared {total_deleted} total records from all tables')

    except Exception as e:
        print(f'❌ Error clearing existing data: {e}')
        session.rollback()
        raise


def load_users_from_csv(session, csv_file_path: str) -> dict[str, int]:
    """Load users from CSV and return mapping of email to database ID"""
    print(f'📥 Loading users from {csv_file_path}...')
    user_id_mapping = {}

    try:
        with open(csv_file_path, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            users_to_add = []

            for row in reader:
                user = User(
                    email=row['email'],
                    name=row['name'],
                    phone=row.get('phone'),
                    address=row.get('address'),
                    created_at=parse_datetime(row['created_at'])
                    if row.get('created_at')
                    else datetime.now(UTC),
                    last_login=parse_datetime(row['last_login'])
                    if row.get('last_login')
                    else None,
                )
                users_to_add.append(user)

            # Bulk insert users
            session.bulk_save_objects(users_to_add, return_defaults=True)
            session.commit()

            # Get all users back with their IDs
            users_in_db = session.query(User).all()
            for user in users_in_db:
                user_id_mapping[user.email] = user.id

            print(f'✅ Loaded {len(users_to_add)} users')
            return user_id_mapping

    except FileNotFoundError:
        print(f'❌ CSV file not found: {csv_file_path}')
        raise
    except Exception as e:
        print(f'❌ Error loading users: {e}')
        session.rollback()
        raise


def load_transactions_from_csv(
    session, csv_file_path: str, user_id_mapping: dict[str, int]
) -> None:
    """Load transactions from CSV"""
    print(f'📥 Loading transactions from {csv_file_path}...')

    try:
        with open(csv_file_path, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            batch_size = 1000
            transactions_to_add = []
            total_loaded = 0
            skipped = 0

            for i, row in enumerate(reader, 1):
                user_email = row.get('user_email')
                if not user_email or user_email not in user_id_mapping:
                    skipped += 1
                    continue

                try:
                    transaction = Transaction(
                        user_id=user_id_mapping[user_email],
                        amount=Decimal(str(row['amount'])),
                        category=row['category'],
                        description=row.get('description', ''),
                        merchant=row.get('merchant', ''),
                        location=row.get('location'),
                        latitude=float(row['latitude'])
                        if row.get('latitude')
                        else None,
                        longitude=float(row['longitude'])
                        if row.get('longitude')
                        else None,
                        transaction_date=parse_datetime(row['transaction_date']),
                        created_at=parse_datetime(row['created_at'])
                        if row.get('created_at')
                        else datetime.now(UTC),
                    )
                    transactions_to_add.append(transaction)

                    # Commit in batches
                    if len(transactions_to_add) >= batch_size:
                        session.bulk_save_objects(transactions_to_add)
                        session.commit()
                        total_loaded += len(transactions_to_add)
                        print(f'   Loaded {total_loaded} transactions...')
                        transactions_to_add = []

                except (ValueError, KeyError) as e:
                    print(f'   ⚠️  Skipping row {i} due to error: {e}')
                    skipped += 1
                    continue

            # Commit remaining transactions
            if transactions_to_add:
                session.bulk_save_objects(transactions_to_add)
                session.commit()
                total_loaded += len(transactions_to_add)

            print(f'✅ Loaded {total_loaded} transactions')
            if skipped > 0:
                print(f'   ⚠️  Skipped {skipped} transactions due to errors')

    except FileNotFoundError:
        print(f'❌ CSV file not found: {csv_file_path}')
        raise
    except Exception as e:
        print(f'❌ Error loading transactions: {e}')
        session.rollback()
        raise


def load_csv_data(
    users_csv_path: str = '/app/data/sample_users.csv',
    transactions_csv_path: str = '/app/data/sample_transactions.csv',
) -> None:
    """Main function to load data from CSV files using sync engine"""
    print('🚀 Starting CSV data loading process (SYNC mode)...')

    # Create sync engine from DATABASE_URL (replace asyncpg with psycopg2)
    database_url = settings.DATABASE_URL.replace('+asyncpg', '+psycopg2')
    print(
        f'📊 Using database: {database_url.split("@")[1] if "@" in database_url else "..."}'
    )

    engine = create_engine(database_url, echo=False)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        try:
            # Clear all existing data first
            clear_existing_data(session)

            # Load users first and get ID mapping
            user_id_mapping = load_users_from_csv(session, users_csv_path)

            if not user_id_mapping:
                print('❌ No users loaded, skipping transactions')
                return

            # Load transactions using the user ID mapping
            load_transactions_from_csv(session, transactions_csv_path, user_id_mapping)

            print('✅ CSV data loading completed successfully!')

        except Exception as e:
            print(f'❌ Error during CSV data loading: {e}')
            session.rollback()
            raise


if __name__ == '__main__':
    load_csv_data()
