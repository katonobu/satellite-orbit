import skyfield.api
from skyfield.api import wgs84
from datetime import datetime, timezone, timedelta
from skyfield.api import Loader

def calc_sat_map(dt=None, tz=timezone(timedelta(hours=9)), force_reload = False):
    if dt is None:
        dt = datetime.now(tz)
    input_params = {'dt':dt, 'tz':tz}

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
    # 衛星軌道情報download URL
    url = "https://celestrak.org/NORAD/elements/gnss.txt"

    internal_params = {
        'min_disp_alt_deg':min_disp_alt_deg,
        'interval_sec':interval_sec,
        'past_generate_count':past_generate_count,
        'future_generate_count':future_generate_count,
        'calc_sats':calc_sats,
        'url':url
    }

    calc_results = []
    rounded_datetime = datetime.fromtimestamp(((dt.timestamp() + interval_sec) // interval_sec) * interval_sec, tz=tz)
    intermediate_params = {
        'rounded_datetime':rounded_datetime
    }

    load = Loader('.', verbose=False)
    try:
        sats = load.tle_file(url, reload=force_reload)

        ts = skyfield.api.load.timescale()
        tss = ts.from_datetimes(
            [rounded_datetime - timedelta(minutes=5 * i) for i in range(-past_generate_count,future_generate_count+1)]
        )
        current_ts = ts.from_datetime(rounded_datetime)
        for sat in sats:
            sat_name = ''
            for sat_key in calc_sats:
                if sat.name.startswith(sat_key):
                    sat_name = sat.name
                    break
            if 0 < len(sat_name):
                sat_calc_result = {'name':sat_name, 'pos':[], 'cpos':None}
                lons = []
                lats = []
                for target_ts in tss:
                    (lat, lon) = wgs84.latlon_of(sat.at(target_ts))
                    lats.append(lat.degrees)
                    lons.append(lon.degrees)
                sat_calc_result['pos'].append({'lons':lons.copy(), 'lats':lats.copy()})            

                target_ts = current_ts
                (lat, lon) = wgs84.latlon_of(sat.at(target_ts))
                sat_calc_result['cpos'] = {'lon':lon.degrees, 'lat':lat.degrees}
                calc_results.append(sat_calc_result.copy())


    except Exception as e:
        print(e)

    return {'calc_results':calc_results, 'input_params':input_params, 'internal_params':internal_params, 'intermediate_params':intermediate_params}


if __name__ == "__main__":
    import json
    def json_serial(obj):
        if isinstance(obj, (datetime)):
            return obj.isoformat()
        if isinstance(obj, (timezone)):
            return obj.tzname(None)
        raise TypeError ("Type %s not serializable" % type(obj))

    calc_results = calc_sat_map()
    print(json.dumps(calc_results, default=json_serial, indent=2))