import subprocess, argparse, os

def parse_arguments():
    ap = argparse.ArgumentParser()

    ap.add_argument('-r', '--raw' , type=str, help='raw videos folder'       )
    ap.add_argument('-f', '--out' , type=str, help='processed_videos_folder' )

    args = vars(ap.parse_args())

    return args['raw'], args['out']

def crop_grayscale_vid(video_path, processed_videos_folder):
    #ffmpeg -i abhay8_L_20181009134724_1343130.avi -vf hue=s=0 -filter:v "crop=562:543:236:145" -c:a copy newww.avi     # mp4 quality is better
    pass

def main():
    raw_videos_folder, processed_videos_folder = parse_arguments()
    raw_vids = os.listdir(raw_videos_folder)
    for video_path in raw_vids:
        crop_grayscale_vid(video_path, processed_videos_folder)

if __name__ == "__main__":
    main()