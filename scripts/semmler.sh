mkdir -p $PANEL_ESTIMATE_STORE_DIR && \
    python3 panel_estimate.py \
	    --panel_name "Semmler" \
	    --panel_direction 170 \
	    --panel_area 480 \
	    --efficiency 16 \
            --battery_threshold 0 \
	    --plot $PANEL_ESTIMATE_STORE_DIR

