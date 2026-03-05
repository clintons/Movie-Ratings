# Using CSV Files (Simpler Alternative to Excel)

## Why CSV is Easier

✅ **Advantages of CSV:**
- No need for openpyxl library (simpler)
- Smaller file size
- Easier to edit (any text editor)
- Faster to read
- Universal format
- Easy to export from Excel

## 📁 Converting Excel to CSV

### Method 1: From Excel (Recommended)

1. Open `Movie Ratings.xlsx` in Excel
2. Click **File → Save As**
3. Choose **CSV (Comma delimited) (*.csv)**
4. Save as `Movie Ratings.csv`
5. Done!

### Method 2: From Google Sheets

1. Open your spreadsheet
2. Click **File → Download → Comma Separated Values (.csv)**
3. Save as `Movie Ratings.csv`

### Method 3: From LibreOffice Calc

1. Open `Movie Ratings.xlsx`
2. Click **File → Save As**
3. File type: **Text CSV (.csv)**
4. Save

## 📋 CSV Format Requirements

### Header Row (First Row)

Your CSV should have a header row with column names like:

```csv
Title,Year,Rating,Date Watched,Dad's Category,Notes
```

Or any variation like:
```csv
Movie,Year,Score,Date,Category,Comments
Movie Name,Release Year,My Rating,Watched On,Genre,Notes
```

The importer auto-detects columns by looking for keywords!

### Example CSV Content

```csv
Title,Year,Rating,Date Watched,Dad's Category,Notes
The Shawshank Redemption,1994,9.5,2023-01-15,Drama,Amazing story about hope
The Godfather,1972,9,2023-02-20,Crime,Classic mafia film
Inception,2010,8.5,2023-03-10,Sci-Fi,Mind-bending thriller
```

## 🚀 Using CSV with the App

### Option 1: Use CSV Instead of Excel (Simplest!)

```bash
# Just place your CSV file in the data folder
cp "F:\Claude\Movie Ratings.csv" data/

# Start the app (it will automatically detect the CSV)
docker-compose up -d
```

The script automatically looks for:
1. `data/Movie Ratings.csv` (first priority)
2. `data/Movie Ratings.xlsx` (fallback)

### Option 2: Use Both (CSV Takes Priority)

If both files exist, CSV is used first:
```
data/
├── Movie Ratings.csv   ← Used (higher priority)
└── Movie Ratings.xlsx  ← Ignored
```

## 📝 CSV Field Mapping

The importer is smart and looks for these keywords:

| Database Field | Matches CSV Headers Containing |
|---------------|-------------------------------|
| `title` | title, movie, name |
| `year` | year |
| `rating` | rating, score |
| `date_watched` | date, watched |
| `dads_category` | category, genre, dad |
| `notes` | note, comment |

**Case insensitive!** Works with: "Title", "TITLE", "title"

## 🔧 Common CSV Issues & Fixes

### Issue 1: Commas in Movie Titles

**Problem:**
```csv
Title,Year
The Good, the Bad and the Ugly,1966  ← Broken! Extra comma
```

**Solution:** Use quotes
```csv
Title,Year
"The Good, the Bad and the Ugly",1966  ✓ Works!
```

Excel handles this automatically when saving as CSV.

### Issue 2: Line Breaks in Notes

**Problem:**
```csv
Title,Notes
Inception,Great movie
but confusing  ← Broken! Unquoted line break
```

**Solution:** Use quotes
```csv
Title,Notes
"Inception","Great movie
but confusing"  ✓ Works!
```

### Issue 3: Encoding Issues (Special Characters)

If you have special characters (é, ñ, ü, etc.):

**Solution:** Save as **UTF-8 CSV**

In Excel:
1. **File → Save As**
2. Choose **CSV UTF-8 (Comma delimited) (*.csv)**

In Notepad:
1. **File → Save As**
2. Encoding: **UTF-8**

## 📊 Sample CSV Template

Create a file called `Movie Ratings.csv`:

```csv
Title,Year,Rating,Date Watched,Dad's Category,Notes
The Shawshank Redemption,1994,9.5,2023-01-15,Drama,One of the greatest films ever made
The Dark Knight,2008,9,2023-02-10,Action,Heath Ledger's Joker is unforgettable
Forrest Gump,1994,8.5,2023-03-05,Drama,Life is like a box of chocolates
The Matrix,1999,8.5,2023-03-20,Sci-Fi,Mind-bending action classic
Pulp Fiction,1994,8,2023-04-12,Crime,Tarantino's masterpiece
```

## 🎯 Quick Start with CSV

**Full workflow:**

```bash
# 1. Export Excel to CSV
# (Do this in Excel: Save As → CSV)

# 2. Copy CSV to project
cp "F:\Claude\Movie Ratings.csv" movie-ratings-app/data/

# 3. Start the app
cd movie-ratings-app
docker-compose up -d

# 4. Watch import logs
docker-compose logs -f web

# 5. Access your site
# Open browser: http://localhost:5000
```

## 📦 Updating the Docker Image

The app now supports both CSV and Excel without any changes needed!

The init script automatically:
1. Checks for `Movie Ratings.csv` first
2. Falls back to `Movie Ratings.xlsx`
3. Auto-detects file format
4. Imports your data

## 💡 Pro Tips

### Tip 1: Keep Both Formats

```
data/
├── Movie Ratings.xlsx  ← Master file (edit here)
└── Movie Ratings.csv   ← Export for app (updated when needed)
```

**Workflow:**
1. Edit `Movie Ratings.xlsx` in Excel
2. Export to CSV when ready to update
3. Restart app: `docker-compose restart`

### Tip 2: Direct CSV Editing

CSV files can be edited directly:
- Notepad, VS Code, Sublime Text
- Excel (File → Open → select CSV)
- Google Sheets (File → Import)
- LibreOffice Calc

### Tip 3: Backup Your CSV

```bash
# Backup before major changes
cp data/Movie\ Ratings.csv data/Movie\ Ratings.backup.csv

# Restore if needed
cp data/Movie\ Ratings.backup.csv data/Movie\ Ratings.csv
```

## 🔄 Switching from Excel to CSV

Already using Excel? Switch to CSV:

```bash
# 1. Export Excel to CSV (in Excel)

# 2. Stop the app
docker-compose down

# 3. Remove old data (optional)
docker-compose down -v  # Removes database

# 4. Add CSV file
cp "F:\Claude\Movie Ratings.csv" data/

# 5. Start fresh
docker-compose up -d
```

## ❓ FAQ

**Q: Can I use both CSV and Excel?**  
A: Yes, but CSV takes priority if both exist.

**Q: Do I need to change anything in the code?**  
A: Nope! The app auto-detects the format.

**Q: What if my CSV has different column names?**  
A: The importer is smart and looks for keywords. Most variations work!

**Q: Can I have quotes in my notes field?**  
A: Yes! Use double quotes: `"He said ""hello"" to me"`

**Q: Does CSV support dates?**  
A: Yes! Use format: `YYYY-MM-DD` (e.g., `2024-01-15`)

## ✅ Recommendation

**For simplicity, use CSV!**

Advantages:
- ✅ Smaller file size
- ✅ Faster import
- ✅ Easy to edit anywhere
- ✅ Universal format
- ✅ No Excel dependency

The only downside:
- ❌ No formatting (bold, colors, etc.)
- But you don't need that for data import!

## 📁 Final File Structure

```
movie-ratings-app/
├── data/
│   └── Movie Ratings.csv   ← Your data file (CSV)
├── posters/
│   └── (auto-generated)
├── docker-compose.yml
└── ...
```

That's it! CSV makes everything simpler. 🎬
