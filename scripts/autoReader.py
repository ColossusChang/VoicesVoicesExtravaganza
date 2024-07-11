import json
from utils.logging_config import logger
from utils.utilities import loadDictFromJson

voices = loadDictFromJson("static/voices.json")
companions = loadDictFromJson("static/companions.json")
creatures = loadDictFromJson("static/creatures.json")
similarContents = loadDictFromJson("static/allSimilarContents.json")
