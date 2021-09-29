// HTML の読み込みが全て完了した後に request.js が実行されるようにすうｒために $(function(){} で宣言
$(function(){
    console.log("load page");

    // ${".xxx"} : `<body>` タグ内の class 名が `pose_panel_select` の要素にアクセス
    var $pose_selectPanel = $('.pose_panel_select');

    //-------------------------------------------------
    // 変数 $pose_selectPanel の要素をクリックしたとき
    //-------------------------------------------------
    $pose_selectPanel.on('click', function(e) {
        // その他の CSS の枠色をクリア
        $pose_selectPanel.css('border', '4px rgba(0,0,0,0) solid');
        $("#selected_file_pose_image_canvas").css('border', '4px rgba(0,0,0,0) solid')

        // クリックした要素のCSSを変更
        $(this).css('border', '4px blue solid');

        // Radio ボタンの選択を消す 
        document.getElementById('pose_select_0').checked = false;
        document.getElementById('pose_select_1').checked = false;
        document.getElementById('pose_select_2').checked = false;
        document.getElementById('pose_select_3').checked = false;
        document.getElementById('pose_select_4').checked = false;
        document.getElementById('pose_select_5').checked = false;

        console.log( this );
        console.log( this.children );
        console.log( this.children[0] );
        console.log( this.children[0].id );
        document.getElementById(this.children[0].id).checked = true;
    });

    //-------------------------------------------------
    // 読み込み人物画像ファイル選択時に呼び出される関数（jQuery 使用）
    //-------------------------------------------------
    jQuery('#selected_file_pose_image').on('change', function(e) {
        // FileReader オブジェクトの作成
        var reader = new FileReader();
        reader.readAsDataURL(e.target.files[0]);    // ファイルが複数読み込まれた際に、1つ目を選択
        reader.onload = function (e) {  // 読み込みが成功時の処理
            img_src = e.target.result;
            drawToCanvas( img_src, "selected_file_pose_image_canvas" );
        }

        // 要素のCSSを変更
        $pose_selectPanel.css('border', '4px rgba(0,0,0,0) solid');
        $("#selected_file_pose_image_canvas").css('border', '4px blue solid');
    });
});

//============================================
// 出力画像生成ボタンクリック時に呼び出される関数
//============================================
function generateOutputImage() {
    console.log( "背景除去画像の生成開始" );

    // API の URL 取得
    var api_url = document.getElementById("api_url").value;
    var cloud_function_url = document.getElementById("cloud_function_url").value;

    //---------------------------------------
    // 選択されている人物画像を取得
    //---------------------------------------
    radio_btn_pose0 = document.getElementById("pose_select_0");
    radio_btn_pose1 = document.getElementById("pose_select_1");
    radio_btn_pose2 = document.getElementById("pose_select_2");
    radio_btn_pose3 = document.getElementById("pose_select_3");
    radio_btn_pose4 = document.getElementById("pose_select_4");
    radio_btn_pose5 = document.getElementById("pose_select_5");
    console.log( "radio_btn_pose0.checked : ", radio_btn_pose0.checked );
    console.log( "radio_btn_pose1.checked : ", radio_btn_pose1.checked );
    console.log( "radio_btn_pose2.checked : ", radio_btn_pose2.checked );
    console.log( "radio_btn_pose3.checked : ", radio_btn_pose3.checked );
    console.log( "radio_btn_pose4.checked : ", radio_btn_pose4.checked );
    console.log( "radio_btn_pose5.checked : ", radio_btn_pose5.checked );

    var pose_img_base64
    if( radio_btn_pose0.checked == true ) {
        // Canvas から画像データを取得
        var pose_img_canvas = document.getElementById("selected_file_pose_image_canvas");
        pose_img_base64 = pose_img_canvas.toDataURL('image/png').replace(/^.*,/, '');
        //console.log( "pose_img_base64 : ", pose_img_base64 );
    }
    else if( radio_btn_pose1.checked == true ) {
        var pose_img = document.getElementById('pose_image_1');
        pose_img_base64 = convImageToBase64( pose_img, 'image/png' ).replace(/^.*,/, '');
    }
    else if( radio_btn_pose2.checked == true ) {
        var pose_img = document.getElementById('pose_image_2');
        pose_img_base64 = convImageToBase64( pose_img, 'image/png' ).replace(/^.*,/, '');
    }
    else if( radio_btn_pose3.checked == true ) {
        var pose_img = document.getElementById('pose_image_3');
        pose_img_base64 = convImageToBase64( pose_img, 'image/png' ).replace(/^.*,/, '');
    }
    else if( radio_btn_pose4.checked == true ) {
        var pose_img = document.getElementById('pose_image_4');
        pose_img_base64 = convImageToBase64( pose_img, 'image/png' ).replace(/^.*,/, '');
    }
    else if( radio_btn_pose5.checked == true ) {
        var pose_img = document.getElementById('pose_image_5');
        pose_img_base64 = convImageToBase64( pose_img, 'image/png' ).replace(/^.*,/, '');
    }
    else{
        var pose_img = document.getElementById('pose_image_1');
        pose_img_base64 = convImageToBase64( pose_img, 'image/png' ).replace(/^.*,/, '');
    }

    //--------------------------------------------------------
    // GKE 上の WebAPI に https 送信（リバースプロキシとしての firebase cloud function 経由で API を呼び出す）
    //--------------------------------------------------------
    try {
        $.ajax({
            url: cloud_function_url,            
            type: 'POST',
            dataType: "json",
            data: JSON.stringify({ "pose_img_base64": pose_img_base64}),
            contentType: 'application/json',
            crossDomain: true,  // API サーバーとリクエスト処理を異なるアプリケーションでデバッグするために必要
            timeout: 60000,
        })
        .done(function(data, textStatus, jqXHR) {
            // 通信成功時の処理を記述
            console.log( "Cloud Function との通信成功" );
            //console.log( data.pose_parse_img_RGB_base64 );
            console.log( textStatus );
            console.log( jqXHR );

            dataURL = `data:image/png;base64,${data.pose_parse_img_RGB_base64}`
            drawToCanvas( dataURL, "output_image_canvas" )
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            // 通信失敗時の処理を記述
            console.log( "Cloud Function との通信失敗" );
            //console.log( textStatus );
            console.log( jqXHR );
            //console.log( errorThrown );
            alert("Cloud Function との通信に失敗しました\n" + cloud_function_url )
        });
    } catch (e) {
        console.error(e)
        alert(e);
    }

    //--------------------------------------------------------
    // GKE 上の WebAPI に http 送信（jQuery での Ajax通信を開始）
    //--------------------------------------------------------
    /*
    try {
        $.ajax({
            url: api_url,            
            type: 'POST',
            dataType: "json",
            data: JSON.stringify({ "pose_img_base64": pose_img_base64}),
            contentType: 'application/json',
            crossDomain: true,  // API サーバーとリクエスト処理を異なるアプリケーションでデバッグするために必要
            timeout: 60000,
        })
        .done(function(data, textStatus, jqXHR) {
            // 通信成功時の処理を記述
            console.log( "APIサーバーとの通信成功" );
            //console.log( data.pose_parse_img_RGB_base64 );
            console.log( textStatus );
            console.log( jqXHR );

            dataURL = `data:image/png;base64,${data.pose_parse_img_RGB_base64}`
            drawToCanvas( dataURL, "output_image_canvas" )
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            // 通信失敗時の処理を記述
            console.log( "APIサーバーとの通信失敗" );
            //console.log( textStatus );
            console.log( jqXHR );
            //console.log( errorThrown );
            alert("APIサーバーとの通信に失敗しました\n" + api_url )
        });
    } catch (e) {
        console.error(e)
        alert(e);
    }
    */
}
