"""
Taken from Panel documentation: https://panel.holoviz.org/tutorials/basic/pn_bind.html
"""

import panel as pn

pn.extension()


def calculate_power(wind_speed, efficiency):
    power_generation = wind_speed * efficiency
    return (
        f"Wind Speed: {wind_speed} m/s, "
        f"Efficiency: {efficiency}, "
        f"Power Generation: {power_generation:.1f} kW"
    )


wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)

efficiency = 0.3

power = pn.bind(
    calculate_power, wind_speed=wind_speed, efficiency=efficiency
)

pn.Column(wind_speed, power).servable()