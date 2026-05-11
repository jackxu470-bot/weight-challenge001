import type { WeightLog } from '../lib/storage';

type Props = { logs: WeightLog[]; initialWeight: number };

export default function WeightChart({ logs, initialWeight }: Props) {
  const sorted = [...logs].sort((a, b) => a.loggedDate.localeCompare(b.loggedDate));

  if (sorted.length < 2) return null;

  const w = 300;
  const h = 160;
  const pad = { top: 10, right: 16, bottom: 24, left: 40 };
  const pw = w - pad.left - pad.right;
  const ph = h - pad.top - pad.bottom;

  const values = [initialWeight, ...sorted.map((l) => l.weight)];
  const minV = Math.min(...values) - 0.5;
  const maxV = Math.max(...values) + 0.5;
  const range = maxV - minV || 1;

  const points = [{ date: '初始', weight: initialWeight }, ...sorted.map((l) => ({ date: l.loggedDate, weight: l.weight }))];

  const getX = (i: number) => pad.left + (i / (points.length - 1)) * pw;
  const getY = (v: number) => pad.top + ((maxV - v) / range) * ph;

  const lineD = points.map((p, i) => `${i === 0 ? 'M' : 'L'}${getX(i)},${getY(p.weight)}`).join(' ');

  return (
    <svg viewBox={`0 0 ${w} ${h}`} width="100%" style={{ maxWidth: w }}>
      {/* y-axis labels */}
      {[minV, (minV + maxV) / 2, maxV].map((v, i) => (
        <text key={i} x={pad.left - 6} y={getY(v) + 4} textAnchor="end" fontSize="10" fill="#c0b0b0">
          {v.toFixed(0)}
        </text>
      ))}

      {/* grid lines */}
      {[minV, (minV + maxV) / 2, maxV].map((v, i) => (
        <line key={i} x1={pad.left} y1={getY(v)} x2={w - pad.right} y2={getY(v)} stroke="#f0e8e8" strokeWidth="0.5" />
      ))}

      {/* line */}
      <path d={lineD} fill="none" stroke="#F8A4A4" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />

      {/* dots */}
      {points.map((p, i) => (
        <circle key={i} cx={getX(i)} cy={getY(p.weight)} r={i === 0 ? 3 : 2.5} fill={i === 0 ? '#F08080' : '#F8A4A4'} />
      ))}

      {/* x-axis labels */}
      {points.map((p, i) => (
        i === 0 || i === points.length - 1 || i % Math.max(1, Math.floor(points.length / 3)) === 0 ? (
          <text key={i} x={getX(i)} y={h - 4} textAnchor="middle" fontSize="9" fill="#c0b0b0">
            {p.date.slice(5)}
          </text>
        ) : null
      ))}
    </svg>
  );
}
