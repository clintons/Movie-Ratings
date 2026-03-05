# Setting Up Your .env File

## Step 1: Rename the File

Rename `.env.example` to `.env`:

**On Windows:**
```powershell
# In the movie-ratings-app folder
Rename-Item .env.example .env
```

**On Linux/Mac:**
```bash
mv .env.example .env
```

## Step 2: Edit the .env File

Open `.env` in any text editor (Notepad, VS Code, nano, etc.)

### Add Your OMDB API Key

Replace `your_api_key_here` with your actual API key:

```bash
# Before:
OMDB_API_KEY=your_api_key_here

# After:
OMDB_API_KEY=a1b2c3d4
```

### Change Database Password (Recommended for Production)

For local testing, you can keep the default. For Proxmox deployment, change it:

```bash
# Default (OK for local testing):
POSTGRES_PASSWORD=postgres

# Production (recommended):
POSTGRES_PASSWORD=YourSecurePassword123!
```

## Step 3: Your Final .env File Should Look Like

```bash
# ==================================================
# Movie Ratings App - Environment Configuration
# ==================================================

# Database Configuration
POSTGRES_DB=movieratings
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YourSecurePassword123!    # <-- Changed this

# Database connection (don't change these)
POSTGRES_HOST=db
POSTGRES_PORT=5432

# OMDB API Key for fetching movie posters
OMDB_API_KEY=a1b2c3d4    # <-- Added your actual key
```

## Important Notes

✅ **Do This:**
- Rename `.env.example` to `.env`
- Add your OMDB API key
- Change the password for production

❌ **Don't Do This:**
- Don't commit `.env` to Git (it's in .gitignore)
- Don't share your API key publicly
- Don't change `POSTGRES_HOST` or `POSTGRES_PORT`

## Verification

After editing, verify your `.env` file exists:

**Windows:**
```powershell
Get-ChildItem -Force | Where-Object {$_.Name -eq ".env"}
```

**Linux/Mac:**
```bash
ls -la .env
```

You should see the `.env` file listed.

## What Happens Next

When you run `docker-compose up -d`, it will:
1. Read the `.env` file automatically
2. Use your OMDB API key for poster fetching
3. Set up PostgreSQL with your chosen credentials
4. Connect the web app to the database

## Troubleshooting

**Problem:** "OMDB_API_KEY not found"
- Make sure you renamed `.env.example` to `.env`
- Check that there are no spaces around the `=` sign
- Verify the file is in the same directory as `docker-compose.yml`

**Problem:** "Database connection failed"
- Make sure `POSTGRES_HOST=db` (not localhost)
- Don't change `POSTGRES_PORT` from 5432
- Ensure password matches in all fields

**Problem:** "No posters loading"
- Verify your OMDB API key is correct
- Check logs: `docker-compose logs web`
- You can manually test: `docker-compose exec web python /app/fetch_posters.py`
