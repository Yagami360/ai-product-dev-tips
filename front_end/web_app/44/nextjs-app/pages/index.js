import 'bootstrap/dist/css/bootstrap.min.css'  // Bootstrap（CSSのフレームワーク）を import。className 属性でスタイルを設定できるようになる
import Button from 'react-bootstrap/Button'
import Layout from '../components/layout'
import Image from '../components/image'

export default function Home() {
  // Bootstrap の className
  // alert alert-色名 : 強調表示。色名には red, blue などの色ではなく、primary, secondary などの役割を表す名前が指定できる
  // mb-x : 下マージン
  return (
    <div>
      <Layout header="header" title="title">
        <div className="alert alert-primary text-center">
          <h5 className="mb-4">
            <p>contents</p>
            <Button variant="outline-primary">button</Button>
            <Image fileName="panda.jpg" width="200" />
          </h5>
        </div>
      </Layout>
    </div>
  )
}
