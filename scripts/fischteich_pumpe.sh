# Esotec 25W for my garden waterpump

mkdir -p $PANEL_ESTIMATE_STORE_DIR && \
    python3 ../panel_estimate.py --panel_name "Fischteich Pumpe" \
	    --panel_direction 170 \
	    --panel_slope 45 \
	    --panel_area 0.1568 \
	    --efficiency 14 \
	    --battery_threshold 0 \
	    --plot $PANEL_ESTIMATE_STORE_DIR

