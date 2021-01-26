import os, argparse
from google.cloud import storage

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'client_credentials.json'

def download_dataset_from_gcs(project_id, bucket_name, dataset_dir):
    client = storage.Client(project_id)
    bucket = client.get_bucket(bucket_name)

    image_names = sorted( [ file.name for file in client.list_blobs(bucket_name) ] )
    print(image_names)

    for name in image_names:
        # ローカルディレクトリにダウンロード
        os.makedirs( os.path.join("datasets",os.path.dirname(name)), exist_ok=True )
        print( "os.path.join(dataset_dir, name) : ", os.path.join(dataset_dir, name) )

        blob = bucket.get_blob( os.path.join(dataset_dir, name) )       # GCS にあるダウンロードしたいファイルを指定
        print( "os.path.join(datasets,name) : ", os.path.join("datasets",name) )
        print( "blob : ", blob )
        blob.download_to_filename( os.path.join("datasets",name) )  # GCS にあるダウンロードしたいファイルをローカルにダウンロード

    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_id", type=str, default="myproject-292103")
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
