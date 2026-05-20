import fastf1
import streamlit as st
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
from streamlit_sortables import sort_items
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MODEL_DIR = BASE_DIR.parent.parent / "BACKEND" / "EMOTION-AS-A-SERVICE" / "model"

stack_model = joblib.load(MODEL_DIR / "f1_race_predictor_model.pkl")
scaler = joblib.load(MODEL_DIR / "scaler.pkl")
feature_columns = joblib.load(MODEL_DIR / "feature_columns.pkl")
filtered_drivers_info = pd.read_csv(
    MODEL_DIR / "DATA" / "filtered_drivers_info.csv"
)
# Get driver list
driver_abbrs = filtered_drivers_info["Abbreviation"].tolist()

# Get 2024 schedule from FastF1
schedule = fastf1.get_event_schedule(2024)
schedule = schedule.drop(0)
event_names = schedule['EventName'].tolist()
event_rounds = schedule['RoundNumber'].tolist()
race_name_to_round = dict(zip(event_names, event_rounds))

# Streamlit UI setup
st.set_page_config(page_title="F1 Predictor", layout="wide")
st.title("Podium Simulator")
st.markdown("Select the race and enter driver grid positions to predict the final standings.")

# Dropdown for race selection
selected_race_name = st.selectbox("Select Race", event_names)
round_number = race_name_to_round[selected_race_name]

# =========================
# F1 STYLE DRAG GRID
# =========================

st.subheader("🏎️ Starting Grid")

st.markdown("""
Drag drivers to change the starting grid.
""")

# CUSTOM CSS
st.markdown("""
<style>

[data-testid="stVerticalBlock"] ul {
    padding: 0;
}

[data-testid="stVerticalBlock"] li {

    list-style-type: none;

    background: linear-gradient(90deg, #15151E 0%, #1E1EAA 100%);

    color: white;

    padding: 20px;

    margin-bottom: 12px;

    border-radius: 18px;

    font-size: 30px;

    font-weight: 900;

    text-align: center;

    border-left: 12px solid #FF1801;

    box-shadow: 0 4px 15px rgba(0,0,0,0.35);

    transition: 0.2s ease;

    cursor: grab;
}

[data-testid="stVerticalBlock"] li:hover {
    transform: scale(1.02);
}

</style>
""", unsafe_allow_html=True)

# DRIVER ORDER
default_order = driver_abbrs.copy()

# SORTABLE
sorted_drivers = sort_items(
    default_order,
    direction="vertical"
)

# GRID POSITIONS
grid_positions = {
    driver: position + 1
    for position, driver in enumerate(sorted_drivers)
}

# CURRENT GRID
grid_df = pd.DataFrame({
    "GridPosition": range(1, len(sorted_drivers)+1),
    "Driver": sorted_drivers
})

st.dataframe(
    grid_df,
    use_container_width=True,
    hide_index=True
)

# Prediction logic
if st.button("Predict Race Results"):
    GridPosition = [grid_positions[driver] for driver in driver_abbrs]

    pred_gp_data = pd.DataFrame({
        "Round": [round_number] * 20,
        "Abbreviation": driver_abbrs,
        "GridPosition": GridPosition,
        "Points": filtered_drivers_info["Points"],
        "AvgQualiPosition": filtered_drivers_info["AvgQualiPosition"],
        "AvgRacePosition": filtered_drivers_info["AvgRacePosition"],
        "QualifyingScore": (filtered_drivers_info["AvgQualiPosition"] + GridPosition) / 2
    })

    label_enc_driver = LabelEncoder()
    pred_gp_data["Abbreviation"] = label_enc_driver.fit_transform(pred_gp_data["Abbreviation"])

    pred_gp_data = pred_gp_data[feature_columns]
    X_scaled = scaler.transform(pred_gp_data)
    predicted_positions = stack_model.predict(X_scaled)
    pred_gp_data["PredictedPosition"] = predicted_positions

    results = pred_gp_data.sort_values("PredictedPosition").reset_index(drop=True)
    results.index += 1
    results.rename_axis("PredictedRank", inplace=True)
    results = results.reset_index()
    results["Driver_Abbreviation"] = label_enc_driver.inverse_transform(results["Abbreviation"])

    st.success(f"📊 Predicted Results for {selected_race_name} (Round {round_number})")
    st.dataframe(results[["PredictedRank", "Driver_Abbreviation"]], use_container_width=True)

