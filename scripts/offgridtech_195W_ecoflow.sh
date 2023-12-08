# Offgridtech 195W to charge power stations
#
# My Ecoflow Delta Max is special since it does not switch on immediately
# with the first input of sun power below a 20 W threshold. This makes
# sense since the device consumes at least 20W during its idle operation.
# So acting below this threshold the battery would discharge. At least
# 40W are required that charging operations makes sense.
#
# Note: The dealer's efficiency of 18% is to my experience exaggerated.
#
mkdir -p $PANEL_ESTIMATE_STORE_DIR/plot && mkdir -p $PANEL_ESTIMATE_STORE_DIR/csv &&\
    python3 ../panel_estimate.py --panel_name "Offgridtech 195W" \
	    --panel_direction 170 \
	    --panel_slope 45 \
	    --efficiency 5 \
	    --threshold 20 \
	    --plot $PANEL_ESTIMATE_STORE_DIR/plot \
	    --csv $PANEL_ESTIMATE_STORE_DIR/csv $1
