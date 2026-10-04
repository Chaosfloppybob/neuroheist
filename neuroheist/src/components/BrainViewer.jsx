import { useEffect, useRef, useState } from "react";
import { Niivue } from "@niivue/niivue";
import "./BrainViewer.css";

// Used when no uploaded file is passed in. Put mni152.nii.gz in your public/ folder.
const SAMPLE_URL = "/mni152.nii.gz";
const SAMPLE_NAME = "mni152.nii.gz";

export default function BrainViewer({ file, maskUrl }) {
  const canvasRef = useRef(null);
  const nvRef = useRef(null); // the NiiVue instance
  const readyRef = useRef(null); // resolves once NiiVue is attached to the canvas
  const [status, setStatus] = useState("loading"); // loading | ready | error

  // Create the viewer once
  useEffect(() => {
    // React StrictMode runs effects twice in development; this stops a second viewer
    if (nvRef.current) return;

    const nv = new Niivue({
      backColor: [0, 0, 0, 0], // transparent, so your glass card shows through
      show3Dcrosshair: false,
    });
    nvRef.current = nv;

    readyRef.current = nv.attachToCanvas(canvasRef.current).then(() => {
      nv.setSliceType(nv.sliceTypeRender); // 3D view instead of 2D slices
    });
  }, []);

  // Load the scan + tumor mask (re-runs if either changes)
  useEffect(() => {
    let cancelled = false;

    async function load() {
      setStatus("loading");

      // An uploaded File becomes a temporary URL NiiVue can read.
      // The name matters: NiiVue checks the .nii / .nii.gz extension to know the format.
      const url = file ? URL.createObjectURL(file) : SAMPLE_URL;
      const name = file ? file.name : SAMPLE_NAME;

      const volumes = [{ url, name }]; // first volume = the brain

      // Second volume = the tumor mask from the backend, drawn on top in red.
      // cal_min 0.5 hides the 0 (no tumor) voxels so only the tumor is colored.
      if (maskUrl) {
        volumes.push({
          url: maskUrl,
          name: maskUrl.split("/").pop().split("?")[0] || "tumor_mask.nii.gz",
          colormap: "red",
          opacity: 0.85,
          cal_min: 0.5,
          cal_max: 1,
        });
      }

      try {
        await readyRef.current;
        await nvRef.current.loadVolumes(volumes); // replaces any previous scan
        if (!cancelled) setStatus("ready");
      } catch (err) {
        console.error("BrainViewer failed to load scan:", err);
        if (!cancelled) setStatus("error");
      } finally {
        if (file) URL.revokeObjectURL(url); // free the temporary URL
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [file, maskUrl]);

  return (
    <div className="brain-viewer">
      <canvas ref={canvasRef} />
      {status !== "ready" && (
        <p className="brain-viewer__status">
          {status === "loading" ? "Loading scan…" : "Couldn't load this scan."}
        </p>
      )}
    </div>
  );
}
