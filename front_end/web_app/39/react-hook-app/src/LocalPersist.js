import React, { useState } from 'react'

// ローカルストレージでのデータの永続化を行う独自フック
function useLocalPersist(key, value) {
  const _key = "hooks:" + key

  // ローカルディスクから key の value を取得する関数
  const getValue = () => {
    try {
      const item = window.localStorage.getItem(_key)
      return item ? JSON.parse(item) : value
    }
    catch (err) {
      console.log(err)
      return value;
    }
  }

  // 
  const [savedValue, setSavedValue] = useState(getValue)

  // key の value を json 形式に変化してローカルストレージに保存する関数
  const setValue = (_value) => {
    try {
      setSavedValue(_value)
      window.localStorage.setItem(key, JSON.stringify(_value))
    }
    catch (err) {
      console.log(err)
    }
  }

  //
  return [savedValue, setValue]
}

export default useLocalPersist