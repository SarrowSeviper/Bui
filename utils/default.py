import time
import json
import discord

from collections import namedtuple


def get(file):
    try:
        with open(file, encoding='utf8') as data:
            return json.load(data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    except AttributeError:
        raise AttributeError("Unknown argument")
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")


def timetext(name):
    return f"{name}_{int(time.time())}.txt"


def date(target):
    return target.strftime("%d %B %Y, %H:%M")


def responsible(target, reason):
    responsible = f"[ {target} ]"
    if reason is None:
        return f"{responsible} no reason given..."
    return f"{responsible} {reason}"


def actionmessage(case, member: discord.Member, mass=False):
    output = f"{case} **{member.name}** (**{member.id}**)"

    if mass is True:
        output = f"**{case}** the IDs/Users"

    return f"Successfully {output}"
