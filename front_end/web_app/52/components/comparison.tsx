// compareProducts ツールの返り値 props を受け取る、事前定義の比較表 UI。
// 天気カードとは別の形状の UI を出し分けられることを示すための例。
export function Comparison(props: {
  category: string;
  items: { name: string; price: string; storage: string; support: string }[];
}) {
  const th: React.CSSProperties = {
    textAlign: "left",
    padding: "10px 12px",
    fontSize: 13,
    color: "white",
    background: "#10b981",
  };
  const td: React.CSSProperties = {
    padding: "10px 12px",
    borderBottom: "1px solid #eee",
  };

  return (
    <div
      style={{
        marginTop: 8,
        border: "1px solid #d1d5db",
        borderRadius: 12,
        overflow: "hidden",
        boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
      }}
    >
      <div
        style={{
          fontWeight: 700,
          padding: "12px 14px",
          background: "#ecfdf5",
          borderBottom: "1px solid #d1fae5",
        }}
      >
        {props.category}
      </div>
      <table style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr>
            <th style={th}>プラン</th>
            <th style={th}>料金</th>
            <th style={th}>ストレージ</th>
            <th style={th}>サポート</th>
          </tr>
        </thead>
        <tbody>
          {props.items.map((item, i) => (
            <tr key={item.name} style={{ background: i % 2 ? "#f9fafb" : "white" }}>
              <td style={{ ...td, fontWeight: 600 }}>{item.name}</td>
              <td style={td}>{item.price}</td>
              <td style={td}>{item.storage}</td>
              <td style={td}>{item.support}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
