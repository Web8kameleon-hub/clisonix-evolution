export class RingBuffer {
  constructor(capacity=1024){
    this.buf = new Array(capacity);
    this.cap = capacity;
    this.head = 0; // next write
    this.size = 0;
  }
  push(v){
    this.buf[this.head] = v;
    this.head = (this.head + 1) % this.cap;
    if (this.size < this.cap) this.size++;
  }
  toArray(){
    const out = new Array(this.size);
    const start = (this.head - this.size + this.cap) % this.cap;
    for (let i=0;i<this.size;i++){
      out[i] = this.buf[(start+i)%this.cap];
    }
    return out;
  }
  last(n=1){
    if (this.size===0) return [];
    const k = Math.min(n, this.size);
    const out = new Array(k);
    let idx = (this.head - 1 + this.cap) % this.cap;
    for (let i=0;i<k;i++){
      out[i] = this.buf[idx];
      idx = (idx - 1 + this.cap) % this.cap;
    }
    return out.reverse();
  }
}
