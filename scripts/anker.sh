mkdir -p $PANEL_ESTIMATE_STORE_DIR && \
    python3 panel_estimate.py \
	    --panel_name "Anker" \
	    --panel_direction 175 \
	    --panel_slope 45 \
	    --panel_area 0.12 \
	    --efficiency 14 \
            --battery_threshold 0 \
	    --plot $PANEL_ESTIMATE_STORE_DIR

