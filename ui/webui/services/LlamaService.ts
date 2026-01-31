
import { AISettings } from '../types';

export class LlamaService {
  private settings: AISettings;
  private recognition: any = null;
  private isListening = false;
  private lastActivityTime = Date.now();

  public onTranscription: (text: string, isUser: boolean) => void = () => {};
  public onThinking: (isThinking: boolean) => void = () => {};
  public onAmplitude: (amp: number) => void = () => {};
  public onUserInputDetected: () => void = () => {};

  constructor(settings: AISettings) {
    this.settings = settings;
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      
      this.recognition.onresult = (event: any) => {
        const result = event.results[event.results.length - 1];
        if (result.isFinal) {
          const text = result[0].transcript;
          this.onTranscription(text, true);
          this.onUserInputDetected();
          this.sendMessage(text);
          this.lastActivityTime = Date.now();
        }
      };
      
      this.recognition.onerror = (event: any) => {
        console.warn('Speech recognition error:', event.error);
      };
    }
  }

  public async connect() {
    if (this.recognition && !this.isListening) {
      try {
        this.recognition.start();
        this.isListening = true;
      } catch (e) {
        console.warn('Could not start speech recognition:', e);
      }
    }
  }

  public disconnect() {
    if (this.recognition && this.isListening) {
      try {
        this.recognition.stop();
      } catch (e) {
        // Ignore errors on stop
      }
      this.isListening = false;
    }
  }

  public getLastActivityTime() {
    return this.lastActivityTime;
  }

  private async sendMessage(text: string) {
    this.onThinking(true);
    this.onAmplitude(0.5);  // Show activity
    
    try {
      const response = await fetch(`${this.settings.llamaEndpoint}/v1/chat/completions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: this.settings.llamaModelPath,
          messages: [{ role: 'user', content: text }],
          stream: false
        }),
        signal: AbortSignal.timeout(30000)  // 30s timeout
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      const reply = data.choices?.[0]?.message?.content || 'Neural pathways processing...';
      this.onTranscription(reply, false);
      this.onAmplitude(0.8);  // Response activity
      
      // Use Web Speech Synthesis for the "voice" of Llama
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(reply);
        utterance.rate = 0.9;
        utterance.pitch = 0.8;
        window.speechSynthesis.speak(utterance);
      }
      
    } catch (error) {
      console.error('Llama Error:', error);
      // Friendly message when native model isn't available
      this.onTranscription("Awaiting neural core initialization. Voice interface ready.", false);
    } finally {
      this.onThinking(false);
      this.onAmplitude(0);
      this.lastActivityTime = Date.now();
    }
  }
}
