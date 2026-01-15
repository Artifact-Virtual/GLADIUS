// test/analyzer.test.js
// Artifact-standard: Minimal test for analyzer.js AI model and worker integration

import { ArtifactAIModel } from '../ai.model.js';

async function testAIModel() {
  const model = new ArtifactAIModel();
  await model.load('model.onnx');
  const result = await model.infer([1, 2, 3, 4]);
  console.assert(result.result === 'stub', 'AI model stub inference failed');
}

testAIModel().then(() => console.log('AI model test passed'));

// Web Worker test (if supported)
if (typeof Worker !== 'undefined') {
  const worker = new Worker('../workers.dataWorker.js');
  worker.onmessage = (e) => {
    console.assert(typeof e.data.mean === 'number', 'Worker mean not computed');
    console.log('Worker test passed');
    worker.terminate();
  };
  const arr = new Float32Array([1, 2, 3, 4]);
  worker.postMessage({ type: 'process', payload: arr.buffer }, [arr.buffer]);
}
