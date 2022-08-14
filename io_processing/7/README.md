# 【Go lang】 cobra を使用して独自の Go lang CLI コマンドを使用する

## ■ 方法

1. Go lang をインストールする
    - MacOS の場合
        ```sh
        brew install go
        ```

    - Linux の場合
        ```sh
        wget https://dl.google.com/go/go1.13.5.linux-amd64.tar.gz
        sudo tar -C /usr/local -xzf go1.13.5.linux-amd64.tar.gz
        export PATH=$PATH:/usr/local/go/bin
        source .profile
        rm -rf go1.13.5.linux-amd64.tar.gz
        ```

1. cobra をインストールする<br>
    - `go get` でインストールする場合<br>
        ```sh
        go mod init ${CLI_NAME}
        go get -u github.com/spf13/cobra@latest
        ```

        > `go get` でインストールする場合は、ローカル環境 `${PWD}/${go mod init で指定したディレクトリ}` 以下にパッケージがインストールされる

1. cobra CLI をインストールする
    ```sh
    go install github.com/spf13/cobra-cli@latest
    ```

1. cobra のプロジェクト（CLIボイラープレート）を作成する
    ```sh
    # 初期設定
    #cobra init
    ~/go/bin/cobra-cli init
    ```

    上記コマンド実行後、以下のようなディレクトリ構造の cobra プロジェクトが自動的に作成される
    ```sh
    + cmd/
    |     + root.go
    + main.go
    ```

    - `main.go`<br>
        ```go
        /*
        Copyright © 2022 NAME HERE <EMAIL ADDRESS>

        */
        package main

        import "my-go-cli/cmd"

        func main() {
            cmd.Execute()
        }
        ```

    - `cmd/root.go`<br>
        ```go
        /*
        Copyright © 2022 NAME HERE <EMAIL ADDRESS>

        */
        package cmd

        import (
            "os"
            "github.com/spf13/cobra"
        )

        // rootCmd represents the base command when called without any subcommands
        var rootCmd = &cobra.Command{
            Use:   "my-go-cli",
            Short: "A brief description of your application",
            Long: `A longer description that spans multiple lines and likely contains
        examples and usage of using your application. For example:

        Cobra is a CLI library for Go that empowers applications.
        This application is a tool to generate the needed files
        to quickly create a Cobra application.`,
            // Uncomment the following line if your bare application
            // has an action associated with it:
            // Run: func(cmd *cobra.Command, args []string) { },
        }

        // Execute adds all child commands to the root command and sets flags appropriately.
        // This is called by main.main(). It only needs to happen once to the rootCmd.
        func Execute() {
            err := rootCmd.Execute()
            if err != nil {
                os.Exit(1)
            }
        }

        func init() {
            // Here you will define your flags and configuration settings.
            // Cobra supports persistent flags, which, if defined here,
            // will be global for your application.

            // rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default is $HOME/.cli.yaml)")

            // Cobra also supports local flags, which will only run
            // when this action is called directly.
            rootCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
        }
        ```

        ポイントは、以下の通り

        - xxx

1. cobra を使用して独自のサブコマンドを作成する
    ```sh
    # サブコマンドを追加
    #cobra add ${COMMAND_NAME}
    ~/go/bin/cobra-cli add ${SUB_COMMAND_NAME_1}
    ```

    上記コマンドを実行すると `cmd/${SUB_COMMAND_NAME_1}.go` にスクリプトが追加される

    - `cmd/command1.go`
        ```go
        /*
        Copyright © 2022 NAME HERE <EMAIL ADDRESS>
        */
        package cmd

        import (
            "fmt"
            "github.com/spf13/cobra"
        )

        // command1Cmd represents the command1 command
        var command1Cmd = &cobra.Command{
            Use:   "command1",
            Short: "A brief description of your command",
            Long: `A longer description that spans multiple lines and likely contains examples
        and usage of using your command. For example:

        Cobra is a CLI library for Go that empowers applications.
        This application is a tool to generate the needed files
        to quickly create a Cobra application.`,
            Run: func(cmd *cobra.Command, args []string) {
                fmt.Println("command1 called")
            },
        }

        func init() {
            rootCmd.AddCommand(command1Cmd)

            // Here you will define your flags and configuration settings.

            // Cobra supports Persistent Flags which will work for this command
            // and all subcommands, e.g.:
            // command1Cmd.PersistentFlags().String("foo", "", "A help for foo")

            // Cobra supports local flags which will only run when this command
            // is called directly, e.g.:
            // command1Cmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
        }
        ```

1. ルートコマンドを実行する<br>
    - コンパイルなしで実行する場合<br>
        ```sh
        go run main.go
        ```

    - コンパイルして実行する場合<br>
        ```sh
        # コンパイル
        go build main.go -o ${CLI_NAME}

        # コンパイルされたファイルを実行
        ./${CLI_NAME}
        ```
        > `go build` の `-o` オプションで、コンパイル結果を `main` ではなく `${CLI_NAME}` に出力するようにすることで、`./${CLI_NAME}` のようにして CLI 名でコマンドを実行できるようにしている

1. サブコマンドを実行する<br>
    - コンパイルなしで実行する場合<br>
        ```sh
        go run main.go ${COMMAND_NAME}
        ```

    - コンパイルして実行する場合<br>
        ```sh
        # コンパイル
        go build main.go -o ${CLI_NAME}

        # コンパイルされたファイルを実行
        ./${CLI_NAME} ${COMMAND_NAME}
        ```

## ■ 参考サイト

- https://tech.excite.co.jp/entry/2022/01/18/154113
- https://simple-minds-think-alike.moritamorie.com/entry/golang-cobra