# Für Module mit einer Fläche größer als 2m² ist eine Genehmigung
# erforderlich. Balkonkraftwerke haben daher in der Regel zwei Module,
# deren gemeinsame Fläche knapp unter 4m² liegt

# Typischerwise hängen sie zum Balkongeländer parallel --> slope 0
#                                   oder fast parallel --> slope 30 
#

# Der Testsieger Solakon SK-011113 hat:
#  - eine Fläche von 2*1.134*1.722 = 3.905 m²
#  - einen theoretischen Wirkungsgrad vin 21.8%
#  - eine berechnete Peak Power von 821Wp. Aber mit 880W beworben!
#

# To achieve a the 890 kWH harvest (anker) of one year an efficiency
# of 12 @ slope 45 is required
#

# Efficiency considering weather (Deutscher Wetterdienst)
# Jan:15, Feb:25, Mar:60, Apr:65, May:78, Jun:79, 
# Jul:80, Aug:74,Sep:49, Oct:36, Nov:15, Dez:15
#

mkdir -p $PANEL_ESTIMATE_STORE_DIR/plot && mkdir -p $PANEL_ESTIMATE_STORE_DIR/csv &&\
    python3 ../panel_estimate.py --panel_name "Balkon KW Solakon SK-011113" \
	    --panel_direction 170 \
	    --panel_slope 30 \
	    --panel_area 3.905 \
	    --panel_efficiency 22 \
	    --threshold 0 \
	    --plot $PANEL_ESTIMATE_STORE_DIR/plot \
	    --csv $PANEL_ESTIMATE_STORE_DIR/csv $1
