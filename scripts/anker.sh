# Anker 14 W panel to charge USB drives

mkdir -p $SOLAR_PROPHET_STORE_DIR && \
    python3 ../solar_prophet.py \
	    --panel_name "Anker" \
	    --panel_direction 175 \
	    --panel_slope 45 \
	    --panel_area 0.12 \
	    --efficiency 14 \
            --threshold 0 \
	    --plot $SOLAR_PROPHET_STORE_DIR/plot $1

