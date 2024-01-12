mkdir -p $SOLAR_PROPHET_STORE_DIR && \
    python3 ../solar_prophet.py \
	    --panel_name "Offgridtech 5W" \
	    --panel_direction 175 \
	    --panel_slope 60
	    --panel_area 0.032 \
	    --efficiency 16 \
            --threshold 0 \
	    --plot $SOLAR_PROPHET_STORE_DIR $1
	    
