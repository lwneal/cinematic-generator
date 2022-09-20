import time
import random
import shutil
import glob
import os
import argparse
import json
import subprocess
import openai
openai.api_key = os.environ["OPENAI_API_KEY"]


EPIC_MUSIC_DIR = os.path.expanduser("~/Music/royaltyfree-cc/epic/")
def get_epic_music_mp3():
    """ Return a random mp3 filename from the EPIC_MUSIC_DIR directory """
    music_files = [f for f in os.listdir(EPIC_MUSIC_DIR) if f.endswith(".mp3")]
    return os.path.join(EPIC_MUSIC_DIR, random.choice(music_files))

INIT_PROMPT = """
History of the World: The Battle of Antietam 

History of the World is a detailed, accurate, and compelling documentary series that brings historical events to life. This highly awaited documentary has brought together a cast of A-list Hollywood stars, as well as the best and brightest historians and artists. The gripping story and stunning visuals have led some reviewers to suggest History of the World may be the greatest documentary film of all time.

The topic of this chapter is the Battle of Antietam.

Background Information:
```
The Battle of Antietam (/ænˈtiːtəm/), or Battle of Sharpsburg particularly in the Southern United States, was a battle of the American Civil War fought on September 17, 1862, between Confederate Gen. Robert E. Lee's Army of Northern Virginia and Union Gen. George B. McClellan's Army of the Potomac near Sharpsburg, Maryland and Antietam Creek. Part of the Maryland Campaign, it was the first field army–level engagement in the Eastern Theater of the American Civil War to take place on Union soil. It remains the bloodiest day in American history, with a combined tally of 22,717 dead, wounded, or missing.[11][12] Although the Union army suffered heavier casualties than the Confederates, the battle was a major turning point in the Union's favor.

After pursuing Confederate Gen. Robert E. Lee into Maryland, Maj. Gen. George B. McClellan of the Union Army launched attacks against Lee's army who were in defensive positions behind Antietam Creek. At dawn on September 17, Maj. Gen. Joseph Hooker's corps mounted a powerful assault on Lee's left flank. Attacks and counterattacks swept across Miller's Cornfield, and fighting swirled around the Dunker Church. Union assaults against the Sunken Road eventually pierced the Confederate center, but the Federal advantage was not followed up. In the afternoon, Union Maj. Gen. Ambrose Burnside's corps entered the action, capturing a stone bridge over Antietam Creek and advancing against the Confederate right. At a crucial moment, Confederate Maj. Gen. A. P. Hill's division arrived from Harpers Ferry and launched a surprise counterattack, driving back Burnside and ending the battle. Although outnumbered two-to-one, Lee committed his entire force, while McClellan sent in less than three-quarters of his army, enabling Lee to fight the Federals to a standstill. During the night, both armies consolidated their lines. In spite of crippling casualties, Lee continued to skirmish with McClellan throughout September 18, while removing his battered army south of the Potomac River.[13]

McClellan successfully turned Lee's invasion back, making the battle a Union victory, but President Abraham Lincoln, unhappy with McClellan's general pattern of overcaution and his failure to pursue the retreating Lee, relieved McClellan of command in November. From a tactical standpoint, the battle was somewhat inconclusive; the Union army successfully repelled the Confederate invasion but suffered heavier casualties and failed to defeat Lee's army outright. However, it was a significant turning point in the war in favor of the Union due in large part to its political ramifications: the battle's result gave Lincoln the political confidence to issue the Emancipation Proclamation, declaring all those held as slaves within enemy territory free. This effectively discouraged the British and French governments from recognizing the Confederacy, as neither power wished to give the appearance of supporting slavery. 
```

We're honored that you've agreed to write this compelling, epic, gripping and detailed chapter of the documentary. The chapter consists of 12 scenes, summarizing all events in the Background Information and describing their broader historical importance. You will be working with our concept artist Greg Rutkowski. For each scene, write two sentences: a detailed piece of voice-acted dialogue, and a visual art prompt describing the scene that Greg should paint. Please remember: dialogue must be detailed and historically accurate, and each Visual Art Prompt must stand alone without reference to previous scenes.

Scene 1:
```
Dialogue:"""


NEXT_SCENE_PROMPT = """
```
Scene {}:
```"""

THANK_YOU_NOW_REPEAT_IN_JSON_PROMPT = """
```

Well done George, thank you. Now if you would kindly repeat all of the previous scenes but in JSON format, as a list of items, each containing "dialogue" and "visualArtPrompt" keys.

JSON:
```"""

def generate_story_prompts(output_filename, num_scenes=12):
    """ The generate_story_prompts function uses GPT-3 to generate a sequence of
        dialogue and DALL-E / StableDiffusion art prompts.
        The prompts are saved to a JSON file.
    """

    prompt = INIT_PROMPT.format(num_scenes)
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=prompt,
        temperature=0.75,
        max_tokens=255,
        stop='```',
    )
    prompt += response["choices"][0]["text"]
    for i in range(2, 13):
        prompt += NEXT_SCENE_PROMPT.format(i)
        print(prompt)
        response = openai.Completion.create(
            model="text-davinci-002",
            prompt=prompt,
            temperature=0.80,
            max_tokens=255,
            stop='```',
        )
        prompt += response["choices"][0]["text"]
    print(prompt)
    prompt += THANK_YOU_NOW_REPEAT_IN_JSON_PROMPT.format(num_scenes)
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=prompt,
        temperature=0.6,
        max_tokens=2000,
        stop='```',
    )
    output_neural_json = response["choices"][0]["text"]
    print(output_neural_json)
    with open(output_filename, 'w') as fp:
        fp.write(output_neural_json)
    return output_neural_json


def load_neural_json(prompt_file):
    """ Load a file that was generated by GPT3 attempting to output valid JSON
        It might be a list, or it might be a dict containing a list
    """
    try:
        with open(prompt_file) as f:
            data = json.load(f)
        if type(data) == list:
            return data
        for key in data:
            if type(data[key]) == list:
                return data[key]
    except:
        print("Error loading JSON file. Please check the file and try again.")
        return None

'''
The generate_cinematic_from_prompts function does the following:
    Load the JSON file. If it is not correctly formatted, it will throw an error.
    Iterate over the contents of the file. The file consists of a list of dictionaries. Each dictionary has a key "dialogue" and a key "visualArtPrompt".
    Using subcommand.run, pass the "dialogue" to the "say" subcommand. Then, pass the "visualArtPrompt" to the "show" subcommand.
'''
def generate_cinematic_from_prompts(prompt_file, output_video_filename):
    data = load_neural_json(prompt_file)

    video_filenames = []
    for i, item in enumerate(data):
        dialogue_filename = "scene_{:02d}.wav".format(i)
        art_filename = "scene_{:02d}.png".format(i)
        generate_dialogue(item["dialogue"], output_filename=dialogue_filename)
        generate_art(item["visualArtPrompt"], output_filename=art_filename)
        video_filename = make_scene_video(dialogue_filename, art_filename)
        video_filenames.append(video_filename)

    # Concatenate the videos together, adding 1 second of pause in between each
    with open("video_list.txt", "w") as f:
        for video_filename in video_filenames:
            f.write("file '{}'\n".format(video_filename))

            
    music_filename = get_epic_music_mp3() 
    # With ffmpeg, concatenate the videos and add the music at 0.5 volume using -filter_complex amix
    subprocess.run(["ffmpeg", "-y", "-f", "concat",
                    "-safe", "0", "-i", "video_list.txt",
                    "-i", music_filename,
                    "-filter_complex",
                    "[0:a]volume=1.0[voiceover];[1:a]volume=0.15[music];[voiceover][music]amix=inputs=2",
                    "-c:v", "libx264",
                    "-crf", "23",
                    "-preset", "veryfast",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-shortest",
                    output_video_filename])

    # Clean up by making a directory and moving all the scene_{%02d}* files into it
    output_dir = 'story_{}'.format(int(time.time()))
    os.mkdir(output_dir)
    for filename in glob.glob("scene_*.png") + glob.glob("scene_*.wav") + glob.glob("scene_*.mp4"):
        shutil.move(filename, output_dir)

    # Move the video_list.txt file into the output directory
    shutil.move("video_list.txt", output_dir)

    # Move the json file into the output directory
    shutil.move(prompt_file, output_dir)

    print("Done! Video saved to {}".format(output_video_filename))
    return output_video_filename


def make_scene_video(input_wav_audio, input_jpg_frame):
    """ Call ffmpeg to make a video that displays the jpg frame and plays the wav audio """
    output_filename = input_wav_audio.replace(".wav", ".mp4")

    # Generate a video that scrolls inward in a Ken Burns effect
    # Make the video with the moov atom at the start, and yuv420p
    # Ensure that the input audio is muxed into the video
    subprocess.run(["ffmpeg", "-y",
                    "-i", input_jpg_frame,
                    "-i", input_wav_audio,
                    "-movflags", "+faststart",
                    "-pix_fmt", "yuv420p",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-ac", "1",
                    "-filter_complex",
                    "scale=3072:4224, zoompan=z='min(zoom+0.0015,1.4)':d=500:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=512x704",
                    "-shortest", output_filename])
    
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
    generate_story_prompts(output_filename=args.story_json)
    generate_cinematic_from_prompts(prompt_file=args.story_json, output_video_filename=args.output_video)
