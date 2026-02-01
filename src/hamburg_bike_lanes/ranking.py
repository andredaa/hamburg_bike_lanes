import pandas as pd

ranking = {
    "Protected Bike Lane": 3,
    "Kopenhagener Radweg": 3,
    "Fahrradstraße": 2,
    "Aufgeweiteter Radaufstellstreifen": 2,
    "Radweg (mit Grünstreifen vom Gehweg getrennt)": 2,
    "Radfahrstreifen": 2,
    "Wege in Grünflächen": 2,
    "Schutzstreifen": 1,
    "Busfahrstreifen mit Radverkehr": 1,
    "Getrennter Geh-/Radweg": 1,
    "Gemeinsamer Geh-/Radweg": 0,
    "Wirtschaftsweg": 0,
}

def rank_bikepath(row: pd.core.series.Series):
    "ranks from 0-3, 0 being worst"
    if str(row["radweg_in_mittellage"]).lower() == "Ja".lower():
        return 0

    if row["breite"] >= 4:
        return 3

    if row["radweg_art"] == "Radfahrstreifen" and row["breite"] < 2:
        return 1
    if row["radweg_art"] == "Schutzstreifen" and row["breite"] < 1.2:
        return 0
    if row["radweg_art"] == "Getrennter Geh-/Radweg" and row["breite"] < 1:
        return 0

    return ranking[row["radweg_art"]]
