from config import *
from torch.utils.data import DataLoader
import random

random.seed(42)

def create_split():
    patient_dirs = []
    train_samples = []
    val_samples = []
    train_split = 0.8

    for patient_dir in TRAIN_DATA_DIR.iterdir():
        if patient_dir.is_dir():
            patient_dirs.append(patient_dir)
    random.shuffle(patient_dirs)

    train_size = int(len(patient_dirs) * train_split)
    train_patients = patient_dirs[:train_size]
    val_patients = patient_dirs[train_size:]

    for patient in train_patients:
        gt_files = list(patient.rglob("*_gt.nii.gz"))
        for gt_file in gt_files:
            image = gt_file.name.replace("_gt.nii.gz", ".nii.gz")
            image_path = patient / image
            if image_path.exists():
                train_samples.append((image_path, gt_file))

    for patient in val_patients:
        gt_files = list(patient.rglob("*_gt.nii.gz"))
        for gt_file in gt_files:
            image = gt_file.name.replace("_gt.nii.gz", ".nii.gz")
            image_path = patient / image
            if image_path.exists():
                val_samples.append((image_path, gt_file))