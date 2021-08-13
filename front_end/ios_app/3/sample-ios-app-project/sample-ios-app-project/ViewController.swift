//
//  ViewController.swift
//  sample-ios-app-project
//
//  Created by 坂井祐介 on 2021/02/19.
//

import UIKit
import Firebase

class ViewController: UIViewController {
    // アウトレット（Swift ソースコード内でのストーリーボード上のオブジェクト（ボタンなど）への参照）
    @IBOutlet weak var firebase_name_label: UILabel!
    @IBOutlet weak var cloud_function_label: UILabel!
    
    // Firebase Cloud Functions インスタンス作成
    lazy var functions = Functions.functions()
    //lazy var functions = Functions.functions(region: "us-central1")
    
    // 起動時のイベントハンドラ（インスタンス化された直後の初回に一度のみ）
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        firebase_name_label.text = FirebaseApp.app()?.name
    }
    
    // ボタンを押したときのイベントハンドラ
    @IBAction func bt_cloud_funtion(_ sender: Any) {
        // Firebase Cloud Functions の呼び出し
        // call() 後の { (result, error) in ... } 内が Firebase Cloud Functions 呼び出し後のコールバック関数（Closure、無名関数）
        // result : Firebase Cloud Functions 内で問題なく値を取得した場合の情報。result.data に実際の値が格納される
        // error : Firebase Cloud Functions 内で例外が発生した場合のエラー（エラークラス NSError のオブジェクト）
        functions.httpsCallable("helloWorld").call() { (result, error) in
            // Firebase Cloud Functions 内でエラー発生時の処理
            if let error = error {
                print( "error : ", error )
            }
            // Firebase Cloud Functions 成功時の処理
            else {
                if let data = result?.data as? String {
                    print( "data : ", data )
                    self.cloud_function_label.text = data
                }
            }
        }
    }
}

