import pandas as pd
import os

participant_id = input("Enter participant ID (e.g., 001): ")

blocks = ["control", "low", "high"]
all_data = []

for block in blocks:
    file_path = f"data/behavioral_data/{block}/{participant_id}_results_block.csv"
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        all_data.append(df)
    else:
        print(f"did not find data for block '{block}' at {file_path}")

if len(all_data) == 0:
    print(f"No data found for participant {participant_id}")
else:
    combined_df = pd.concat(all_data, ignore_index=True)
    winning_trial = combined_df.sample(n=1).iloc[0]
    final_value = winning_trial["final_value"]

    # 7. Print the official payout receipt!
    print("PAYOUT DRAW")
    print(f"Participant    : {participant_id}")
    print(f"PAYOUT: {round(final_value, 2)} DKK")
