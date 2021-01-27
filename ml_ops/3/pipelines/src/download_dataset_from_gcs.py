from tqdm import tqdm
import os, argparse
from google.cloud import storage

IMG_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.ppm', '.bmp', '.pgm', '.tif',
    '.JPG', '.JPEG', '.PNG', '.PPM', '.BMP', '.PGM', '.TIF',
)

# サービスアカウントキーの登録
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'client_credentials.json'

def download_dataset_from_gcs(project_id, bucket_name, dataset_dir):
    client = storage.Client(project_id)
    bucket = client.get_bucket(bucket_name)

    image_names = sorted( [ f.name for f in client.list_blobs(bucket_name) ] )
    image_names = sorted( [ f for f in image_names if f.endswith(IMG_EXTENSIONS) ] )
    print(image_names)

    for name in tqdm(image_names):
        # ローカルディレクトリ作成
        os.makedirs( os.path.join("datasets",os.path.dirname(name)), exist_ok=True )

        # GCS にあるダウンロードしたいファイルを指定
        blob = bucket.blob( name )

        # GCS にあるダウンロードしたいファイルをローカルにダウンロード
        blob.download_to_filename( os.path.join("datasets",name) )

    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_id", type=str, default="my-project2-303004")
    parser.add_argument("--bucket_name", type=str, default="ml_dataset_360")
    parser.add_argument("--dataset_dir", type=str, default="gs://ml_dataset_360")
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    if not os.path.isdir("datasets"):
        os.mkdir("datasets")
        
    download_dataset_from_gcs(args.project_id, args.bucket_name, args.dataset_dir)
