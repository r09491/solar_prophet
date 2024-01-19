Estimate the power of solar panels for a given day dependent on various factors

'solar_prophet.py' is the only script provided. It is dependent on 'pysolar', 'pandas' and 'matplotlib' to be installed somehow.

```
~/solar_prophet/scripts $ solar_prophet.py -h
usage: solar_prophet.py [-h] [--version] [--lat LAT] [--lon LON] [--panel_name PANEL_NAME] [--panel_direction PANEL_DIRECTION]
                        [--panel_slope PANEL_SLOPE] [--panel_area PANEL_AREA] [--panel_efficiency PANEL_EFFICIENCY]
                        [--system_barrier SYSTEM_BARRIER] [--inverter_limit INVERTER_LIMIT] [--battery_split BATTERY_SPLIT]
                        [--battery_full BATTERY_FULL] [--battery_first] [--csv CSV] [--plot PLOT]
                        [forecast_day]

Estimates the power and energy of a solar panel

positional arguments:
  forecast_day          Day for forecast

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --lat LAT             The latitude of the panel position [0 - 360]
  --lon LON             The longitude of the panel position [0 - 360]
  --panel_name PANEL_NAME
                        The name of the panel
  --panel_direction PANEL_DIRECTION
                        The direction of the panel normale relative to north [0 - 360]
  --panel_slope PANEL_SLOPE
                        The slope of the panel normale relative to surface [0 - 360]
  --panel_area PANEL_AREA
                        The size of the panel area [m²]
  --panel_efficiency PANEL_EFFICIENCY
                        The efficiency of the panel [%]. Blue Sky ~ 180. Mist ~ 20
  --system_barrier SYSTEM_BARRIER
                        The threshold above which the system (solarbank, inverter, powerstation) is working [W]
  --inverter_limit INVERTER_LIMIT
                        The maximum power limit of the inverter [W]
  --battery_split BATTERY_SPLIT
                        The threshold when to charge the battery in systems with storage [W]
  --battery_full BATTERY_FULL
                        The energy when a battery is considered full in systems with storage [Wh]
  --battery_first       Serve the battery first! Serve the house second!
  --csv CSV             The directory for saving of the CSV file if needed
  --plot PLOT           The directory for saving of the PNG file if needed

Estimates the power of a solar panel dependent on different factors like location and pannel attitude
~/solar_prophet $

```

Under scripts there are a few examples. To run define the SOLAR_PROPHET_STORE_DIR first.

The following is for standard weather conditions. To be specified with an efficiency of 100%!

```
~/solar_prophet/scripts $ . balkonkraftwerk_solix.sh
INFO:solar_prophet.py:Estimating the harvest of "Balkon KW Solakon SK-011113" on "2024-01-19"
INFO:solar_prophet.py: Area: "3.90m²", Lat/Lon:"49.05/11.78", Dir/Slope:"180/37"
INFO:solar_prophet.py: Efficiency: "100%", Start Barrier: "30W", Inverter Limit: "600W"
INFO:solar_prophet.py:Best Radiation Attitude # "180/21" @ "12:24 CET"
INFO:solar_prophet.py:Sun # Rise:"08:01 CET", Set:"16:46 CET", "8.8h"
INFO:solar_prophet.py:Sun # Mean:"593W/m²", Max:"828W/m²", Total:"5202Wh/m²"
INFO:solar_prophet.py:Meteo # Mean:"77W/m²", Max:"108W/m²", Total:"677Wh/m²"
INFO:solar_prophet.py:Harvest # Rise: "08:29 CET", Set:"16:18 CET", "7.8h"
INFO:solar_prophet.py:Harvest # Mean:"253W", Max:"404W", Total:"2215Wh", "177Ah"
INFO:solar_prophet.py:PLOT saved to  "/data/data/com.termux/files/home/storage/solar_prophet/plot/Balkon_KW_Solakon_SK-011113_240119.png"
~/solar_prophet/scripts $ feh  "/data/data/com.termux/files/home/storage/solar_prophet/plot/Balkon_KW_Solakon_SK-011113_240119.png"
```

![alt text](images/Balkon_KW_Solakon_SK-011113_240119_bright.png)

However we have very bad weather. Almost foggy! To be specified with an efficiency of 10%

```
~/solar_prophet/scripts $ . balkonkraftwerk_solix.sh
INFO:solar_prophet.py:Estimating the harvest of "Balkon KW Solakon SK-011113" on "2024-01-19"
INFO:solar_prophet.py: Area: "3.90m²", Lat/Lon:"49.05/11.78", Dir/Slope:"180/37"
INFO:solar_prophet.py: Efficiency: "10%", Start Barrier: "30W", Inverter Limit: "600W"
INFO:solar_prophet.py:Best Radiation Attitude # "180/21" @ "12:24 CET"
INFO:solar_prophet.py:Sun # Rise:"08:01 CET", Set:"16:46 CET", "8.8h"
INFO:solar_prophet.py:Sun # Mean:"593W/m²", Max:"828W/m²", Total:"5202Wh/m²"
INFO:solar_prophet.py:Meteo # Mean:"77W/m²", Max:"108W/m²", Total:"677Wh/m²"
INFO:solar_prophet.py:Harvest # Rise: "10:17 CET", Set:"14:30 CET", "4.2h"
INFO:solar_prophet.py:Harvest # Mean:"18W", Max:"40W", Total:"156Wh", "13Ah"
INFO:solar_prophet.py:PLOT saved to  "/data/data/com.termux/files/home/storage/solar_prophet/plot/Balkon_KW_Solakon_SK-011113_240119.png"
~/solar_prophet/scripts $ feh  "/data/data/com.termux/files/home/storage/solar_prophet/plot/Balkon_KW_Solakon_SK-011113_240119.png"
```

![alt text](images/Balkon_KW_Solakon_SK-011113_240119_dark.png)

