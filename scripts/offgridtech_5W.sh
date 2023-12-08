mkdir -p $PANEL_ESTIMATE_STORE_DIR && \
    python3 ../panel_estimate.py \
	    --panel_name "Offgridtech 5W" \
	    --panel_direction 175 \
	    --panel_slope 60
	    --panel_area 0.032 \
	    --efficiency 16 \
            --threshold 0 \
	    --plot $PANEL_ESTIMATE_STORE_DIR $1
	    
