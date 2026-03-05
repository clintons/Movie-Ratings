#!/usr/bin/env python3
"""Batch fetch movie posters for all movies in database"""

import psycopg2
from psycopg2.extras import RealDictCursor
import requests
from PIL import Image
from io import BytesIO
import os
import time
import sys

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'movieratings'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

OMDB_API_KEY = os.getenv('OMDB_API_KEY', '')
POSTER_DIR = '/app/static/posters'

def fetch_poster(title, year, movie_id):
    """Fetch and save movie poster"""
    poster_path = f"{POSTER_DIR}/{movie_id}.jpg"
    
    # Check if already exists
    if os.path.exists(poster_path):
        print(f"✓ Poster exists for: {title}")
        return True
    
    if not OMDB_API_KEY:
        print(f"⚠ No API key - skipping: {title}")
        return False
    
    try:
        # Query OMDB API
        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
        if year:
            url += f"&y={year}"
        
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get('Poster') and data['Poster'] != 'N/A':
            # Download poster
            poster_response = requests.get(data['Poster'], timeout=10)
            if poster_response.status_code == 200:
                # Resize and save
                img = Image.open(BytesIO(poster_response.content))
                img.thumbnail((300, 450), Image.Resampling.LANCZOS)
                img.save(poster_path, 'JPEG', quality=85)
                print(f"✓ Downloaded: {title} ({year})")
                return True
        
        print(f"✗ No poster found: {title}")
        return False
        
    except Exception as e:
        print(f"✗ Error fetching {title}: {e}")
        return False

def main():
    """Fetch posters for all movies"""
    # Create posters directory
    os.makedirs(POSTER_DIR, exist_ok=True)
    
    # Check API key
    if not OMDB_API_KEY or OMDB_API_KEY == 'your_api_key_here':
        print("\n⚠️  WARNING: No OMDB API key configured!")
        print("Set OMDB_API_KEY in .env file to fetch posters.")
        print("Get free key at: http://www.omdbapi.com/apikey.aspx")
        return 1
    
    # Parse command line arguments for batch mode
    batch_size = None
    skip_count = 0
    
    if len(sys.argv) > 1:
        try:
            batch_size = int(sys.argv[1])
        except ValueError:
            print(f"Error: Invalid batch size '{sys.argv[1]}'. Must be a number.")
            return 1
    
    if len(sys.argv) > 2:
        try:
            skip_count = int(sys.argv[2])
        except ValueError:
            print(f"Error: Invalid skip count '{sys.argv[2]}'. Must be a number.")
            return 1
    
    # Connect to database
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all movies without posters
        cur.execute("SELECT id, title, year FROM movies ORDER BY id")
        all_movies = cur.fetchall()
        
        # Filter to only movies without posters
        movies_needing_posters = [
            m for m in all_movies 
            if not os.path.exists(f"{POSTER_DIR}/{m['id']}.jpg")
        ]
        
        # Count existing posters
        existing = len(all_movies) - len(movies_needing_posters)
        to_fetch = len(movies_needing_posters)
        
        print(f"\n{'='*70}")
        print(f"🎬 MOVIE POSTER BATCH FETCH")
        print(f"{'='*70}")
        print(f"Total movies in database: {len(all_movies)}")
        print(f"Already have posters:     {existing}")
        print(f"Need to fetch:            {to_fetch}")
        
        if to_fetch == 0:
            print(f"\n✅ All posters already downloaded! Nothing to do.")
            return 0
        
        # Apply skip if specified
        if skip_count > 0:
            movies_needing_posters = movies_needing_posters[skip_count:]
            print(f"Skipping first:           {skip_count} movies (already fetched)")
            print(f"Remaining to fetch:       {len(movies_needing_posters)}")
        
        # Apply batch limit if specified
        if batch_size:
            actual_batch = min(batch_size, len(movies_needing_posters))
            movies_to_fetch = movies_needing_posters[:batch_size]
            remaining_after = len(movies_needing_posters) - actual_batch
            
            print(f"\n📦 BATCH MODE:")
            print(f"Fetching this batch:      {actual_batch} posters")
            print(f"Will remain after:        {remaining_after} posters")
            
            if remaining_after > 0:
                next_skip = skip_count + actual_batch
                print(f"\n💡 Next batch command:")
                print(f"   docker-compose exec web python /app/fetch_posters.py {batch_size} {next_skip}")
        else:
            movies_to_fetch = movies_needing_posters
            print(f"\n⚠️  Fetching ALL {len(movies_to_fetch)} remaining posters")
        
        # Warn about API limit
        if len(movies_to_fetch) > 900:
            print(f"\n{'='*70}")
            print(f"⚠️  API LIMIT WARNING")
            print(f"{'='*70}")
            print(f"OMDB free tier limit: 1,000 calls/day")
            print(f"You are about to fetch: {len(movies_to_fetch)} posters")
            print(f"\n💡 TIP: Use batch mode to stay under limit:")
            print(f"   docker-compose exec web python /app/fetch_posters.py 900 0")
            print(f"{'='*70}")
            response = input(f"\nContinue with {len(movies_to_fetch)} API calls? (y/N): ")
            if response.lower() != 'y':
                print("\n❌ Cancelled. Use batch mode to fetch in chunks.")
                return 0
        
        print(f"\n{'='*70}")
        print(f"Starting poster download...")
        print(f"{'='*70}\n")
        
        success = 0
        failed = 0
        skipped = 0
        
        for idx, movie in enumerate(movies_to_fetch, 1):
            print(f"[{idx}/{len(movies_to_fetch)}] ", end="")
            result = fetch_poster(movie['title'], movie['year'], movie['id'])
            if result:
                if os.path.exists(f"{POSTER_DIR}/{movie['id']}.jpg"):
                    success += 1
                else:
                    skipped += 1
            else:
                failed += 1
            
            # Rate limiting - be nice to the API
            time.sleep(0.5)
        
        print(f"\n{'='*70}")
        print(f"📊 BATCH RESULTS")
        print(f"{'='*70}")
        print(f"✅ Successfully downloaded: {success}")
        print(f"❌ Failed to fetch:         {failed}")
        print(f"⏭️  Skipped (no poster):    {skipped}")
        print(f"{'='*70}")
        
        # Show next steps if more remain
        total_remaining = to_fetch - len(movies_to_fetch)
        if batch_size and total_remaining > 0:
            next_skip = skip_count + len(movies_to_fetch)
            print(f"\n🔜 NEXT STEPS:")
            print(f"Posters still needed:     {total_remaining}")
            print(f"\nRun tomorrow (after API limit resets):")
            print(f"  docker-compose exec web python /app/fetch_posters.py {batch_size} {next_skip}")
            print(f"{'='*70}")
        elif to_fetch - skip_count > len(movies_to_fetch):
            remaining = to_fetch - skip_count - len(movies_to_fetch)
            next_skip = skip_count + len(movies_to_fetch)
            print(f"\n🔜 NEXT STEPS:")
            print(f"Posters still needed:     {remaining}")
            print(f"\nRun tomorrow:")
            print(f"  docker-compose exec web python /app/fetch_posters.py 900 {next_skip}")
            print(f"{'='*70}")
        else:
            print(f"\n✅ ALL POSTERS COMPLETE!")
            print(f"{'='*70}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
