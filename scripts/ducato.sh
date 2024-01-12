# 120W panel on the roof of my camping van

# To assess the flat installation of the panel and car headings

mkdir -p $SOLAR_PROPHET_STORE_DIR && \
    python3 ../solar_prophet.py \
	    --panel_name "Ducato" \
	    --panel_slope 90 \
	    --panel_area 0.6 \
	    --efficiency 16 \
            --threshold 0 $1

