# Mp4 to translation

![Mp4 to translation](img/readme.jpg)

Me and my girlfriend needed a tool to translate puppy videos from Swedish to English.

It's quite generic, so I figured I can just publish it on git.

Any language that OpenAI whisperer supports will work, and it will translate to English, one sentence per row.

## How to use

1. Get your [OpenAI API key ready](https://platform.openai.com/docs/api-reference/authentication)
   1. This needs to be set as an environment variable `OPENAI_API_KEY`
   1. See [openai python sdk](https://github.com/openai/openai-python) for additional details
1. [Install ffmpeg](https://www.ffmpeg.org/download.html)
1. Download some nice juicy mp4's you'd like to see the translation of
1. Put them in the "to_transcribe" directory
1. Run the script `./generate_subtitles.py`
1. Follow the wizard
