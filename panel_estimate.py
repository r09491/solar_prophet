#!/usr/bin/env python3

__doc__="""
Estimates the power of a solar panel dependent on different factors
"""
__version__ = "0.0.0"
__author__ = "sepp.heid@t-online.de"


import argparse
import os, sys

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from datetime import datetime 
from pysolar import solar, radiation

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(os.path.basename(sys.argv[0]))


def get_vector(azimuth, altitude):
    azi, alt = np.radians(azimuth), np.radians(altitude) 
    dir = np.array([np.sin(azi), np.cos(azi), np.tan(alt)])
    dir = -dir if altitude > 90 and altitude <= 270 else dir
    norm = np.linalg.norm(dir)
    return dir / norm 


class Panel_Power(object):

    def __init__(self, lat, lon, name, direction, slope, area, efficiency, threshold, day):
        tzinfo = datetime.now().astimezone().tzinfo
        start = datetime(day.year, day.month, day.day, tzinfo=tzinfo)
        stamps = pd.date_range(start = start, periods = 24*60, freq = 'T', tz=tzinfo)
        minutes = [stamp.to_pydatetime() for stamp in stamps]

        alts = [solar.get_altitude(lat, lon, minute) for minute in minutes]
        azis = [solar.get_azimuth(lat, lon, minute) for minute in minutes]
        rads = [radiation.get_radiation_direct(minute, alt) for minute, alt in zip(minutes, alts)]
        vecs = [get_vector(azi, alt) for azi, alt in zip(azis, alts)]

        is_sun = np.array(alts) > 0
        sunalts = np.array(alts)[is_sun]
        sunazis = np.array(azis)[is_sun]
        sunrads = np.array(rads)[is_sun]
        sunvecs = np.array(vecs)[is_sun]
  
        powers = np.dot(sunvecs, get_vector(direction, slope))
        powers *= sunrads
        powers *= area*efficiency  
        powers[powers[:] < threshold] = 0

        data = {'altitude' : sunalts, 'azimuth':sunazis,
                'radiation' : sunrads, 'power' : powers}
        self.df = pd.DataFrame(data = data, index = stamps[is_sun])

        self.tzinfo = tzinfo
        self.name = name

        
        
    def summarize(self):
        dates = self.df.index
        azis = self.df.azimuth
        alts = self.df.altitude
        rads = self.df.radiation
        pows = self.df.power
        name = self.name

        maxindex = rads.argmax()
        maxdate = dates[maxindex]
        maxazi = azis[maxindex]
        maxalt = alts[maxindex]

        logger.info(f'Sun Rise:"{dates[0].strftime("%H:%M %Z")}", Set:"{dates[-1].strftime("%H:%M %Z")}"')
        logger.info(f' Mean:"{np.mean(rads):.0f}W/m²", Max:"{np.max(rads):.0f}W/m²", Total:"{np.sum(rads):.0f}Wh/m²"')
        logger.info(f' Azimuth/Altitude (Max): "{maxazi:.0f}/{maxalt:.0f}" @ "{maxdate.strftime("%H:%M %Z")}"')

        if len(dates[pows>0]) == 0:
            logger.info("No Harvesting in the provided configuration!")
            return 1
        
        logger.info(f'Harvest Start:"{dates[pows>0][0].strftime("%H:%M %Z")}", End:"{dates[pows>0][-1].strftime("%H:%M %Z")}"')
        logger.info(f' Mean:"{np.mean(pows):.0f}W", Max:"{np.max(pows):.0f}W", Total:"{np.sum(pows/60):.0f}Wh", "{np.sum(pows/60/12.5):.0f}Ah"')

        return 0

    
    def save_plot(self, name, lat, lon, direction, slope, area, efficiency):
        dformatter = mdates.DateFormatter('%H:%M')
        dformatter.set_tzinfo(self.tzinfo)

        fig, axes = plt.subplots(nrows=5, figsize=(9,9))

        today = self.df.index[0].strftime("%Y-%m-%d")
        pows = self.df.power
        text = f'Power Forecast {today}'
        fig.text(0.5, 0.0, text, ha='center', fontsize='x-large')

        axes[0].plot(self.df.index, self.df.azimuth)
        axes[0].grid(which='major', linestyle='-', linewidth=2, axis='both')
        axes[0].grid(which='minor', linestyle='--', linewidth=1, axis='x')
        axes[0].minorticks_on()
        axes[0].set_title(f'Sun Azimuth @ {lat:.2f}/{lon:.2f}')
        axes[0].set_ylabel('Azimuth [deg]')
        axes[0].xaxis.set_major_formatter(dformatter)

        axes[1].plot(self.df.index, self.df.altitude)
        axes[1].grid(which='major', linestyle='-', linewidth=2, axis='both')
        axes[1].grid(which='minor', linestyle='--', linewidth=1, axis='x')
        axes[1].minorticks_on()
        axes[1].set_title(f'Sun Altitude @ {lat:.2f}/{lon:.2f}')
        axes[1].set_ylabel('Altitude [deg]')
        axes[1].xaxis.set_major_formatter(dformatter)

        axes[2].plot(self.df.index, self.df.radiation, color='red')
        axes[2].grid(which='major', linestyle='-', linewidth=2, axis='both')
        axes[2].grid(which='minor', linestyle='--', linewidth=1, axis='x')
        axes[2].minorticks_on()
        axes[2].set_title(f'Sun Radiation @ {lat:.2f}/{lon:.2f}')
        axes[2].set_ylabel('Radiation [W/m²]')
        axes[2].xaxis.set_major_formatter(dformatter)

        axes[3].plot(self.df.index, self.df.power, color='brown')
        axes[3].grid(which='major', linestyle='-', linewidth=2, axis='both')
        axes[3].grid(which='minor', linestyle='--', linewidth=1, axis='x')
        axes[3].minorticks_on()
        axes[3].set_title(f'{self.name} Power Forecast # {direction:.0f}°/{slope:.0f}°  {area:.2f}m² {efficiency:.0f}%  {np.mean(pows):.0f}W|{np.max(pows):.0f}W' )
        axes[3].set_ylabel('Power [W]')
        axes[3].xaxis.set_major_formatter(dformatter)

        axes[4].plot(self.df.index, np.cumsum(self.df.power/60), color='green')
        axes[4].grid(which='major', linestyle='-', linewidth=2, axis='both')
        axes[4].grid(which='minor', linestyle='--', linewidth=1, axis='x')
        axes[4].minorticks_on()
        axes[4].set_title(f'{self.name} Harvest Forecast + {np.sum(pows)/60:.0f}Wh')
        axes[4].set_ylabel('Work [Wh]')
        axes[4].xaxis.set_major_formatter(dformatter)

        fig.tight_layout(pad=2.0)

        fig.savefig(name)
        plt.close(fig) 
        #plt.show()


    def save_csv(self, name):
        self.df.to_csv(name)
        

def parse_arguments():
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(
        prog=os.path.basename(sys.argv[0]),
        description='Estimates the power of a solar panel',
        epilog=__doc__)

    parser.add_argument('--version', action = 'version', version = __version__)

    parser.add_argument('--lat', type = float, default = 49.04885,
                        help = "Latitude of the panel position")

    parser.add_argument('--lon', type = float, default = 11.78333,
                        help = "Longitude of the panel position")
    
    parser.add_argument('--panel_name', default = 'Offgridtech 195W-FSP-2',
                        help = "Name of the panel")

    parser.add_argument('--panel_direction', type = float, default = 180.0,
                        help = "Direction of the panel normale relative to north [0 - 360]")
    
    parser.add_argument('--panel_slope', type = float, default = 45.0,
                        help = "Slope of the panel normale relative to surface [0 - 360]")

    parser.add_argument('--panel_area', type = float, default = 0.39*0.78*3,
                        help = "Size of the panel area [m²]")

    parser.add_argument('--efficiency', type = float, default = 18.5,
                        help = "Efficiency of the panel [%%]. Can be used for other degradations!")


    parser.add_argument('--threshold', type = float, default = 20.0,
                        help = "Threshold when battery accepts input power [W]")

    parser.add_argument('--plot', default = None,
                        help = "Directory for saving of the plots if needeed")

    parser.add_argument('--csv', default = None,
                        help = "Directory for saving of the CSV file if needed")


    parser.add_argument('forecast_day',
                        type=lambda d: datetime.strptime(d, '%Y-%m-%d').date(),
                        default = datetime.now().strftime('%Y-%m-%d'), nargs = '?',
                        help = 'Day for forecast')
        
    return parser.parse_args()


def main():
    print(sys.argv[-1])

    args = parse_arguments()
        
    if args.lat < -90 or args.lat > 90:
        logger.error('The latitude of the panel position is out of range  "{}".'.format(args.lat))
        return 1

    if args.lon < -180 or args.lat > 180:
        logger.error('The longitude of the panel position is out of range  "{}".'.format(args.lon))
        return 2

    if args.panel_direction < 0 or args.panel_direction > 360:
        logger.error('The direction of the panel is out of range  "{}".'.format(args.panel_direction))
        return 3

    if args.panel_slope < 0 or args.panel_slope > 360:
        logger.error('The slope of the panel is out of range  "{}".'.format(args.panel_slope))
        return 4

    if not args.plot is None and not os.path.isdir(args.plot):
        logger.error('The directory to save the plots does not exist "{}".'.format(args.plot))
        return 5

    if not args.csv is None and not os.path.isdir(args.csv):
        logger.error('The directory to save the CSV does not exist "{}".'.format(args.csv))
        return 6

    logger.info(f'Estimating the harvest of "{args.panel_name}" on "{args.forecast_day}"' )
    logger.info(f' Lat/Lon:"{args.lat:.2f}/{args.lon:.2f}", Dir/Slope:"{args.panel_direction:.0f}/{args.panel_slope:.0f}"')
    logger.info(f' Area: "{args.panel_area:.2f}m²", Efficiency: "{args.efficiency:.0f}%", Threshold: "{args.threshold:.0f}W"' )

    pp = Panel_Power(args.lat, \
                     args.lon, \
                     args.panel_name, \
                     args.panel_direction, \
                     args.panel_slope, \
                     args.panel_area,
                     args.efficiency / 100, \
                     args.threshold,
                     args.forecast_day)

    errcode = pp.summarize()
    if errcode > 0:
        logger.error(f'The cobination of provided parameters does not qualify for harvesting')
        return 7

    if not args.plot is None:
        save_name = args.panel_name.replace(' ', '_') + args.forecast_day.strftime("_%Y-%m-%d") + '.png'
        pp.save_plot(os.path.join(args.plot, save_name), \
                     args.lat, args.lon, args.panel_direction, \
                     args.panel_slope, args.panel_area, args.efficiency)
        logger.info(f'Plot saved to  "{os.path.join(args.plot, save_name)}"' )

    if not args.csv is None:            
        save_name = args.panel_name.replace(' ', '_') + args.forecast_day.strftime("_%Y-%m-%d") + '.csv'
        pp.save_csv(os.path.join(args.csv, save_name))
        logger.info(f'CSV saved to  "{os.path.join(args.csv, save_name)}"' )
        
    return 0

if __name__ == '__main__':
    try:
        err = main()
    except KeyboardInterrupt:
        err = 99

    sys.exit(err)
