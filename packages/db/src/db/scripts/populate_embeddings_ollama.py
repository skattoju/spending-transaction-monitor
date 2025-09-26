#!/usr/bin/env python3
"""
Ollama Embedding Population Script
Generates local embeddings using Ollama and populates the database.
"""

import asyncio
import json
from typing import List
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, text
from db import get_db
from db.models import MerchantCategoryEmbedding


# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
EMBEDDING_MODEL = "all-minilm"  # 384 dimensions - fast and efficient
EXPECTED_DIMENSIONS = 384

# Canonical categories (matching updated seed_category_data.py from real CSV data)
CANONICAL_CATEGORIES = [
    "dining",
    "grocery", 
    "retail",
    "entertainment",
    "fuel",
    "health_fitness",
    "personal_care",
    "travel",
    "home",
    "kids_pets",
    "misc_net",
    "misc_pos"
]


async def clear_existing_embeddings(session: AsyncSession) -> None:
    """Clear existing embeddings for fresh population"""
    print("🧹 Clearing existing embeddings...")
    await session.execute(delete(MerchantCategoryEmbedding))
    await session.commit()
    print("✅ Cleared existing embeddings")


async def generate_embedding_ollama(text: str) -> List[float]:
    """Generate embedding using Ollama API"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/embeddings",
                json={
                    "model": EMBEDDING_MODEL,
                    "prompt": text
                }
            )
            response.raise_for_status()
            result = response.json()
            
            embedding = result.get("embedding", [])
            if len(embedding) != EXPECTED_DIMENSIONS:
                raise ValueError(f"Expected {EXPECTED_DIMENSIONS} dimensions, got {len(embedding)}")
            
            return embedding
            
    except Exception as e:
        print(f"❌ Error generating embedding for '{text}': {e}")
        raise


async def update_database_schema(session: AsyncSession) -> None:
    """Update the embedding column to match Ollama model dimensions"""
    print(f"🔧 Updating database schema for {EXPECTED_DIMENSIONS} dimensions...")
    
    try:
        # Drop and recreate the column with correct dimensions
        await session.execute(text("ALTER TABLE merchant_category_embeddings DROP COLUMN embedding"))
        await session.execute(text(f"ALTER TABLE merchant_category_embeddings ADD COLUMN embedding vector({EXPECTED_DIMENSIONS})"))
        await session.commit()
        print(f"✅ Updated embedding column to {EXPECTED_DIMENSIONS} dimensions")
    except Exception as e:
        print(f"⚠️  Schema update note: {e}")
        # Column might already be the right size or table might be empty
        await session.rollback()


async def populate_category_embeddings(session: AsyncSession) -> None:
    """Generate and store embeddings for all canonical categories"""
    print(f"🤖 Generating Ollama embeddings using model: {EMBEDDING_MODEL}")
    print(f"📏 Expected dimensions: {EXPECTED_DIMENSIONS}")
    
    successful_embeddings = 0
    
    for i, category in enumerate(CANONICAL_CATEGORIES, 1):
        print(f"  [{i}/{len(CANONICAL_CATEGORIES)}] Generating embedding for '{category}'...")
        
        try:
            # Generate embedding using Ollama
            embedding = await generate_embedding_ollama(category)
            
            # Store in database
            embedding_obj = MerchantCategoryEmbedding(
                category=category,
                embedding=embedding
            )
            session.add(embedding_obj)
            successful_embeddings += 1
            
            print(f"    ✅ Generated {len(embedding)} dimensional embedding")
            
        except Exception as e:
            print(f"    ❌ Failed to generate embedding for '{category}': {e}")
            continue
    
    # Commit all embeddings
    await session.commit()
    print(f"✅ Successfully generated {successful_embeddings}/{len(CANONICAL_CATEGORIES)} embeddings")


async def validate_embeddings(session: AsyncSession) -> None:
    """Validate that embeddings were stored correctly"""
    print("🔍 Validating stored embeddings...")
    
    result = await session.execute(select(MerchantCategoryEmbedding))
    embeddings = result.scalars().all()
    
    print(f"✅ Found {len(embeddings)} embeddings in database")
    
    # Validate embedding dimensions
    for embedding_obj in embeddings:
        if len(embedding_obj.embedding) != EXPECTED_DIMENSIONS:
            print(f"❌ Invalid embedding dimension for '{embedding_obj.category}': {len(embedding_obj.embedding)}")
        else:
            print(f"✅ '{embedding_obj.category}' embedding: {len(embedding_obj.embedding)} dimensions ✓")


async def test_semantic_search(session: AsyncSession) -> None:
    """Test semantic search functionality using Ollama embeddings"""
    print("🧪 Testing semantic search...")
    
    test_queries = [
        "food",
        "restaurant", 
        "gas station",
        "hotel",
        "computer",
        "netflix"
    ]
    
    for query in test_queries:
        try:
            # Generate embedding for test query
            query_embedding = await generate_embedding_ollama(query)
            
            # Find most similar category using vector distance
            result = await session.execute(text("""
                SELECT category, embedding <-> :query_vector as distance
                FROM merchant_category_embeddings
                ORDER BY embedding <-> :query_vector
                LIMIT 1
            """), {"query_vector": query_embedding})
            
            row = result.fetchone()
            if row:
                category, distance = row
                print(f"  '{query}' → '{category}' (distance: {distance:.4f})")
            else:
                print(f"  '{query}' → No match found")
                
        except Exception as e:
            print(f"  '{query}' → Error: {e}")


async def check_ollama_connection() -> bool:
    """Check if Ollama is running and model is available"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Check Ollama is running
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
            models = response.json()
            
            # Check if our model is available
            model_names = [model["name"] for model in models.get("models", [])]
            if EMBEDDING_MODEL not in model_names and f"{EMBEDDING_MODEL}:latest" not in model_names:
                print(f"❌ Model '{EMBEDDING_MODEL}' not found in Ollama")
                print(f"Available models: {model_names}")
                print(f"Run: ollama pull {EMBEDDING_MODEL}")
                return False
                
            print(f"✅ Ollama is running with model '{EMBEDDING_MODEL}'")
            return True
            
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print(f"Make sure Ollama is running: ollama serve")
        return False


async def main():
    """Main embedding population function"""
    print("🚀 Starting Ollama Embedding Population...")
    print(f"📊 Will generate embeddings for {len(CANONICAL_CATEGORIES)} categories")
    print(f"🤖 Using Ollama model: {EMBEDDING_MODEL} ({EXPECTED_DIMENSIONS} dimensions)")
    
    # Check Ollama connection
    if not await check_ollama_connection():
        return 1
    
    # Get async database session  
    db_gen = get_db()
    session = await db_gen.__anext__()
    
    try:
        await update_database_schema(session)
        await clear_existing_embeddings(session)
        await populate_category_embeddings(session)
        await validate_embeddings(session)
        
        # Optional: Test semantic search if all embeddings were successful
        result = await session.execute(select(MerchantCategoryEmbedding))
        if len(result.scalars().all()) == len(CANONICAL_CATEGORIES):
            await test_semantic_search(session)
    finally:
        await session.close()
    
    print("🎉 Ollama embedding population completed successfully!")
    print()
    print("📋 Categories with Embeddings:")
    for category in sorted(CANONICAL_CATEGORIES):
        print(f"  • {category}")
    print()
    print("🔗 Next steps:")
    print("  1. Test CategoryNormalizer service")
    print("  2. Integrate with transaction creation pipeline")
    print("  3. Update query endpoints for semantic search")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    if exit_code:
        exit(exit_code)
