mkdir -p $PANEL_ESTIMATE_STORE_DIR && \
    python3 panel_estimate.py \
	    --panel_name "Ducato" \
	    --panel_slope 0 \
	    --panel_area 0.6 \
	    --efficiency 16 \
            --battery_threshold 0 \
	    --plot $PANEL_ESTIMATE_STORE_DIR
