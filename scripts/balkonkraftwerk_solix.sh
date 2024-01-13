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

mkdir -p $SOLAR_PROPHET_STORE_DIR/plot && mkdir -p $SOLAR_PROPHET_STORE_DIR/csv &&\
    python3 ../solar_prophet.py --panel_name "Balkon KW Solakon SK-011113" \
	    --panel_direction 180 \
	    --panel_slope 37 \
	    --panel_area 3.905 \
	    --panel_efficiency 100 \
	    --threshold 10 \
	    --battery_split 50 \
	    --battery_full 1600 \
	    --battery_swap 0 \
	    --plot $1
