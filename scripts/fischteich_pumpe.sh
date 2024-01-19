# Esotec 25W for my garden waterpump

mkdir -p $SOLAR_PROPHET_STORE_DIR && \
    python3 ../solar_prophet.py --panel_name "Fischteich Pumpe" \
	    --panel_direction 170 \
	    --panel_slope 45 \
	    --panel_area 0.1568 \
	    --panel_efficiency 100 \
	    --system_barrier 0 \
	    --plot $1


