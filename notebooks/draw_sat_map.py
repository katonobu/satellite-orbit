from datetime import datetime,timezone, timedelta
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.feature.nightshade import Nightshade
from cartopy.crs import PlateCarree
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from warnings import simplefilter
simplefilter("ignore") # 警告を出さないようにする

def setup_cartopy(ax, title_str, utc_date):
    ax.set_title(title_str)    
    #ax.stock_img() # 色がきれいだが、衛星情報が見にくいのでcoastlines()にする。
    ax.coastlines()
    ax.add_feature(Nightshade(utc_date, alpha=0.05))
    ax.set_xticks(np.linspace(-180, 180, 13), crs=PlateCarree()) # crs=PlateCarree()のところでMatplotlibDeprecationWarningが出るが，現状公式でのticksの描き方がこれ
    ax.set_yticks(np.linspace(-90, 90, 13), crs=PlateCarree())
    ax.set_ylim(-80,80)
    ax.xaxis.set_major_formatter(LongitudeFormatter()) # ﾟNなどを描いてくれる
    ax.yaxis.set_major_formatter(LatitudeFormatter())



# 昼夜影あり白地図に現在時刻±30分の衛星軌道情報を描画する。
def draw_sat_map(calc_results, dt=None):
    calc_sats = calc_results['internal_params']['calc_sats']
    if dt is None:
        if isinstance(calc_results['intermediate_params']['rounded_datetime'],datetime):
            dt = calc_results['intermediate_params']['rounded_datetime']
        else:
            print("art dt must be specified if calc_results comes from json")
            return

    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())


    utc_tz=timezone(timedelta(hours=0))
    utc_date = dt.astimezone(utc_tz)
    sat_sys_str = ','.join(calc_sats)

    setup_cartopy(ax, f"{sat_sys_str} Satellites at {dt}", utc_date)

    marker_tables = [",","o","v","^","<",">",]
    shape_table = { name:marker_tables[i] for i, name in enumerate(calc_sats)}

    cmap = plt.get_cmap("tab10")
    cidx = 0

    for result in calc_results['calc_results']:
        shape = ''
        for sat_key in shape_table.keys():
            if result['name'].startswith(sat_key):
                shape = shape_table[sat_key]
                break
        if 0 < len(shape):
            for line in result['pos']:
                # 経度180度をまたぐ線は引かず、分割して描画させる。
                lons0 = []
                lats0 = []
                prev_lon = line['lons'][0]
                for idx in range(len(line['lons'])):
                    lon = line['lons'][idx]
                    if prev_lon * lon < 0 and (lon < -90 or 90 < lon):
                        # 前の経度とかけ合わせて負になるなら、符号が変化しているので、ここまでのデータで描画
                        ax.plot(lons0,lats0,color=cmap(cidx))
                        # 描画用配列をクリア
                        lons0 = []
                        lats0 = []
                    else:
                        lons0.append(lon)
                        lats0.append(line['lats'][idx])
                    prev_lon = lon
                ax.plot(lons0,lats0,color=cmap(cidx))
            if result['cpos']:
                ax.scatter([result['cpos']['lon']],
                        [result['cpos']['lat']],
                        marker=shape, label=result['name'], color=cmap(cidx))
            cidx += 1
            cidx %= 10

    plt.legend(loc='upper left', bbox_to_anchor=(1, 1),fontsize="xx-small")

if __name__ == "__main__":
    import json
    import os
    from datetime import datetime, timezone, timedelta, date

    json_file_path = os.path.join(os.path.dirname(__file__), 'sample_result_map.json')
    with open(json_file_path, 'r') as f:
        calc_map_results = json.load(f)
        draw_sat_map(calc_map_results, datetime.fromisoformat(calc_map_results['intermediate_params']['rounded_datetime']))
        plt.show()
