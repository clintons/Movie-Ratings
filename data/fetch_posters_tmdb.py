#!/usr/bin/env python3
"""
Fetch movie posters from TMDB API (The Movie Database)
More reliable poster source than OMDB
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import os
import sys
import time
from PIL import Image
from io import BytesIO

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'movieratings'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'db'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
TMDB_READ_TOKEN = os.getenv('TMDB_READ_ACCESS_TOKEN', '')
POSTER_DIR = '/app/static/posters'

# TMDB poster base URL - using w500 size (good quality, reasonable file size)
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

def get_movies_without_posters():
    """Get movies that need posters - only those truly missing posters"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT id, title, year
        FROM movies
        WHERE poster_path IS NULL 
           OR poster_path = '/static/posters/placeholder.jpg'
           OR poster_path = ''
        ORDER BY year DESC, id
    """)
    
    movies = cur.fetchall()
    cur.close()
    conn.close()
    return movies

def search_tmdb_movie(title, year=None):
    """
    Search TMDB for a movie
    Returns movie data including poster path
    """
    if not TMDB_API_KEY:
        print("    ❌ TMDB_API_KEY not set!")
        return None
    
    try:
        # Search for movie
        url = f"https://api.themoviedb.org/3/search/movie"
        params = {
            'api_key': TMDB_API_KEY,
            'query': title,
            'include_adult': 'false'
        }
        
        if year:
            params['year'] = year
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('results') and len(data['results']) > 0:
            # Return first result
            movie = data['results'][0]
            return {
                'title': movie.get('title'),
                'year': movie.get('release_date', '')[:4] if movie.get('release_date') else None,
                'poster_path': movie.get('poster_path'),
                'tmdb_id': movie.get('id'),
                'overview': movie.get('overview'),
                'vote_average': movie.get('vote_average')
            }
        
        # If no results with year, try without year
        if year and data.get('results') == []:
            params.pop('year')
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('results') and len(data['results']) > 0:
                movie = data['results'][0]
                return {
                    'title': movie.get('title'),
                    'year': movie.get('release_date', '')[:4] if movie.get('release_date') else None,
                    'poster_path': movie.get('poster_path'),
                    'tmdb_id': movie.get('id'),
                    'overview': movie.get('overview'),
                    'vote_average': movie.get('vote_average'),
                    'year_mismatch': True
                }
        
        return None
        
    except Exception as e:
        print(f"    ⚠️  TMDB API Error: {e}")
        return None

def download_and_save_poster(poster_path, movie_id):
    """
    Download poster from TMDB and save locally
    """
    try:
        # Construct full poster URL
        poster_url = f"{TMDB_IMAGE_BASE}{poster_path}"
        
        # Download poster
        response = requests.get(poster_url, timeout=10)
        if response.status_code != 200:
            return None
        
        # Open and resize image
        img = Image.open(BytesIO(response.content))
        img.thumbnail((300, 450), Image.Resampling.LANCZOS)
        
        # Save to poster directory
        save_path = f"{POSTER_DIR}/{movie_id}.jpg"
        img.save(save_path, 'JPEG', quality=85)
        
        return f"/static/posters/{movie_id}.jpg"
        
    except Exception as e:
        print(f"    ⚠️  Download Error: {e}")
        return None

def update_poster_path(movie_id, poster_path):
    """Update poster path in database"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    cur.execute(
        "UPDATE movies SET poster_path = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
        (poster_path, movie_id)
    )
    
    conn.commit()
    cur.close()
    conn.close()

def main():
    if not TMDB_API_KEY:
        print("=" * 70)
        print("❌ TMDB_API_KEY not set in environment!")
        print("=" * 70)
        print("Add it to your .env file:")
        print("  TMDB_API_KEY=your_api_key_here")
        print("\nThen restart docker compose:")
        print("  docker compose down && docker compose up -d")
        sys.exit(1)
    
    print("=" * 70)
    print("🎬 MOVIE POSTER FETCH - TMDB Edition")
    print("=" * 70)
    
    movies = get_movies_without_posters()
    total = len(movies)
    
    if total == 0:
        print("✅ All movies have posters!")
        return
    
    print(f"Movies without posters: {total}")
    
    # Get batch parameters
    batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    skip_count = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    # Apply skip
    movies_to_process = movies[skip_count:skip_count + batch_size]
    
    print(f"Batch size:             {len(movies_to_process)}")
    print(f"Skipped first:          {skip_count}")
    print("=" * 70)
    print()
    
    success = 0
    failed = 0
    no_poster = 0
    api_calls = 0
    
    for i, movie in enumerate(movies_to_process, 1):
        print(f"[{i}/{len(movies_to_process)}] {movie['title']} ({movie['year'] or 'no year'})")
        
        # Search TMDB
        result = search_tmdb_movie(movie['title'], movie['year'])
        api_calls += 1
        
        if not result:
            print(f"    ❌ Not found in TMDB")
            failed += 1
            time.sleep(0.3)
            continue
        
        if not result.get('poster_path'):
            print(f"    ⚠️  Found but no poster available")
            print(f"       TMDB: {result['title']} ({result['year']})")
            no_poster += 1
            time.sleep(0.3)
            continue
        
        # Check if year matches
        if result.get('year_mismatch'):
            print(f"    ⚠️  Year mismatch - found: {result['title']} ({result['year']})")
        else:
            print(f"    ✓ Found: {result['title']} ({result['year']})")
        
        # Download poster
        poster_url = download_and_save_poster(result['poster_path'], movie['id'])
        
        if poster_url:
            update_poster_path(movie['id'], poster_url)
            print(f"    ✅ Poster saved")
            success += 1
        else:
            print(f"    ❌ Failed to download")
            failed += 1
        
        time.sleep(0.3)  # Rate limiting
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 BATCH RESULTS")
    print("=" * 70)
    print(f"✅ Successfully downloaded: {success}")
    print(f"⚠️  No poster available:     {no_poster}")
    print(f"❌ Failed to fetch:         {failed}")
    print(f"🔢 API calls used:          {api_calls}")
    print("=" * 70)
    
    remaining = total - (skip_count + len(movies_to_process))
    if remaining > 0:
        print(f"\n🔜 NEXT STEPS:")
        print(f"Posters still needed: {remaining}")
        print(f"Run next batch:")
        print(f"  docker compose exec web python /app/fetch_posters_tmdb.py {batch_size} {skip_count + len(movies_to_process)}")
    else:
        print(f"\n🎉 All done! No more posters to fetch.")
    
    print("=" * 70)

if __name__ == '__main__':
    main()
