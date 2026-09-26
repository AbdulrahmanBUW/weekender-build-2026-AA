// Captures mic audio, downsamples to 16 kHz mono, emits Int16 PCM chunks (~100 ms).
class MicDownsampler extends AudioWorkletProcessor {
  constructor() {
    super();
    this.ratio = sampleRate / 16000;
    this.buffer = [];
    this.pos = 0;
  }
  process(inputs) {
    const ch = inputs[0] && inputs[0][0];
    if (!ch) return true;
    // simple averaging decimator (good enough for speech)
    for (let i = 0; i < ch.length; i++) {
      this.pos += 1;
      this.acc = (this.acc || 0) + ch[i];
      this.n = (this.n || 0) + 1;
      if (this.pos >= this.ratio) {
        this.buffer.push(this.acc / this.n);
        this.pos -= this.ratio; this.acc = 0; this.n = 0;
      }
    }
    if (this.buffer.length >= 1600) {
      const out = new Int16Array(this.buffer.length);
      for (let i = 0; i < this.buffer.length; i++) {
        const s = Math.max(-1, Math.min(1, this.buffer[i]));
        out[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
      }
      this.port.postMessage(out.buffer, [out.buffer]);
      this.buffer = [];
    }
    return true;
  }
}
registerProcessor('mic-downsampler', MicDownsampler);
