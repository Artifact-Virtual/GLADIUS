
import { GoogleGenAI, LiveServerMessage, Modality, Blob } from '@google/genai';

function decode(base64: string) {
  const binaryString = atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes;
}

function encode(bytes: Uint8Array) {
  let binary = '';
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

async function decodeAudioData(
  data: Uint8Array,
  ctx: AudioContext,
  sampleRate: number,
  numChannels: number,
): Promise<AudioBuffer> {
  const dataInt16 = new Int16Array(data.buffer);
  const frameCount = dataInt16.length / numChannels;
  const buffer = ctx.createBuffer(numChannels, frameCount, sampleRate);
  for (let channel = 0; channel < numChannels; channel++) {
    const channelData = buffer.getChannelData(channel);
    for (let i = 0; i < frameCount; i++) {
      channelData[i] = dataInt16[i * numChannels + channel] / 32768.0;
    }
  }
  return buffer;
}

export class LiveService {
  private ai: any;
  private session: any;
  private inputAudioContext: AudioContext | null = null;
  private outputAudioContext: AudioContext | null = null;
  private outputNode: GainNode | null = null;
  private nextStartTime = 0;
  private sources = new Set<AudioBufferSourceNode>();
  private analyzer: AnalyserNode | null = null;
  private amplitudeData: Uint8Array | null = null;
  public lastActivityTime: number = Date.now();

  public onTranscription: (text: string, isUser: boolean) => void = () => {};
  public onThinking: (isThinking: boolean) => void = () => {};
  public onAmplitude: (amp: number) => void = () => {};
  public onUserInputDetected: () => void = () => {};

  constructor() {
    this.ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  }

  public async connect() {
    if (this.session) return;

    this.inputAudioContext = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
    this.outputAudioContext = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });
    this.outputNode = this.outputAudioContext.createGain();
    this.outputNode.connect(this.outputAudioContext.destination);

    this.analyzer = this.outputAudioContext.createAnalyser();
    this.analyzer.fftSize = 256;
    this.outputNode.connect(this.analyzer);
    this.amplitudeData = new Uint8Array(this.analyzer.frequencyBinCount);

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    const sessionPromise = this.ai.live.connect({
      model: 'gemini-2.5-flash-native-audio-preview-12-2025',
      callbacks: {
        onopen: () => {
          const source = this.inputAudioContext!.createMediaStreamSource(stream);
          const scriptProcessor = this.inputAudioContext!.createScriptProcessor(4096, 1, 1);
          scriptProcessor.onaudioprocess = (e) => {
            const inputData = e.inputBuffer.getChannelData(0);
            const pcmBlob = this.createBlob(inputData);
            sessionPromise.then((s: any) => s.sendRealtimeInput({ media: pcmBlob }));
          };
          source.connect(scriptProcessor);
          scriptProcessor.connect(this.inputAudioContext!.destination);
          this.onThinking(false);
        },
        onmessage: async (message: LiveServerMessage) => {
          if (message.serverContent?.outputTranscription) {
            this.lastActivityTime = Date.now();
            this.onTranscription(message.serverContent.outputTranscription.text, false);
          } else if (message.serverContent?.inputTranscription) {
            const text = message.serverContent.inputTranscription.text;
            if (text && text.trim().length > 0) {
              this.lastActivityTime = Date.now();
              this.onUserInputDetected();
              this.onTranscription(text, true);
            }
          }

          if (message.serverContent?.modelTurn?.parts?.[0]?.inlineData?.data) {
            this.lastActivityTime = Date.now();
            this.playAudio(message.serverContent.modelTurn.parts[0].inlineData.data);
          }

          if (message.serverContent?.turnComplete || message.serverContent?.modelTurn) {
            this.onThinking(false);
          }
        },
        onerror: (e: any) => {
          console.error('Live error', e);
        },
        onclose: () => { this.session = null; },
      },
      config: {
        responseModalities: [Modality.AUDIO],
        speechConfig: {
          voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Puck' } },
        },
        systemInstruction: 'You are a sentient swarm. Speak briefly and ethereally.',
        outputAudioTranscription: {},
        inputAudioTranscription: {},
      },
    });

    this.session = await sessionPromise;
    this.updateAmplitude();
  }

  private updateAmplitude() {
    if (!this.analyzer || !this.amplitudeData) return;
    this.analyzer.getByteFrequencyData(this.amplitudeData);
    let sum = 0;
    for (let i = 0; i < this.amplitudeData.length; i++) sum += this.amplitudeData[i];
    this.onAmplitude(sum / (this.amplitudeData.length * 128));
    requestAnimationFrame(() => this.updateAmplitude());
  }

  private async playAudio(base64: string) {
    if (!this.outputAudioContext || !this.outputNode) return;
    this.nextStartTime = Math.max(this.nextStartTime, this.outputAudioContext.currentTime);
    const audioBuffer = await decodeAudioData(decode(base64), this.outputAudioContext, 24000, 1);
    const source = this.outputAudioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(this.outputNode);
    source.start(this.nextStartTime);
    this.nextStartTime += audioBuffer.duration;
    this.sources.add(source);
    source.onended = () => this.sources.delete(source);
  }

  private createBlob(data: Float32Array): Blob {
    const int16 = new Int16Array(data.length);
    for (let i = 0; i < data.length; i++) int16[i] = data[i] * 32768;
    return { data: encode(new Uint8Array(int16.buffer)), mimeType: 'audio/pcm;rate=16000' };
  }

  public disconnect() {
    this.session?.close();
    this.session = null;
    this.sources.forEach(s => s.stop());
    this.sources.clear();
    this.inputAudioContext?.close();
    this.outputAudioContext?.close();
  }
}
