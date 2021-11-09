import 'bootstrap/dist/css/bootstrap.min.css'

//-----------------------------------------------
// 画面のレイアウトを設定して表示するコンポーネント
// [引数]
//   props.fileName : ファイル名（画面ファイルはpulicディレクトリ以下に配置する必要あり）
//   props.width : 画像の幅
//-----------------------------------------------
export default function Image(props) {
  let fileName = './' + props.fileName  // public 以下に配置したファイルは、サーバー直下に置かれるので、ファイルパスは ./ファイル名 になる
  let width = props.width + "px"

  return (
    <div className="container my-3">
      <img width={width} border="1" src={fileName} />
    </div>
  )
}
