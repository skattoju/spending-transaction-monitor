import asyncio
import json
import os
import sys
import uuid
import argparse
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Add the parent directory to sys.path to make imports work when run as script
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from db.database import SessionLocal
from db.models import CreditCard, Transaction, User, AlertRule, AlertNotification
from sqlalchemy import text, select, func


def get_user_confirmation() -> bool:
    """Get user confirmation to proceed with data deletion"""
    print("\n" + "="*60)
    print("⚠️  WARNING: DATABASE RESET IMMINENT")
    print("="*60)
    print("🗑️  This script will DELETE ALL existing data from:")
    print("   • Users")
    print("   • Credit Cards") 
    print("   • Transactions")
    print("   • Alert Rules")
    print("   • Alert Notifications")
    print("\n🔄 Then it will seed the database with new test data.")
    print("="*60)
    
    while True:
        response = input("\n❓ Do you want to continue? (type 'YES' to confirm, 'no' to cancel): ").strip()
        if response == 'YES':
            print("✅ Confirmed. Proceeding with database reset and seeding...")
            return True
        elif response.lower() in ['no', 'n']:
            print("❌ Cancelled. No changes made to database.")
            return False
        else:
            print("⚠️  Please type 'YES' to confirm or 'no' to cancel.")


async def reset_database(session) -> None:
    """Delete all data from database tables"""
    print("\n🗑️  Clearing existing database data...")
    
    try:
        # Delete in correct order (respecting foreign key constraints)
        print("📋 Deleting alert_notifications...")
        await session.execute(text("DELETE FROM alert_notifications"))
        
        print("⚠️  Deleting alert_rules...")
        await session.execute(text("DELETE FROM alert_rules"))
        
        print("💳 Deleting transactions...")
        await session.execute(text("DELETE FROM transactions"))
        
        print("🏦 Deleting credit_cards...")
        await session.execute(text("DELETE FROM credit_cards"))
        
        print("👤 Deleting users...")
        await session.execute(text("DELETE FROM users"))
        
        await session.commit()
        print("✅ Database cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error during database reset: {e}")
        await session.rollback()
        raise


def normalize_json_structure(data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Normalize JSON structure to handle both singular and plural formats"""
    normalized = {}
    
    # Handle users
    if 'users' in data:
        normalized['users'] = data['users']
    elif 'user' in data:
        normalized['users'] = [data['user']]
    else:
        normalized['users'] = []
    
    # Handle credit_cards  
    if 'credit_cards' in data:
        normalized['credit_cards'] = data['credit_cards']
    elif 'credit_card' in data:
        normalized['credit_cards'] = [data['credit_card']]
    else:
        normalized['credit_cards'] = []
        
    # Handle transactions
    if 'transactions' in data:
        normalized['transactions'] = data['transactions']
    else:
        normalized['transactions'] = []
    
    return normalized


def convert_timestamps(obj_data: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """Convert string timestamps to datetime objects"""
    obj_copy = obj_data.copy()
    for field in fields:
        if obj_copy.get(field):
            # Only convert if it's a string (not already a datetime object)
            if isinstance(obj_copy[field], str):
                # Remove Z and parse ISO format
                timestamp_str = obj_copy[field].replace('Z', '+00:00')
                obj_copy[field] = datetime.fromisoformat(timestamp_str)
            # If it's already a datetime object, leave it as is
    return obj_copy


async def seed_from_json(json_file_path: str) -> None:
    """Seed database with data from JSON file"""
    
    # Validate file exists
    if not os.path.exists(json_file_path):
        raise FileNotFoundError(f"JSON file not found: {json_file_path}")
    
    print(f"📂 Loading fixture from: {json_file_path}")
    with open(json_file_path) as f:
        fixture_data = json.load(f)
    
    # Normalize JSON structure
    fixture = normalize_json_structure(fixture_data)
    
    async with SessionLocal() as session:
        try:
            # Reset database first
            await reset_database(session)
            
            print(f"\n🔄 Starting seeding from {os.path.basename(json_file_path)}...")
            
            # --- Insert Users ---
            for user_data in fixture['users']:
                user_data_copy = convert_timestamps(user_data, [
                    'created_at', 'updated_at', 
                    'last_app_location_timestamp', 'last_transaction_timestamp'
                ])
                
                user = User(**user_data_copy)
                await session.merge(user)
                print(f'👤 Seeded User: {user.first_name} {user.last_name}')

            # --- Insert Credit Cards ---
            for card_data in fixture['credit_cards']:
                card_data_copy = convert_timestamps(card_data, ['created_at', 'updated_at'])
                
                card = CreditCard(**card_data_copy)
                await session.merge(card)
                print(f'💳 Seeded Credit Card: ****{card.card_number[-4:]}')

            # --- Insert Transactions (with dynamic dates) ---
            if fixture['transactions']:
                now = datetime.now()
                print(f'\n⏰ Current time: {now}')
                print(f'📊 Processing {len(fixture["transactions"])} transactions...')
                print(f'🔍 fixture["transactions"] type: {type(fixture["transactions"])}')
                print(f'🔍 First transaction: {fixture["transactions"][0] if fixture["transactions"] else "None"}')

                for i, txn_data in enumerate(fixture['transactions']):
                    print(f'🔍 Loop iteration {i}, type(i): {type(i)}')
                    print(f'🔍 Processing transaction {i}: {txn_data.get("trans_num", "Unknown")}')
                    print(f'🔍 About to copy txn_data')
                    txn_data_copy = txn_data.copy()
                    print(f'🔍 Copy successful')
                    
                    # Generate new UUID and dynamic timestamps within the last hour
                    print(f'🔍 Generating UUID')
                    txn_data_copy['id'] = str(uuid.uuid4())
                    print(f'🔍 UUID generated: {txn_data_copy["id"]}')
                    
                    print(f'🔍 Calculating minutes offset: 5 * {i}')
                    minutes_offset = 5 * i  # Debug: ensure this is an integer
                    print(f'🔍 Minutes offset: {minutes_offset}, type: {type(minutes_offset)}')
                    
                    print(f'🔍 Creating timedelta with minutes={minutes_offset}')
                    txn_data_copy['transaction_date'] = now - timedelta(minutes=minutes_offset)
                    print(f'🔍 Transaction date set to: {txn_data_copy["transaction_date"]}')
                    
                    txn_data_copy['created_at'] = txn_data_copy['transaction_date']
                    txn_data_copy['updated_at'] = txn_data_copy['transaction_date']
                    print(f'🔍 All dates set successfully')
                    
                    # Convert any remaining string timestamps
                    txn_data_copy = convert_timestamps(txn_data_copy, 
                        ['transaction_date', 'created_at', 'updated_at'])

                    print(f'🔍 Creating Transaction object with data keys: {list(txn_data_copy.keys())}')
                    try:
                        txn = Transaction(**txn_data_copy)
                        await session.merge(txn)
                        print(f'💰 Seeded Transaction: {txn.trans_num} - ${txn.amount} at {txn.merchant_name} ({txn.transaction_date})')
                    except Exception as e:
                        print(f'❌ Failed to create transaction: {e}')
                        print(f'❌ Transaction data: {txn_data_copy}')
                        raise

            # Commit all changes
            await session.commit()
            print('\n✅ All data committed to database')

            # Verify insertion
            user_count = await session.scalar(select(func.count(User.id)))
            card_count = await session.scalar(select(func.count(CreditCard.id)))
            txn_count = await session.scalar(select(func.count(Transaction.id)))
            alert_rule_count = await session.scalar(select(func.count(AlertRule.id)))
            alert_notif_count = await session.scalar(select(func.count(AlertNotification.id)))

            print(f'\n📈 Final counts:')
            print(f'   • Users: {user_count}')
            print(f'   • Credit Cards: {card_count}') 
            print(f'   • Transactions: {txn_count}')
            print(f'   • Alert Rules: {alert_rule_count}')
            print(f'   • Alert Notifications: {alert_notif_count}')
            print('\n🎉 Seeding completed successfully!')

        except Exception as e:
            print(f'\n❌ Error during seeding: {e}')
            await session.rollback()
            raise


def main():
    """Main function to handle command line arguments and execute seeding"""
    parser = argparse.ArgumentParser(
        description='Seed database with test data from JSON file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python seed_alert_rules.py json/spending_amount_dining.json
  python seed_alert_rules.py json/transaction_last_hour.json
  
Available JSON files in json/ directory:
  • spending_amount_dining.json - Dining transactions test data
  • transaction_last_hour.json - Recent transactions test data
        """
    )
    
    parser.add_argument(
        'json_file', 
        help='Path to JSON file containing test data (relative to script directory or absolute path)'
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Skip confirmation prompt and proceed directly'
    )
    
    args = parser.parse_args()
    
    # Resolve JSON file path
    if os.path.isabs(args.json_file):
        json_file_path = args.json_file
    else:
        script_dir = os.path.dirname(__file__)
        json_file_path = os.path.join(script_dir, args.json_file)
    
    # Get user confirmation unless forced
    if not args.force:
        if not get_user_confirmation():
            return
    else:
        print("🔧 Force mode enabled. Skipping confirmation...")
    
    # Execute seeding
    try:
        asyncio.run(seed_from_json(json_file_path))
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n💥 Failed to complete seeding: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
