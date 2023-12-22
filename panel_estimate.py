#!/usr/bin/env python3

__doc__="""
Estimates the power of a solar panel dependent on different factors.
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

    def __init__(self, lat, lon, name, direction, slope, area, efficiency, threshold, battery_split, battery_full, day):
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
  
        pows = np.dot(sunvecs, get_vector(direction, slope))
        pows *= sunrads*area*efficiency
        pows[pows[:] < threshold] = 0

        data = {'altitude' : sunalts, 'azimuth':sunazis,
                'radiation' : sunrads, 'power' : pows}
        self.df = pd.DataFrame(data = data, index = stamps[is_sun])

        self.battery_split = battery_split
        self.battery_full = battery_full
        
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

        if len(dates[pows>0]) == 0:
            logger.info("No Harvesting in the provided configuration!")
            return 1

        text = f'Best Radiation Attitude #'
        text += f' "{maxazi:.0f}/{maxalt:.0f}"'
        text += f' @ "{maxdate.strftime("%H:%M %Z")}"'
        logger.info(text)

        text = f'Sun # Rise:"{dates[0].strftime("%H:%M %Z")}",'
        text += f' Set:"{dates[-1].strftime("%H:%M %Z")}"'
        logger.info(text)

        text = f' Mean:"{np.mean(rads):.0f}W/m²",'
        text += f' Max:"{np.max(rads):.0f}W/m²",'
        text += f' Total:"{np.sum(rads):.0f}Wh/m²"'
        logger.info(text)

        text = f'Harvest # Rise: "{dates[pows>0][0].strftime("%H:%M %Z")}",'
        text += f' Set:"{dates[pows>0][-1].strftime("%H:%M %Z")}"'
        logger.info(text)
        
        text = f' Mean:"{np.mean(pows):.0f}W",'
        text += f' Max:"{np.max(pows):.0f}W",'
        text += f' Total:"{np.sum(pows/60):.0f}Wh",'
        text += f' "{np.sum(pows/60/12.5):.0f}Ah"'
        logger.info(text)
        
        return 0

    
    def save_plot(self, name, lat, lon, direction, slope, area, efficiency):
        dformatter = mdates.DateFormatter('%H:%M')
        dformatter.set_tzinfo(self.tzinfo)

        dates = self.df.index
        azis = self.df.azimuth
        alts = self.df.altitude
        rads = self.df.radiation
        pows = self.df.power

        today = dates[0].strftime("%Y-%m-%d")
        text = f'{self.name} Forecast {today}'
        fig, axes = plt.subplots(nrows=5, figsize=(9,12))
        fig.text(0.5, 0.0, text, ha='center', fontsize='x-large')

        axes[0].plot(dates, azis, color='red')
        axes[0].grid(which='major', linestyle='-', linewidth=2, axis='both')
        axes[0].grid(which='minor', linestyle='--', linewidth=1, axis='x')
        axes[0].minorticks_on()
        axes[0].set_title(f'Sun Azimuth @ {lat:.2f}/{lon:.2f}')
        axes[0].set_ylabel('Azimuth [deg]')
        axes[0].xaxis.set_major_formatter(dformatter)

        axes[1].plot(dates, alts, color='red')
        axes[1].grid(which='major', linestyle='-', linewidth=2, axis='both')
        axes[1].grid(which='minor', linestyle='--', linewidth=1, axis='x')
        axes[1].minorticks_on()
        axes[1].set_title(f'Sun Altitude @ {lat:.2f}/{lon:.2f}')
        axes[1].set_ylabel('Altitude [deg]')
        axes[1].xaxis.set_major_formatter(dformatter)

        
        axes[2].plot(dates, rads, color='red')
        axes[2].grid(which='major', linestyle='-', linewidth=2, axis='both')
        axes[2].grid(which='minor', linestyle='--', linewidth=1, axis='x')
        axes[2].minorticks_on()

        title = f'Sun Radiation @ {lat:.2f}/{lon:.2f}, '
        title +=  f' {np.mean(rads):.0f}W/m²^{np.max(rads):.0f}W/m²'
        axes[2].set_title(title)

        axes[2].set_ylabel('Radiation [W/m²]')
        axes[2].xaxis.set_major_formatter(dformatter)


        batpows = pows
        batischarge = batpows > self.battery_split
                
        axes[3].fill_between(dates, pows,
                             color='magenta', label='BAT', alpha=0.4)

        axes[3].grid(which='major', linestyle='-', linewidth=2, axis='both')
        axes[3].grid(which='minor', linestyle='--', linewidth=1, axis='x')
        axes[3].minorticks_on()

        title = f'Power Forecast #'
        title +=  f' {direction:.0f}°/{slope:.0f}°'
        title +=  f' {area:.2f}m² {efficiency:.0f}%'
        title +=  f' {np.mean(pows):.0f}W^{np.max(pows):.0f}W'
        axes[3].set_title(title )

        axes[3].set_ylabel('Power [W]')
        axes[3].xaxis.set_major_formatter(dformatter)
        
        batsums = np.cumsum(batpows/60)
        axes[4].fill_between(dates, batsums, color='black', label='Lost', alpha=0.6)
        
        if self.battery_full is not None:
            batisfull = batsums >= self.battery_full
            batsums[batisfull] =  self.battery_full
            axes[4].fill_between(dates, batsums, color='magenta', label='BAT', alpha=0.8)

            axes[4].axhline(self.battery_full, color='black', linewidth=2, label='FULL')

            batlost = batischarge & batisfull
            if batlost.any():
                axes[3].fill_between(dates[batlost], batpows[batlost],
                                     color='black', label='LOST', alpha=0.6)

        if self.battery_split is not None:
            powissplit = pows >= self.battery_split
            pows[powissplit] =  self.battery_split
            axes[3].fill_between(dates, pows, color='cyan', label='House', alpha=0.8)

            axes[3].axhline(self.battery_split, color='black', linewidth=2, label='SPLIT')

            powsums = np.cumsum(pows/60)
            axes[4].fill_between(dates, powsums, color='cyan', label='House')

        axes[3].legend(loc="upper left")
            
        axes[4].legend(loc="upper left")
        axes[4].grid(which='major', linestyle='-', linewidth=2, axis='both')
        axes[4].grid(which='minor', linestyle='--', linewidth=1, axis='x')
        axes[4].minorticks_on()
        title = f'Harvest Forecast'
        title += f' + {np.sum(pows)/60:.0f}Wh'
        axes[4].set_title(title)
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

    parser.add_argument('--panel_efficiency', type = float, default = 18.5,
                        help = "Nominal efficiency of the panel [%%]. There is a best value relative to 1000 [W/m²] in the data sheets. This can propably not ne achieved. Can be reduced for degradations like scattered sky etc")

    parser.add_argument('--threshold', type = float, default = 20.0,
                        help = "Threshold when system accepts input power [W]")

    parser.add_argument('--battery_split', type = float, default = None,
                        help = "Threshold when to charge battery in systems with storage [W]")

    parser.add_argument('--battery_full', type = float, default = None,
                        help = "Energy when a battery is considered full in systems with storage [Wh]")
    
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

    if args.panel_efficiency < 0 or args.panel_efficiency > 100:
        logger.error('The efficiency of the panel is out of range  "{}".'.format(args.panel_efficiency))
        return 5

    if args.battery_split is not None and args.battery_split < 0:
        logger.error('The split power is out of range  "{}".'.format(args.battery_split))
        return 6

    if args.battery_full is not None and args.battery_full < 0:
        logger.error('The full energy is out of range  "{}".'.format(args.battery_split))
        return 6
    
    if not args.plot is None and not os.path.isdir(args.plot):
        logger.error('The directory to save the plots does not exist "{}".'.format(args.plot))
        return 7

    if not args.csv is None and not os.path.isdir(args.csv):
        logger.error('The directory to save the CSV does not exist "{}".'.format(args.csv))
        return 8

    logger.info(f'Estimating the harvest of "{args.panel_name}" on "{args.forecast_day}"' )
    logger.info(f' Lat/Lon:"{args.lat:.2f}/{args.lon:.2f}", Dir/Slope:"{args.panel_direction:.0f}/{args.panel_slope:.0f}"')
    logger.info(f' Area: "{args.panel_area:.2f}m²", Efficiency: "{args.panel_efficiency:.0f}%", Threshold: "{args.threshold:.0f}W"' )

    pp = Panel_Power(args.lat, 
                     args.lon, 
                     args.panel_name, 
                     args.panel_direction, 
                     args.panel_slope, 
                     args.panel_area,
                     args.panel_efficiency / 100, 
                     args.threshold,
                     args.battery_split,
                     args.battery_full,
                     args.forecast_day)

    errcode = pp.summarize()
    if errcode > 0:
        logger.error(f'The cobination of provided parameters does not qualify for harvesting')
        return 7

    if not args.plot is None:
        save_name = args.panel_name.replace(' ', '_') + args.forecast_day.strftime("_%Y-%m-%d") + '.png'
        pp.save_plot(os.path.join(args.plot, save_name), \
                     args.lat, args.lon, args.panel_direction, \
                     args.panel_slope, args.panel_area, args.panel_efficiency)
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
