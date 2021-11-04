import { useState } from 'react'

// ローカルストレージでのデータの永続化を行う独自フック
function useLocalPersist(key, initValue) {
  const _key = "hooks:" + key

  // ローカルディスクから key の value を取得する関数
  // 初回の書き込みで key がない場合は、初期値 initValue を返す
  const loadValueFromStorage = () => {
    try {
      const item = window.localStorage.getItem(_key)
      return item ? JSON.parse(item) : initValue
    }
    catch (err) {
      console.log(err)
      return initValue;
    }
  }

  // ローカルストレージから読み込んだ initVal
  const [savedValue, setSavedValue] = useState(loadValueFromStorage)

  // key の value を json 形式に変化してローカルストレージに保存する関数
  // この関数を第２戻り値として return し、state の値を更新する関数とする
  const saveValueToStorage = (value) => {
    try {
      setSavedValue(value)
      window.localStorage.setItem(_key, JSON.stringify(value))
    }
    catch (err) {
      console.log(err)
    }
  }

  // ローカルストレージから読み込んだ value と key の value をローカルストレージに保存する関数を retrun
  return [savedValue, saveValueToStorage]
}

export default useLocalPersist