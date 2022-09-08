package main

import (
	"testing"

	"github.com/golang/mock/gomock"
)

var userEntity = &main.UserEntity{id: 1, name: "Yagami"}

func TestUser(t *testing.T) {
	// モックの呼び出しを管理する Controller を生成
	mockCtrl := gomock.NewController(t)

	// この関数の最後に Controller を Finish() する
	defer mockCtrl.Finish()

	// モックの生成
	mockUser := mock_main.NewMockUser(mockCtrl)

	// テスト中に呼ばれるべき関数と期待される戻り値を指定
	// EXPECT().呼ばれるべき関数（今回の場合は、インターフェイスで定義していた Update()）
	// Return() : 単体テストで期待される返り値を指定
	mockUser.EXPECT().Update(userEntity).Return(nil)

	// do test...

}
