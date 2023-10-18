import skyfield.api
from skyfield.api import wgs84
from datetime import datetime, timezone, timedelta

def calc_sat_view(dt=datetime.now(), tz=timezone(timedelta(hours=9)), view_from_lat = 35.400334, view_from_lon = 139.543152):
    # 表示する最低仰角
    min_disp_alt_deg = 5

    # 計算時刻間隔[秒]
    interval_sec = 5*60
    # 過去側計算回数
    past_generate_count = 6  
    # 未来側計算回数  
    future_generate_count = 6

    # 描画用対象衛星定義
    calc_sats = [
        'NAVSTAR',
        'QZS',
    ]

    sats = skyfield.api.load.tle_file("https://celestrak.org/NORAD/elements/gnss.txt", reload=True)
    rounded_datetime = datetime.fromtimestamp(((dt.timestamp() + interval_sec) // interval_sec) * interval_sec, tz=tz)

    ts = skyfield.api.load.timescale()
    tss = ts.from_datetimes(
        [rounded_datetime - timedelta(minutes=5 * i) for i in range(-past_generate_count,future_generate_count+1)]
    )
    current_ts = ts.from_datetime(rounded_datetime)
    view_from = wgs84.latlon(view_from_lat,view_from_lon) 
    calc_results = []
    for sat in sats:
        sat_name = ''
        for sat_key in calc_sats:
            if sat.name.startswith(sat_key):
                sat_name = sat.name
                break
        if 0 < len(sat_name):
            sat_calc_result = {'name':sat_name, 'pos':[], 'cpos':None}
            alts = []
            azs = []
            difference = sat - view_from
            prev_appended = False
            for target_ts in tss:
                topocentric = difference.at(target_ts)
                alt, az, _ = topocentric.altaz()
                if min_disp_alt_deg < alt.degrees:
                    alts.append(alt.degrees)
                    azs.append(az.degrees)
                    prev_appended = True
                else:
                    if prev_appended and 0 < len(alts) and 0 < len(azs):
                        prev_appended = False
                        sat_calc_result['pos'].append({'alts':alts.copy(), 'azs':azs.copy()})
                        alts = []
                        azs = []
            if 0 < len(alts) and 0 < len(azs):
                sat_calc_result['pos'].append({'alts':alts.copy(), 'azs':azs.copy()})
                alts = []
                azs = []

            target_ts = current_ts
            topocentric = difference.at(target_ts)
            alt, az, _ = topocentric.altaz()
            if min_disp_alt_deg < alt.degrees:
                sat_calc_result['cpos'] = {'az':az.degrees, 'alt':alt.degrees}
                calc_results.append(sat_calc_result.copy())
            elif 0 < len(sat_calc_result['pos']):
                calc_results.append(sat_calc_result.copy())

    return calc_results