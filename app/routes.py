from app import app
from flask import render_template, request, current_app, send_file, redirect
import os
from werkzeug.utils import secure_filename
import subprocess
import ffmpeg


@app.route('/')
@app.route('/index')
def index():

    return render_template('index.html')


@app.route('/video_page')
def video_page():
    return render_template('video_page.html')


# @app.route('/success', methods=['POST'])
@app.route('/video_page', methods=['POST'])
def success():
    print("------------------------------\n")
    print(request.path)
    print("------------------------------\n")
    if request.method == 'POST':
        f = request.files['file']

        input_file_path = os.path.join(current_app.root_path,
                                       os.path.join(
                                           app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))

        f.save(input_file_path)

        # TODO: handle directory selection by user
        if os.path.isdir(input_file_path):
            return redirect('video_page')

        output_file_path = input_file_path.split(
            '.')[-2] + '_compressed.' + input_file_path.split('.')[-1]

        print(f'OUTPUT FILE PATH: {output_file_path}')

        input_file_info = ffmpeg.probe(input_file_path)

        for i in input_file_info['streams']:
            if i['codec_type'] == 'video':
                print("Video Information:")
                video_codec_name = f"codec_name: {i['codec_name']}"
                video_coded_height = f"coded_height: {i['coded_height']}"
                video_coded_width = f"coded_width: {i['coded_width']}"
                video_duration = f"duration: {input_file_info['format']['duration']} seconds"
                sec = int(float(input_file_info['format']['duration']))
                min, sec = divmod(sec, 60)
                hour, min = divmod(min, 60)
                video_duration = "Duration: %d:%02d:%02d" % (hour, min, sec)
                video_bit_rate = f"bit_rate: {round(int(i['bit_rate'])/1000, 2)} kb/s"
                video_size = f"size: {round(int(input_file_info['format']['size'])/1000000, 2)} MB"

            if i['codec_type'] == 'audio':
                print("\nAudio Information:")
                audio_codec_name = f"codec_name: {i['codec_name']}"
                audio_channel_layout = f"channel_layout: {i['channel_layout']}"
                audio_duration = f"duration: {i['duration']} seconds"
                sec = int(float(i['duration']))
                min, sec = divmod(sec, 60)
                hour, min = divmod(min, 60)
                audio_duration = "Duration: %d:%02d:%02d" % (hour, min, sec)
                audio_bit_rate = f"bit_rate: {round(int(i['bit_rate'])/1000, 2)} kb/s"
                audio_sample_rate = f"sample_rate: {round(int(i['sample_rate'])/1000, 2)} KHz"

        # result = subprocess.run("ffmpeg -i " + input_file_path +
        #                         " -vcodec libx264 -crf 24 -y " + output_file_path, shell=True)

        res = ffmpeg.input(input_file_path,)
        res = ffmpeg.output(res, output_file_path,
                            vcodec='libx264', crf='24',)

        ffmpeg.run(res, overwrite_output=True,)

        output_file_info = ffmpeg.probe(output_file_path)

        context = {
            'input_file_name': f.filename,
            'output_file_path': output_file_path,
            'output_file_name': output_file_path.split('/')[-1],
        }

        # return render_template("success.html", context=context)
        return render_template("video_page.html", context=context)


@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    print(f'UPLOADS PATH: {uploads}')
    print(f'FILENAME: {filename}')
    file_path = uploads + '/' + filename
    print(f'FILEPATH: {file_path}')
    return send_file(file_path, as_attachment=True)
