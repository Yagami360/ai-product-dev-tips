// displayWeather ツールの返り値 props をそのまま受け取る、事前定義の天気カード UI。
export function Weather(props: {
  location: string;
  temperature: number;
  condition: string;
  weeklyForecast: { day: string; temperature: number }[];
}) {
  return (
    <div
      style={{
        background: "#3b82f6",
        color: "white",
        borderRadius: 12,
        padding: 16,
        marginTop: 8,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <div>
          <div style={{ fontSize: 13, opacity: 0.9 }}>{props.location}</div>
          <div style={{ fontSize: 32, fontWeight: 700 }}>
            {props.temperature}°C
          </div>
        </div>
        <div style={{ alignSelf: "center", fontSize: 16 }}>{props.condition}</div>
      </div>
      <div style={{ display: "flex", gap: 14, marginTop: 12 }}>
        {props.weeklyForecast.map((f) => (
          <div key={f.day} style={{ textAlign: "center", fontSize: 12 }}>
            <div>{f.day}</div>
            <div>{f.temperature}°</div>
          </div>
        ))}
      </div>
    </div>
  );
}
