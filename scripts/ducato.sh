# 120W panel on the roof of my camping van

# To assess the flat installation of the panel and car headings

mkdir -p $PANEL_ESTIMATE_STORE_DIR && \
    python3 ../panel_estimate.py \
	    --panel_name "Ducato" \
	    --panel_slope 90 \
	    --panel_area 0.6 \
	    --efficiency 16 \
            --threshold 0 \
	    --plot $PANEL_ESTIMATE_STORE_DIR
