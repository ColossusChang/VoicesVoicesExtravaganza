# Voices Voices Extravaganza

Voice and speech files for characters from Baldur's Gate games.

## Workflow

Current supported platforms: ElevenLabs, Natural Readers, Play.HT, and Typecast.

### Installing Dependencies

```bash
pip install -r requirements.txt
```

### Preparing the Environment

Make a copy of `.env.template` and rename it to `.env`. Fill in the necessary values for the platform you are using:

- ElevenLabs: Fill in the API key.
- Natural Readers: Log in on the browser. Press F12 and go to the Network tab. Refresh the page and look for a request with an `Authorization` header value. Paste it in the `NATURALREADERS_AUTH` field.
- Typecast: Log in on the browser. Press F12 and go to the Network tab. Refresh the page and look for a request with an `Authorization` header value. Paste it in the `TYPECAST_AUTH` field.
- Play.HT: Fill in `PLAYHT_AUTH` and `PLAYHT_USERID`.

The script expects to find the txts of the lines to be voiced in `bg/BGtxt`. You can change the path in `scripts/utils/utilities.py`. You can find the txts from the discontinued [Infinity Speech Project](https://github.com/B4st13n/InfinitySpeechProject/).

### Voicing a Creature

If the creatureID is already in `scripts/static/voices.json`, that means all its lines have been voiced. If not, pick a suitable voice from a platform of your choice and add the corresponding information to `scripts/static/voices.json`. Remember to keep it sorted in alphabetical order.

Next, run the following command to automatically voice all the lines for the creature using the voice you selected:

```bash
cd scripts
python3 getSound.py -c CREATUREID
```

The generated voices will be downloaded to `bg/vveBG/WAV/`.

Alternatively, if you already have the voice files generated, you can manually add then to the `bg/vveBG/WAV/` directory. Remember to document the voice source in `scripts/static/voices.json`.

## Installing the mod

Copy the contents of `bg/vveBG` to your game directory. Run `setup-vveBG.exe` and follow the instructions.
