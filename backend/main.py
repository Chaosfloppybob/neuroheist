import os
import tempfile

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from inference import segment_brain


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "NeuroHeist backend is running"
    }


@app.post("/upload")
async def upload_scan(
    file: UploadFile = File(...)
):
    # Make sure the uploaded file is NIfTI.
    filename = file.filename.lower()

    if not (
        filename.endswith(".nii")
        or filename.endswith(".nii.gz")
    ):
        return {
            "error": "Only .nii and .nii.gz files are supported."
        }

    # Save uploaded file temporarily.
    suffix = ".nii.gz" if filename.endswith(".nii.gz") else ".nii"

    input_file = tempfile.NamedTemporaryFile(
        suffix=suffix,
        delete=False
    )

    input_path = input_file.name

    try:
        contents = await file.read()

        input_file.write(contents)
        input_file.close()

        # Run the actual AI segmentation.
        mask_path = segment_brain(input_path)

        return {
            "message": "Scan segmented successfully.",
            "tumor_mask": f"/tumor-mask/{os.path.basename(mask_path)}"
        }

    except Exception as error:
        input_file.close()

        print("SEGMENTATION ERROR:")
        print(error)

        return {
            "error": str(error)
        }


@app.get("/tumor-mask/{filename}")
def get_tumor_mask(filename: str):
    path = os.path.join(
        os.path.dirname(__file__),
        "outputs",
        filename
    )
    if not os.path.exists(path):
        return {
            "error": "Tumor mask not found."
        }

    return FileResponse(
        path,
        media_type="application/gzip",
        filename=filename
    )