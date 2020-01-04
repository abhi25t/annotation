import subprocess, argparse, os

def parse_arguments():
    ap = argparse.ArgumentParser()

    ap.add_argument('-r', '--raw' , type=str, help='raw videos folder'       )
    ap.add_argument('-f', '--out' , type=str, help='processed_videos_folder' )
    ap.add_argument('-t', '--typ' , type=str, help='output file type' )

    args = vars(ap.parse_args())

    return args['raw'], args['out'], args['typ']

def crop_grayscale_vid(video_path, processed_videos_folder, typ):
    base = os.path.basename(video_path)
    out_file = os.path.join(processed_videos_folder, os.path.splitext(base)[0] + '.' + typ )  
    ffmpeg_cmd = 'ffmpeg -i ' + video_path + ' -vf hue=s=0 -filter:v "crop=562:543:236:145" -c:a copy ' + out_file
    print ('==================================================')
    print (ffmpeg_cmd)
    subprocess.call(ffmpeg_cmd, shell=True)

def main():
    raw_videos_folder, processed_videos_folder, typ = parse_arguments()
    raw_vids = os.listdir(raw_videos_folder)
    for video_path in raw_vids:
        crop_grayscale_vid(  os.path.join(raw_videos_folder, video_path ) , processed_videos_folder, typ)

if __name__ == "__main__":
    main()