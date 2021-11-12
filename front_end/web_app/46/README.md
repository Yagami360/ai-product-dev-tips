# 【React】React で Material-UI を使用する（TypeScript 使用）

Material-UI は、Google が公開している [Material Design](https://material.io/design) というガイドラインに従ってデザインされた、React ライブラリである。

Material Design は、「こういった場合はマージンを16pxにして、こちらの場合では72pxにする」や「こういった部品を作る際は高さを56pxにする」といった具合に定量的なデザイン基準や用意すべきUI部品（コンポーネント）の種類や名前、どのようなカスタマイズを実施すべきかといった項目などの仕様化を行っており、Material-UI を使えば、この Material Design の仕様に沿った GUI 画面を作成できるようになる。

ここでは、TypeScript での React アプリで Material-UI を使用する方法を記載する

> Material-UI は、JavaScript でも使えることに注意



## ■ 方法

1. npm をインストール
	- MacOS の場合
		```sh
		# Node.jsをインストール
		$ brew install node
		```
	> npm : Node.js のパッケージを管理するコマンド

1. React プロジェクトを作成する<br>
  Node.js に組み込まれている `npx` コマンドを用いて、Create React App で React プロジェクトを作成する

	```sh
	# 強制 yes にする場合
	$ npx -y create-react-app ${PROJECT_NAME} --template typescript 
	```

  > 今回は TypeScript での React アプリを作成するので、`--template typescript` を設定している

1. ルーティング用パッケージをインストールする<br>
  ルーティング（＝別ページへのリンクやリダイレクトなど）用パッケージ
  ```sh
  npm install --save react-router-dom                       # ルーティング（リダイレクト）用パッケージ
  npm install --save-dev @types/react-router-dom            # ルーティング（リダイレクト）用パッケージ
  ```
  > 後述の Material-UI のテンプレート集コード内で上記パッケージを使用しているのでインストールが必要

1. Material-UI をインストールする<br>
  ```sh
  $ cd ${ROOT_DIR}/${PROJECT_NAME}
  $ npm install --save @material-ui/core @material-ui/icons
  ```

1. フォントを導入する<br>
  `public/index.html` に以下の `<link>` タグを追加し、Material-UI と相性の良いGoogle日本語フォントとフォントアイコンを導入する<br>

  ```html
  <head>
    ...
    <!-- Material-UI と相性の良いGoogle日本語フォントとフォントアイコンを CDN で導入する -->
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Noto+Sans+JP&subset=japanese" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons" />
    ...
  </head>
  ```

1. Material-UI のテンプレート集から気に入ったテンプレートのソースファイルをコピペする。
  [Material-UIが公開しているテンプレート集](https://mui.com/getting-started/templates/) から、気に入ったテンプレートのソースファイルをコピペする。<br>
  ここでは、`src/Components/GenericTemplate.tsx` にテンプレートのコードをコピペする

  ```tsx
  import React from "react";
  import clsx from "clsx";
  import { createMuiTheme } from "@material-ui/core/styles";
  import * as colors from "@material-ui/core/colors";
  import { makeStyles, createStyles, Theme } from "@material-ui/core/styles";
  import { ThemeProvider } from "@material-ui/styles";
  import CssBaseline from "@material-ui/core/CssBaseline";
  import Drawer from "@material-ui/core/Drawer";
  import Box from "@material-ui/core/Box";
  import AppBar from "@material-ui/core/AppBar";
  import Toolbar from "@material-ui/core/Toolbar";
  import List from "@material-ui/core/List";
  import Typography from "@material-ui/core/Typography";
  import Divider from "@material-ui/core/Divider";
  import Container from "@material-ui/core/Container";
  import { Link } from "react-router-dom";
  import MenuIcon from "@material-ui/icons/Menu";
  import ChevronLeftIcon from "@material-ui/icons/ChevronLeft";
  import IconButton from "@material-ui/core/IconButton";
  import HomeIcon from "@material-ui/icons/Home";
  import ShoppingCartIcon from "@material-ui/icons/ShoppingCart";
  import ListItem from "@material-ui/core/ListItem";
  import ListItemIcon from "@material-ui/core/ListItemIcon";
  import ListItemText from "@material-ui/core/ListItemText";

  const drawerWidth = 240;

  const theme = createMuiTheme({
    typography: {
      fontFamily: [
        "Noto Sans JP",
        "Lato",
        "游ゴシック Medium",
        "游ゴシック体",
        "Yu Gothic Medium",
        "YuGothic",
        "ヒラギノ角ゴ ProN",
        "Hiragino Kaku Gothic ProN",
        "メイリオ",
        "Meiryo",
        "ＭＳ Ｐゴシック",
        "MS PGothic",
        "sans-serif",
      ].join(","),
    },
    palette: {
      primary: { main: colors.blue[800] }, // テーマの色
    },
  });

  const useStyles = makeStyles((theme: Theme) =>
    createStyles({
      root: {
        display: "flex",
      },
      toolbar: {
        paddingRight: 24,
      },
      toolbarIcon: {
        display: "flex",
        alignItems: "center",
        justifyContent: "flex-end",
        padding: "0 8px",
        ...theme.mixins.toolbar,
      },
      appBar: {
        zIndex: theme.zIndex.drawer + 1,
        transition: theme.transitions.create(["width", "margin"], {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.leavingScreen,
        }),
      },
      appBarShift: {
        marginLeft: drawerWidth,
        width: `calc(100% - ${drawerWidth}px)`,
        transition: theme.transitions.create(["width", "margin"], {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.enteringScreen,
        }),
      },
      menuButton: {
        marginRight: 36,
      },
      menuButtonHidden: {
        display: "none",
      },
      title: {
        flexGrow: 1,
      },
      pageTitle: {
        marginBottom: theme.spacing(1),
      },
      drawerPaper: {
        position: "relative",
        whiteSpace: "nowrap",
        width: drawerWidth,
        transition: theme.transitions.create("width", {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.enteringScreen,
        }),
      },
      drawerPaperClose: {
        overflowX: "hidden",
        transition: theme.transitions.create("width", {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.leavingScreen,
        }),
        width: theme.spacing(7),
        [theme.breakpoints.up("sm")]: {
          width: theme.spacing(9),
        },
      },
      appBarSpacer: theme.mixins.toolbar,
      content: {
        flexGrow: 1,
        height: "100vh",
        overflow: "auto",
      },
      container: {
        paddingTop: theme.spacing(4),
        paddingBottom: theme.spacing(4),
      },
      paper: {
        padding: theme.spacing(2),
        display: "flex",
        overflow: "auto",
        flexDirection: "column",
      },
      link: {
        textDecoration: "none",
        color: theme.palette.text.secondary,
      },
    })
  );

  const Copyright = () => {
    return (
      <Typography variant="body2" color="textSecondary" align="center">
        {"Copyright © "}
        <Link color="inherit" to="/">
          管理画面
        </Link>{" "}
        {new Date().getFullYear()}
        {"."}
      </Typography>
    );
  };

  export interface GenericTemplateProps {
    children: React.ReactNode;
    title: string;
  }

  const GenericTemplate: React.FC<GenericTemplateProps> = ({
    children,
    title,
  }) => {
    const classes = useStyles();
    const [open, setOpen] = React.useState(true);
    const handleDrawerOpen = () => {
      setOpen(true);
    };
    const handleDrawerClose = () => {
      setOpen(false);
    };

    return (
      <ThemeProvider theme={theme}>
        <div className={classes.root}>
          <CssBaseline />
          <AppBar
            position="absolute"
            className={clsx(classes.appBar, open && classes.appBarShift)}
          >
            <Toolbar className={classes.toolbar}>
              <IconButton
                edge="start"
                color="inherit"
                aria-label="open drawer"
                onClick={handleDrawerOpen}
                className={clsx(
                  classes.menuButton,
                  open && classes.menuButtonHidden
                )}
              >
                <MenuIcon />
              </IconButton>
              <Typography
                component="h1"
                variant="h6"
                color="inherit"
                noWrap
                className={classes.title}
              >
                管理画面
              </Typography>
            </Toolbar>
          </AppBar>
          <Drawer
            variant="permanent"
            classes={{
              paper: clsx(classes.drawerPaper, !open && classes.drawerPaperClose),
            }}
            open={open}
          >
            <div className={classes.toolbarIcon}>
              <IconButton onClick={handleDrawerClose}>
                <ChevronLeftIcon />
              </IconButton>
            </div>
            <Divider />
            <List>
              <Link to="/" className={classes.link}>
                <ListItem button>
                  <ListItemIcon>
                    <HomeIcon />
                  </ListItemIcon>
                  <ListItemText primary="トップページ" />
                </ListItem>
              </Link>
              <Link to="/products" className={classes.link}>
                <ListItem button>
                  <ListItemIcon>
                    <ShoppingCartIcon />
                  </ListItemIcon>
                  <ListItemText primary="商品ページ" />
                </ListItem>
              </Link>
            </List>
          </Drawer>
          <main className={classes.content}>
            <div className={classes.appBarSpacer} />
            <Container maxWidth="lg" className={classes.container}>
              <Typography
                component="h2"
                variant="h5"
                color="inherit"
                noWrap
                className={classes.pageTitle}
              >
                {title}
              </Typography>
              {children}
              <Box pt={4}>
                <Copyright />
              </Box>
            </Container>
          </main>
        </div>
      </ThemeProvider>
    );
  };
  export default GenericTemplate;
  ```


1. `src/App.js` を修正する<br>
    上記テンプレートのコンポーネントを使って、アプリ画面

    ```js
    ```

    ポイントは、以下の通り

    - xxx

1. 【オプション】プロジェクトをビルドする
	React を用いたアプリケーションを公開したい場合は、以下のコマンドでプロジェクトをビルドして公開する
	```sh
	$ npm run build
	```

	> ビルドしたプロジェクトは `${PROJECT_NAME}/build` ディレクトリに作成される。この build ディレクトリのファイルを全部アップロードすることで、アプリケーションを公開できる。

1. 作成した React のプロジェクトのサーバーを起動する
	```sh
	$ cd ${PROJECT_NAME}
	$ npm start
	```

	コマンド実行後、作成した React アプリの Web サイト（デフォルトでは http://localhost:3000）が自動的に開く
