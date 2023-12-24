# Offgridtech 195W with Victron Smartsolar MPPT 75/15 charging 50% of 12Ah battery on foggy day

mkdir -p $PANEL_ESTIMATE_STORE_DIR/plot && mkdir -p $PANEL_ESTIMATE_STORE_DIR/csv &&\
    python3 ../panel_estimate.py --panel_name "Offgridtech 195W" \
	    --panel_direction 170 \
	    --panel_slope 30 \
	    --panel_efficiency 2 \
	    --threshold 0 \
	    --battery_full 75 \
	    --plot $PANEL_ESTIMATE_STORE_DIR/plot \
	    --csv $PANEL_ESTIMATE_STORE_DIR/csv $1
