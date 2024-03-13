import numpy as np
import matplotlib.pyplot as plt
import panel as pn

pn.extension("matplotlib")
plt.rcParams["font.sans-serif"] = ["SimHei"]

# Create the data
x = np.linspace(0, 2, 200)
y = np.exp(x)

# Create the plot
fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_title("这是一个标题")

# Create a Panel object
matplotlib_pane = pn.pane.Matplotlib(fig, width=500)

# Show the Panel object
matplotlib_pane.servable()
