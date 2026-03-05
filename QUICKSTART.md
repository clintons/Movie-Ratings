# Movie Ratings App - Quick Setup Guide

## 🎯 What You Need

1. Your Excel file: `Movie Ratings.xlsx`
2. Docker installed on your system
3. (Optional) Free OMDB API key for movie posters

## 📦 Complete Package

This folder contains everything needed to run your movie ratings website:

```
movie-ratings-app/
├── app/                    # Flask web application
├── data/                   # Place your Excel file here
├── posters/                # Movie posters (auto-generated)
├── docker-compose.yml      # Docker configuration
├── start.sh               # Easy startup script
├── README.md              # Full documentation
└── PROXMOX_DEPLOYMENT.md  # Proxmox setup guide
```

## 🚀 Three Ways to Run

### Option 1: Quick Start (Easiest)

```bash
# 1. Copy your Excel file
cp "/path/to/Movie Ratings.xlsx" ./data/

# 2. Run the startup script
./start.sh

# 3. Open browser
# http://localhost:5000
```

### Option 2: Manual Docker

```bash
# 1. Copy Excel file
mkdir -p data
cp "F:\Claude\Movie Ratings.xlsx" ./data/

# 2. (Optional) Get OMDB API key
# Visit: http://www.omdbapi.com/apikey.aspx
# Edit .env file with your key

# 3. Start Docker containers
docker-compose up -d

# 4. View logs
docker-compose logs -f

# 5. Access at http://localhost:5000
```

### Option 3: Deploy to Proxmox LXC

See `PROXMOX_DEPLOYMENT.md` for complete guide.

Quick version:
1. Create Ubuntu LXC with nesting enabled
2. Install Docker in LXC
3. Copy this folder to LXC
4. Run `docker-compose up -d`

## 🎨 Features

### ✅ What Works Out of the Box

- View all movies paginated (10 per page)
- Search by title or category
- Sort by: Date Watched, Year, Rating, Category, Title
- Add new movies via web form
- Edit existing entries
- Automatic database creation from Excel
- Placeholder posters

### 🔑 With OMDB API Key

- Automatic movie poster downloads
- High-quality thumbnail images
- Professional look

## 📋 Common Tasks

### View Your Movies
Just open: http://localhost:5000

### Add a New Movie
Click "+ Add Movie" button → Fill form → Submit

### Edit a Movie
Click "Edit" link next to any movie → Modify → Save

### Fetch All Posters
```bash
docker-compose exec web python /app/fetch_posters.py
```

### Backup Database
```bash
docker-compose exec db pg_dump -U postgres movieratings > backup.sql
```

### Stop the App
```bash
docker-compose down
```

### Restart the App
```bash
docker-compose restart
```

## 🔧 Customization

### Change Port
Edit `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Use port 8080 instead of 5000
```

### Modify Design
Edit `app/templates/base.html` for styling changes

### Add Custom Fields
1. Edit `app/init_db.py` - add database columns
2. Edit `app/app.py` - update routes
3. Edit templates - add form fields

## 🐛 Troubleshooting

### "Database not ready"
Wait 10 seconds and try again. First startup takes time.

### "Port 5000 in use"
Change port in docker-compose.yml or stop other service.

### "Excel import failed"
- Verify file is named exactly: `Movie Ratings.xlsx`
- Check it's in the `data/` folder
- View logs: `docker-compose logs web`

### Posters not loading
- Get OMDB API key and add to `.env`
- Or live with placeholder images
- Manual fetch: `docker-compose exec web python /app/fetch_posters.py`

## 📊 Excel File Format

The app auto-detects columns. Supported headers include:

- **Title** (required): Movie name
- **Year**: Release year  
- **Rating**: Your rating (any format)
- **Date Watched**: When you watched it
- **Category/Genre**: Dad's category
- **Notes**: Your comments

Headers are flexible - the importer looks for keywords.

## 🎬 Example Workflow

1. **Initial Setup**:
   ```bash
   ./start.sh
   ```

2. **Get OMDB Key** (optional):
   - Visit http://www.omdbapi.com/apikey.aspx
   - Copy key to `.env` file
   - Restart: `docker-compose restart`

3. **Fetch Posters**:
   ```bash
   docker-compose exec web python /app/fetch_posters.py
   ```

4. **Use the App**:
   - Browse movies
   - Search and filter
   - Add new entries
   - Edit ratings

5. **Share** (optional):
   - Deploy to Proxmox for 24/7 access
   - Set up reverse proxy with domain
   - Add HTTPS with Let's Encrypt

## 💾 Data Files

### Your Data Locations

- **Database**: Docker volume `postgres_data`
- **Posters**: `./posters/` folder
- **Excel backup**: Keep original in `./data/`

### Backup Everything

```bash
# Backup script
docker-compose exec db pg_dump -U postgres movieratings > backup-$(date +%Y%m%d).sql
tar -czf posters-backup-$(date +%Y%m%d).tar.gz posters/
```

## 📱 Access from Other Devices

Find your computer's IP address:

```bash
# Linux/Mac
ip addr show | grep inet

# Windows
ipconfig
```

Then access from phone/tablet: `http://<YOUR-IP>:5000`

## 🌐 Production Deployment

For serious/permanent deployment:

1. **Use Proxmox LXC** - See PROXMOX_DEPLOYMENT.md
2. **Set Strong Passwords** - Edit `.env`, change database password
3. **Enable HTTPS** - Use Let's Encrypt with NGINX
4. **Regular Backups** - Set up cron jobs
5. **Monitor Resources** - Check Docker logs

## 📚 Documentation

- **Full README**: `README.md` - Complete feature documentation
- **Proxmox Guide**: `PROXMOX_DEPLOYMENT.md` - LXC deployment
- **This File**: Quick reference for common tasks

## 🎯 Next Steps

1. ✅ Get your app running locally
2. ✅ Import your Excel data
3. ✅ Get OMDB API key for posters
4. ✅ Try adding/editing movies
5. 🚀 Deploy to Proxmox for permanent hosting

## 💡 Tips

- **Search**: Type in search box and press Enter
- **Sort**: Click column buttons to toggle ASC/DESC
- **Pagination**: Use arrows at bottom to navigate pages
- **Edit**: Small "Edit" link appears next to each movie
- **Posters**: Auto-fetch on add, or batch fetch later

## ❓ Questions?

Check the logs:
```bash
docker-compose logs web
docker-compose logs db
```

Still stuck? Review:
- README.md for detailed docs
- PROXMOX_DEPLOYMENT.md for deployment help
- Docker docs: https://docs.docker.com

---

**Enjoy your movie ratings website! 🎬**

Blog: [blog.strombotne.com](http://blog.strombotne.com)
