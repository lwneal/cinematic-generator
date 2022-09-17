import time
import os
import argparse
import json
import subprocess
import openai
openai.api_key = os.environ["OPENAI_API_KEY"]

'''
The generate_story_prompts function uses GPT-3 to generate a set of dialogue
and art prompts for a story. The prompts are saved to a JSON file.
'''
def generate_story_prompts(output_filename, num_scenes=12):
    prompt = """
FOR GEORGE R. R. MARTIN

Scroll of the Rings IV: Lords of the Orb is a massively multiplayer online virtual reality experience unlike anything the world has ever seen.

This highly awaited installment in the Scroll of the Rings series has brought together a cast of A-list Hollywood stars, as well as the best and brightest from the game industry and the world of digital art. The gripping story, stunning visuals, and immersive gameplay have led some reviewers to suggest LotO will be not just the greatest SotR game yet, but the greatest computer game ever made.

Mr. Martin, we're honored that you've agreed to write the epic cinematic introduction to the game. The introduction consists of 12 scenes. You will be working with our concept artist Greg Rutkowski. For each scene, write two sentences: the dialogue to be voice-acted, and a visual art prompt describing the scene that Greg should paint. REMEMBER: Each Visual Art Prompt must describe a scene in detail without pronouns or references to previous scenes.

Scene 1:
```
Dialogue: "In the darkest of ages, Lords from across the Realm vie for control of an ancient and magical Orb"
Visual Art Prompt:"""
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=prompt,
        temperature=0.7,
        max_tokens=255,
        stop='```',
    )
    prompt += response["choices"][0]["text"]
    for i in range(2, 13):
        prompt += """
```

Scene {}:
```""".format(i)
        print(prompt)
        response = openai.Completion.create(
            model="text-davinci-002",
            prompt=prompt,
            temperature=0.7,
            max_tokens=255,
            stop='```',
        )
        prompt += response["choices"][0]["text"]
    print(prompt)
    prompt += """
```

Well done George, thank you. Now if you would kindly repeat all of the previous scenes but in JSON format, as a list of items with keys "dialogue"and "visualArtPrompt"

JSON:
```""".format(i)
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=prompt,
        temperature=0.7,
        max_tokens=2000,
        stop='```',
    )
    output_neural_json = response["choices"][0]["text"]
    print(output_neural_json)
    with open(output_filename, 'w') as fp:
        fp.write(output_neural_json)
    return output_neural_json


'''
The generate_cinematic_from_prompts function does the following:
    Load the JSON file. If it is not correctly formatted, it will throw an error.
    Iterate over the contents of the file. The file consists of a list of dictionaries. Each dictionary has a key "dialogue" and a key "visualArtPrompt".
    Using subcommand.run, pass the "dialogue" to the "say" subcommand. Then, pass the "visualArtPrompt" to the "show" subcommand.
'''
def generate_cinematic_from_prompts(prompt_file, output_video_filename):
    try:
        with open(prompt_file) as f:
            data = json.load(f)
    except:
        print("Error loading JSON file. Please check the file and try again.")
        return

    video_filenames = []
    for i, item in enumerate(data):
        dialogue_filename = "scene_{:02d}.wav".format(i)
        art_filename = "scene_{:02d}.png".format(i)
        generate_dialogue(item["dialogue"], output_filename=dialogue_filename)
        generate_art(item["visualArtPrompt"], output_filename=art_filename)
        video_filename = make_scene_video(dialogue_filename, art_filename)
        video_filenames.append(video_filename)

    # Use ffmpeg to concatenate the videos into a single video
    with open("video_list.txt", "w") as f:
        for video_filename in video_filenames:
            f.write("file '{}'\n".format(video_filename))
    subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", "video_list.txt", "-c", "copy", output_video_filename])


def make_scene_video(input_wav_audio, input_jpg_frame):
    """ Call ffmpeg to make a video that displays the jpg frame and plays the wav audio """
    output_filename = input_wav_audio.replace(".wav", ".mp4")
    # Make the video with the moov atom at the start, and yuv420p
    subprocess.run(["ffmpeg", "-i", input_jpg_frame, "-i", input_wav_audio, 
        "-movflags", "faststart", "-pix_fmt", "yuv420p", output_filename])
    return output_filename


def generate_dialogue(text, output_filename):
    """ Call the "tts" script with the ouput filename as the first argument
    and the text as the second argument, in a subprocess. """
    subprocess.run(["tts", output_filename, text])


def generate_art(text, output_filename):
    """ Call the "art" script with the ouput filename as the first argument
    and the text as the second argument, in a subprocess. """
    subprocess.run(["art", output_filename, text])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--story-json", help="JSON file where the story should be written", default="story_{}.json".format(int(time.time())))
    parser.add_argument("--output-video", help="Video file where the story should be written", default="story_{}.mp4".format(int(time.time())))
    args = parser.parse_args()
    #generate_story_prompts(output_filename=args.story_json)
    generate_cinematic_from_prompts(prompt_file=args.story_json, output_video_filename=args.output_video)
