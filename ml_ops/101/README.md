# 【Golang】go test と go mock を使用してコードの単体テストを行う

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

1. go-mock をインストールする<br>
    ```sh
    mkdir -p src
    cd src
    go mod init src
    go get github.com/golang/mock/gomock
    ```

    > `go get` でインストールする場合は、ローカル環境 `${PWD}/${go mod init で指定したディレクトリ}` 以下にパッケージがインストールされる

1. mockgen CLI をインストールする
    ```sh
    go install github.com/golang/mock/mockgen@v1.6.0
    mockgen -version
    ```

    > `go install` でインストールした場合は、グローバル環境 `$GOPATH/bin` 以下にパッケージがインストールされる

1. テスト対象のコード（＝モックの作成対象コード）を実装する
    ```go
    package main

    type User struct {
      id    int64
      value string
    }

    type User interface {
      Update(user *User) error
    }
    ```

1. mockgen コマンドでモックを作成する
    ```sh
    mockgen -source main.go -destination main_mock.go
    ```

1. 自動生成されたモックのコードを確認する
    ```go
    // Code generated by MockGen. DO NOT EDIT.
    // Source: main.go

    // Package mock_main is a generated GoMock package.
    package mock_main

    import (
      reflect "reflect"
      src "src"

      gomock "github.com/golang/mock/gomock"
    )

    // MockUser is a mock of User interface.
    type MockUser struct {
      ctrl     *gomock.Controller
      recorder *MockUserMockRecorder
    }

    // MockUserMockRecorder is the mock recorder for MockUser.
    type MockUserMockRecorder struct {
      mock *MockUser
    }

    // NewMockUser creates a new mock instance.
    func NewMockUser(ctrl *gomock.Controller) *MockUser {
      mock := &MockUser{ctrl: ctrl}
      mock.recorder = &MockUserMockRecorder{mock}
      return mock
    }

    // EXPECT returns an object that allows the caller to indicate expected use.
    func (m *MockUser) EXPECT() *MockUserMockRecorder {
      return m.recorder
    }

    // Update mocks base method.
    func (m *MockUser) Update(user *src.User) error {
      m.ctrl.T.Helper()
      ret := m.ctrl.Call(m, "Update", user)
      ret0, _ := ret[0].(error)
      return ret0
    }

    // Update indicates an expected call of Update.
    func (mr *MockUserMockRecorder) Update(user interface{}) *gomock.Call {
      mr.mock.ctrl.T.Helper()
      return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "Update", reflect.TypeOf((*MockUser)(nil).Update), user)
    }
    ```

    この自動生成コードは、後述の単体テストのコードで利用する

1. go-test を使用した単体テストのコードを実装する<br>
    ```go

    ```

    ポイントは、以下の通り

    - go-test を使用した単体テストのコードのファイル名は `***_test.go` にする必要があり、また関数名は `TestXxx(t *testing.T)` にする必要がある

    - `MockUser` 構造体は、元の `main.go` で定義した `User` インターフェイスに対応しているモックの構造体であり、以下の手順で元の `User` インターフェイスで定義した関数を呼び出せる
      1. `mockUser := mock_main.NewMockUser(mockCtrl)`
      1. `mockUser.EXPECT().Update(userEntity).Return(nil)` 

    - `MockUserMockRecorder` は Mock の呼び出しなどを管理する構造体

    - xxx


1. 単体テストを実行する<br>
    ```sh
    go test -v --cover main_test.go
    ```
    - `-v` : 詳細表示
    - `--cover` : コードの coverage を計算

## ■ 参考サイト

- https://zenn.dev/sanpo_shiho/articles/01da627ead98f5
- https://www.asobou.co.jp/blog/web/gomock
- https://qiita.com/rkunihiro/items/e89c426e255bef2aff2c