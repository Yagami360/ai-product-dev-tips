import 'bootstrap/dist/css/bootstrap.min.css'

//-----------------------------------------------
// フッターのレイアウトを設定して表示するコンポーネント
// [引数]
//   props.header : フッターの文字列
//-----------------------------------------------
export default function Footer(props) {
  return (
    <div className="text-center h6 my-4">
      <div>{props.footer}</div>
    </div>
  )
}