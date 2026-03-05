#!/usr/bin/env python3
"""
Verify movie titles against OMDB API and suggest corrections
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import os
import time
import sys

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'movieratings'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'db'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

OMDB_API_KEY = os.getenv('OMDB_API_KEY', '')

def get_movies_without_posters():
    """Get movies that don't have posters"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT id, title, year, poster_path
        FROM movies
        WHERE poster_path IS NULL 
           OR poster_path = '/static/posters/placeholder.jpg'
        ORDER BY year DESC, title
    """)
    
    movies = cur.fetchall()
    cur.close()
    conn.close()
    return movies

def check_title_with_omdb(title, year):
    """Check if title exists in OMDB and get the correct title"""
    if not OMDB_API_KEY:
        return None
    
    try:
        # First try exact match
        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
        if year:
            url += f"&y={year}"
        
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get('Response') == 'True':
            return {
                'found': True,
                'correct_title': data.get('Title'),
                'year': data.get('Year'),
                'poster': data.get('Poster'),
                'imdb_id': data.get('imdbID')
            }
        
        # If not found, try searching
        search_url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={title}"
        if year:
            search_url += f"&y={year}"
        
        response = requests.get(search_url, timeout=5)
        data = response.json()
        
        if data.get('Response') == 'True' and data.get('Search'):
            # Return first search result
            first_result = data['Search'][0]
            return {
                'found': True,
                'correct_title': first_result.get('Title'),
                'year': first_result.get('Year'),
                'poster': first_result.get('Poster'),
                'imdb_id': first_result.get('imdbID'),
                'is_search_result': True
            }
        
        return {'found': False}
        
    except Exception as e:
        print(f"  ⚠️  API Error: {e}")
        return None

def update_movie_title(movie_id, new_title):
    """Update movie title in database"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    cur.execute(
        "UPDATE movies SET title = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
        (new_title, movie_id)
    )
    
    conn.commit()
    cur.close()
    conn.close()

def main():
    if not OMDB_API_KEY:
        print("❌ OMDB_API_KEY not set in environment!")
        print("Add it to your .env file and restart docker compose")
        sys.exit(1)
    
    print("=" * 70)
    print("🎬 MOVIE TITLE VERIFICATION & CORRECTION")
    print("=" * 70)
    
    movies = get_movies_without_posters()
    print(f"\nFound {len(movies)} movies without posters")
    print(f"Checking titles against OMDB API...\n")
    
    corrections_found = []
    not_found = []
    api_calls = 0
    
    for i, movie in enumerate(movies, 1):
        print(f"[{i}/{len(movies)}] Checking: {movie['title']} ({movie['year'] or 'no year'})")
        
        result = check_title_with_omdb(movie['title'], movie['year'])
        api_calls += 1
        
        if result is None:
            print(f"  ⏭️  Skipping (API error)")
            time.sleep(0.3)
            continue
        
        if not result['found']:
            print(f"  ❌ Not found in OMDB")
            not_found.append(movie)
            time.sleep(0.3)
            continue
        
        correct_title = result['correct_title']
        
        # Check if title is different
        if movie['title'] != correct_title:
            print(f"  ⚠️  Title mismatch!")
            print(f"     Your title:    {movie['title']}")
            print(f"     OMDB title:    {correct_title}")
            
            if result.get('is_search_result'):
                print(f"     (from search results - verify this is correct!)")
            
            corrections_found.append({
                'id': movie['id'],
                'old_title': movie['title'],
                'new_title': correct_title,
                'year': movie['year'],
                'is_search': result.get('is_search_result', False)
            })
        else:
            print(f"  ✅ Title matches OMDB")
        
        time.sleep(0.3)  # Rate limiting
        
        # Stop if we're approaching API limit
        if api_calls >= 950:
            print("\n⚠️  Approaching API limit (950/1000), stopping...")
            break
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"Movies checked:           {api_calls}")
    print(f"Title corrections found:  {len(corrections_found)}")
    print(f"Not found in OMDB:        {len(not_found)}")
    print()
    
    if corrections_found:
        print("=" * 70)
        print("🔧 SUGGESTED CORRECTIONS")
        print("=" * 70)
        
        for correction in corrections_found:
            print(f"\nID {correction['id']}: {correction['old_title']} ({correction['year']})")
            print(f"  → {correction['new_title']}")
            if correction['is_search']:
                print(f"     ⚠️  From search - verify first!")
        
        print("\n" + "=" * 70)
        print("Would you like to apply these corrections? (yes/no)")
        print("=" * 70)
        
        # For non-interactive use, check command line arg
        if len(sys.argv) > 1 and sys.argv[1] == '--auto-apply':
            apply = True
            print("Auto-apply enabled, applying corrections...")
        else:
            try:
                response = input("Apply corrections? (yes/no): ").strip().lower()
                apply = response in ['yes', 'y']
            except:
                apply = False
        
        if apply:
            print("\nApplying corrections...")
            for correction in corrections_found:
                print(f"  Updating ID {correction['id']}: {correction['old_title']} → {correction['new_title']}")
                update_movie_title(correction['id'], correction['new_title'])
            print(f"\n✅ Applied {len(corrections_found)} corrections!")
            print("\nNow run fetch_posters.py to get the missing posters:")
            print("  docker compose exec web python /app/fetch_posters.py")
        else:
            print("\nNo corrections applied.")
            print("\nTo manually update a title:")
            print("  docker compose exec db psql -U postgres -d movieratings \\")
            print("    -c \"UPDATE movies SET title = 'Correct Title' WHERE id = 123;\"")
    
    if not_found:
        print("\n" + "=" * 70)
        print("❌ MOVIES NOT FOUND IN OMDB")
        print("=" * 70)
        print("These titles couldn't be found. Check for typos or missing years:")
        for movie in not_found[:20]:  # Show first 20
            print(f"  ID {movie['id']}: {movie['title']} ({movie['year'] or 'NO YEAR'})")
        if len(not_found) > 20:
            print(f"  ... and {len(not_found) - 20} more")

if __name__ == '__main__':
    main()
