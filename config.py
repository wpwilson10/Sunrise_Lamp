import ujson

with open("config.json", "r") as f:
    CONFIG = ujson.load(f)
