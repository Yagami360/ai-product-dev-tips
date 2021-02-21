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
    @IBOutlet weak var imageView: UIImageView!
    @IBOutlet weak var firebase_name_label: UILabel!
    @IBOutlet weak var cloud_function_label: UILabel!
    
    // Firebase Cloud Functions インスタンス作成
    lazy var functions = Functions.functions()
    
    // 起動時のイベントハンドラ（インスタンス化された直後の初回に一度のみ）
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        imageView.image = UIImage(named: "5.jpg")
        firebase_name_label.text = FirebaseApp.app()?.name
    }
    
    // ボタンを押したときのイベントハンドラ
    @IBAction func bt_cloud_funtion(_ sender: Any) {
        // Firebase Cloud Functions の呼び出し
        functions.httpsCallable("helloWorld").call() { (result, error) in

        }
        
        cloud_function_label.text = "hello firebase cloud functions!!"
    }
}

