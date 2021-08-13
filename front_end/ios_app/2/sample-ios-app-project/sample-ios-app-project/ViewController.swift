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

    // UIImageView の起動時の画像読み込み
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        imageView.image = UIImage(named: "5.jpg")
        firebase_name_label.text = FirebaseApp.app()?.name
    }
}

