import 'bootstrap/dist/css/bootstrap.min.css'

//-----------------------------------------------
// ヘッダーのレイアウトを設定して表示するコンポーネント
// [引数]
//   props.header : ヘッダーの文字列
//-----------------------------------------------
export default function Header(props) {
  //------------------------
  // JSX での表示処理
  //------------------------
  // Bootstrap の className
  // bg-色名 : 背景色。色名には red, blue などの色ではなく、primary, secondary などの役割を表す名前が指定できる
  // text-色名 : テキスト色
  // display-x : 通常のヘッダよりもさらに目立たせたいヘッダがあれば、.display-1～.display-4 を用いてさらに大きな見出しに出来る
  // px-x : 左右のパティング
  return (
    <div>
      <h1 className="bg-primary px-3 text-white display-4 text-right">{props.header}</h1>
    </div>
  )
}
