import { Component } from 'react';
import {initStore} from '../store';

const isServer = typeof window === 'undefined'
const _NRS_ = '__NEXT_REDUX_STORE__'

function getOrCreateStore (initialState) {
  if (isServer) {
    return initStore(initialState)
  }
  if (!window[_NRS_]) {
    window[_NRS_] = initStore(initialState)
  }
  return window[_NRS_]
}

export default (App) => {
  // AppWithRedux コンポーネントでは、Redux の store を初期化し、それに属性を指定して App コンポーネントを生成する
  return class AppWithRedux extends Component {
    static async getInitialProps (appContext) {
      const reduxStore = getOrCreateStore()
      appContext.ctx.reduxStore = reduxStore
      let appProps = {}
      if (typeof App.getInitialProps === 'function') {
        appProps = await App.getInitialProps(appContext)
      }
      return {
        ...appProps,
        initialReduxState: reduxStore.getState()
      }
    }

    constructor (props) {
      super(props)

      // getOrCreateStore() 内部で、initStore() でストアを初期化している
      this.reduxStore = getOrCreateStore(props.initialReduxState)
    }

    render () {
      return <App {...this.props}
        reduxStore={this.reduxStore} />
    }
  }
}
