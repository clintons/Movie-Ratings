#!/usr/bin/env python3
"""
Fix titles from a specific list of movies without posters
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import os
import time
import sys
import re

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'movieratings'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'db'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

OMDB_API_KEY = os.getenv('OMDB_API_KEY', '')

def parse_title_list(filename):
    """Parse the uploaded text file with movie titles"""
    titles = []
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Parse: "[41/224] ? No poster found: The Age of Adeline"
                match = re.search(r'No poster found: (.+)$', line.strip())
                if match:
                    title = match.group(1).strip()
                    titles.append(title)
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        print("Upload it to /root/movie-ratings/data/ on your LXC")
        sys.exit(1)
    
    return titles

def find_movie_in_db(title):
    """Find movie in database by title (case-insensitive)"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Try exact match first
    cur.execute(
        "SELECT id, title, year, poster_path, dad_rating, k_rating FROM movies WHERE title = %s",
        (title,)
    )
    movie = cur.fetchone()
    
    # If not found, try case-insensitive
    if not movie:
        cur.execute(
            "SELECT id, title, year, poster_path, dad_rating, k_rating FROM movies WHERE LOWER(title) = LOWER(%s)",
            (title,)
        )
        movie = cur.fetchone()
    
    cur.close()
    conn.close()
    return movie

def search_omdb(title, year=None):
    """Search OMDB for movie and return top results"""
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
            return [{
                'title': data.get('Title'),
                'year': data.get('Year'),
                'poster': data.get('Poster'),
                'imdb_id': data.get('imdbID'),
                'type': data.get('Type'),
                'match_type': 'exact'
            }]
        
        # If not found, search for similar titles
        search_url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={title}"
        response = requests.get(search_url, timeout=5)
        data = response.json()
        
        if data.get('Response') == 'True' and data.get('Search'):
            results = []
            for item in data['Search'][:5]:  # Top 5 results
                results.append({
                    'title': item.get('Title'),
                    'year': item.get('Year'),
                    'poster': item.get('Poster'),
                    'imdb_id': item.get('imdbID'),
                    'type': item.get('Type'),
                    'match_type': 'search'
                })
            return results
        
        return None
        
    except Exception as e:
        print(f"    ⚠️  API Error: {e}")
        return None

def update_movie(movie_id, new_title=None, new_year=None):
    """Update movie title and/or year"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    updates = []
    params = []
    
    if new_title:
        updates.append("title = %s")
        params.append(new_title)
    
    if new_year:
        updates.append("year = %s")
        params.append(int(new_year))
    
    if updates:
        params.append(movie_id)
        query = f"UPDATE movies SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
        cur.execute(query, params)
        conn.commit()
    
    cur.close()
    conn.close()

def get_user_choice(prompt, options):
    """Get user input with validation"""
    while True:
        try:
            choice = input(prompt).strip().lower()
            if choice in options:
                return choice
            print(f"    Invalid choice. Please enter one of: {', '.join(options)}")
        except (EOFError, KeyboardInterrupt):
            print("\n\n⏹️  Interrupted by user")
            sys.exit(0)

def main():
    if not OMDB_API_KEY:
        print("❌ OMDB_API_KEY not set in environment!")
        sys.exit(1)
    
    # Get filename from command line or use default
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = '/app/data/no_poster_found.txt'
    
    print("=" * 80)
    print("🎬 FIX TITLES FROM LIST")
    print("=" * 80)
    print(f"Reading titles from: {filename}\n")
    
    titles = parse_title_list(filename)
    total = len(titles)
    
    if total == 0:
        print("❌ No titles found in file!")
        sys.exit(1)
    
    print(f"Found {total} titles to check\n")
    print("=" * 80)
    
    corrected = 0
    skipped = 0
    not_found_in_db = 0
    not_found_in_omdb = 0
    api_calls = 0
    
    for i, title in enumerate(titles, 1):
        print(f"\n[{i}/{total}] 🎬 {title}")
        
        # Find in database
        movie = find_movie_in_db(title)
        
        if not movie:
            print(f"    ❌ Not found in your database!")
            not_found_in_db += 1
            
            choice = get_user_choice(
                "    Options: (s)kip, (q)uit: ",
                ['s', 'skip', 'q', 'quit']
            )
            
            if choice in ['q', 'quit']:
                break
            else:
                skipped += 1
                continue
        
        print(f"    DB: {movie['title']} ({movie['year'] or 'NO YEAR'})")
        if movie['dad_rating'] or movie['k_rating']:
            print(f"    Ratings: Dad={movie['dad_rating'] or '-'}, K={movie['k_rating'] or '-'}")
        
        # Search OMDB
        results = search_omdb(title, movie['year'])
        api_calls += 1
        
        if results is None:
            print(f"    ❌ Not found in OMDB")
            not_found_in_omdb += 1
            
            choice = get_user_choice(
                "    Options: (s)kip, (m)anual edit, (q)uit: ",
                ['s', 'skip', 'm', 'manual', 'q', 'quit']
            )
            
            if choice in ['q', 'quit']:
                break
            elif choice in ['m', 'manual']:
                new_title = input("    Enter correct title (or blank to skip): ").strip()
                if new_title:
                    new_year_str = input("    Enter year (or blank to keep current): ").strip()
                    new_year = new_year_str if new_year_str else None
                    update_movie(movie['id'], new_title, new_year)
                    print(f"    ✅ Updated manually")
                    corrected += 1
                else:
                    skipped += 1
            else:
                skipped += 1
            
            time.sleep(0.3)
            continue
        
        # Show results
        print(f"\n    📊 Found {len(results)} match(es) in OMDB:")
        for idx, result in enumerate(results, 1):
            match_indicator = "✓ EXACT" if result['match_type'] == 'exact' else "  search"
            print(f"    {idx}. [{match_indicator}] {result['title']} ({result['year']}) [{result['type']}]")
        
        # Check if title/year matches
        title_matches = movie['title'] == results[0]['title']
        year_matches = str(movie['year']) == results[0]['year'] if movie['year'] else False
        
        if title_matches and year_matches:
            print(f"    ✅ Perfect match - title and year correct!")
            skipped += 1
            time.sleep(0.3)
            continue
        
        # Suggest changes
        print(f"\n    📝 Suggested changes:")
        if not title_matches:
            print(f"    Title:  '{movie['title']}'")
            print(f"         → '{results[0]['title']}'")
        if not year_matches:
            print(f"    Year:   {movie['year'] or 'NOT SET'}")
            print(f"         → {results[0]['year']}")
        
        # Ask user
        if len(results) == 1:
            choice = get_user_choice(
                "\n    Options: (y)es update, (n)o skip, (m)anual edit, (q)uit: ",
                ['y', 'yes', 'n', 'no', 'm', 'manual', 'q', 'quit']
            )
        else:
            choice = get_user_choice(
                f"    Choose: 1-{len(results)}, (n)o skip, (m)anual, (q)uit: ",
                [str(x) for x in range(1, len(results) + 1)] + ['n', 'no', 'm', 'manual', 'q', 'quit']
            )
        
        if choice in ['q', 'quit']:
            print("\n⏹️  Stopping...")
            break
        
        elif choice in ['n', 'no']:
            print(f"    ⏭️  Skipped")
            skipped += 1
        
        elif choice in ['m', 'manual']:
            new_title = input("    Enter correct title (or blank to skip): ").strip()
            if new_title:
                new_year_str = input("    Enter year (or blank to keep current): ").strip()
                new_year = new_year_str if new_year_str else None
                update_movie(movie['id'], new_title, new_year)
                print(f"    ✅ Updated manually")
                corrected += 1
            else:
                skipped += 1
        
        elif choice in ['y', 'yes'] or choice.isdigit():
            # Apply correction
            idx = 0 if choice in ['y', 'yes'] else int(choice) - 1
            selected = results[idx]
            
            new_title = selected['title'] if not title_matches else None
            new_year = selected['year'] if not year_matches else None
            
            update_movie(movie['id'], new_title, new_year)
            
            changes = []
            if new_title:
                changes.append(f"title → {new_title}")
            if new_year:
                changes.append(f"year → {new_year}")
            
            print(f"    ✅ Updated: {', '.join(changes)}")
            corrected += 1
        
        time.sleep(0.3)
        
        # API limit check
        if api_calls >= 950:
            print("\n⚠️  Approaching API limit, stopping...")
            break
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SESSION SUMMARY")
    print("=" * 80)
    print(f"Titles from file:     {total}")
    print(f"Checked:              {i}")
    print(f"Corrected:            {corrected}")
    print(f"Skipped:              {skipped}")
    print(f"Not in DB:            {not_found_in_db}")
    print(f"Not in OMDB:          {not_found_in_omdb}")
    print(f"API calls used:       {api_calls}")
    
    if corrected > 0:
        print("\n✅ Updates saved to database!")
        print("\nNext: Fetch posters for corrected movies:")
        print("  docker compose exec web python /app/fetch_posters.py")
    
    print("=" * 80)

if __name__ == '__main__':
    main()
