import matplotlib.pyplot as plt
import math

def draw_sat_view(calc_results, dt, view_from_lat = 35.400334, view_from_lon = 139.543152, calc_sats=['NAVSTAR','QZS']):
    marker_tables = [",","o","v","^","<",">",]
    shape_table = { name:marker_tables[i] for i, name in enumerate(calc_sats)}

    fig = plt.figure(figsize=[8,4.5])
    ax = fig.add_subplot(projection='polar')

    ax.set_theta_offset(math.pi/2)
    ax.set_theta_direction(-1)

    rtick_deg = [90,60,45,30,0]
    ax.set_rticks([math.cos(deg/180 * math.pi) for deg in rtick_deg],[str(deg) for deg in rtick_deg])
    plt.title("Satellite view from [{},{}] at {}".format(view_from_lat, view_from_lon, dt.strftime('%Y/%m/%d %H:%M:%S')))

    cmap = plt.get_cmap("tab10")
    cidx = 0

    for result in calc_results:
        shape = ''
        for sat_key in shape_table.keys():
            if result['name'].startswith(sat_key):
                shape = shape_table[sat_key]
                break
        if 0 < len(shape):
            for line in result['pos']:
                ax.plot([az/180 * math.pi for az in line['azs']],
                        [math.cos(alt/180 * math.pi) for alt in line['alts']],
                    color=cmap(cidx))
            if result['cpos']:
                ax.scatter([result['cpos']['az']/180 * math.pi],
                        [math.cos(result['cpos']['alt']/180 * math.pi)],
                        marker=shape, label=result['name'], color=cmap(cidx))
            cidx += 1
            cidx %= 10

    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
