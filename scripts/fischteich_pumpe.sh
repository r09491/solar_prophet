# Esotec 25W for my garden waterpump

mkdir -p $SOLAR_PROPHET_STORE_DIR && \
    python3 ../solar_prophet.py --panel_name "Fischteich Pumpe" \
	    --panel_direction 170 \
	    --panel_slope 45 \
	    --panel_area 0.1568 \
	    --efficiency 14 \
	    --threshold 0 $1


