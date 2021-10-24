// アロー関数 ()=>{...} の return に JSX 形式で表示させる内容を記述し、export default で外部公開
export default () =>{
  return (
    <div>
      {/* ビルドインcss*/ }
      <style jsx>{`
      h1 {
        font-size:68pt;
        font-weight:bold;
        text-align:left;
        letter-spacing:-8px;
        color:#f0f0f0;
        margin:-32px 0px;
      }
      p {
          margin:0px;
          color:#666;
          font-size:16pt;
      }
      `}</style>

      <h1>Next.js</h1>
      <div>Welcome to next.js!</div>
    </div>
  );
}
