import os, argparse
from tqdm import tqdm
from PIL import Image
import requests
from bs4 import BeautifulSoup
from time import sleep

IMG_EXTENSION = [ "png", "PNG", "jpg", "JPG", "jpeg", "JPEG", "bmp", "BMP" ]

if __name__ == '__main__':
    """
    WEB ページから画像を取得する。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("url", type=str )
    parser.add_argument("--out_dir", type=str, default="results")
    parser.add_argument("--connect_timeout", type=float, default=3.0, help="相手のサーバーと接続を確立する(establish a connection)までの待機時間" )
    parser.add_argument("--read_timeout", type=float, default=3.0, help="サーバーがレスポンスを返してくるまでの待機時間" )
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    if not os.path.isdir(args.out_dir):
        os.mkdir(args.out_dir)

    #---------------------------------------------
    # requests モジュールで Webページの HTML を取得
    #---------------------------------------------
    try :
        responce = requests.get(args.url, timeout=(args.connect_timeout, args.read_timeout) )
        print( "HTTPステータスコード : ", responce.status_code )
        if( args.debug ):
            print( responce.text )

    except requests.exceptions.ConnectionError as e:
        print( "requests.exceptions.ConnectionError : ", e )
        exit()
    
    except requests.exceptions.ReadTimeout as e:
        print( "requests.exceptions.ReadTimeout : ", e )
        exit()

    #---------------------------------------------
    # BeautifulSoup で取得した HTML の構文解析
    #---------------------------------------------
    # "lxml" : response.text の構文パーサー
    soup = BeautifulSoup( responce.text, "lxml" )

    # HTML の <title> タグ
    if( args.debug ):
        print( "title", soup.title.string )

    # link : <a> タグ（単一の場合）
    """
    if( args.debug ):
        print( "url link : ", soup.a.get('href') )
    """

    # link : <a> タグ（すべてのリンク）
    if( args.debug ):
        links = soup.findAll('a')
        for link in links:
            print( "url link : ", link.get('href') )

    # 画像リンクの取得
    img_links = []
    for img_link in soup.find_all("img"):
        # img_link.get("src") : <img src> タグを取得
        img_link = img_link.get("src")

        # zalando の HTML 画像リンクは、https://xxx ではなく //xxx で始まっているので、https: を追加
        if not( "https:" in img_link ):
            img_link = "https:" + img_link

        if( img_link.split(".")[-1] in IMG_EXTENSION ):
            img_links.append(img_link)

    if( args.debug ):
        print( "img_links :", img_links )

    print( "検出した画像数 : ", len(img_links) )

    #---------------------------------------------
    # 取得した画像リンクの画像を読み込み
    #---------------------------------------------
    for img_link in img_links:
        img = requests.get( img_link )
        with open( os.path.join( args.out_dir, img_link.split('/')[-1] ), 'wb' ) as f:
            # requests.content : ページ先画像のデータを取得する
            f.write(img.content)      
