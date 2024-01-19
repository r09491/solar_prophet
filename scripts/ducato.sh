# 120W panel on the roof of my camping van

# To assess the flat installation of the panel and car headings

mkdir -p $SOLAR_PROPHET_STORE_DIR/csv && \
    python3 ../solar_prophet.py \
	    --panel_name "Ducato" \
	    --panel_slope 90 \
	    --panel_area 0.6 \
	    --panel_efficiency 100 \
            --system_barrier 0 \
	    --plot $1

