import fastf1
import streamlit as st
import pandas as pd
import joblib

from sklearn.preprocessing import LabelEncoder
from pathlib import Path

from components.sortable_grid import show_sortable_grid


def show_grid_positioning():

    BASE_DIR = Path(__file__).resolve().parent
    MODEL_DIR = (
        BASE_DIR.parent.parent
        / "BACKEND"
        / "EMOTION-AS-A-SERVICE"
        / "model"
    )

    stack_model = joblib.load(
        MODEL_DIR / "f1_race_predictor_model.pkl"
    )

    scaler = joblib.load(
        MODEL_DIR / "scaler.pkl"
    )

    feature_columns = joblib.load(
        MODEL_DIR / "feature_columns.pkl"
    )

    filtered_drivers_info = pd.read_csv(
        MODEL_DIR / "DATA" / "filtered_drivers_info.csv"
    )

    driver_abbrs = (
        filtered_drivers_info["Abbreviation"]
        .tolist()
    )

    schedule = fastf1.get_event_schedule(2024)
    schedule = schedule.drop(0)

    event_names = schedule["EventName"].tolist()
    event_rounds = schedule["RoundNumber"].tolist()

    race_name_to_round = dict(
        zip(event_names, event_rounds)
    )

    st.title("Podium Simulator")

    st.markdown(
        """
        Select the race and enter driver grid positions
        to predict the final standings.
        """
    )

    selected_race_name = st.selectbox(
        "Select Race",
        event_names
    )

    round_number = race_name_to_round[
        selected_race_name
    ]

    sorted_drivers = show_sortable_grid(
        driver_abbrs
    )

    grid_positions = {
        driver: position + 1
        for position, driver in enumerate(
            sorted_drivers
        )
    }

    grid_df = pd.DataFrame({
        "GridPosition": range(
            1,
            len(sorted_drivers) + 1
        ),
        "Driver": sorted_drivers
    })

    st.dataframe(
        grid_df,
        use_container_width=True,
        hide_index=True
    )

    if st.button("Predict Race Results"):

        GridPosition = [
            grid_positions[driver]
            for driver in driver_abbrs
        ]

        pred_gp_data = pd.DataFrame({
            "Round": [round_number] * 20,
            "Abbreviation": driver_abbrs,
            "GridPosition": GridPosition,
            "Points":
                filtered_drivers_info["Points"],
            "AvgQualiPosition":
                filtered_drivers_info[
                    "AvgQualiPosition"
                ],
            "AvgRacePosition":
                filtered_drivers_info[
                    "AvgRacePosition"
                ],
            "QualifyingScore":
                (
                    filtered_drivers_info[
                        "AvgQualiPosition"
                    ]
                    + GridPosition
                ) / 2
        })

        label_enc_driver = LabelEncoder()

        label_enc_driver.fit(driver_abbrs)

        pred_gp_data["Abbreviation"] = (
            label_enc_driver.transform(
                pred_gp_data["Abbreviation"]
            )
        )

        pred_gp_data = pred_gp_data[
            feature_columns
        ]

        X_scaled = scaler.transform(
            pred_gp_data
        )

        predicted_positions = (
            stack_model.predict(X_scaled)
        )

        pred_gp_data[
            "PredictedPosition"
        ] = predicted_positions

        results = (
            pred_gp_data
            .sort_values("PredictedPosition")
            .reset_index(drop=True)
        )

        results.index += 1

        results.rename_axis(
            "PredictedRank",
            inplace=True
        )

        results = results.reset_index()

        results["Driver_Abbreviation"] = (
            label_enc_driver.inverse_transform(
                results["Abbreviation"]
            )
        )

        st.success(
            f"""
            📊 Predicted Results for
            {selected_race_name}
            (Round {round_number})
            """
        )

        st.dataframe(
            results[
                [
                    "PredictedRank",
                    "Driver_Abbreviation"
                ]
            ],
            use_container_width=True
        )