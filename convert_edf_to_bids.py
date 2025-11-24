import os
import os.path as op
import mne
import shutil
import pandas as pd
import json
from mne_bids import BIDSPath, write_raw_bids, make_dataset_description


# ----------------------------------------------------------
# Load external JSON metadata files
# ----------------------------------------------------------
def load_metadata(json_file):
    """Load a JSON file safely."""
    if not op.exists(json_file):
        raise FileNotFoundError(f"Metadata file not found: {json_file}")

    with open(json_file, "r") as f:
        return json.load(f)


# ----------------------------------------------------------
# Convert EDF → BIDS
# ----------------------------------------------------------
def convert_edf_to_bids(edf_file, bids_root, subject, session=None, task="default", overwrite=False):
    raw = mne.io.read_raw_edf(edf_file, preload=True)
    raw.info["line_freq"] = 50

    bids_path = BIDSPath(subject=subject, session=session, task=task, root=bids_root)

    write_raw_bids(
        raw,
        bids_path,
        overwrite=overwrite,
        allow_preload=True,
        format="EDF"
    )

    print(f"Converted {edf_file} → BIDS (sub-{subject}, task-{task})")


# ----------------------------------------------------------
# Update EEG JSON sidecar files
# ----------------------------------------------------------
def update_eeg_json_files(bids_root, general_metadata, task_details):
    """
    Traverses the BIDS directory and appends metadata into *_eeg.json files.
    """
    print("\nUpdating EEG JSON metadata...\n")

    for root, dirs, files in os.walk(bids_root):
        if "eeg" not in root:
            continue

        for file in files:
            if not file.endswith("_eeg.json"):
                continue

            eeg_json_path = op.join(root, file)
            print(f"Processing: {eeg_json_path}")

            # Load existing JSON
            with open(eeg_json_path, "r") as f:
                try:
                    existing = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON: {eeg_json_path}")
                    continue

            # Add task-specific metadata
            for ending, updates in task_details.items():
                if file.endswith(ending):
                    existing.update(updates)
                    break

            # Add general metadata
            existing.update(general_metadata)

            # Save back
            with open(eeg_json_path, "w") as f:
                json.dump(existing, f, indent=4)


# ----------------------------------------------------------
# MAIN EXECUTION
# ----------------------------------------------------------
def main():
    print("\n===== BIDS Conversion Pipeline =====\n")

    # -------- Paths --------
    data_dir = os.getcwd()
    csv_path = op.join(data_dir, "info.csv")
    bids_root = op.join(data_dir, "BIDS")

    # -------- Load metadata from external JSON files --------
    metadata = load_metadata(op.join(data_dir, "general_metadata.json"))
    dataset_meta = metadata["dataset"]
    general_metadata = metadata["eeg_general"]
    task_details = load_metadata(op.join(data_dir, "task_details.json"))

    # -------- Load participant mapping CSV --------
    mapping_df = pd.read_csv(csv_path)

    required_columns = {"edf_file", "participant_id", "task"}
    optional_columns = {"age", "sex", "hand", "weight", "height"}

    if not required_columns.issubset(mapping_df.columns):
        raise ValueError(f"CSV must contain the following columns: {required_columns}")

    available_optional_columns = optional_columns.intersection(mapping_df.columns)

    # -------- Re-create BIDS root folder --------
    if op.exists(bids_root):
        shutil.rmtree(bids_root)
    os.makedirs(bids_root, exist_ok=True)

    # -------- Convert each participant --------
    for _, row in mapping_df.iterrows():
        edf_file = row["edf_file"]
        participant_id = int(row["participant_id"])
        task = row["task"]

        metadata_row = {col: row[col] for col in available_optional_columns}

        edf_path = op.join(data_dir, edf_file)
        if not op.exists(edf_path):
            print(f"Warning: Missing file {edf_file} → skipping.")
            continue

        bids_sub = f"{participant_id:03d}"

        convert_edf_to_bids(
            edf_path,
            bids_root,
            subject=bids_sub,
            task=task,
            overwrite=True,
        )

        # --- Update participants.tsv ---
        participants_tsv = op.join(bids_root, "participants.tsv")

        if op.exists(participants_tsv):
            df = pd.read_csv(participants_tsv, sep="\t")
        else:
            df = pd.DataFrame(columns=["participant_id"] + list(optional_columns))

        rowdata = {"participant_id": f"sub-{bids_sub}", **metadata_row}

        if rowdata["participant_id"] in df["participant_id"].values:
            df.loc[df["participant_id"] == rowdata["participant_id"], rowdata.keys()] = rowdata.values()
        else:
            df = pd.concat([df, pd.DataFrame([rowdata])], ignore_index=True)

        df.to_csv(participants_tsv, sep="\t", index=False, na_rep="n/a")

    # -------- Create dataset_description.json --------
    make_dataset_description(
    path=bids_root,
    name=dataset_meta["Name"],
    authors=dataset_meta["Authors"],
    data_license=dataset_meta["License"],
    acknowledgements=dataset_meta.get("Acknowledgements"),
    funding=dataset_meta.get("Funding"),
    how_to_acknowledge=dataset_meta.get("HowToAcknowledge"),
    overwrite=True
	)


    # -------- Update all *_eeg.json files --------
    update_eeg_json_files(bids_root, general_metadata, task_details)

    print("\n===== Conversion complete! =====\n")


# ----------------------------------------------------------
if __name__ == "__main__":
    main()

