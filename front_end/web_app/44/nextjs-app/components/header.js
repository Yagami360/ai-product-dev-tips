// ヘッダーのレイアウトを設定するコンポーネント
// [引数]
//   props.header : ヘッダーの文字列
export default function Header(props) {
  // CDN 版 Bootstrap（CSSのフレームワーク）をインストールされているので、className 属性でスタイルを設定できるようになっている
  // bg-色名 : 背景色。色名には red, blue などの色ではなく、primary, secondary などの役割を表す名前が指定できる
  // text-色名 : テキスト色
  // px-x : 左右のパティング
  return (
    <div>
      <h1 className="bg-primary px-3 text-white display-4 text-right">{props.header}</h1>
    </div>
  )
}
