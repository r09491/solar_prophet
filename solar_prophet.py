#!/usr/bin/env python3

__doc__="""
Estimates the power of a solar panel dependent on different factors
like location and pannel attitude
"""
__version__ = "0.0.3"
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

import warnings
warnings.simplefilter("ignore")

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

    def __init__(self, lat, lon, name, direction, slope, area, efficiency, bifacial, albedo,system_barrier,
                 inverter_limit, battery_split, battery_full, battery_first, day):
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

        # Consider panel features 
        best_w = sunrads*area*(efficiency+albedo)
        best_w -= albedo*best_w
        
        # Cosine between actual vector to sun and norm vector of panel
        suncos = np.dot(sunvecs, get_vector(direction, slope))

        # Consider attitude of panel and direct radiation from the front
        direct_w = best_w*suncos
        direct_w[suncos<0] = 0

        tot_w = direct_w
        
        # Consider attitude of panel and bifacial radiation from the rear
        bifacial_w = best_w*suncos
        bifacial_w[suncos>=0] = 0
        bifacial_w *= -bifacial
        
        tot_w += bifacial_w

        # Consider the albedo effect
        tot_w += albedo*tot_w

        # Consider start barrier        
        tot_w[:np.where(tot_w >= system_barrier)[0][0]] = 0

        if battery_first:
            """ The power is delivered to the battery first """
            bat_w = tot_w.copy()
            if battery_split is not None:
                bat_w[bat_w > battery_split] = battery_split
            bat_wh = bat_w.cumsum()/60
            if battery_full is not None:
                bat_wh[bat_wh >= battery_full] = battery_full
                bat_w[bat_wh >= battery_full] = 0

            """ The rest is for the house """
            
            house_w = tot_w.copy() - bat_w
            if inverter_limit is not None:
                house_w[house_w > inverter_limit] = inverter_limit
            house_wh = house_w.cumsum()/60
            if battery_split is not None:
                bat_w[bat_w > battery_split] = battery_split

        else:
            """ The power is delivered to the house first """

            house_w = tot_w.copy()
            if battery_split is not None:
                house_w[house_w > battery_split] = battery_split
            if inverter_limit is not None:
                house_w[house_w > inverter_limit] = inverter_limit
            house_wh = house_w.cumsum()/60

            """ The rest is for the battery """

            bat_w = np.full_like(tot_w, 0.0) \
                if battery_split is None \
                else tot_w.copy() - house_w
            bat_wh = bat_w.cumsum()/60
            if battery_full is not None:
                bat_wh[bat_wh >= battery_full] = battery_full
                bat_w[bat_wh >= battery_full] = 0

        lost_w = tot_w.copy() - house_w - bat_w
        lost_wh = lost_w.cumsum()/60

        data = {'azimuth':sunazis, 'altitude':sunalts,'sunrads':sunrads,
                'best_w':best_w, 'tot_w':tot_w, 'house_w':house_w, 'bat_w':bat_w,
                'lost_w':lost_w, 'house_wh':house_wh, 'bat_wh':bat_wh,'lost_wh':lost_wh}
        self.df = pd.DataFrame(data = data, index = stamps[is_sun])

        self.efficiency = efficiency
        self.inverter_limit = inverter_limit

        self.battery_split = battery_split 
        self.battery_full = battery_full
        self.battery_first = battery_first
        

        self.tzinfo = tzinfo
        self.name = name

        
    def summarize(self):
        dates = self.df.index
        azis = self.df.azimuth
        alts = self.df.altitude
        rads = self.df.sunrads
        best_w = self.df.best_w
        tot_w = self.df.tot_w
        name = self.name

        maxradsdate = rads.argmax()
        maxradsazi = azis[maxradsdate]
        maxradsalt = alts[maxradsdate]

        if type(maxradsdate) == np.int64:
            # python >= 3.11
            maxradsdate = dates[maxradsdate]
              
        if len(dates[tot_w>0]) == 0:
            logger.info("No Harvesting in the provided configuration!")
            return 1

        text = f'Best Radiation Attitude #'
        text += f' "{maxradsazi:.0f}/{maxradsalt:.0f}"'
        text += f' @ "{maxradsdate.strftime("%H:%M %Z")}"'
        logger.info(text)

        text = f'Sun # Rise:"{dates[0].strftime("%H:%M %Z")}",'
        text += f' Set:"{dates[-1].strftime("%H:%M %Z")}",'
        text += f' "{(dates[-1] - dates[0]).total_seconds()/3600:.1f}h"'
        logger.info(text)
        text = f'Sun # Mean:"{np.mean(rads):.0f}W/m²",'
        text += f' Max:"{np.max(rads):.0f}W/m²",'
        text += f' Total:"{np.sum(rads/60):.0f}Wh/m²"'
        logger.info(text)

        text = f'Harvest # Rise: "{dates[tot_w>0][0].strftime("%H:%M %Z")}",'
        text += f' Set:"{dates[tot_w>0][-1].strftime("%H:%M %Z")}",'
        text += f' "{(dates[tot_w>0][-1] - dates[tot_w>0][0]).total_seconds()/3600:.1f}h"'
        logger.info(text)
        text = f'Harvest # Mean:"{np.mean(tot_w):.0f}W",'
        text += f' Max:"{np.max(tot_w):.0f}W",'
        text += f' Total:"{np.sum(tot_w/60):.0f}Wh",'
        text += f' "{np.sum(tot_w/60/12.5):.0f}Ah"'
        logger.info(text)
        
        return 0

    
    def save_plot(self, lat, lon, direction, slope, area, full_save_name):
        dformatter = mdates.DateFormatter('%H:%M')
        dformatter.set_tzinfo(self.tzinfo)

        dates = self.df.index
        azis = self.df.azimuth
        alts = self.df.altitude
        rads = self.df.sunrads
        best_w = self.df.best_w
        tot_w = self.df.tot_w
        house_w = self.df.house_w
        bat_w = self.df.bat_w
        lost_w = self.df.lost_w
        house_wh = self.df.house_wh
        bat_wh = self.df.bat_wh
        lost_wh = self.df.lost_wh

        best_mean = best_w.mean()
        best_max = best_w.max()
        best_sum = best_w.sum()/60
        best_wh = best_w.cumsum()/60

        tot_mean = tot_w.mean()
        tot_max = tot_w.max()
        tot_sum = tot_w.sum()/60
        tot_wh = tot_w.cumsum()/60

        pefficiency = self.efficiency
        ilimit = self.inverter_limit
        bsplit = self.battery_split
        bfull =  self.battery_full
        bfirst =  self.battery_first

        """ Prepare plots """

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

        
        axes[2].plot(dates, rads, color='red', label='SUN')
        axes[2].legend(loc="upper left")    
        axes[2].grid(which='major', linestyle='-', linewidth=2, axis='both')
        axes[2].grid(which='minor', linestyle='--', linewidth=1, axis='x')
        axes[2].minorticks_on()

        title = f'Direct Radiation '
        title +=  f' {np.mean(rads):.0f}W/m²^{np.max(rads):.0f}W/m² |'
        axes[2].set_title(title)

        axes[2].set_ylabel('Radiation [W/m²]')
        axes[2].xaxis.set_major_formatter(dformatter)
        

        axes[3].fill_between(dates, house_w + bat_w + lost_w,
                             color='black', label='LOST', alpha = 0.5)        
        axes[3].fill_between(dates, house_w + bat_w,
                             color='magenta', label='BAT', alpha = 0.7)        
        axes[3].fill_between(dates, house_w,
                             color='cyan', label='HOUSE', alpha = 0.9)        

        if bsplit is not None:
            axes[3].axhline(bsplit, color='cyan', linewidth=2, label='SPLIT')

        if ilimit is not None and ilimit < best_max:
            axes[3].axhline(ilimit, color='black', linestyle='--', label='INVERTER')

        axes[3].plot(dates, best_w, color='black', linestyle='--', label = "BEST")
    
        axes[3].legend(loc="upper left")    
        axes[3].grid(which='major', linestyle='-', linewidth=2, axis='both')
        axes[3].grid(which='minor', linestyle='--', linewidth=1, axis='x')
        axes[3].minorticks_on()

        title = f'Power Forecast #'
        title +=  f' {direction:.0f}°/{slope:.0f}°'
        title +=  f' | {area:.2f}m² | {100*pefficiency:.0f}%'
        title +=  f' > {tot_mean:.0f}W^{tot_max:.0f}W'
        axes[3].set_title(title )
        axes[3].set_ylabel('Power [W]')
        axes[3].xaxis.set_major_formatter(dformatter)

        
        axes[4].fill_between(dates, house_wh + bat_wh + lost_wh,
                             color='black', label='LOST', alpha = 0.5)        
        axes[4].fill_between(dates, house_wh + bat_wh,
                             color='magenta', label='BAT', alpha = 0.7)        
        axes[4].fill_between(dates, house_wh,
                             color='cyan', label='HOUSE', alpha = 0.9)        

        if bfull is not None and 0 < bat_wh[-1] < bfull:
            axes[4].axhline(bfull+house_wh[-1], color='magenta', linewidth=2, label='FULL')

        axes[4].plot(dates, best_wh, color='black', linestyle='--', label = "BEST")

        axes[4].legend(loc="upper left")
        axes[4].grid(which='major', linestyle='-', linewidth=2, axis='both')
        axes[4].grid(which='minor', linestyle='--', linewidth=1, axis='x')
        axes[4].minorticks_on()
        title = f'Harvest Forecast #'
        title += f' {house_wh[-1]:.0f}'
        title += f' + {bat_wh[-1]:.0f}'
        title += f' + {lost_wh[-1]:.0f}'
        title += f' = {tot_sum:.0f}Wh'
        axes[4].set_title(title)
        axes[4].set_ylabel('Work [Wh]')
        axes[4].xaxis.set_major_formatter(dformatter)


        fig.tight_layout(pad=2.0)

        fig.savefig(full_save_name)
        plt.close(fig) 
        #plt.show()


    def save_csv(self, full_save_name):
        self.df.to_csv(full_save_name)

def ymd2date(ymd):
    return datetime.strptime(ymd, '%Y-%m-%d').date()
        

def parse_arguments():
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(
        prog=os.path.basename(sys.argv[0]),
        description='Estimates the power and energy of a solar panel',
        epilog=__doc__)

    parser.add_argument('--version', action = 'version', version = __version__)

    parser.add_argument('--lat', type = float, default = 49.04885,
                        help = 'The latitude of the panel position [0 - 360]')

    parser.add_argument('--lon', type = float, default = 11.78333,
                        help = 'The longitude of the panel position [0 - 360]')
    
    parser.add_argument('--panel_name', default = 'Offgridtech 195W-FSP-2',
                        help = 'The name of the panel')

    parser.add_argument('--panel_direction', type = float, default = 180.0,
                        help = 'The direction of the panel normale relative to north [0 - 360]')
    
    parser.add_argument('--panel_slope', type = float, default = 45.0,
                        help = 'The slope of the panel normale relative to surface [0 - 360]')

    parser.add_argument('--panel_area', type = float, default = 0.39*0.78*3,
                        help = 'The size of the panel area [m²]')

    parser.add_argument('--panel_efficiency', type = float, default = 100.0,
                        help = 'The efficiency of the panel [%%]. Blue Sky ~ 180. Mist ~ 20')

    parser.add_argument('--panel_bifacial', type = float, default = 0.0,
                        help = 'The bifacial factor of the panel [%%]')

    parser.add_argument('--panel_albedo', type = float, default = 0.0,
                        help = 'The albedo factor of the panel [%%]')

    parser.add_argument('--system_barrier', type = float, default = 20.0,
                        help = 'The threshold above which the system (solarbank, inverter, powerstation) is working [W]')

    parser.add_argument('--inverter_limit', type = float, default = None,
                        help = 'The maximum power limit of the inverter [W]')
    
    parser.add_argument('--battery_split', type = float, default = None,
                        help = 'The threshold when to charge the battery in systems with storage [W]')

    parser.add_argument('--battery_full', type = float, default = None,
                        help = 'The energy when a battery is considered full in systems with storage [Wh]')

    parser.add_argument('--battery_first', action = 'store_true', dest='battery_first',
                        help = 'Serve the battery first! Serve the house second!')
    
    parser.add_argument('--csv', default = None,
                        help = 'The directory for saving of the CSV file if needed')

    parser.add_argument('--plot', default = None,
                        help = 'The directory for saving of the PNG file if needed')
    
    parser.add_argument('forecast_day',
                        type=ymd2date, default = datetime.now().strftime('%Y-%m-%d'), nargs = '?',
                        help = 'Day for forecast')

    parser.set_defaults(battery_first = False)

    return parser.parse_args()


def main():
    args = parse_arguments()
        
    if args.lat < -90 or args.lat > 90:
        logger.error(f'The latitude of the panel position is out of range  "{args.lat}"')
        return 1

    if args.lon < -180 or args.lat > 180:
        logger.error(f'The longitude of the panel position is out of range  "{args.lon}"')
        return 2

    if args.panel_direction < 0 or args.panel_direction > 360:
        logger.error(f'The direction of the panel is out of range  "{args.panel_direction}"')
        return 3

    if args.panel_slope < 0 or args.panel_slope > 360:
        logger.error(f'The slope of the panel is out of range  "{args.panel_slope}"')
        return 4

    if args.panel_efficiency < 0 or args.panel_efficiency > 100:
        logger.error(f'The efficiency of the panel is out of range  "{args.panel_efficiency}"')
        return 5

    if args.panel_bifacial < 0 or args.panel_bifacial > 60:
        logger.error(f'The bifacial factor of the panel is out of range  "{args.panel_bifacial}"')
        return 6

    if args.panel_albedo < 0 or args.panel_albedo > 30:
        logger.error(f'The albedo of the panel is out of range  "{args.panel_albedo}"')
        return 7
    
    if args.system_barrier < 0:
        logger.error(f'The system barrier is out of range  "{args.system_barrier}"')
        return 8

    if args.inverter_limit is not None and (args.inverter_limit < 0 or args.inverter_limit > 800):
        logger.error(f'The inverter limit is out of range  "{args.inverter_limit}"')
        return 9
    
    if args.battery_split is not None and args.battery_split < 0:
        logger.error(f'The split power is out of range  "{args.battery_split}"')
        return 10

    if args.battery_full is not None and args.battery_full < 0:
        logger.error(f'The full energy is out of range  "{args.battery_full}"')
        return 11

    if args.battery_first and args.battery_split is None and args.battery_full is None:
        logger.error(f'The combination of battery parameters is illegal.')
        return 12
        
    if not args.csv is None and not os.path.isdir(args.csv):
        logger.error(f'The directory to save the CSV does not exist "{args.csv}"')
        return 13

    
    logger.info(f'Estimating the harvest of "{args.panel_name}" on "{args.forecast_day}"' )

    text = f' Area: "{args.panel_area:.2f}m²"'
    text += f', Lat/Lon:"{args.lat:.2f}/{args.lon:.2f}"'
    text += f', Dir/Slope:"{args.panel_direction:.0f}/{args.panel_slope:.0f}"'
    logger.info(text)
    text = f' Efficiency: "{args.panel_efficiency:.0f}%"'
    text += f', Start Barrier: "{args.system_barrier:.0f}W"'
    if args.inverter_limit is not None:
        text += f', Inverter Limit: "{args.inverter_limit:.0f}W"' 
    logger.info(text)
    text = f' Bifacial: "{args.panel_bifacial:.0f}%"'
    text += f', Albedo: "{args.panel_albedo:.0f}%"'
    logger.info(text)

    pp = Panel_Power(args.lat, 
                     args.lon, 
                     args.panel_name, 
                     args.panel_direction, 
                     args.panel_slope, 
                     args.panel_area,
                     args.panel_efficiency / 100,
                     args.panel_bifacial / 100,
                     args.panel_albedo / 100,
                     args.system_barrier,
                     args.inverter_limit,
                     args.battery_split,
                     args.battery_full,
                     args.battery_first,
                     args.forecast_day)

    errcode = pp.summarize()
    if errcode > 0:
        logger.error(f'The combination of the provided parameters does not qualify for harvesting')
        return 12

    if not args.csv is None:            
        save_name = args.panel_name.replace(' ', '_') + args.forecast_day.strftime("_%y%m%d") + '.csv'
        pp.save_csv(os.path.join(args.csv, save_name))
        logger.info(f'CSV saved to  "{os.path.join(args.csv, save_name)}"' )
        
    if not args.plot is None:
        save_name = args.panel_name.replace(' ', '_') + args.forecast_day.strftime("_%y%m%d") + '.png'
        pp.save_plot(args.lat, args.lon, args.panel_direction,
                     args.panel_slope, args.panel_area,
                     os.path.join(args.plot, save_name))
        logger.info(f'PLOT saved to  "{os.path.join(args.plot, save_name)}"' )
        
    return 0


if __name__ == '__main__':
    try:
        err = main()
    except KeyboardInterrupt:
        err = 99

    sys.exit(err)
