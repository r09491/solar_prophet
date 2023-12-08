# Offgridtech 195W with Victron Smartsolar MPPT 75/15

# To asses the the Ecoflow 20 threshold

# Wirkungsgrade
#  Diesiger Wintertag: 2
#  Bewölkter Wintertag: 4 ? TBD
#  Blauer Wintertag: 8 ? TBD
#  Bewölkter Sommertag: 14 ? TBD
#  Blauer Sommertag: 18 ? TBD
#

mkdir -p $PANEL_ESTIMATE_STORE_DIR/plot && mkdir -p $PANEL_ESTIMATE_STORE_DIR/csv &&\
    python3 ../panel_estimate.py --panel_name "Offgridtech 195W" \
	    --panel_direction 170 \
	    --panel_slope 25 \
	    --efficiency 2 \
	    --threshold 0 \
	    --plot $PANEL_ESTIMATE_STORE_DIR/plot \
	    --csv $PANEL_ESTIMATE_STORE_DIR/csv
