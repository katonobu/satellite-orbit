import matplotlib.pyplot as plt
import math

def draw_sat_view(calc_results):
    dt = calc_results['intermediate_params']['rounded_datetime']
    view_from_lat = calc_results['input_params']['view_from']['lat']
    view_from_lon = calc_results['input_params']['view_from']['lon']
    calc_sats = calc_results['internal_params']['calc_sats']

    marker_tables = [",","o","v","^","<",">",]
    shape_table = { name:marker_tables[i] for i, name in enumerate(calc_sats)}

    fig = plt.figure(figsize=[8,4.5])
    ax = fig.add_subplot(projection='polar')

    ax.set_theta_offset(math.pi/2)
    ax.set_theta_direction(-1)

    rtick_deg = [90,60,45,30,0]
    ax.set_rticks([math.cos(deg/180 * math.pi) for deg in rtick_deg],[str(deg) for deg in rtick_deg])
    plt.title(f"Satellite view from [{view_from_lat},{view_from_lon}] at {dt}")

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
                ax.plot([az/180 * math.pi for az in line['azs']],
                        [math.cos(alt/180 * math.pi) for alt in line['alts']],
                    color=cmap(cidx))
            if result['cpos']:
                ax.scatter([result['cpos']['az']/180 * math.pi],
                        [math.cos(result['cpos']['alt']/180 * math.pi)],
                        marker=shape, label=result['name'], color=cmap(cidx))
            cidx += 1
            cidx %= 10

    plt.legend(loc='upper left', bbox_to_anchor=(1, 1),fontsize="xx-small")

if __name__ == "__main__":
  import json
  import os
  json_file_path = os.path.join(os.path.dirname(__file__), 'sample_result_view.json')
  with open(json_file_path, 'r') as f:
    draw_sat_view(json.load(f))
    plt.show()
