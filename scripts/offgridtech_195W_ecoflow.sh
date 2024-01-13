# Offgridtech 195W to charge power stations
#
# My Ecoflow Delta Max is special since it does not switch on immediately
# with the first input of sun power below a 20 W threshold. This makes
# sense since the device consumes at least 20W during its idle operation.
# So acting below this threshold the battery would discharge. At least
# 40W are required that charging operations makes sense.
#
# The split power 200W cannot be achieved with the Offgridtech 195W. The
# Ecoflow does not allow.
#
# Note: The dealer's efficiency of 18% is to my experience exaggerated.
#
mkdir -p $SOLAR_PROPHET_STORE_DIR/plot && mkdir -p $SOLAR_PROPHET_STORE_DIR/csv &&\
    python3 ../solar_prophet.py --panel_name "Offgridtech 195W" \
	    --panel_direction 170 \
	    --panel_slope 30 \
	    --panel_efficiency 50 \
	    --start_barrier 20 \
	    --battery_split 200 \
	    --battery_full 2060 \
	    --battery_first \
	    --plot \
	    --csv $SOLAR_PROPHET_STORE_DIR/csv $1
