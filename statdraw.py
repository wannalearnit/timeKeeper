import numpy as np
import matplotlib.pyplot as plt
import time
import sqlite3


# here in all_snaps(timestamp, duration) uses
def drawdailyshit(user_id):
    con = sqlite3.connect("TimeBase.db")
    cur = con.cursor()
    today_stamp = (int(time.time()) // 86400) * 86400 - 3600 * 3
    tomorrow_stamp = today_stamp + 86400
    all_snaps = cur.execute(
        "SELECT timestamp, duration FROM all_sets WHERE (user_id = ?) AND (timestamp > ?) AND (timestamp < ?)",
        [user_id, today_stamp, tomorrow_stamp]).fetchall()
    con.close()
    if len(all_snaps) > 0:
        mas = np.array(all_snaps).T
        mas[0] = mas[0] - mas[1] * 60
        mas = mas.T
    else:
        mas = np.empty([0, 2])
    processed_arr = np.empty([0, 2])
    for i in mas:
        # i[0] - start i; i[1] - duration
        right_diap = ((i[0] // 3600) + 1) * 3600
        if i[0] + i[1] * 60 <= right_diap:
            processed_arr = np.vstack([processed_arr, i])
        else:
            new_dur = (right_diap - i[0]) // 60
            processed_arr = np.vstack([processed_arr, [i[0], new_dur]])
            new_dur = i[1] - new_dur
            if right_diap + new_dur * 60 <= right_diap + 3600:
                processed_arr = np.vstack([processed_arr, [right_diap, new_dur]])
            else:
                processed_arr = np.vstack([processed_arr, [right_diap, 60]])
                processed_arr = np.vstack([processed_arr, [right_diap + 3600, new_dur - 60]])
    processed_arr = processed_arr.T
    fig, ax = plt.subplots()
    ax.hist(processed_arr[0], bins=24, range=(today_stamp, tomorrow_stamp),
            weights=processed_arr[1], rwidth=0.95, color='aqua')
    ax.set_facecolor("gainsboro")
    position = np.array([today_stamp + 7200 * i for i in range(13)])
    ax.set_xticks(position)
    ax.set_xticklabels(['00:00', '02:00', '04:00', '06:00', '08:00', '10:00',
                        '12:00', '14:00', '16:00', '18:00', '20:00', '22:00', '24:00'])
    ax.grid(color='white')
    plt.xlabel("Время")
    plt.ylabel("Продолжительность")
    fig.set_figwidth(10)
    fig.set_figheight(6)
    name_f = str(user_id) + '.png'
    plt.savefig(name_f)
    return 0
