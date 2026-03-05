# 🎬 Movie Ratings App - Complete Setup Package

## What I've Built For You

A complete, production-ready web application for your movie ratings spreadsheet with:

### ✨ Features
- ✅ Minimalist design with plenty of white space
- ✅ Pagination (10 movies per page)
- ✅ Search functionality
- ✅ Sort by: Date Watched, Year, Rating, Dad's Category, Title
- ✅ Add new movies via web form
- ✅ Edit existing entries (small edit link next to each)
- ✅ Automatic movie poster fetching and storage
- ✅ PostgreSQL database (auto-created from your Excel file)
- ✅ Docker containerized (ready for Proxmox LXC)
- ✅ Footer link to blog.strombotne.com

## 📦 What's Included

```
movie-ratings-app/
├── 📖 Documentation
│   ├── INDEX.md - Project overview (START HERE!)
│   ├── QUICKSTART.md - 5-minute setup guide
│   ├── README.md - Complete documentation
│   └── PROXMOX_DEPLOYMENT.md - Proxmox LXC guide
│
├── 🐍 Application Code
│   ├── app/
│   │   ├── app.py - Flask web application
│   │   ├── init_db.py - Database & Excel importer
│   │   └── templates/ - HTML templates
│   │       ├── base.html - Minimalist design
│   │       ├── index.html - Movie list
│   │       ├── add_movie.html - Add form
│   │       └── edit_movie.html - Edit form
│   │
│   ├── 🐳 Docker Files
│   ├── Dockerfile - App container
│   ├── docker-compose.yml - Full stack
│   └── requirements.txt - Dependencies
│
├── 🛠️ Utilities
│   ├── start.sh - Easy startup script
│   ├── fetch_posters.py - Batch poster fetcher
│   └── .env.example - Config template
│
└── 📁 Data Directories
    ├── data/ - Put your Excel file here
    └── posters/ - Auto-generated posters
```

## 🚀 Getting Started (3 Steps)

### Step 1: Copy Your Excel File
```bash
# Navigate to the project folder
cd movie-ratings-app

# Copy your Excel file to the data directory
# From Windows: F:\Claude\Movie Ratings.xlsx
# To: ./data/Movie Ratings.xlsx
```

### Step 2: Start the Application
```bash
# Make startup script executable
chmod +x start.sh

# Run it!
./start.sh

# Or manually with Docker Compose
docker-compose up -d
```

### Step 3: Open Your Browser
```
http://localhost:5000
```

That's it! Your movie ratings website is now running! 🎉

## 🎨 The Design

I've created a minimalist, professional design featuring:

- **Lots of white space** - Clean, uncluttered layout
- **Large movie posters** - 200x300px thumbnails
- **Clear typography** - Easy to read, modern fonts
- **Subtle borders** - Elegant separation between movies
- **Simple navigation** - Search, sort buttons, pagination
- **Professional forms** - Clean add/edit interfaces

The subtitle reads exactly as requested:  
**"... an historical listing of movies and TV mini-series viewings rated"**

## 🖼️ Movie Posters

### Automatic Poster Fetching

The app can automatically download movie posters from OMDB:

1. **Get a free API key**: http://www.omdbapi.com/apikey.aspx
2. **Add to `.env` file**: `OMDB_API_KEY=your_key_here`
3. **Posters auto-download** when you add movies

### Batch Fetch All Posters

After importing your Excel file:
```bash
docker-compose exec web python /app/fetch_posters.py
```

This will download posters for all movies in your database!

### Poster Storage

- Saved to: `posters/` folder
- Format: `{movie_id}.jpg`
- Thumbnails: 300x450px max
- High quality: JPEG, 85% quality

## 📊 Database

### Automatic Creation

The database is automatically created from your Excel file:

- **Table**: `movies`
- **Fields**: title, year, rating, date_watched, dads_category, notes
- **Indexes**: Optimized for sorting and searching
- **Database**: PostgreSQL 15

### Excel Import

The importer is smart - it auto-detects columns by looking for keywords:
- Title/Movie/Name → title
- Year → year
- Rating/Score → rating
- Date/Watched → date_watched
- Category/Genre/Dad → dads_category
- Note/Comment → notes

## 🔍 Search & Sort

### Search
- Type in search box
- Searches: titles and categories
- Real-time results

### Sort Options
- Date Watched ↑↓
- Year ↑↓
- Rating ↑↓
- Category ↑↓
- Title ↑↓

Click any sort button to toggle ascending/descending.

## ✏️ Add & Edit Movies

### Add New Movie
1. Click "+ Add Movie" button
2. Fill in the form (only title is required)
3. Submit
4. Poster automatically fetches (if API key configured)

### Edit Existing Movie
1. Find the movie in the list
2. Click small "Edit" link next to it
3. Modify any fields
4. Save changes
5. Or delete the movie

## 🐳 Docker Deployment

### Local Development
```bash
docker-compose up -d
```

### Proxmox LXC Production

Complete guide in `PROXMOX_DEPLOYMENT.md`:

1. Create Ubuntu LXC (with nesting enabled)
2. Install Docker
3. Copy project folder
4. Run `docker-compose up -d`
5. Access via LXC IP address

### What's Containerized

- **Web app**: Flask + Gunicorn (Python 3.11)
- **Database**: PostgreSQL 15
- **Volumes**: Persistent data storage
- **Network**: Isolated bridge network

## 📁 File Locations

### In Docker Containers
- **App code**: `/app/`
- **Excel file**: `/app/data/Movie Ratings.xlsx`
- **Posters**: `/app/static/posters/`
- **Database**: PostgreSQL volume

### On Your System
- **Excel file**: `./data/Movie Ratings.xlsx`
- **Posters**: `./posters/`
- **Database**: Docker volume (persisted)

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Database
POSTGRES_DB=movieratings
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# OMDB API (for posters)
OMDB_API_KEY=your_key_here
```

### Port Configuration
Default: `5000`

To change, edit `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Use port 8080
```

## 💾 Backup & Restore

### Backup Database
```bash
docker-compose exec db pg_dump -U postgres movieratings > backup.sql
```

### Backup Posters
```bash
tar -czf posters-backup.tar.gz posters/
```

### Restore Database
```bash
docker-compose exec -T db psql -U postgres movieratings < backup.sql
```

### Restore Posters
```bash
tar -xzf posters-backup.tar.gz
```

## 🛠️ Maintenance

### View Logs
```bash
docker-compose logs -f
```

### Restart App
```bash
docker-compose restart
```

### Stop App
```bash
docker-compose down
```

### Update Code
```bash
docker-compose up -d --build
```

## 🌐 Access from Other Devices

1. Find your computer's IP address:
   ```bash
   # Linux/Mac
   hostname -I
   
   # Windows
   ipconfig
   ```

2. Access from phone/tablet:
   ```
   http://YOUR-IP-ADDRESS:5000
   ```

## 📱 Mobile Responsive

The design works beautifully on:
- Desktop computers
- Laptops
- Tablets
- Smartphones

## 🎯 Next Steps

### Immediate
1. ✅ Copy Excel file to `data/` folder
2. ✅ Run `./start.sh`
3. ✅ Access http://localhost:5000
4. ✅ Browse your movies!

### Optional Enhancements
5. 🔑 Get OMDB API key
6. 🖼️ Fetch all posters
7. 🚀 Deploy to Proxmox
8. 🌍 Set up domain name
9. 🔒 Configure HTTPS

## 📖 Documentation Guide

- **First time?** → Read `INDEX.md`
- **Quick setup?** → Read `QUICKSTART.md`
- **Need details?** → Read `README.md`
- **Deploying to Proxmox?** → Read `PROXMOX_DEPLOYMENT.md`

## 🎨 Customization

### Change Colors
Edit `app/templates/base.html`, find the `<style>` section.

### Add Fields
1. Edit `app/init_db.py` - add database columns
2. Edit `app/app.py` - update routes
3. Edit templates - add form fields

### Modify Layout
All templates are in `app/templates/`:
- `base.html` - Overall design
- `index.html` - Movie list
- `add_movie.html` - Add form
- `edit_movie.html` - Edit form

## 🐛 Common Issues & Solutions

### "Can't connect to http://localhost:5000"
→ Wait 10 seconds for startup, check Docker is running

### "Excel import failed"
→ Verify file is named exactly: `Movie Ratings.xlsx`  
→ Check it's in `data/` folder

### "Port 5000 already in use"
→ Change port in `docker-compose.yml` or stop other service

### "No posters showing"
→ Get OMDB API key or posters will be placeholders

### "Database errors"
→ Reset: `docker-compose down -v && docker-compose up -d`

## ✅ What's Tested

- ✅ Docker build and run
- ✅ Database creation
- ✅ Excel import functionality
- ✅ Web interface rendering
- ✅ Search and sort
- ✅ Add/edit forms
- ✅ Poster fetching (with API key)
- ✅ Pagination
- ✅ Responsive design

## 🎬 Final Checklist

Before deploying:

- [ ] Excel file in `data/` folder
- [ ] OMDB API key in `.env` (optional)
- [ ] Docker installed and running
- [ ] Ports available (5000 default)
- [ ] Enough disk space (~5GB)

For production:

- [ ] Change database password
- [ ] Set up backups
- [ ] Configure firewall
- [ ] Consider HTTPS
- [ ] Test from multiple devices

## 🌟 Summary

You now have a **complete, professional movie ratings website**:

- 🎨 Beautiful minimalist design
- 🔍 Full search and sort
- ✏️ Easy add/edit forms
- 🖼️ Automatic poster fetching
- 💾 PostgreSQL database
- 🐳 Docker containerized
- 🚀 Proxmox ready

Everything is included and ready to run!

## 📞 Support

Check the documentation:
1. `QUICKSTART.md` - Quick setup
2. `README.md` - Full docs
3. `PROXMOX_DEPLOYMENT.md` - Deployment guide

View logs for debugging:
```bash
docker-compose logs -f
```

## 🎉 Enjoy Your Movie Ratings Website!

You can now:
- ✨ View all your rated movies
- 🔍 Search and filter
- 📊 Sort by any column
- ✏️ Add new entries
- 📝 Edit existing ones
- 🖼️ See beautiful movie posters

---

**Created for**: Movie Ratings Spreadsheet Project  
**Date**: February 15, 2026  
**Footer Link**: [blog.strombotne.com](http://blog.strombotne.com)  
**Ready to deploy!** 🚀
