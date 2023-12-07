# Offgridtech 195W with Victron Smartsolar MPPT 75/15

# To asses the the Ecoflow 20 threshold

mkdir -p $PANEL_ESTIMATE_STORE_DIR/plot && mkdir -p $PANEL_ESTIMATE_STORE_DIR/csv &&\
    python3 ../panel_estimate.py --panel_name "Offgridtech 195W" \
	    --panel_direction 170 \
	    --panel_slope 25 \
	    --efficiency 1 \
	    --threshold 0 \
	    --plot $PANEL_ESTIMATE_STORE_DIR/plot \
	    --csv $PANEL_ESTIMATE_STORE_DIR/csv
