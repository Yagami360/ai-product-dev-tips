import 'bootstrap/dist/css/bootstrap.min.css'  // Bootstrap（CSSのフレームワーク）を import。className 属性でスタイルを設定できるようになる
import Head from 'next/head'
import Header from './Header'
import Footer from './Footer'

//-----------------------------------------------
// ページ全体のレイアウトを設定するコンポーネント
// [引数]
//   props.header : ヘッダー文字列
//   props.title : タイトル文字列
//   props.children : コンテンツ部分。 このコンポーネント呼び出し元での <Layout>xxx</Layout> の xxx が props.children になる
//-----------------------------------------------
export default function Layout(props) {
  // Bootstrap の className
  // <div className="container"> : コンテンツを配置するときに使用。各コンテンツ間が適度な余白で表示されるようになる
  // my-x : 上下のマージン
  return (
    <div>
      <Head>
        <title>{props.title}</title>
      </Head>
      <Header header={props.header} />
      <div className="container">
        <h3 className="my-3 text-primary text-center">{props.title}</h3>
        {props.children}
      </div>
      <Footer footer="footer" />
    </div>
  )
}