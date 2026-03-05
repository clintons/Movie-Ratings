#!/usr/bin/env python3
"""Initialize database and import CSV data - Complete Movie Ratings structure"""

import psycopg2
import csv
import sys
import os
from datetime import datetime

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'movieratings'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

def wait_for_db():
    """Wait for database to be ready"""
    import time
    max_retries = 30
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            print("Database is ready!")
            return True
        except psycopg2.OperationalError:
            print(f"Waiting for database... ({i+1}/{max_retries})")
            time.sleep(2)
    return False

def create_tables():
    """Create database tables with all columns"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Drop existing table to recreate with new structure
    cur.execute("DROP TABLE IF EXISTS movies CASCADE")
    
    # Create movies table with ALL columns from CSV
    cur.execute("""
        CREATE TABLE movies (
            id SERIAL PRIMARY KEY,
            date_dad_watched DATE,
            date_k_watched DATE,
            title VARCHAR(500) NOT NULL,
            year INTEGER,
            streaming VARCHAR(200),
            lang_country VARCHAR(200),
            genre VARCHAR(200),
            k_rating VARCHAR(50),
            dad_rating VARCHAR(50),
            spencer_rating VARCHAR(50),
            dad_category VARCHAR(200),
            imdb_link TEXT,
            poster_path VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for sorting
    cur.execute("CREATE INDEX idx_date_dad_watched ON movies(date_dad_watched DESC NULLS LAST)")
    cur.execute("CREATE INDEX idx_date_k_watched ON movies(date_k_watched DESC NULLS LAST)")
    cur.execute("CREATE INDEX idx_year ON movies(year DESC NULLS LAST)")
    cur.execute("CREATE INDEX idx_genre ON movies(genre)")
    cur.execute("CREATE INDEX idx_dad_rating ON movies(dad_rating)")
    cur.execute("CREATE INDEX idx_k_rating ON movies(k_rating)")
    cur.execute("CREATE INDEX idx_spencer_rating ON movies(spencer_rating)")
    cur.execute("CREATE INDEX idx_dad_category ON movies(dad_category)")
    cur.execute("CREATE INDEX idx_title ON movies(title)")
    
    conn.commit()
    cur.close()
    conn.close()
    print("Tables created successfully!")

def parse_date(date_str):
    """Parse MM/DD/YYYY date format to PostgreSQL date"""
    if not date_str or not date_str.strip():
        return None
    
    try:
        return datetime.strptime(date_str.strip(), '%m/%d/%Y').date()
    except:
        try:
            return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
        except:
            return None

def import_csv_data(csv_path):
    """
    Import ALL data from CSV file
    
    CSV Column Positions:
    0: date Dad watched (MM/DD/YYYY)
    1: date K watched (MM/DD/YYYY)
    2: Movie (title)
    3: Year (integer)
    4: Streaming (service name)
    5: Lang/ Country
    6: Genre
    7: K's Rating
    8: Dad's Rating
    9: Spencer's Rating
    10: Dad's Category
    11: Link (IMDB URL)
    12: (empty column - ignored)
    """
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        print("Skipping import. Database is ready for manual entry.")
        return
    
    try:
        print(f"Reading CSV file: {csv_path}")
        
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        imported = 0
        skipped = 0
        
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            
            # Read and display header
            headers = next(reader)
            print(f"\nCSV Structure:")
            for idx, header in enumerate(headers):
                if header:
                    print(f"  Position {idx}: {header}")
            print()
            
            # Import data rows
            for row_num, row in enumerate(reader, start=2):
                if not any(row):
                    continue
                
                if len(row) < 11:
                    print(f"Row {row_num}: Skipping - insufficient columns")
                    skipped += 1
                    continue
                
                # Extract ALL columns by position
                date_dad = row[0].strip() if row[0] else ''
                date_k = row[1].strip() if row[1] else ''
                title = row[2].strip() if row[2] else ''
                year_str = row[3].strip() if row[3] else ''
                streaming = row[4].strip() if row[4] else ''
                lang_country = row[5].strip() if row[5] else ''
                genre = row[6].strip() if row[6] else ''
                k_rating = row[7].strip() if row[7] else ''
                dad_rating = row[8].strip() if row[8] else ''
                spencer_rating = row[9].strip() if row[9] else ''
                dad_category = row[10].strip() if row[10] else ''
                imdb_link = row[11].strip() if len(row) > 11 and row[11] else ''
                
                # Skip if no title
                if not title:
                    skipped += 1
                    continue
                
                # Parse dates
                date_dad_watched = parse_date(date_dad)
                date_k_watched = parse_date(date_k)
                
                # Parse year
                year = None
                if year_str:
                    try:
                        year = int(year_str)
                    except:
                        pass
                
                # Convert empty strings to None
                streaming = streaming or None
                lang_country = lang_country or None
                genre = genre or None
                k_rating = k_rating or None
                dad_rating = dad_rating or None
                spencer_rating = spencer_rating or None
                dad_category = dad_category or None
                imdb_link = imdb_link or None
                
                # Insert into database
                try:
                    cur.execute("""
                        INSERT INTO movies (
                            date_dad_watched, date_k_watched, title, year,
                            streaming, lang_country, genre,
                            k_rating, dad_rating, spencer_rating,
                            dad_category, imdb_link
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        date_dad_watched, date_k_watched, title, year,
                        streaming, lang_country, genre,
                        k_rating, dad_rating, spencer_rating,
                        dad_category, imdb_link
                    ))
                    imported += 1
                    
                    if imported % 100 == 0:
                        print(f"  Imported {imported} movies...")
                        
                except Exception as e:
                    print(f"Row {row_num}: Error importing '{title}' - {e}")
                    skipped += 1
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"\n{'='*60}")
        print(f"✅ Import Complete!")
        print(f"   Successfully imported: {imported} movies")
        print(f"   Skipped: {skipped} rows")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"Error importing CSV: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("Waiting for database...")
    if not wait_for_db():
        print("Database not available!")
        sys.exit(1)
    
    print("Creating tables...")
    create_tables()
    
    csv_path = '/app/data/Movie Ratings.csv'
    print(f"Importing data from {csv_path}...")
    import_csv_data(csv_path)
    
    print("Database initialization complete!")
