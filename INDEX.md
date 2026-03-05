# Movie Ratings Spreadsheet - Project Index

## 📦 What's Included

This is a complete, ready-to-deploy web application for managing movie ratings.

### 📄 Documentation Files

- **QUICKSTART.md** ⭐ - Start here! Quick 5-minute setup guide
- **README.md** - Complete feature documentation  
- **PROXMOX_DEPLOYMENT.md** - Guide for deploying to Proxmox LXC
- **INDEX.md** - This file

### 🚀 Application Files

#### Core Application
- `app/app.py` - Main Flask web application
- `app/init_db.py` - Database initialization and Excel import
- `app/templates/` - HTML templates
  - `base.html` - Base template with minimalist design
  - `index.html` - Main movie list page
  - `add_movie.html` - Add new movie form
  - `edit_movie.html` - Edit existing movie

#### Configuration
- `docker-compose.yml` - Docker orchestration
- `Dockerfile` - Application container definition
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variable template
- `.gitignore` - Git ignore rules

#### Utilities
- `start.sh` - Easy startup script
- `fetch_posters.py` - Batch poster download utility
- `create_placeholder.py` - Generate placeholder poster image

### 📁 Directories

- `data/` - Place your `Movie Ratings.xlsx` file here
- `posters/` - Movie poster images (auto-generated)
- `app/` - Application code

## 🎯 Quick Start (3 Steps)

1. **Copy your Excel file**:
   ```bash
   cp "F:\Claude\Movie Ratings.xlsx" ./data/
   ```

2. **Start the application**:
   ```bash
   ./start.sh
   ```

3. **Open in browser**:
   - http://localhost:5000

## 🌟 Features

✅ **View movies** - Paginated list (10 per page)  
✅ **Search** - Find movies by title or category  
✅ **Sort** - By date, year, rating, category, or title  
✅ **Add movies** - Web form with validation  
✅ **Edit movies** - Update any entry  
✅ **Movie posters** - Auto-download from OMDB API  
✅ **Minimalist design** - Clean, white space, professional  
✅ **Docker ready** - One command deployment  
✅ **Proxmox compatible** - Run in LXC container  

## 📖 Documentation Quick Links

### For First-Time Users
→ Read **QUICKSTART.md**

### For Detailed Information
→ Read **README.md**

### For Proxmox Deployment
→ Read **PROXMOX_DEPLOYMENT.md**

## 🔧 System Requirements

### To Run Locally
- Docker and Docker Compose
- 2GB free RAM
- 5GB free disk space

### To Run on Proxmox
- Ubuntu LXC container
- 2 CPU cores
- 2GB RAM
- 10GB disk

## 🎬 What Happens on First Run

1. **Database creation** - PostgreSQL database initialized
2. **Excel import** - Your movie data imported automatically
3. **Web server start** - Flask app running on port 5000
4. **Ready!** - Access at http://localhost:5000

## 💡 Pro Tips

- **Get OMDB API key** (free) for movie posters:
  - http://www.omdbapi.com/apikey.aspx
  - Add to `.env` file

- **Batch fetch posters**:
  ```bash
  docker-compose exec web python /app/fetch_posters.py
  ```

- **Backup your data**:
  ```bash
  docker-compose exec db pg_dump -U postgres movieratings > backup.sql
  ```

## 🛠️ Common Commands

```bash
# Start
./start.sh

# Stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f

# Backup database
docker-compose exec db pg_dump -U postgres movieratings > backup.sql
```

## 🌐 Access from Other Devices

Find your computer's IP and access from any device on your network:
- http://YOUR-IP:5000

## 📱 Mobile Friendly

The web interface works great on:
- Desktop browsers
- Tablets
- Phones

## 🔐 Security Notes

For local use:
- Default passwords are fine
- No internet exposure

For production/Proxmox:
- Change database password in `.env`
- Set up firewall rules
- Consider HTTPS with reverse proxy

## 📊 Data Structure

Your Excel file should have columns like:
- Title (required)
- Year
- Rating  
- Date Watched
- Category/Genre
- Notes

Column names are flexible - the importer auto-detects.

## 🎨 Customization

All easily customizable:
- **Colors/Fonts**: Edit `app/templates/base.html`
- **Port**: Edit `docker-compose.yml`
- **Fields**: Edit `app/init_db.py` and templates

## 🐛 Troubleshooting

**Problem**: Can't connect to http://localhost:5000  
**Solution**: Wait 10 seconds for startup, or check logs

**Problem**: Excel import failed  
**Solution**: Verify file name and location: `data/Movie Ratings.xlsx`

**Problem**: Port already in use  
**Solution**: Edit docker-compose.yml and change port

**Problem**: No posters showing  
**Solution**: Get OMDB API key or use placeholders

## 📦 What's Next?

1. ✅ Run locally and test
2. ✅ Add/edit some movies
3. ✅ Get OMDB key for posters  
4. 🚀 Deploy to Proxmox for permanent hosting

## 🎓 Learning Resources

- Flask: https://flask.palletsprojects.com/
- Docker: https://docs.docker.com/
- PostgreSQL: https://www.postgresql.org/docs/
- Proxmox: https://pve.proxmox.com/wiki/

## 📞 Support

Having issues?
1. Check the logs: `docker-compose logs`
2. Read troubleshooting in README.md
3. Review QUICKSTART.md for setup steps

## 🌟 Enjoy!

You now have a complete, professional movie ratings website!

- Clean, minimalist design ✨
- Fast and responsive 🚀
- Easy to use 👌
- Fully contained in Docker 🐳
- Deploy anywhere 🌍

---

**Blog**: [blog.strombotne.com](http://blog.strombotne.com)

**Created**: February 2026
