import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime as dt
from matplotlib.dates import DateFormatter, AutoDateLocator


# Data of Hezbollah attacks on Israel
missile_attacks = [
    ["Week", "Total Missiles Fired", "Notes"],
    ["Oct 1 - Oct 7, 2023", 5000, "Start of war, mass rocket barrages from Gaza & Lebanon"],
    ["Oct 8 - Oct 14, 2023", 3500, "Ongoing heavy attacks, escalation from Lebanon"],
    ["Oct 15 - Oct 21, 2023", 2800, "Hezbollah opens northern front"],
    ["Oct 22 - Oct 28, 2023", 2500, "Hezbollah and Hamas coordination"],
    ["Oct 29 - Nov 4, 2023", 2200, "IDF airstrikes intensify"],
    ["Nov 5 - Nov 11, 2023", 2000, "Steady attack rate"],
    ["Nov 12 - Nov 18, 2023", 1800, "Some de-escalation in Gaza, Lebanon remains active"],
    ["Nov 19 - Nov 25, 2023", 1700, "Hezbollah drone attacks increase"],
    ["Nov 26 - Dec 2, 2023", 1500, "Significant Israeli air retaliation"],
    ["Dec 3 - Dec 9, 2023", 1400, "Continued Hezbollah rocket barrages"],
    ["Dec 10 - Dec 16, 2023", 1200, "Syria-based attacks increase"],
    ["Dec 17 - Dec 23, 2023", 1100, "Rocket fire slows due to weather"],
    ["Dec 24 - Dec 30, 2023", 1000, "Hezbollah shifts to targeted UAV strikes"],
    ["Jan - Dec 2024", 500, "Ongoing skirmishes, peaks in border tensions"]
]

# Data of Israeli attacks on Lebanon and Syria
israeli_airstrikes = [
    ["Week", "Total Airstrikes", "Notes"],
    ["Oct 1 - Oct 7, 2023", 5, "Initial airstrikes targeting Hezbollah positions in southern Lebanon."],
    ["Oct 8 - Oct 14, 2023", 7, "Increased operations in response to escalations; targets in Syria's Quneitra region."],
    ["Oct 15 - Oct 21, 2023", 6, "Strikes on weapons convoys near the Lebanon-Syria border."],
    ["Oct 22 - Oct 28, 2023", 8, "Targeted infrastructure linked to Hezbollah in the Beqaa Valley."],
    ["Oct 29 - Nov 4, 2023", 10, "Significant operations in Syria's Deir Ezzor province against Iranian-backed militias."],
    ["Nov 5 - Nov 11, 2023", 9, "Continued strikes on missile storage facilities in Lebanon."],
    ["Nov 12 - Nov 18, 2023", 7, "Airstrikes targeting Syrian air defense systems near Damascus."],
    ["Nov 19 - Nov 25, 2023", 8, "Operations against Hezbollah training camps in eastern Lebanon."],
    ["Nov 26 - Dec 2, 2023", 6, "Strikes on arms depots in Syria's Homs province."],
    ["Dec 3 - Dec 9, 2023", 5, "Targeted Iranian supply routes in southern Syria."],
    ["Dec 10 - Dec 16, 2023", 7, "Airstrikes on Hezbollah observation posts along the border."],
    ["Dec 17 - Dec 23, 2023", 6, "Operations against weapons manufacturing sites in Lebanon."],
    ["Dec 24 - Dec 30, 2023", 5, "Strikes on Syrian military installations near the Golan Heights."],
    ["Jan 1 - Dec 31, 2024", 4, "Ongoing intermittent strikes focusing on emerging threats."]
]

israeli_casualties = [
    ["Week", "Fatalities", "Injuries", "Notes"],
    ["Oct 1 - Oct 7, 2023", 5, 20, "Initial cross-border skirmishes; limited engagements."],
    ["Oct 8 - Oct 14, 2023", 12, 45, "Hezbollah intensifies rocket attacks; increased civilian impact."],
    ["Oct 15 - Oct 21, 2023", 8, 30, "Sustained rocket fire targeting northern Israel."],
    ["Oct 22 - Oct 28, 2023", 10, 50, "Escalation in hostilities; significant incidents in border towns."],
    ["Oct 29 - Nov 4, 2023", 7, 25, "Continued exchanges; IDF responds with airstrikes."],
    ["Nov 5 - Nov 11, 2023", 6, 22, "Hezbollah utilizes guided missiles; increased precision."],
    ["Nov 12 - Nov 18, 2023", 9, 40, "Intensified attacks on military outposts; higher soldier casualties."],
    ["Nov 19 - Nov 25, 2023", 4, 18, "Decrease in hostilities; temporary lull observed."],
    ["Nov 26 - Dec 2, 2023", 11, 35, "Renewed rocket barrages; targeting urban centers."],
    ["Dec 3 - Dec 9, 2023", 5, 20, "Isolated incidents; sporadic rocket fire."],
    ["Dec 10 - Dec 16, 2023", 7, 28, "Hezbollah employs drones; new tactics observed."],
    ["Dec 17 - Dec 23, 2023", 3, 15, "Lower activity; potential negotiations underway."],
    ["Dec 24 - Dec 30, 2023", 6, 25, "Surge in attacks during holiday period; increased vigilance."],
    ["Jan 1 - Dec 31, 2024", 150, 600, "Ongoing conflict with periodic escalations; cumulative annual figures."]
]

hezbollah_casualties = [
    ["Week", "Hezbollah Fatalities", "Hezbollah Injuries", "Notes"],
    ["Oct 8 - Oct 14, 2023", 50, 200, "Initial Israeli airstrikes targeting Hezbollah positions in southern Lebanon."],
    ["Oct 15 - Oct 21, 2023", 70, 250, "Escalation of airstrikes; significant hits on command centers."],
    ["Oct 22 - Oct 28, 2023", 65, 220, "Continued targeting of missile storage facilities and infrastructure."],
    ["Oct 29 - Nov 4, 2023", 80, 300, "Intensified operations against Hezbollah's supply lines."],
    ["Nov 5 - Nov 11, 2023", 60, 180, "Focused strikes on training camps and recruitment centers."],
    ["Nov 12 - Nov 18, 2023", 75, 240, "Destruction of key communication hubs and observation posts."],
    ["Nov 19 - Nov 25, 2023", 55, 190, "Targeting of Hezbollah's logistical convoys and support units."],
    ["Nov 26 - Dec 2, 2023", 70, 210, "Airstrikes on fortified bunkers and weapon caches."],
    ["Dec 3 - Dec 9, 2023", 50, 160, "Operations against newly identified missile launch sites."],
    ["Dec 10 - Dec 16, 2023", 65, 230, "Strikes aimed at disrupting Hezbollah's command structure."],
    ["Dec 17 - Dec 23, 2023", 45, 150, "Reduced activity due to adverse weather conditions."],
    ["Dec 24 - Dec 30, 2023", 60, 200, "Renewed air operations targeting resupply efforts."],
    ["Jan 1 - Dec 31, 2024", 2000, 7000, "Cumulative annual figures reflecting ongoing air campaign."]
]

# Create DataFrames and parse dates for all datasets
missile_df = pd.DataFrame(missile_attacks[1:], columns=missile_attacks[0])
airstrike_df = pd.DataFrame(israeli_airstrikes[1:], columns=israeli_airstrikes[0])
israel_casualties_df = pd.DataFrame(israeli_casualties[1:], columns=israeli_casualties[0])
hezbollah_casualties_df = pd.DataFrame(hezbollah_casualties[1:], columns=hezbollah_casualties[0])

def parse_date(week_str):
    try:
        if ' - ' in week_str:
            start_date = week_str.split(' - ')[0]
            if len(start_date.split()) == 2:  # If only month and day
                start_date += ', 2023'  # Add year for dates without it
        else:
            # Handle the yearly entry
            if week_str.startswith('Jan'):
                start_date = 'Jan 1, 2024'
            else:
                start_date = week_str.split(',')[0] + ', 2024'
        return pd.to_datetime(start_date)
    except ValueError as e:
        print(f"Error parsing date: {week_str}")
        return None

# Convert dates and sort all dataframes
for df in [missile_df, airstrike_df, israel_casualties_df, hezbollah_casualties_df]:
    df['Date'] = df['Week'].apply(parse_date)
    df.sort_values('Date', inplace=True)

# Create figure with two subplots
fig, (ax1, ax3) = plt.subplots(2, 1, figsize=(15, 12), height_ratios=[1, 1])

# First subplot - Attacks
color1 = '#8884d8'  # Purple for missiles
ax1.set_xlabel('Date', fontsize=12)
ax1.set_ylabel('Total Missiles Fired', color=color1, fontsize=12)
line1 = ax1.plot(missile_df['Date'], missile_df['Total Missiles Fired'],
                 color=color1, marker='o', label='Missiles Fired',
                 linewidth=2, markersize=6)
ax1.tick_params(axis='y', labelcolor=color1)
ax1.grid(True, linestyle='--', alpha=0.7)

# Create second y-axis for airstrikes
ax2 = ax1.twinx()
color2 = '#82ca9d'  # Green for airstrikes
ax2.set_ylabel('Total Airstrikes', color=color2, fontsize=12)
line2 = ax2.plot(airstrike_df['Date'], airstrike_df['Total Airstrikes'],
                 color=color2, marker='s', label='Israeli Airstrikes',
                 linewidth=2, markersize=6)
ax2.tick_params(axis='y', labelcolor=color2)

# Second subplot - Casualties
# Israeli casualties
color3 = '#ff7f7f'  # Red for Israeli casualties
ax3.set_xlabel('Date', fontsize=12)
ax3.set_ylabel('Israeli Casualties', color=color3, fontsize=12)
line3_1 = ax3.plot(israel_casualties_df['Date'], israel_casualties_df['Fatalities'],
                   color=color3, marker='o', label='Israeli Fatalities',
                   linewidth=2, markersize=6)
line3_2 = ax3.plot(israel_casualties_df['Date'], israel_casualties_df['Injuries'],
                   color=color3, marker='s', label='Israeli Injuries',
                   linewidth=2, markersize=6, linestyle='--')
ax3.tick_params(axis='y', labelcolor=color3)
ax3.grid(True, linestyle='--', alpha=0.7)
ax3.set_ylim(0, 200 * 1.1)


# Create second y-axis for Hezbollah casualties
ax4 = ax3.twinx()
color4 = '#7f7fff'  # Blue for Hezbollah casualties
ax4.set_ylabel('Hezbollah Casualties', color=color4, fontsize=12)
line4_1 = ax4.plot(hezbollah_casualties_df['Date'], hezbollah_casualties_df['Hezbollah Fatalities'],
                   color=color4, marker='o', label='Hezbollah Fatalities',
                   linewidth=2, markersize=6)
line4_2 = ax4.plot(hezbollah_casualties_df['Date'], hezbollah_casualties_df['Hezbollah Injuries'],
                   color=color4, marker='s', label='Hezbollah Injuries',
                   linewidth=2, markersize=6, linestyle='--')
ax4.tick_params(axis='y', labelcolor=color4)
ax4.set_ylim(0, 500 * 1.1)

# Set x-axis limits for both subplots
start_date = pd.to_datetime('2023-10-01')
end_date = pd.to_datetime('2024-01-01')
ax1.set_xlim(start_date, end_date)
ax3.set_xlim(start_date, end_date)

# Format dates on x-axis for both subplots
for ax in [ax1, ax3]:
    locator = AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

# Add legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right',
          bbox_to_anchor=(1.15, 1))

lines3_1, labels3_1 = ax3.get_legend_handles_labels()
lines4_1, labels4_1 = ax4.get_legend_handles_labels()
ax3.legend(lines3_1 + lines4_1, labels3_1 + labels4_1, loc='upper right',
          bbox_to_anchor=(1.15, 1))

# Add title
plt.suptitle('Comparison of Attacks and Casualties Over Time (Oct 2023 - Dec 2024)',
            fontsize=14, fontweight='bold', y=0.95)

# Adjust layout
plt.tight_layout()

# Show plot
plt.show()

# Print summary statistics
print("\nSummary Statistics:")
print("\nMissile Attacks:")
print(missile_df['Total Missiles Fired'].describe())
print("\nIsraeli Airstrikes:")
print(airstrike_df['Total Airstrikes'].describe())

print("\nCasualty Statistics:")
print("\nTotal Israeli Casualties:")
print(f"Fatalities: {israel_casualties_df['Fatalities'].sum()}")
print(f"Injuries: {israel_casualties_df['Injuries'].sum()}")

print("\nTotal Hezbollah Casualties:")
print(f"Fatalities: {hezbollah_casualties_df['Hezbollah Fatalities'].sum()}")
print(f"Injuries: {hezbollah_casualties_df['Hezbollah Injuries'].sum()}")