# Balkonkraftwerke dürfen 4m² per Gesetz nicht überschreiten

# Typischerwise hängen sie parallel zom Balkongeländer --> slope 0

# Der Testsieger Solakon SK-011113 hat:
#  - eine Fläche von 2*1.134*1.722 = 3.905 m²
#  - einen theoretischen Wirkungsgrad vin 21.8%
#  - eine berechnete Peak Power von 821Wp. Aber mit 880W beworben!
#
# Wirkungsgrade
#  Diesiger Wintertag: 2
#  Bewölkter Wintertag: 4?
#  Blauer Wintertag: 8?
#  Bewölkter Sommertag: 14?
#  Blauer Sommertag: 18?
#

mkdir -p $PANEL_ESTIMATE_STORE_DIR/plot && mkdir -p $PANEL_ESTIMATE_STORE_DIR/csv &&\
    python3 ../panel_estimate.py --panel_name "Balkon KW Solakon SK-011113" \
	    --panel_direction 170 \
	    --panel_slope 0 \
	    --panel_area 3.905 \
	    --efficiency 12 \
	    --threshold 0 \
	    --plot $PANEL_ESTIMATE_STORE_DIR/plot \
	    --csv $PANEL_ESTIMATE_STORE_DIR/csv $1
