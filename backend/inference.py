import os
import urllib.request

import nibabel as nib
import numpy as np
import torch

from monai.inferers import SlidingWindowInferer
from monai.transforms import NormalizeIntensity
from monai.transforms import Resize

from model import create_model


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "brats_mri_segmentation.pth"
)

MODEL_URL = os.getenv("MODEL_URL")


model = None
normalizer = NormalizeIntensity(
    nonzero=True,
    channel_wise=True
)

inferer = SlidingWindowInferer(
    roi_size=(64, 128, 128),
    sw_batch_size=1,
    overlap=0.25
)


def load_model():
    global model

    if model is not None:
        return model

    print("LOADING SEGMENTATION MODEL")

    if not os.path.exists(MODEL_PATH):
        if not MODEL_URL:
            raise RuntimeError(
                "Model file not found and MODEL_URL is not configured."
            )

        print("Downloading segmentation model...")

        urllib.request.urlretrieve(
            MODEL_URL,
            MODEL_PATH
        )

        print("Model download complete.")

    device = torch.device("cpu")

    model = create_model()

    state_dict = torch.load(
        MODEL_PATH,
        map_location=device
    )

    model.load_state_dict(state_dict)

    model.to(device)
    model.eval()

    print("SEGMENTATION MODEL READY")

    return model


def segment_brain(input_path):
    print("STARTING SEGMENTATION")
    model = load_model()
    nii = nib.load(input_path)

    image = nii.get_fdata().astype(np.float32)
    print("MRI LOADED")
    print("MRI shape:", image.shape)
    print("MRI memory MB:", image.nbytes / 1024 / 1024)
    original_shape = image.shape[:3]
    original_affine = nii.affine.copy()

    print("Original MRI shape:", image.shape)

    if image.ndim != 4:
        raise ValueError(
            "Expected a 4D NIfTI containing 4 MRI modalities."
        )

    if image.shape[-1] != 4:
        raise ValueError(
            f"Expected 4 MRI channels, but received shape {image.shape}."
        )

    # [D,H,W,C] -> [C,D,H,W]
    image = np.transpose(image, (3, 2, 0, 1))

    image = normalizer(image)

    # Downsample for much faster CPU inference
    resize = Resize(
        spatial_size=(64, 128, 128),
        mode="trilinear"
    )

    image = resize(image)

    tensor = torch.from_numpy(
        np.asarray(image, dtype=np.float32)
    )

    tensor = tensor.unsqueeze(0)

    print("Model input shape:", tensor.shape)
    print("STARTING MODEL INFERENCE")
    with torch.no_grad():

        prediction = inferer(
            inputs=tensor,
            network=model
        )

    probabilities = torch.sigmoid(prediction)

    prediction_mask = probabilities > 0.5

    prediction_mask = prediction_mask[0].cpu().numpy()

    # Convert 3 output channels to BraTS labels
    tumor_mask = np.zeros(
        prediction_mask.shape[1:],
        dtype=np.uint8
    )

    # TC
    tumor_mask[prediction_mask[0]] = 1

    # WT
    tumor_mask[prediction_mask[1]] = 2

    # ET
    tumor_mask[prediction_mask[2]] = 4

    # [D,H,W] -> [H,W,D]
    tumor_mask = np.transpose(
        tumor_mask,
        (1, 2, 0)
    )
    mask_tensor = torch.from_numpy(tumor_mask).float()
    mask_tensor = mask_tensor.unsqueeze(0).unsqueeze(0)

    mask_tensor = torch.nn.functional.interpolate(
        mask_tensor,
        size=original_shape,
        mode="nearest"
    )

    tumor_mask = mask_tensor[0, 0].numpy().astype(np.uint8)
    mask_nii = nib.Nifti1Image(
        tumor_mask,
        np.eye(4)
    )

    OUTPUT_DIR = os.path.join(
        os.path.dirname(__file__),
        "outputs"
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    mask_path = os.path.join(
        OUTPUT_DIR,
        "tumor_mask.nii.gz"
    )

    nib.save(
        mask_nii,
        mask_path
    )

    print("Tumor mask saved:", mask_path)

    return mask_path