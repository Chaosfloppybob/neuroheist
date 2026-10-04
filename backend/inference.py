import gc
import os
import resource
import urllib.request

import nibabel as nib
import numpy as np
import torch

from monai.transforms import NormalizeIntensity, Resize

from model import create_model


MODEL_PATH = os.path.join(os.path.dirname(__file__), "brats_mri_segmentation.pth")
MODEL_URL = os.getenv("MODEL_URL")

model = None
normalizer = NormalizeIntensity(nonzero=True, channel_wise=True)


def log_mem(tag):
    # Peak memory used by this process so far (Linux reports KB)
    peak_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    print(f"[mem] {tag}: peak {peak_mb:.0f} MB", flush=True)


def load_model():
    global model
    if model is not None:
        return model

    print("LOADING SEGMENTATION MODEL", flush=True)

    if not os.path.exists(MODEL_PATH):
        if not MODEL_URL:
            raise RuntimeError("Model file not found and MODEL_URL is not configured.")
        print("Downloading segmentation model...", flush=True)
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

    device = torch.device("cpu")
    net = create_model()
    state_dict = torch.load(MODEL_PATH, map_location=device)
    net.load_state_dict(state_dict)
    del state_dict

    net.to(device)
    net.eval()
    model = net

    gc.collect()
    print("SEGMENTATION MODEL READY", flush=True)
    return model


def segment_brain(input_path):
    log_mem("start")
    net = load_model()
    log_mem("model loaded")

    # nib.load only reads the header; no voxel data is in memory yet
    nii = nib.load(input_path)
    print("MRI shape:", nii.shape, flush=True)

    if len(nii.shape) != 4 or nii.shape[-1] != 4:
        raise ValueError(
            f"Expected a 4D NIfTI with 4 MRI channels, but received shape {nii.shape}."
        )

    original_shape = tuple(int(s) for s in nii.shape[:3])
    resize = Resize(spatial_size=(64, 128, 128), mode="trilinear")

    # Load, normalize and downsample ONE channel at a time.
    # Normalization is per-channel, so the result is identical to before.
    channels = []
    for c in range(4):
        ch = np.asarray(nii.dataobj[..., c], dtype=np.float32)  # [H,W,D]
        ch = np.transpose(ch, (2, 0, 1))[None]                  # [1,D,H,W]
        ch = normalizer(ch)
        ch = np.asarray(resize(ch), dtype=np.float32)           # [1,64,128,128]
        channels.append(ch)
        del ch
        gc.collect()
        log_mem(f"channel {c} done")

    image = np.concatenate(channels, axis=0)  # [4,64,128,128]
    del channels
    gc.collect()

    tensor = torch.from_numpy(image).unsqueeze(0)  # [1,4,64,128,128]
    print("Model input shape:", tuple(tensor.shape), flush=True)

    with torch.inference_mode():
        prediction = net(tensor)  # input already equals the ROI size

    prediction_mask = (torch.sigmoid(prediction) > 0.5)[0].numpy()
    del tensor, prediction, image
    gc.collect()
    log_mem("inference done")

    # 3 output channels -> BraTS labels
    tumor_mask = np.zeros(prediction_mask.shape[1:], dtype=np.uint8)
    tumor_mask[prediction_mask[0]] = 1  # TC
    tumor_mask[prediction_mask[1]] = 2  # WT
    tumor_mask[prediction_mask[2]] = 4  # ET
    del prediction_mask

    # [D,H,W] -> [H,W,D]
    tumor_mask = np.transpose(tumor_mask, (1, 2, 0))

    mask_tensor = torch.from_numpy(np.ascontiguousarray(tumor_mask)).float()
    mask_tensor = mask_tensor.unsqueeze(0).unsqueeze(0)
    mask_tensor = torch.nn.functional.interpolate(
        mask_tensor, size=original_shape, mode="nearest"
    )
    tumor_mask = mask_tensor[0, 0].numpy().astype(np.uint8)
    del mask_tensor
    gc.collect()

    output_dir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    mask_path = os.path.join(output_dir, "tumor_mask.nii.gz")

    # Same as before (np.eye(4)), so your viewer behaves the same.
    nib.save(nib.Nifti1Image(tumor_mask, np.eye(4)), mask_path)

    log_mem("saved")
    print("Tumor mask saved:", mask_path, flush=True)
    return mask_path