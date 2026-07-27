progress = {
    "upload": {
        "percent": 0,
        "step": "",
    },
    "keywords": {
        "percent": 0,
        "step": "",
    },
}


def update_upload(percent, step):
    progress["upload"]["percent"] = percent
    progress["upload"]["step"] = step


def update_keywords(percent, step):
    progress["keywords"]["percent"] = percent
    progress["keywords"]["step"] = step


def get_progress():
    return progress