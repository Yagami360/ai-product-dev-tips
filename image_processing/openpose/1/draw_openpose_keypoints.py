import os
import argparse
import json
import matplotlib.pyplot as plt

if __name__ == '__main__':
    """
    openpose が出力する json ファイルの keypoint 情報を描写する。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('in_json_path', type=str )
    parser.add_argument('out_image_path', type=str )
    args = parser.parse_args()

    with open(args.in_json_path, 'r') as f:
        json_data = json.load(f)
        f.close()

    version = json_data["version"]
    print("openpose version :", version)
    #if( version != 1.1 ):
    #warning

    if( len(json_data['people']) != 0 ):
        keyPoints = json_data['people'][0]["pose_keypoints_2d"]
        points_x = []
        points_y = []
        for i,data in enumerate( keyPoints ):
            if( (i+1) % 3 == 0 ):
                continue
            elif( i % 3 == 0 ):
                points_x.append( data )
            else:
                points_y.append( data )
    else:
        points_x = [0 for i in range(18)]
        points_y = [0 for i in range(18)]

    #----------------------------------------------
    # 取得したデータを plot
    #----------------------------------------------
    plt.clf()
    for i in range( 0, len(points_x) ):
        plt.plot(
            points_x[i], points_y[i],
            marker = "o",
            markersize = 5,
            color = 'red',
            label = str(i),
            linestyle='None'
        )
        plt.text(
            points_x[i], points_y[i]-10,
            str(i),
            ha='center',
            va='center',
            fontsize=14, rotation=0
        )

    plt.title( "keyPoints" )
    #plt.legend()
    plt.ylim( [ max( points_y ) + 50, 0 ] )
    plt.xlabel( "x" )
    plt.ylabel( "y" )
    plt.grid()
    plt.tight_layout()
    plt.savefig(args.out_image_path)