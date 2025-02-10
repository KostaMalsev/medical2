import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Merged Hezbollah attacks data
hezbollah_attacks = [
   ["Week", "Missiles Fired", "Drone Attacks", "Notes"],
   ["Oct 1 - Oct 7, 2023", 5000, 10, "Start of war, mass rocket barrages from Gaza & Lebanon"],
   ["Oct 8 - Oct 14, 2023", 3500, 12, "Ongoing heavy attacks, escalation from Lebanon"],
   ["Oct 15 - Oct 21, 2023", 2800, 15, "Hezbollah opens northern front"], 
   ["Oct 22 - Oct 28, 2023", 2500, 20, "Hezbollah and Hamas coordination"],
   ["Oct 29 - Nov 4, 2023", 2200, 18, "IDF airstrikes intensify"],
   ["Nov 5 - Nov 11, 2023", 2000, 22, "Steady attack rate"],
   ["Nov 12 - Nov 18, 2023", 1800, 25, "Some de-escalation in Gaza, Lebanon remains active"],
   ["Nov 19 - Nov 25, 2023", 1700, 30, "Hezbollah drone attacks increase"],
   ["Nov 26 - Dec 2, 2023", 1500, 28, "Significant Israeli air retaliation"],
   ["Dec 3 - Dec 9, 2023", 1400, 35, "Continued Hezbollah rocket barrages"],
   ["Dec 10 - Dec 16, 2023", 1200, 38, "Syria-based attacks increase"],
   ["Dec 17 - Dec 23, 2023", 1100, 40, "Rocket fire slows due to weather"],
   ["Dec 24 - Dec 30, 2023", 1000, 45, "Hezbollah shifts to targeted UAV strikes"],
   ["Jan 1 - Jan 7, 2024", 0, 0, "No significant reported activity"],
   ["Jan 8 - Jan 14, 2024", 0, 0, "No significant reported activity"],
   ["Jan 15 - Jan 21, 2024", 0, 0, "No significant reported activity"],
   ["Jan 22 - Jan 28, 2024", 0, 0, "No significant reported activity"], 
   ["Jan 29 - Feb 4, 2024", 0, 0, "No significant reported activity"],
   ["Feb 5 - Feb 11, 2024", 0, 0, "No significant reported activity"],
   ["Feb 12 - Feb 18, 2024", 0, 0, "No significant reported activity"],
   ["Feb 19 - Feb 25, 2024", 0, 0, "No significant reported activity"],
   ["Feb 26 - Mar 3, 2024", 0, 0, "No significant reported activity"],
   ["Mar 4 - Mar 10, 2024", 0, 0, "No significant reported activity"],
   ["Mar 11 - Mar 17, 2024", 0, 0, "No significant reported activity"],
   ["Mar 18 - Mar 24, 2024", 0, 0, "No significant reported activity"],
   ["Mar 25 - Mar 31, 2024", 0, 0, "No significant reported activity"],
   ["Apr 1 - Apr 7, 2024", 0, 0, "No significant reported activity"],
   ["Apr 8 - Apr 14, 2024", 0, 0, "No significant reported activity"],
   ["Apr 15 - Apr 21, 2024", 0, 0, "No significant reported activity"],
   ["Apr 22 - Apr 28, 2024", 35, 1, "Missiles fired in Ein Zeitim area"],
   ["Apr 29 - May 5, 2024", 0, 0, "No significant reported activity"],
   ["May 6 - May 12, 2024", 0, 0, "No significant reported activity"],
   ["May 13 - May 19, 2024", 135, 3, "60 rockets at Golan Heights"],
   ["May 20 - May 26, 2024", 0, 0, "No significant reported activity"],
   ["May 27 - Jun 2, 2024", 0, 0, "No significant reported activity"],
   ["Jun 3 - Jun 9, 2024", 0, 0, "No significant reported activity"],
   ["Jun 10 - Jun 16, 2024", 180, 30, "150 rockets and 30 drones at northern Israel"],
   ["Jun 17 - Jun 23, 2024", 30, 0, "30 rockets at Kiryat Shmona"],
   ["Jun 24 - Jun 30, 2024", 0, 0, "No significant reported activity"],
   ["Jul 1 - Jul 7, 2024", 200, 20, "200 rockets and 20 drones at IDF bases"],
   ["Jul 8 - Jul 14, 2024", 0, 0, "No significant reported activity"],
   ["Jul 15 - Jul 21, 2024", 0, 0, "No significant reported activity"],
   ["Jul 22 - Jul 28, 2024", 0, 0, "No significant reported activity"],
   ["Jul 29 - Aug 4, 2024", 0, 0, "No significant reported activity"],
   ["Aug 5 - Aug 11, 2024", 10, 0, "10 rockets into Western Galilee"],
   ["Aug 12 - Aug 18, 2024", 0, 0, "No significant reported activity"],
   ["Aug 19 - Aug 25, 2024", 0, 0, "No significant reported activity"],
   ["Aug 26 - Sep 1, 2024", 0, 0, "No significant reported activity"],
   ["Sep 2 - Sep 8, 2024", 0, 0, "No significant reported activity"],
   ["Sep 9 - Sep 15, 2024", 20, 2, "20 rockets and drones at IDF's Filon Base"],
   ["Sep 16 - Sep 22, 2024", 10, 0, "10 rockets into Upper Galilee"],
   ["Sep 23 - Sep 29, 2024", 0, 0, "No significant reported activity"],
   ["Sep 30 - Oct 6, 2024", 0, 0, "No significant reported activity"],
   ["Oct 7 - Oct 13, 2024", 0, 0, "No significant reported activity"],
   ["Oct 14 - Oct 20, 2024", 0, 1, "Drone attack on IDF base"],
   ["Oct 21 - Oct 27, 2024", 0, 0, "No significant reported activity"],
   ["Oct 28 - Nov 3, 2024", 0, 0, "No significant reported activity"],
   ["Nov 4 - Nov 10, 2024", 0, 0, "No significant reported activity"],
   ["Nov 11 - Nov 17, 2024", 0, 0, "No significant reported activity"],
   ["Nov 18 - Nov 24, 2024", 250, 0, "250 rockets into Israel"],
   ["Nov 25 - Dec 1, 2024", 0, 0, "No significant reported activity"],
   ["Dec 2 - Dec 8, 2024", 0, 0, "No significant reported activity"],
   ["Dec 9 - Dec 15, 2024", 0, 0, "No significant reported activity"],
   ["Dec 16 - Dec 22, 2024", 0, 0, "No significant reported activity"],
   ["Dec 23 - Dec 29, 2024", 0, 0, "No significant reported activity"]
]

# Merged Israeli airstrikes data
israeli_airstrikes = [
   ["Week", "Total Airstrikes", "Notes"],
   ["Oct 1 - Oct 7, 2023", 5, "Initial airstrikes in southern Lebanon"],
   ["Oct 8 - Oct 14, 2023", 7, "Increased operations, Syria's Quneitra"],
   ["Oct 15 - Oct 21, 2023", 6, "Strikes on weapons convoys"],
   ["Oct 22 - Oct 28, 2023", 8, "Targeted Hezbollah infrastructure"],
   ["Oct 29 - Nov 4, 2023", 10, "Operations in Deir Ezzor province"],
   ["Nov 5 - Nov 11, 2023", 9, "Strikes on missile facilities"],
   ["Nov 12 - Nov 18, 2023", 7, "Targeting Syrian air defense"],
   ["Nov 19 - Nov 25, 2023", 8, "Operations against training camps"],
   ["Nov 26 - Dec 2, 2023", 6, "Strikes on arms depots"],
   ["Dec 3 - Dec 9, 2023", 5, "Targeted Iranian supply routes"],
   ["Dec 10 - Dec 16, 2023", 7, "Strikes on observation posts"],
   ["Dec 17 - Dec 23, 2023", 6, "Operations against weapon sites"],
   ["Dec 24 - Dec 30, 2023", 5, "Strikes on military installations"],
   ["Jan 1 - Jan 7, 2024", 0, "No significant reported activity"],
   ["Jan 8 - Jan 14, 2024", 0, "No significant reported activity"],
   ["Jan 15 - Jan 21, 2024", 0, "No significant reported activity"],
   ["Jan 22 - Jan 28, 2024", 0, "No significant reported activity"],
   ["Jan 29 - Feb 4, 2024", 0, "No significant reported activity"],
   ["Feb 5 - Feb 11, 2024", 0, "No significant reported activity"],
   ["Feb 12 - Feb 18, 2024", 0, "No significant reported activity"],
   ["Feb 19 - Feb 25, 2024", 0, "No significant reported activity"],
   ["Feb 26 - Mar 3, 2024", 0, "No significant reported activity"],
   ["Mar 4 - Mar 10, 2024", 0, "No significant reported activity"],
   ["Mar 11 - Mar 17, 2024", 3, "Airstrikes in multiple areas"],
   ["Mar 18 - Mar 24, 2024", 4, "Strikes near Damascus"],
   ["Mar 25 - Mar 31, 2024", 2, "Strikes on Hezbollah infrastructure"],
   ["Apr 1 - Apr 7, 2024", 0, "No significant reported activity"],
   ["Apr 8 - Apr 14, 2024", 0, "No significant reported activity"],
   ["Apr 15 - Apr 21, 2024", 0, "No significant reported activity"],
   ["Apr 22 - Apr 28, 2024", 0, "No significant reported activity"],
   ["Apr 29 - May 5, 2024", 0, "No significant reported activity"],
   ["May 6 - May 12, 2024", 0, "No significant reported activity"],
   ["May 13 - May 19, 2024", 0, "No significant reported activity"],
   ["May 20 - May 26, 2024", 0, "No significant reported activity"],
   ["May 27 - Jun 2, 2024", 0, "No significant reported activity"],
   ["Jun 3 - Jun 9, 2024", 0, "No significant reported activity"],
   ["Jun 10 - Jun 16, 2024", 0, "No significant reported activity"],
   ["Jun 17 - Jun 23, 2024", 0, "No significant reported activity"],
   ["Jun 24 - Jun 30, 2024", 0, "No significant reported activity"],
   ["Jul 1 - Jul 7, 2024", 0, "No significant reported activity"],
   ["Jul 8 - Jul 14, 2024", 3, "Strikes in Damascus and Lebanon"],
   ["Jul 15 - Jul 21, 2024", 4, "Multiple strikes in different areas"],
   ["Jul 22 - Jul 28, 2024", 5, "Strikes in Lebanon and Golan"],
   ["Jul 29 - Aug 4, 2024", 2, "Strikes in Beirut area"],
   ["Aug 5 - Aug 11, 2024", 0, "No significant reported activity"],
   ["Aug 12 - Aug 18, 2024", 0, "No significant reported activity"],
   ["Aug 19 - Aug 25, 2024", 6, "Multiple strikes across region"],
   ["Aug 26 - Sep 1, 2024", 0, "No significant reported activity"],
   ["Sep 2 - Sep 8, 2024", 0, "No significant reported activity"],
   ["Sep 9 - Sep 15, 2024", 0, "No significant reported activity"],
   ["Sep 16 - Sep 22, 2024", 0, "No significant reported activity"],
   ["Sep 23 - Sep 29, 2024", 10, "Major bombing campaign"],
   ["Sep 30 - Oct 6, 2024", 0, "No significant reported activity"],
   ["Oct 7 - Oct 13, 2024", 0, "No significant reported activity"],
   ["Oct 14 - Oct 20, 2024", 0, "No significant reported activity"],
   ["Oct 21 - Oct 27, 2024", 0, "No significant reported activity"],
   ["Oct 28 - Nov 3, 2024", 0, "No significant reported activity"],
   ["Nov 4 - Nov 10, 2024", 0, "No significant reported activity"],
   ["Nov 11 - Nov 17, 2024", 0, "No significant reported activity"],
   ["Nov 18 - Nov 24, 2024", 0, "No significant reported activity"],
   ["Nov 25 - Dec 1, 2024", 0, "No significant reported activity"],
   ["Dec 2 - Dec 8, 2024", 0, "No significant reported activity"],
   ["Dec 9 - Dec 15, 2024", 0, "No significant reported activity"],
   ["Dec 16 - Dec 22, 2024", 0, "No significant reported activity"], 
   ["Dec 23 - Dec 29, 2024", 0, "No significant reported activity"],
   ["Dec 30 - Dec 31, 2024", 0, "No significant reported activity"]
]

# Merged Israeli casualties data
israeli_casualties = [
   ["Week", "Israeli Casualties", "Notes"],
   ["Sep 1 - Sep 7, 2023", 0, "No significant reported casualties"],
   ["Sep 8 - Sep 14, 2023", 0, "No significant reported casualties"],
   ["Sep 15 - Sep 21, 2023", 0, "No significant reported casualties"],
   ["Sep 22 - Sep 28, 2023", 0, "No significant reported casualties"],
   ["Sep 29 - Oct 5, 2023", 1200, "Hamas attack casualties"],
   ["Oct 6 - Oct 12, 2023", 0, "No specific figures reported"],
   ["Oct 13 - Oct 19, 2023", 0, "No specific figures reported"],
   ["Oct 20 - Oct 26, 2023", 0, "No specific figures reported"],
   ["Oct 27 - Nov 2, 2023", 0, "No specific figures reported"],
   ["Nov 3 - Nov 9, 2023", 0, "No specific figures reported"],
   ["Nov 10 - Nov 16, 2023", 0, "No specific figures reported"],
   ["Nov 17 - Nov 23, 2023", 0, "No specific figures reported"],
   ["Nov 24 - Nov 30, 2023", 0, "No specific figures reported"],
   ["Dec 1 - Dec 7, 2023", 0, "No specific figures reported"],
   ["Dec 8 - Dec 14, 2023", 0, "No specific figures reported"],
   ["Dec 15 - Dec 21, 2023", 0, "No specific figures reported"],
   ["Dec 22 - Dec 28, 2023", 0, "No specific figures reported"],
   ["Dec 29 - Dec 31, 2023", 0, "No specific figures reported"],
   ["Jan 1 - Jan 7, 2024", 0, "No significant reported casualties"],
   ["Jan 8 - Jan 14, 2024", 0, "No significant reported casualties"],
   ["Jan 15 - Jan 21, 2024", 0, "No significant reported casualties"],
   ["Jan 22 - Jan 28, 2024", 0, "No significant reported casualties"],
   ["Jan 29 - Feb 4, 2024", 0, "No significant reported casualties"],
   ["Feb 5 - Feb 11, 2024", 0, "No significant reported casualties"],
   ["Feb 12 - Feb 18, 2024", 0, "No significant reported casualties"],
   ["Feb 19 - Feb 25, 2024", 0, "No significant reported casualties"],
   ["Feb 26 - Mar 3, 2024", 0, "No significant reported casualties"],
   ["Mar 4 - Mar 10, 2024", 0, "No significant reported casualties"],
   ["Mar 11 - Mar 17, 2024", 0, "No significant reported casualties"],
   ["Mar 18 - Mar 24, 2024", 0, "No significant reported casualties"],
   ["Mar 25 - Mar 31, 2024", 0, "No significant reported casualties"],
   ["Apr 1 - Apr 7, 2024", 0, "No significant reported casualties"],
   ["Apr 8 - Apr 14, 2024", 0, "No significant reported casualties"],
   ["Apr 15 - Apr 21, 2024", 0, "No significant reported casualties"],
   ["Apr 22 - Apr 28, 2024", 0, "No significant reported casualties"],
   ["Apr 29 - May 5, 2024", 0, "No significant reported casualties"],
   ["May 6 - May 12, 2024", 2, "Two soldiers killed by drone"],
   ["May 13 - May 19, 2024", 1, "Civilian killed by missile"],
   ["May 20 - May 26, 2024", 0, "No significant reported casualties"],
   ["May 27 - Jun 2, 2024", 0, "No significant reported casualties"],
   ["Jun 3 - Jun 9, 2024", 0, "No significant reported casualties"],
   ["Jun 10 - Jun 16, 2024", 0, "No significant reported casualties"],
   ["Jun 17 - Jun 23, 2024", 0, "No significant reported casualties"],
   ["Jun 24 - Jun 30, 2024", 0, "No significant reported casualties"],
   ["Jul 1 - Jul 7, 2024", 0, "No significant reported casualties"],
   ["Jul 8 - Jul 14, 2024", 0, "No significant reported casualties"],
   ["Jul 15 - Jul 21, 2024", 0, "No significant reported casualties"],
   ["Jul 22 - Jul 28, 2024", 0, "No significant reported casualties"],
   ["Jul 29 - Aug 4, 2024", 0, "No significant reported casualties"],
   ["Aug 5 - Aug 11, 2024", 0, "No significant reported casualties"],
   ["Aug 12 - Aug 18, 2024", 2, "Two soldiers injured by drone"],
   ["Aug 19 - Aug 25, 2024", 1, "Navy officer killed by rocket"],
   ["Sep 9 - Sep 15, 2024", 1, "Civilian injured by shrapnel"],
   ["Sep 16 - Sep 22, 2024", 0, "No significant reported casualties"],
   ["Sep 23 - Sep 29, 2024", 0, "No significant reported casualties"],
   ["Sep 30 - Oct 6, 2024", 0, "No significant reported casualties"],
   ["Oct 7 - Oct 13, 2024", 0, "No significant reported casualties"],
   ["Oct 14 - Oct 20, 2024", 0, "No significant reported casualties"],
   ["Oct 21 - Oct 27, 2024", 0, "No significant reported casualties"],
   ["Oct 28 - Nov 3, 2024", 0, "No significant reported casualties"],
   ["Nov 4 - Nov 10, 2024", 0, "No significant reported casualties"],
   ["Nov 11 - Nov 17, 2024", 0, "No significant reported casualties"],
   ["Nov 18 - Nov 24, 2024", 0, "No significant reported casualties"],
   ["Nov 25 - Dec 1, 2024", 0, "No significant reported casualties"],
   ["Dec 2 - Dec 8, 2024", 0, "No significant reported casualties"],
   ["Dec 9 - Dec 15, 2024", 0, "No significant reported casualties"],
   ["Dec 16 - Dec 22, 2024", 0, "No significant reported casualties"],
   ["Dec 23 - Dec 29, 2024", 0, "No significant reported casualties"],
   ["Dec 30 - Dec 31, 2024", 0, "No significant reported casualties"]
]

# Merged Hezbollah casualties data
hezbollah_casualties = [
   ["Week", "Hezbollah Casualties", "Notes"],
   ["Sep 1 - Sep 7, 2023", 0, "No significant reported casualties"],
   ["Sep 8 - Sep 14, 2023", 0, "No significant reported casualties"], 
   ["Sep 15 - Sep 21, 2023", 9, "Deaths from explosive devices"],
   ["Sep 22 - Sep 28, 2023", 550, "Casualties from airstrikes"],
   ["Sep 29 - Oct 5, 2023", 0, "No specific figures reported"],
   ["Oct 6 - Oct 12, 2023", 0, "No specific figures reported"],
   ["Oct 13 - Oct 19, 2023", 0, "No specific figures reported"],
   ["Oct 20 - Oct 26, 2023", 0, "No specific figures reported"],
   ["Oct 27 - Nov 2, 2023", 0, "No specific figures reported"],
   ["Nov 3 - Nov 9, 2023", 0, "No specific figures reported"],
   ["Nov 10 - Nov 16, 2023", 0, "No specific figures reported"],
   ["Nov 17 - Nov 23, 2023", 0, "No specific figures reported"],
   ["Nov 24 - Nov 30, 2023", 0, "No specific figures reported"],
   ["Dec 1 - Dec 7, 2023", 2, "Airstrike casualties"],
   ["Dec 8 - Dec 14, 2023", 6, "Casualties from strikes/clashes"],
   ["Dec 15 - Dec 21, 2023", 5, "Casualties from strikes/clashes"],
   ["Dec 22 - Dec 28, 2023", 7, "Casualties from strikes/clashes"],
   ["Dec 29 - Dec 31, 2023", 5, "Casualties from strikes/clashes"],
   ["Jan 1 - Jan 7, 2024", 0, "No significant reported casualties"],
   ["Jan 8 - Jan 14, 2024", 0, "No significant reported casualties"],
   ["Jan 15 - Jan 21, 2024", 0, "No significant reported casualties"],
   ["Jan 22 - Jan 28, 2024", 0, "No significant reported casualties"],
   ["Jan 29 - Feb 4, 2024", 0, "No significant reported casualties"],
   ["Feb 5 - Feb 11, 2024", 0, "No significant reported casualties"],
   ["Feb 12 - Feb 18, 2024", 0, "No significant reported casualties"],
   ["Feb 19 - Feb 25, 2024", 0, "No significant reported casualties"],
   ["Feb 26 - Mar 3, 2024", 0, "No significant reported casualties"],
   ["Mar 4 - Mar 10, 2024", 0, "No significant reported casualties"],
   ["Mar 11 - Mar 17, 2024", 0, "No significant reported casualties"],
   ["Mar 18 - Mar 24, 2024", 0, "No significant reported casualties"],
   ["Mar 25 - Mar 31, 2024", 0, "No significant reported casualties"],
   ["Apr 1 - Apr 7, 2024", 0, "No significant reported casualties"],
   ["Apr 8 - Apr 14, 2024", 0, "No significant reported casualties"],
   ["Apr 15 - Apr 21, 2024", 0, "No significant reported casualties"],
   ["Apr 22 - Apr 28, 2024", 0, "No significant reported casualties"],
   ["Apr 29 - May 5, 2024", 0, "No significant reported casualties"],
   ["May 6 - May 12, 2024", 0, "No significant reported casualties"],
   ["May 13 - May 19, 2024", 0, "No significant reported casualties"],
   ["Aug 19 - Aug 25, 2024", 6, "Airstrike casualties"],
   ["Sep 23 - Sep 29, 2024", 10, "Air raid casualties"],
   ["Nov 18 - Nov 24, 2024", 15, "Casualties from major strikes"],
   ["Dec 30 - Dec 31, 2024", 0, "No significant reported casualties"]
]


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def parse_date(week_range):
    try:
        start_date = week_range.split(" - ")[0]
        year = "2024" if "2024" in week_range else "2023"
        return pd.to_datetime(f"{start_date} {year}")
    except Exception as e:
        print(f"Error parsing date: {week_range} -> {e}")
        return None

# Create DataFrames
missile_df = pd.DataFrame(hezbollah_attacks[1:], columns=hezbollah_attacks[0])
airstrike_df = pd.DataFrame(israeli_airstrikes[1:], columns=israeli_airstrikes[0])
israel_casualties_df = pd.DataFrame(israeli_casualties[1:], columns=israeli_casualties[0])
hezbollah_casualties_df = pd.DataFrame(hezbollah_casualties[1:], columns=hezbollah_casualties[0])

# Convert dates and sort
for df in [missile_df, airstrike_df, israel_casualties_df, hezbollah_casualties_df]:
    df["Date"] = df["Week"].apply(parse_date)
    df.sort_values("Date", inplace=True)

# Create figure
fig, (ax1, ax3) = plt.subplots(2, 1, figsize=(15, 12), height_ratios=[1, 1])
plt.subplots_adjust(right=0.85, hspace=0.3)

# Attacks subplot
ax1.set_xlabel("Date", fontsize=12)
ax1.set_ylabel("Total Missiles Fired", color="tab:blue", fontsize=12)
ax1.plot(missile_df["Date"], missile_df["Missiles Fired"], color="tab:blue", marker="o", label="Missiles Fired", linewidth=2)
ax1.tick_params(axis="y", labelcolor="tab:blue")
ax1.grid(True, alpha=0.3)

# Airstrikes on second y-axis
ax2 = ax1.twinx()
ax2.set_ylabel("Total Airstrikes", color="tab:green", fontsize=12)
ax2.plot(airstrike_df["Date"], airstrike_df["Total Airstrikes"], color="tab:green", marker="s", label="Israeli Airstrikes", linewidth=2)
ax2.tick_params(axis="y", labelcolor="tab:green")

# Casualties subplot
ax3.set_xlabel("Date", fontsize=12)
ax3.set_ylabel("Israeli Fatalities", color="tab:red", fontsize=12)
ax3.plot(israel_casualties_df["Date"], israel_casualties_df["Israeli Casualties"], color="tab:red", marker="o", label="Israeli Fatalities", linewidth=2)
ax3.tick_params(axis="y", labelcolor="tab:red")
ax3.grid(True, alpha=0.3)

# Hezbollah casualties on second y-axis
ax4 = ax3.twinx()
ax4.set_ylabel("Hezbollah Fatalities", color="tab:orange", fontsize=12)
ax4.plot(hezbollah_casualties_df["Date"], hezbollah_casualties_df["Hezbollah Casualties"], color="tab:orange", marker="o", label="Hezbollah Fatalities", linewidth=2)
ax4.tick_params(axis="y", labelcolor="tab:orange")

# Format x-axis
start_date = pd.to_datetime("2023-09-01")
end_date = pd.to_datetime("2024-12-31")
for ax in [ax1, ax3]:
    ax.set_xlim(start_date, end_date)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
    ax.set_ylim(bottom=0)

# Add legends
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")
ax3.legend(loc="upper left")
ax4.legend(loc="upper right")

plt.suptitle("Israel-Hezbollah Conflict Analysis (Sep 2023 - Dec 2024)", fontsize=14, fontweight="bold", y=0.95)
plt.tight_layout()
plt.show()

# Print statistics
stats_df = pd.DataFrame({
    "Category": ["Missile Attacks", "Israeli Airstrikes", "Israeli Fatalities", "Hezbollah Fatalities"],
    "Total": [
        missile_df["Missiles Fired"].sum(),
        airstrike_df["Total Airstrikes"].sum(),
        israel_casualties_df["Israeli Casualties"].sum(),
        hezbollah_casualties_df["Hezbollah Casualties"].sum()
    ],
    "Maximum Weekly": [
        missile_df["Missiles Fired"].max(),
        airstrike_df["Total Airstrikes"].max(),
        israel_casualties_df["Israeli Casualties"].max(),
        hezbollah_casualties_df["Hezbollah Casualties"].max()
    ],
    "Average Weekly": [
        missile_df["Missiles Fired"].mean(),
        airstrike_df["Total Airstrikes"].mean(),
        israel_casualties_df["Israeli Casualties"].mean(),
        hezbollah_casualties_df["Hezbollah Casualties"].mean()
    ]
})

print("\nConflict Statistics Summary (Sep 2023 - Dec 2024)")
print("-" * 50)
for _, row in stats_df.iterrows():
    print(f"\n{row['Category']}:")
    print(f"Total: {row['Total']:,.0f}")
    print(f"Maximum weekly: {row['Maximum Weekly']:,.0f}")
    print(f"Average weekly: {row['Average Weekly']:.1f}")