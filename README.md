# BIDS Conversion Pipeline

This repository contains a complete and modular workflow for converting EEG EDF recordings into a fully structured BIDS dataset.
All dataset-level, subject-level, and task-specific metadata are stored in external JSON configuration files, allowing easy editing and reproducibility.

## Project Structure

```
project/
│
├── info.csv                     # Participant-to-file mapping table
├── metadata.json                # Combined dataset + EEG general metadata
├── task_details.json            # Task-specific metadata (description, instructions)
├── convert_to_bids.py           # Main conversion script
├── EDF/                         # (Optional) folder containing EDF files
└── BIDS/                        # BIDS dataset output (auto-generated)
```

## Files Overview

**1. info.csv**

A table describing each EDF recording:

| Column           | Required | Description                              |
| ---------------- | -------- | ---------------------------------------- |
| `edf_file`       | ✔        | Path or filename of the EDF file         |
| `participant_id` | ✔        | Participant number (integer)             |
| `task`           | ✔        | Task label (must match JSON definitions) |
| `age`            | optional | Age of participant                       |
| `sex`            | optional | Sex (M/F/Other)                          |
| `hand`           | optional | Handedness                               |
| `weight`         | optional | Weight (kg)                              |
| `height`         | optional | Height (cm)                              |

**2. metadata.json**

Contains two sections:

* `dataset:` metadata for dataset_description.json

* `eeg_general:` metadata added to all *_eeg.json sidecar files

Example:
```
{
    "dataset": {
        "Name": "Stimulus_artifact_ASSR",
        "Authors": ["Jan Strobl"],
        "License": "CC-BY 4.0",
        "Acknowledgements": "NIMH Klecany Clinical Research Program",
        "Funding": "None",
        "HowToAcknowledge": "Please cite the project authors."
    },

    "eeg_general": {
        "EEGReference": "Cz",
        "EEGGround": "COM",
        "EEGPlacementScheme": "GSN-HydroCel-257",
        "Manufacturer": "Electrical Geodesics Inc. (EGI)",
        "ManufacturersModelName": "MagStim EGI NetAmp GES 400 HdEEG",
        "SoftwareVersions": "Net Station 5.4.2",
        "DeviceSerialNumber": "2014-0131",
        "SubjectArtefactDescription": "Stimulus, muscle, eye, cardiac, line noise, bad electrode",
        "InstitutionName": "National Institute of Mental Health, Klecany"
    }
}
```

**3. task_details.json**

Holds task-specific descriptions and instructions, matched by filename ending:

``` ňňňňňǩǩǩ
{
    "Headphones_eeg.json": {
        "TaskDescription": "Subjects sat still ... headphones.",
        "Instructions": "The subject was asked to ..."
    },
    "Speakers_eeg.json": {
        "TaskDescription": "Subjects sat ... speakers.",
        "Instructions": "The subject was asked to ..."
    },
    "SpeakersArtifact_eeg.json": {
        "TaskDescription": "Subjects produced muscle artifacts ...",
        "Instructions": "The subject was asked to randomly clench ..."
    }
}
```

## How to Run

1. Install dependencies:

`pip install mne mne-bids pandas`

2. Place:

* Your EDF files

* info.csv

* metadata.json

* task_details.json

in the same directory as the script.

3. Run:

`python convert_to_bids.py`

4. The output will appear in:

`./BIDS/`


## Resulting BIDS Outputs

The script generates:

* dataset_description.json

* participants.tsv

* sub-xxx/
  * eeg/
    * sub-xxx_task-yyy_eeg.edf
	* sub-xxx_task-yyy_eeg.json (auto-updated)
	* sub-xxx_task-yyy_channels.tsv
	* sub-xxx_task-yyy_electrodes.tsv (if applicable)

All metadata is consistently injected and validated through JSON merging.



