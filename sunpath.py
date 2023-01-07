# calculate and plot azimuth and elevationa angle of sun for specific location
# plot sun analemmas and monthly traces

import matplotlib.pyplot as plt
import DateTime
import numpy as np
import pandas as pd

# define Darmstadt as location
latitude = 49.827304
longitude = 8.645111

startday = DateTime.DateTime(2023, 1, 1, 0, 0, 0)


def calc_azimuth_and_elevation_of_sun(t, latitude, longitude):
    """ function to calculate the azimuth and elevation of the sun depending of the Date anf location"""
    # based on the solar energy book of Klaus Jäger et al.
    refday = DateTime.DateTime(2000, 1, 1, 13, 0, 0)  # not noon but 13h due to different time zone
    Tag_Zeitumstellung = DateTime.DateTime(2023, 3, 26, 0, 0, 0)
    Tag_Zeitumstellung2 = DateTime.DateTime(2023, 10, 29, 0, 0, 0)

    # comment in/out to consider time shift in germany
    if t > Tag_Zeitumstellung and t < Tag_Zeitumstellung2:
        t = t - 1 / 24

    D = t - refday  # julian date

    # mean longitude of the sun accrodung to 16.3 on p228
    q = 280.459 + 0.98564736 * D
    q = q - int(q / 360) * 360  # normalize to [0,360°]

    # mean anomaly of the sun accordung to 16.4 on p228
    g = 357.529 + 0.98560028 * D
    g = g - int(g / 360) * 360  # normalize to [0,360°]

    # ecliptic longitude of the sun according to 16.5 on p 228
    lamda_s = q + 1.915 * np.sin(g / 180 * np.pi) + 0.02 * np.sin(2 * g / 180 * np.pi)

    # axial tilt e of the Earth frim 16.8
    epsilon = 23.429 - 0.00000036 * D

    # Greenweich meridian standard time
    GMST = 18.697374558 + 24.06570982441908 * D + 0.000026 * (D / 36525) ** 2
    GMST = GMST - int(GMST / 24) * 24  # normalize to [0,24]

    theta_L = GMST * 15 + longitude
    theta_L = theta_L - int(theta_L / 360) * 360  # normalize to [0,360°]

    v_S = - np.sin(theta_L / 180 * np.pi) * np.cos(lamda_s / 180 * np.pi) + np.cos(theta_L / 180 * np.pi) * \
          np.cos(epsilon / 180 * np.pi) * np.sin(lamda_s / 180 * np.pi)
    Epsilon_S = - np.sin(latitude / 180 * np.pi) * np.cos(theta_L / 180 * np.pi) * np.cos(lamda_s / 180 * \
                                                                                          np.pi) - (
                            np.sin(latitude / 180 * np.pi) * np.sin(theta_L / 180 * np.pi) * np.cos(epsilon / 180 * \
                                                                                                    np.pi) - np.cos(
                        latitude / 180 * np.pi) * np.sin(epsilon / 180 * np.pi)) * np.sin(lamda_s / 180 * \
                                                                                          np.pi)
    Zeta_S = np.cos(latitude / 180 * np.pi) * np.cos(theta_L / 180 * np.pi) * \
             np.cos(lamda_s / 180 * np.pi) + (np.cos(latitude / 180 * np.pi) * np.sin(theta_L / 180 * np.pi) * \
                                              np.cos(epsilon / 180 * np.pi) + np.sin(latitude / 180 * np.pi) * np.sin(
                epsilon / 180 * np.pi)) * \
             np.sin(lamda_s / 180 * np.pi)

    tan_AS = v_S / Epsilon_S
    sin_aS = Zeta_S

    # based on the solar energy book of Klaus Jäger et al.
    if Epsilon_S > 0 and v_S > 0:
        azimuth_sun = np.arctan(tan_AS) / np.pi * 180
    elif Epsilon_S > 0 and v_S < 0:
        azimuth_sun = np.arctan(tan_AS) / np.pi * 180 + 360
    else:
        azimuth_sun = np.arctan(tan_AS) / np.pi * 180 + 180
    elevation_sun = max(np.arcsin(sin_aS) / np.pi * 180, 0)

    return azimuth_sun, elevation_sun

# === plot sunpath at location
plt.figure(figsize=(10, 8))
plot_colors = "bg" * 12  # "bgrcmy" * 6
color_ind = -1

# === sun Analemmas for each hour over the year ============
for ii in range(24):
    if ii % 2 == 1:
        continue  # plot only for every other hour
    color_ind += 1
    t = np.arange(startday + ii / 24, startday + 365 + ii / 24, 1)
    results = map(calc_azimuth_and_elevation_of_sun, t, [latitude] * len(t), [longitude] * len(t))
    azimuth_sun, elevation_sun = zip(*results)
    if max(elevation_sun) <= 0:
        continue
    plt.plot(azimuth_sun, elevation_sun, '.', color=plot_colors[color_ind])
    plt.text(azimuth_sun[elevation_sun.index(max(elevation_sun))], max(elevation_sun), \
             str(ii) + "h", color=plot_colors[color_ind], ha="center")
    if ii > 7 and ii < 17:
        plt.text(azimuth_sun[elevation_sun.index(min(elevation_sun))], min(elevation_sun) - 2, \
                 str(ii) + "h", color=plot_colors[color_ind], ha="center")

# === suntraces for each month ===========================
dates = pd.date_range(start="2023-01-01", periods=12, freq='MS')
months = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", \
          "November", "Dezember"]
for date in dates:
    futureday = DateTime.DateTime(date)
    t = np.arange(futureday, futureday + 1, 0.01)
    results = map(calc_azimuth_and_elevation_of_sun, t, [latitude] * len(t), [longitude] * len(t))
    azimuth_sun, elevation_sun = zip(*results)
    if max(elevation_sun) <= 0:
        continue
    if date.month % 2 == 0:
        plt.plot(azimuth_sun, elevation_sun, ':', color="k")
    else:
        plt.plot(azimuth_sun, elevation_sun, '--', color="k")
    plt.text(azimuth_sun[elevation_sun.index(max(elevation_sun))], max(elevation_sun), months[date.month - 1])

plt.title("Sonnenstand in Darmstadt")
plt.xlabel("Himmelsrichtung")
plt.xticks([0, 45, 90, 135, 180, 225, 270, 315, 360], ["Nord", "Nord-Ost", "Ost", "Süd-Ost", "Süd", \
                                                       "Süd-West", "West", "Nord-West", "Nord"])
plt.ylabel("Einfallswinkel in °")
plt.grid()
plt.show()
