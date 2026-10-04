import { useEffect, useRef, useState } from "react";
import { Niivue } from "@niivue/niivue";
import "./BrainViewer.css";

// Used when no uploaded file is passed in. Put mni152.nii.gz in your public/ folder.
const SAMPLE_URL = "/mni152.nii.gz";
const SAMPLE_NAME = "mni152.nii.gz";

export default function BrainViewer({ file, maskUrl, brainOpacity = 1, tumorOpacity = 0.85 }) {
  const canvasRef = useRef(null);
  const nvRef = useRef(null); // the NiiVue instance
  const readyRef = useRef(null); // resolves once NiiVue is attached to the canvas
  const loadIdRef = useRef(0); // increases with every load; used to skip outdated loads
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
        // Hide the 2D slice planes in the 3D rendering.
      nv.opts.show3Dcrosshair = false;
      nv.opts.show3DRender = true;
      nv.setSliceType(nv.sliceTypeRender);
      nv.setRenderAzimuthElevation(0, 0);
    });
  }, []);

  // Load the scan + tumor mask (re-runs if either changes)
  useEffect(() => {
    // In development, React StrictMode runs this effect twice in a row. Two overlapping
    // loadVolumes calls on the same viewer can scramble each other (the tumor layer gets
    // lost), so each run gets an id and only the newest one is allowed to load.
    const loadId = ++loadIdRef.current;
    const isOutdated = () => loadId !== loadIdRef.current;

    async function load() {
      setStatus("loading");
      await readyRef.current;
      if (isOutdated()) return; // a newer load already started; let that one do the work

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
          colormap: "violet",
          opacity: 0.8,
          cal_min: 0.5,
          cal_max: 1,
        });
      }

      try {
        await nvRef.current.loadVolumes(volumes); // replaces any previous scan
        if (!isOutdated()) setStatus("ready");
      } catch (err) {
        console.error("BrainViewer failed to load scan:", err);
        if (!isOutdated()) setStatus("error");
      } finally {
        if (file) URL.revokeObjectURL(url); // free the temporary URL
      }
    }

    load();
  }, [file, maskUrl]);

  // Apply the Layers panel settings. Re-runs when a slider/toggle changes,
  // and again after each load finishes (status becomes "ready").
  useEffect(() => {
    const nv = nvRef.current;
    if (status !== "ready" || !nv || nv.volumes.length === 0) return;
    nv.setOpacity(0, brainOpacity); // volume 0 = brain
    if (nv.volumes.length > 1) nv.setOpacity(1, tumorOpacity); // volume 1 = tumor
  }, [brainOpacity, tumorOpacity, status]);

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