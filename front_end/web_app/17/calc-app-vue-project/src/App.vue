<template>
  <div id="app">
    <HelloWorld title="Hello"
      message="※これは、Vue3のサンプルプロジェクトです。"/>
  </div>
</template>

<script>
import HelloWorld from './components/HelloWorld.vue'

export default {
  name: 'App',
  components: {
    HelloWorld
  }
}
</script>