import React from "react";
import Typography from '@material-ui/core/Typography';    // 文字表示を表現できるコンポーネント。文字位置や文字色、どのタグ（h1など）とするか、どのタグのスタイルをあてるかなどを設定できる。
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import AppBar from '@material-ui/core/AppBar';            // ナビゲーションバー
import Toolbar from '@material-ui/core/Toolbar';          // ナビゲーションバー
import MenuIcon from '@material-ui/icons/Menu';           // メニューコンポーネント群。Buttonと組み合わせて、クリックされたときにメニューを開くといったように使う。
import { useTheme } from '@material-ui/core/styles';
import { ThemeProvider　} from '@material-ui/core/styles';

// React.VFC : React に関数コンポーネントの型（VFC : Void Function Component）
const App: React.VFC = () => {
  // useTheme() でテーマ（画面全体のスタイル）のオブジェクトを作成
  const theme = useTheme();

  // <ThemeProvider> コンポーネントの theme 属性に useTheme() で作成した theme オブジェクトを設定し、他の Material-UI コンポーネントを包むことでテーマを適用出来る（※ theme オブジェクトの各属性（theme.palette など）を各コンポーネントの style 属性に設定することでもテーマのスタイルを適用できる）
  // 各 Material UI コンポーネントの variant 属性 : 各コンポーネント毎に定義された表示バリエーションを定義（例えば、ボタンコンポーネントの場合は "outlined", "contained" などがある）
  // 各 Material UI コンポーネントの color 属性 : primary or secondary と呼ばれる2つの色を定義
  return (
    <ThemeProvider theme={theme}>
      <AppBar position="static">
        <Toolbar>
          <IconButton edge="start" color="inherit" aria-label="menu">
            <MenuIcon />
          </IconButton>
          <Typography variant="h6">Material UI Sample App</Typography>
        </Toolbar>        
      </AppBar>
      <Button variant="contained">contained</Button>
      <Button variant="outlined">outlined</Button>
      <Button variant="contained" color="primary">primary</Button>
      <Button variant="contained" color="secondary">secondary</Button>
    </ThemeProvider>
  );
};

export default App;
