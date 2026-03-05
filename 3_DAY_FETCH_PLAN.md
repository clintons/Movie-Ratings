# 3-Day Poster Fetch Plan (2,300 Movies)

## Your Scenario
- Total movies: ~2,300
- API limit: 1,000 calls/day
- Need: 3 days to fetch all posters

## 📅 Day-by-Day Plan

### Day 1: Fetch First 900 Posters

```bash
# SSH into your LXC
ssh root@<LXC-IP>

# Navigate to project
cd /opt/movie-ratings-app

# Fetch first batch (900 posters, stay safely under 1,000 limit)
docker-compose exec web python /app/fetch_posters.py 900 0

# The script will show:
# - How many it's fetching (900)
# - Progress for each movie
# - Final results
# - Command for next day
```

**What the parameters mean:**
- `900` = Batch size (how many to fetch)
- `0` = Skip count (start from beginning)

**Expected output:**
```
======================================================================
🎬 MOVIE POSTER BATCH FETCH
======================================================================
Total movies in database: 2300
Already have posters:     0
Need to fetch:            2300

📦 BATCH MODE:
Fetching this batch:      900 posters
Will remain after:        1400 posters

💡 Next batch command:
   docker-compose exec web python /app/fetch_posters.py 900 900
======================================================================
```

### Day 2: Fetch Next 900 Posters

**Wait 24 hours** for API limit to reset (midnight UTC)

```bash
# SSH into your LXC
ssh root@<LXC-IP>

# Navigate to project
cd /opt/movie-ratings-app

# Fetch second batch (skip first 900, fetch next 900)
docker-compose exec web python /app/fetch_posters.py 900 900
```

**What happens:**
- Skips movies 1-900 (already have posters)
- Fetches movies 901-1800
- Shows next command for Day 3

**Expected output:**
```
======================================================================
🎬 MOVIE POSTER BATCH FETCH
======================================================================
Total movies in database: 2300
Already have posters:     900
Need to fetch:            1400
Skipping first:           900 movies (already fetched)
Remaining to fetch:       500

📦 BATCH MODE:
Fetching this batch:      500 posters
Will remain after:        0 posters
======================================================================
```

Wait, that's not right for 2,300 movies. Let me recalculate...

Actually for 2,300 movies:
- Day 1: Movies 1-900 (900 posters)
- Day 2: Movies 901-1800 (900 posters)  
- Day 3: Movies 1801-2300 (500 posters)

### Day 3: Fetch Remaining ~500 Posters

**Wait another 24 hours**

```bash
# SSH into your LXC
ssh root@<LXC-IP>

# Navigate to project
cd /opt/movie-ratings-app

# Fetch final batch (skip first 1800, fetch remaining)
docker-compose exec web python /app/fetch_posters.py 900 1800
```

**What happens:**
- Skips movies 1-1800 (already have posters)
- Fetches remaining ~500 movies
- Shows completion message

**Expected output:**
```
======================================================================
🎬 MOVIE POSTER BATCH FETCH
======================================================================
Total movies in database: 2300
Already have posters:     1800
Need to fetch:            500
Skipping first:           1800 movies (already fetched)
Remaining to fetch:       500

📦 BATCH MODE:
Fetching this batch:      500 posters
Will remain after:        0 posters

======================================================================
Starting poster download...
======================================================================
[1/500] ✓ Downloaded: The Shawshank Redemption (1994)
[2/500] ✓ Downloaded: The Godfather (1972)
...
[500/500] ✓ Downloaded: Final Movie (2024)

======================================================================
📊 BATCH RESULTS
======================================================================
✅ Successfully downloaded: 450
❌ Failed to fetch:         30
⏭️  Skipped (no poster):    20
======================================================================

✅ ALL POSTERS COMPLETE!
======================================================================
```

## 🎯 Quick Reference Commands

| Day | Command | Fetches Movies |
|-----|---------|---------------|
| 1 | `docker-compose exec web python /app/fetch_posters.py 900 0` | 1-900 |
| 2 | `docker-compose exec web python /app/fetch_posters.py 900 900` | 901-1800 |
| 3 | `docker-compose exec web python /app/fetch_posters.py 900 1800` | 1801-2300 |

## 💡 Tips

### Check Progress Anytime
```bash
# Count posters already downloaded
ls posters/*.jpg 2>/dev/null | wc -l

# Or from Windows PowerShell (if accessing the folder)
(Get-ChildItem posters\*.jpg).Count
```

### If You Forget Where You Left Off
Just run without parameters and it will tell you:
```bash
docker-compose exec web python /app/fetch_posters.py
```

It will show how many you have and suggest the next batch command.

### Resume After Interruption
If the script stops mid-batch, just run the same command again:
```bash
# It will skip already-downloaded posters automatically
docker-compose exec web python /app/fetch_posters.py 900 900
```

### View Logs in Real-Time
```bash
# In another terminal, watch the logs
docker-compose logs -f web
```

## ⚠️ Important Notes

1. **Wait for limit reset** - OMDB resets at midnight UTC
   - Check current UTC time: `date -u`
   - Or use: https://time.is/UTC

2. **Script auto-skips existing posters** - Safe to re-run commands

3. **Each fetch takes time** - 900 posters × 0.5 seconds = ~7.5 minutes

4. **Network issues?** - Just re-run the same command, it resumes

5. **Don't delete posters** between batches!

## 🔍 Verification

After each day, verify your progress:

```bash
# Check poster count
ls -1 posters/*.jpg | wc -l

# Check against database
docker-compose exec db psql -U postgres -d movieratings -c "SELECT COUNT(*) FROM movies;"

# Should show:
# Day 1: ~900 posters
# Day 2: ~1800 posters  
# Day 3: ~2300 posters
```

## 📊 Expected Timeline

| Time | Action | API Calls | Total Posters |
|------|--------|-----------|---------------|
| Day 1, 3:00 PM | Run first batch | 900 | 900 |
| Day 2, 3:00 PM | Run second batch | 900 | 1,800 |
| Day 3, 3:00 PM | Run final batch | 500 | 2,300 |

**Total time: 3 days**  
**Total API calls: 2,300**  
**Cost: $0** (free tier)

## 🎬 What to Do While Waiting

Between fetch days, you can:
- ✅ Browse your movies (already imported)
- ✅ Add new movies manually
- ✅ Edit existing entries
- ✅ Test search and sort features
- ✅ Customize the design

Movies without posters will show the placeholder image until fetched.

## 🚨 Troubleshooting

**Script says "No API key":**
- Check `.env` file has `OMDB_API_KEY=your_actual_key`
- Restart containers: `docker-compose restart`

**"Connection refused" error:**
- Database not ready yet, wait 10 seconds and retry

**Hit rate limit mid-batch:**
- Don't worry! Tomorrow, run the same command again
- It will skip already-downloaded posters

**Some posters failed:**
- Normal - not all movies are in OMDB
- They'll show placeholder images
- You can manually add poster images to `posters/` folder

## ✅ Success Criteria

After Day 3, you should have:
- ✅ ~2,000-2,200 posters (some movies won't have posters in OMDB)
- ✅ Beautiful movie website with images
- ✅ All within free API tier

## 🎯 Alternative: Manual Control

If you want more control, you can specify exact ranges:

```bash
# Day 1: Movies with ID 1-900
docker-compose exec web python /app/fetch_posters.py 900 0

# Day 2: Movies with ID 901-1800  
docker-compose exec web python /app/fetch_posters.py 900 900

# Day 3: Movies with ID 1801+
docker-compose exec web python /app/fetch_posters.py 900 1800
```

The script handles everything automatically - you just need to wait between days!
