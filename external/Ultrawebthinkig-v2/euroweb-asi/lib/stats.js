export const mean = arr => arr.reduce((a,b)=>a+b,0)/Math.max(arr.length,1);
export const std = arr => {
  if (arr.length<=1) return 0;
  const m = mean(arr);
  const v = mean(arr.map(x => (x-m)*(x-m)));
  return Math.sqrt(v);
};
export const zscore = (x, m, s) => s>0 ? (x-m)/s : 0;
export const percentile = (arr, p=0.5) => {
  if (!arr.length) return 0;
  const sorted = [...arr].sort((a,b)=>a-b);
  const idx = Math.min(sorted.length-1, Math.max(0, Math.floor(p*(sorted.length-1))));
  return sorted[idx];
};
export const iqrAnomaly = (arr, k=1.5) => {
  if (arr.length<8) return {low:-Infinity, high:Infinity};
  const q1 = percentile(arr, 0.25);
  const q3 = percentile(arr, 0.75);
  const iqr = q3 - q1;
  return { low: q1 - k*iqr, high: q3 + k*iqr };
};
export class EWMA {
  constructor(alpha=0.2, initial=0){
    this.alpha = alpha; this.val = initial; this.init=false;
  }
  next(x){
    if(!this.init){ this.val = x; this.init=true; return this.val; }
    this.val = this.alpha * x + (1-this.alpha) * this.val;
    return this.val;
  }
}
