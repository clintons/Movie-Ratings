# Managing OMDB API Quota (1,000 calls/day limit)

## 📊 Understanding API Usage

### What Uses API Calls?

✅ **Uses API calls:**
- Running `fetch_posters.py` (1 call per movie without poster)
- Adding new movie via web form (1 call per movie)

❌ **Does NOT use API calls:**
- Starting/stopping Docker containers
- Viewing existing movies on website
- Editing movie details
- Searching/sorting movies
- Restarting the application
- Any movie that already has a poster

## 🎯 Your Poster Status

Check how many posters you already have:

```bash
# Count existing posters
ls -1 posters/*.jpg 2>/dev/null | wc -l

# Count movies in database
docker-compose exec db psql -U postgres -d movieratings -c "SELECT COUNT(*) FROM movies;"
```

## 💡 Strategy for Large Collections

### If you have MORE than 1,000 movies:

#### Option 1: Fetch in Daily Batches

**Day 1: Fetch first 1,000**
```bash
# Edit fetch_posters.py temporarily:
# Change line: cur.execute("SELECT id, title, year FROM movies ORDER BY id")
# To:          cur.execute("SELECT id, title, year FROM movies WHERE id <= 1000 ORDER BY id")

docker-compose exec web python /app/fetch_posters.py
```

**Day 2: Fetch next 1,000**
```bash
# Change to: WHERE id > 1000 AND id <= 2000
docker-compose exec web python /app/fetch_posters.py
```

#### Option 2: Fetch Most Important First

Prioritize movies by rating or date watched:

```bash
# Edit fetch_posters.py:
# Change: ORDER BY id
# To:     ORDER BY rating DESC LIMIT 1000
```

#### Option 3: Skip Poster Fetching

Just use placeholder images for now. Posters are nice-to-have, not required!

### If you have LESS than 1,000 movies:

**Just fetch them all at once:**
```bash
docker-compose exec web python /app/fetch_posters.py
```

## 🔄 Day-to-Day Operations

### Normal Daily Use (No API Calls):

```bash
# Starting the app
docker-compose up -d         # 0 API calls

# Stopping the app
docker-compose down          # 0 API calls

# Restarting
docker-compose restart       # 0 API calls

# Viewing movies
# Browse website             # 0 API calls
```

### Adding New Movies (1 API Call Each):

When you add a movie via the web form:
- Form submitted → 1 API call to fetch poster
- Poster saved to disk
- Never fetched again

**Monthly usage example:**
- Add 20 new movies/month = 20 API calls/month
- Well under the 30,000 monthly limit (1,000 × 30 days)

## 📅 Tracking Your Usage

The OMDB API doesn't provide usage statistics, but you can estimate:

```bash
# Count posters fetched today (Linux/Mac)
find posters/ -name "*.jpg" -mtime -1 | wc -l

# On Windows PowerShell
(Get-ChildItem posters\*.jpg | Where-Object {$_.LastWriteTime -gt (Get-Date).AddDays(-1)}).Count
```

## 🛡️ Built-in Protections

The app already has safeguards:

1. **Checks if poster exists** before making API calls
2. **Batch script warns** if over 900 posters needed
3. **Posters persist** in volume - never re-fetched
4. **Rate limiting** - 0.5 second delay between calls

## 🎬 Recommended Workflow

### Initial Setup:

```bash
# 1. Start app (imports Excel → database)
docker-compose up -d

# 2. Check how many movies you have
docker-compose exec db psql -U postgres -d movieratings -c "SELECT COUNT(*) FROM movies;"

# 3. If < 1000: Fetch all posters
docker-compose exec web python /app/fetch_posters.py

# 4. If > 1000: Fetch in batches (see Option 1 above)
```

### Ongoing Use:

```bash
# Just use the app normally
# - Add movies via web form (auto-fetches poster)
# - Edit existing movies (no API call)
# - Browse and search (no API calls)
```

## 💾 Poster Backup

Since posters are stored on disk, you can backup and restore:

```bash
# Backup
tar -czf posters-backup.tar.gz posters/

# Restore (if you rebuild container)
tar -xzf posters-backup.tar.gz
```

This way you never have to re-fetch posters!

## 🔧 Advanced: Fetch Specific Movies

Edit `fetch_posters.py` to fetch only specific movies:

```python
# Fetch only movies from a specific year
cur.execute("SELECT id, title, year FROM movies WHERE year = 2024 ORDER BY id")

# Fetch only movies with high ratings
cur.execute("SELECT id, title, year FROM movies WHERE rating >= '8' ORDER BY id")

# Fetch only recent additions
cur.execute("SELECT id, title, year FROM movies WHERE date_watched >= '2024-01-01' ORDER BY id")

# Fetch specific ID range
cur.execute("SELECT id, title, year FROM movies WHERE id BETWEEN 100 AND 200 ORDER BY id")
```

## ⚠️ If You Hit the Limit

If you exceed 1,000 calls in a day:

1. **API returns error** - Script shows failure message
2. **Posters already fetched** - Still work fine
3. **Wait until tomorrow** - Limit resets at midnight UTC
4. **Continue where you left off** - Script skips existing posters

## 📈 Scaling Beyond Free Tier

If you need more than 1,000/day:

**OMDB Plans:**
- Free: 1,000 calls/day
- Patron ($1/month): 100,000 calls/day
- Only needed if you frequently add many movies

**Alternative:**
- Just live with placeholder images
- Manually upload poster images to `posters/` folder
- Use different API (TMDb, etc.) - would require code changes

## ✅ Best Practices

1. **Fetch once, keep forever** - Backup your `posters/` folder
2. **Add movies gradually** - 1-10 movies/day is fine
3. **Don't re-run batch fetch** unless you delete posters
4. **Monitor your usage** - Count posters fetched per day
5. **Batch large imports** across multiple days

## 🎯 Bottom Line

For typical use:
- **Initial setup**: 1 large batch fetch (under 1,000 movies)
- **Daily use**: 0 API calls (just viewing movies)
- **Adding movies**: 1-5 API calls/day (adding new entries)
- **Total monthly**: ~150-300 calls (well under limit)

You'll rarely hit the 1,000/day limit unless doing initial bulk import of 1,000+ movies!
