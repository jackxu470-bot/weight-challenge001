type Props = {
  ranked: { name: string; lossPct: number }[];
  prizePool: number;
};

export default function PrizeDisplay({ ranked, prizePool }: Props) {
  const totalLossPct = ranked.reduce((sum, p) => sum + Math.max(0, p.lossPct), 0);
  const hasWeightLoss = totalLossPct > 0;

  return (
    <div style={{ borderTop: '1px solid #f0e8e8', paddingTop: 16 }}>
      <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12, color: '#888' }}>💰 奖金分配</h3>
      <p style={{ fontSize: 12, color: '#c0b0b0', marginBottom: 12 }}>总奖金池：<strong style={{ color: '#F08080' }}>¥{prizePool}</strong>（按减重百分比占比分配）</p>

      {!hasWeightLoss ? (
        <p className="empty-state" style={{ padding: '12px 0', fontSize: 13 }}>还没有人减重，暂无可分配奖金</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {ranked.map((p) => {
            const share = p.lossPct > 0 ? (p.lossPct / totalLossPct) * prizePool : 0;
            return (
              <div key={p.name} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid #f5f0f0', fontSize: 14 }}>
                <span>{p.name}</span>
                <span style={{ fontWeight: 600, color: '#F08080' }}>
                  ¥{share.toFixed(0)}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
