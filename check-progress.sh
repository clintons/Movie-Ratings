#!/bin/bash
# Check poster fetch progress

echo "======================================================================="
echo "🎬 MOVIE POSTER PROGRESS CHECK"
echo "======================================================================="

# Count posters
POSTER_COUNT=$(ls -1 posters/*.jpg 2>/dev/null | wc -l)
echo "📁 Posters downloaded:    $POSTER_COUNT"

# Get total movies from database
if command -v docker &> /dev/null; then
    TOTAL_MOVIES=$(docker compose exec -T db psql -U postgres -d movieratings -t -c "SELECT COUNT(*) FROM movies;" 2>/dev/null | tr -d ' ')
    
    if [ ! -z "$TOTAL_MOVIES" ]; then
        echo "📊 Total movies in DB:    $TOTAL_MOVIES"
        
        REMAINING=$((TOTAL_MOVIES - POSTER_COUNT))
        echo "⏳ Posters still needed:  $REMAINING"
        
        # Calculate percentage
        if [ $TOTAL_MOVIES -gt 0 ]; then
            PERCENT=$((POSTER_COUNT * 100 / TOTAL_MOVIES))
            echo "📈 Progress:              $PERCENT%"
        fi
        
        echo "======================================================================="
        
        # Suggest next batch command
        if [ $REMAINING -gt 0 ]; then
            if [ $REMAINING -le 900 ]; then
                BATCH_SIZE=$REMAINING
            else
                BATCH_SIZE=900
            fi
            
            echo ""
            echo "💡 NEXT STEP:"
            echo "   docker compose exec web python /app/fetch_posters.py $BATCH_SIZE $POSTER_COUNT"
            echo ""
            echo "⏰ Wait until tomorrow if you've already fetched 900+ today"
            echo "   (OMDB limit: 1,000 calls/day, resets at midnight UTC)"
        else
            echo ""
            echo "✅ ALL POSTERS DOWNLOADED!"
            echo "   Your movie website is complete with all available posters."
        fi
    else
        echo "⚠️  Cannot connect to database"
        echo "   Make sure containers are running: docker compose up -d"
    fi
else
    echo "⚠️  docker not found"
    echo "   Make sure Docker is installed and running"
fi

echo "======================================================================="
