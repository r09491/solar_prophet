# My neighbours solar park on the roof of his house
#
# Efficiency 1% on a foggy winter day
# Efficiency 12% on a nice summer day
#

mkdir -p $PANEL_ESTIMATE_STORE_DIR && \
    python3 ../panel_estimate.py \
	    --panel_name "Solardach" \
	    --panel_direction 170 \
	    --panel_area 480 \
	    --efficiency 1 \
            --battery_threshold 0 \
	    --plot $PANEL_ESTIMATE_STORE_DIR

