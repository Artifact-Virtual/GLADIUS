// workers/dataWorker.js
// Artifact-standard: Web Worker for parallel data processing (zero-copy, transferable objects)

self.onmessage = function(e) {
  // e.data: { type: 'process', payload: ArrayBuffer }
  if (e.data.type === 'process') {
    const arr = new Float32Array(e.data.payload);
    // Example: Compute min/max/mean (can be extended)
    let min = Infinity, max = -Infinity, sum = 0;
    for (let v of arr) {
      if (v < min) min = v;
      if (v > max) max = v;
      sum += v;
    }
    const mean = arr.length ? sum / arr.length : 0;
    self.postMessage({ min, max, mean, length: arr.length });
  }
};
