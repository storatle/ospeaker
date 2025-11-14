#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import matplotlib.pyplot as plt
import re
import numpy as np

def bonus_points():
   return {
           
          'N':700,
          'H 10':700,
          'D 10':700,
          'H 11-12':650,
          'D 11-12':650,
          'D 13-14':500,
          'D 15-16':300,
          'D 17-20':250,
          'D 21-39':200,
          'D 40':250,
          'D 50':400,
          'D 60':500,
          'D 70':600,
          'D 80':700,
          'H 13-14':400,
          'H 15-16':200,
          'H 17-20':150,
          'H 21-39':100,
          'H 40':150,
          'H 50':200,
          'H 60':350,
          'H 70':400,
          'H 80':500,
          'Trim':300
          }
print("Hello")
data = bonus_points()



# ---- SPLITT UT DATA ----
d_data = {k[2:]: v for k, v in data.items() if k.startswith("D")}
h_data = {k[2:]: v for k, v in data.items() if k.startswith("H")}
other_data = {k: v for k, v in data.items() if not k.startswith("D") and not k.startswith("H")}

# Alle gruppene fra D- og H-klasser
groups = sorted(set(d_data.keys()) | set(h_data.keys()))

# Verdier for D og H (0 hvis mangler)
d_values = [d_data.get(g, 0) for g in groups]
h_values = [h_data.get(g, 0) for g in groups]

# Legg til OTHER som egen "gruppe" på slutten
other_groups = list(other_data.keys())
other_values = list(other_data.values())

# ---- PLOTTING ----
x_main = np.arange(len(groups))  # posisjoner for D/H
x_other = np.arange(len(other_groups)) + len(groups) + 1  # legg dem etter et gap

width = 0.28  # bredde på søylene

plt.figure(figsize=(14, 6))

# D-søyler
plt.bar(x_main - width, d_values, width, label="D", color="tab:blue")

# H-søyler
plt.bar(x_main, h_values, width, label="H", color="tab:orange")

# OTHER-søyler – tredje farge
plt.bar(x_other, other_values, width, label="Andre klasser", color="tab:green")

# X-aksen: D/H labels + gap + other labels
xticks = list(groups) + [""] + other_groups
x_positions = list(x_main) + [len(groups)] + list(x_other)

plt.xticks(x_positions, xticks, rotation=45)

plt.ylabel("Poeng")
plt.title("Bonuspoeng – D, H og øvrige klasser")
plt.legend()
plt.tight_layout()
plt.show()
