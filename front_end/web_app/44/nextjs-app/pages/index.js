import Layout from '../components/layout'

export default function Home() {
  return (
    <div>
      <Layout header="header" title="title">
        <div className="alert alert-primary text-center">
          <h5 className="mb-4">contents</h5>
        </div>
      </Layout>
    </div>
  )
}
