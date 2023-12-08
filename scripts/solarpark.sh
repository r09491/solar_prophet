# My neighbours solar park on the roof of his house
#
# Wirkungsgrade
#  Diesiger Wintertag: 2
#  Bewölkter Wintertag: 4 ? TBD
#  Blauer Wintertag: 8 ? TBD
#  Bewölkter Sommertag: 14 ? TBD
#  Blauer Sommertag: 18 ? TBD
#

mkdir -p $PANEL_ESTIMATE_STORE_DIR && \
    python3 ../panel_estimate.py \
	    --panel_name "Solarpark" \
	    --panel_direction 180 \
	    --panel_slope 45 \
	    --panel_area 480 \
	    --efficiency 2 \
            --threshold 0 \
	    --plot $PANEL_ESTIMATE_STORE_DIR
