# BIDS Conversion Pipeline

This repository contains a workflow for converting EEG EDF recordings into a BIDS dataset.
All dataset-level, subject-level, and task-specific metadata are stored in external JSON and CSV configuration files.

## Project Structure

```
project/
│
├── info.csv                     # Participant-to-file mapping table
├── metadata.json                # Combined dataset + EEG general metadata
├── task_details.json            # Task-specific metadata (description, instructions)
├── convert_to_bids.py           # Main conversion script
├── *.edf                        # EDF files
└── BIDS/                        # BIDS dataset output (auto-generated)
```

## Dependencies
```
Python 3.10.12
mne==1.9.0
mne-bids==0.16.0
pandas==2.2.3
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

``` 
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
    
---

The script uses MNE-BIDS and a module of MNE-BIDS dedicated to EEG:

Appelhoff, S., Sanderson, M., Brooks, T., Vliet, M., Quentin, R., Holdgraf, C., Chaumon, M., Mikulan, E., Tavabi, K., Höchenberger, R., Welke, D., Brunner, C., Rockhill, A., Larson, E., Gramfort, A., & Jas, M. (2019). MNE-BIDS: Organizing electrophysiological data into the BIDS format and facilitating their analysis. Journal of Open Source Software, 4:1896. DOI: 10.21105/joss.01896

Pernet, C.R., Appelhoff, S., Gorgolewski, K.J. et al. EEG-BIDS, an extension to the brain imaging data structure for electroencephalography. Sci Data 6, 103 (2019). https://doi.org/10.1038/s41597-019-0104-8
