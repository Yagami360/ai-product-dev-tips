import User from '../components/User';

// アロー関数 ()=>{...} の return に JSX 形式で表示させる内容を記述し、export default で外部公開
export default () =>{
  return (
    <div>
      <h1>Next.js</h1>
      <div>Welcome to next.js!</div>      
      <User id="1" name="Yagami" />
      <User id="2" name="Yagoo" />
     </div>
  );
}

