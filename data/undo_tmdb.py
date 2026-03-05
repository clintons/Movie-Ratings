#!/usr/bin/env python3
"""
Undo recent TMDB poster updates - reset them so OMDB can refetch
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import sys

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'movieratings'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'db'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

POSTER_DIR = '/app/static/posters'

def get_recently_updated_movies(minutes=30):
    """Get movies updated in the last N minutes"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute(f"""
        SELECT id, title, year, poster_path, updated_at
        FROM movies
        WHERE poster_path IS NOT NULL 
          AND poster_path != '/static/posters/placeholder.jpg'
          AND updated_at > NOW() - INTERVAL '{minutes} minutes'
        ORDER BY updated_at DESC
    """)
    
    movies = cur.fetchall()
    cur.close()
    conn.close()
    return movies

def reset_poster(movie_id):
    """Reset a movie's poster - delete file and clear DB entry"""
    # Delete poster file
    poster_file = f"{POSTER_DIR}/{movie_id}.jpg"
    try:
        if os.path.exists(poster_file):
            os.remove(poster_file)
            print(f"    Deleted: {poster_file}")
    except Exception as e:
        print(f"    Warning: Could not delete file: {e}")
    
    # Update database
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("UPDATE movies SET poster_path = NULL WHERE id = %s", (movie_id,))
    conn.commit()
    cur.close()
    conn.close()
    print(f"    Database updated")

def main():
    if len(sys.argv) > 1:
        minutes = int(sys.argv[1])
    else:
        minutes = 30
    
    print("=" * 70)
    print("🔄 UNDO RECENT TMDB POSTER UPDATES")
    print("=" * 70)
    print(f"Looking for movies updated in the last {minutes} minutes...\n")
    
    movies = get_recently_updated_movies(minutes)
    
    if not movies:
        print(f"✅ No movies were updated in the last {minutes} minutes.")
        print("\nTo check a different time window:")
        print(f"  docker compose exec web python /app/data/undo_tmdb.py 60  # last hour")
        print(f"  docker compose exec web python /app/data/undo_tmdb.py 120  # last 2 hours")
        return
    
    print(f"Found {len(movies)} movies updated recently:\n")
    
    for movie in movies:
        print(f"ID {movie['id']}: {movie['title']} ({movie['year']})")
        print(f"  Updated: {movie['updated_at']}")
        print(f"  Poster: {movie['poster_path']}")
    
    print("\n" + "=" * 70)
    print("⚠️  WARNING: This will DELETE these posters and reset them to NULL")
    print("=" * 70)
    
    try:
        response = input("\nReset these posters? (yes/no): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n\nCancelled.")
        return
    
    if response not in ['yes', 'y']:
        print("Cancelled. No changes made.")
        return
    
    print("\nResetting posters...\n")
    
    for movie in movies:
        print(f"Resetting ID {movie['id']}: {movie['title']}")
        reset_poster(movie['id'])
    
    print("\n" + "=" * 70)
    print("✅ DONE!")
    print("=" * 70)
    print(f"Reset {len(movies)} posters")
    print("\nNext steps:")
    print("  1. Run OMDB to fetch the correct posters:")
    print(f"     docker compose exec web python /app/fetch_posters.py {len(movies)}")
    print("\n  2. For any remaining failures, use TMDB:")
    print("     docker compose exec web python /app/data/fetch_posters_tmdb.py")
    print("=" * 70)

if __name__ == '__main__':
    main()
