"""Song book for the 10-minute compilation.

Each song -> build_<id>/{song_in.json, chords.json, vis.json, bpm}
Word spec: "Text|spoken note:beats note:beats"  (|spoken optional)
Every line is 8 beats; the intro is 8 beats.
"""
import json, pathlib, sys

def W(spec):
    head, *notes = spec.split(" ")
    return [head.replace("_", " "), [[n.split(":")[0], float(n.split(":")[1])] for n in notes]]

def line(tag, *specs):
    ws = [W(s) for s in specs]
    used = sum(b for w in ws for _, b in w[1]); assert used <= 8, (tag, used)
    return [tag, ws + ([None] if used < 8 else [])]

R = ["#ff3b3b", "#2f8bff", "#ffc400", "#2fd65a", "#ff5fa2", "#7b5bff", "#ff8a00", "#14c3c3", "#a0522d", "#3b3b55"]

SONGS = {}

# ---------------- Numbers ----------------
L1 = line("n15", "One C4:1", "two D4:1", "three E4:1", "four F4:1", "five, G4:2")
L2 = line("n610", "Six A4:1", "seven B4:1", "eight C5:1", "nine D5:1", "ten! C5:2")
L3 = line("ch_count", "Count E4:1", "with G4:1", "me, C5:2", "count E4:1", "with G4:1", "me! C5:2")
L4 = line("float", "Ten G4:1", "little E4:1", "balloons F4:1", "up A4:1", "so B4:1", "high! C5:2")
L9 = line("ch_yay", "Yay! C5:2", "We G4:.5", "can A4:.5", "count B4:1", "to B4:1", "ten! C5:2")
SONGS["numbers"] = dict(
    title="Numbers Song!", bpm=116, theme="day",
    lines=[L1, L2, L3, L4] * 3 + [L9],
    chords=[["C","F","G","C"]] + [["C","C","F","C"], ["F","G","C","C"], ["C","C","Am","C"], ["C","F","G","C"]] * 3 + [["C","G","C","C"]],
    items=[dict(model="balloon", label=str(i + 1), color=R[i]) for i in range(10)],
    show={"n15": dict(mode="perWord", items=[0,1,2,3,4], words=["1","2","3","4","5"]),
          "n610": dict(mode="perWord", items=[5,6,7,8,9], words=["6","7","8","9","10"], keep=[0,1,2,3,4]),
          "ch_count": dict(mode="row", items=list(range(10)), text="COUNT!"),
          "float": dict(mode="float", items=list(range(10)), text="10 BALLOONS!"),
          "ch_yay": dict(mode="row", items=list(range(10)), text="YAY!")})

# ---------------- Shapes ----------------
S = [line("s0", "Circle, E4:.5 G4:.5", "circle, E4:.5 G4:.5", "round C5:1", "and B4:1", "round! A4:2"),
     line("s1", "Square, A4:1", "square, A4:1", "four F4:1", "sides, G4:1", "see? A4:2"),
     line("s2", "Triangle, G4:.5 E4:.5", "triangle, G4:.5 E4:.5", "one, C5:1", "two, B4:1", "three! A4:2"),
     line("s3", "Star, G4:1", "star, G4:1", "shining A4:.5 B4:.5", "bright! C5:2"),
     line("s4", "Heart, E4:1", "heart, E4:1", "I F4:1", "love D4:1", "you! C4:2"),
     line("ch_shapes", "Shapes, E4:1", "shapes, G4:1", "everywhere! C5:1 B4:1 C5:2"),
     line("ch_all", "Circle, C5:1", "square, A4:1", "triangle, G4:1", "star, E4:1", "heart! C5:2")]
SONGS["shapes"] = dict(
    title="Shapes Song!", bpm=112, theme="day", lines=S * 3,
    chords=[["C","F","G","C"]] + [["C","C","C","F"], ["F","F","C","F"], ["C","C","G","F"], ["C","C","G","C"], ["C","C","G","C"], ["C","C","G","C"], ["C","F","C","C"]] * 3,
    items=[dict(model="shape", kind=k, color=c) for k, c in
           [("circle", "#ff3b3b"), ("square", "#2f8bff"), ("triangle", "#2fd65a"), ("star", "#ffc400"), ("heart", "#ff5fa2")]],
    show={**{f"s{i}": dict(mode="solo", item=i, text=n) for i, n in enumerate(["CIRCLE!", "SQUARE!", "TRIANGLE!", "STAR!", "HEART!"])},
          "ch_shapes": dict(mode="row", items=[0,1,2,3,4], text="SHAPES!"),
          "ch_all": dict(mode="row", items=[0,1,2,3,4], hl=True, text="")})

# ---------------- Fruits ----------------
F = [line("f0", "Crunchy E4:.5 G4:.5", "apple, A4:.5 G4:.5", "yum, C5:1", "yum, C5:1", "yum! C5:2"),
     line("f1", "Yellow E4:.5 G4:.5", "banana, A4:.5 G4:.5", "yum, D5:1", "yum, D5:1", "yum! C5:2"),
     line("f2", "Juicy F4:.5 A4:.5", "orange, B4:.5 A4:.5", "yum, B4:1", "yum, B4:1", "yum! G4:2"),
     line("f3", "Purple E4:.5 G4:.5", "grapes, A4:1", "yum, C5:1", "yum, C5:1", "yum! C5:2"),
     line("f4", "Sweet G4:1", "strawberry, A4:.5 G4:.5", "yum, D4:1", "yum, E4:1", "yum! C4:2"),
     line("ch_fruits", "Fruits E4:.5", "are G4:.5", "yummy, C5:.5 C5:.5", "eat B4:1", "them A4:1", "up! G4:2"),
     line("ch_all", "Apple, C5:1", "banana, A4:1", "orange, G4:1", "grapes, E4:1", "strawberry! C5:2")]
SONGS["fruits"] = dict(
    title="Yummy Fruits!", bpm=112, theme="day", lines=F * 2,
    chords=[["C","F","G","C"]] + [["C","F","C","C"], ["C","F","G","C"], ["F","F","G","G"], ["C","F","C","C"], ["C","C","G","C"], ["C","C","G","C"], ["C","F","C","C"]] * 2,
    items=[dict(model=m) for m in ["apple", "banana", "orange", "grapes", "strawberry"]],
    show={**{f"f{i}": dict(mode="solo", item=i, text=n) for i, n in enumerate(["APPLE!", "BANANA!", "ORANGE!", "GRAPES!", "STRAWBERRY!"])},
          "ch_fruits": dict(mode="row", items=[0,1,2,3,4], text="YUMMY!"),
          "ch_all": dict(mode="row", items=[0,1,2,3,4], hl=True, text="")})

# ---------------- Animals ----------------
A = [line("a0", "The C4:.5", "cow E4:.5", "says G4:1", "moo, C5:1", "moo, C5:1", "moo! C5:2"),
     line("a1", "The C4:.5", "pig E4:.5", "says G4:1", "oink, A4:1", "oink, A4:1", "oink! A4:2"),
     line("a2", "The C4:.5", "duck E4:.5", "says G4:1", "quack, B4:1", "quack, B4:1", "quack! G4:2"),
     line("a3", "The C4:.5", "cat F4:.5", "says A4:1", "meow, C5:1", "meow, B4:1", "meow! A4:2"),
     line("a4", "The D4:.5", "dog G4:.5", "says F4:1", "woof, E4:1", "woof, D4:1", "woof! C4:2"),
     line("ch_farm", "Animals, E4:.5 G4:.5", "animals, E4:.5 G4:.5", "on C5:1", "the B4:1", "farm! C5:2"),
     line("ch_all", "Moo, C5:1", "oink, A4:1", "quack, G4:1", "meow, E4:1", "woof! C5:2")]
SONGS["animals"] = dict(
    title="Farm Animals!", bpm=108, theme="day", lines=A * 2,
    chords=[["C","F","G","C"]] + [["C","C","F","C"], ["C","C","F","F"], ["C","C","G","G"], ["F","F","C","F"], ["G","G","C","C"], ["C","C","G","C"], ["C","F","C","C"]] * 2,
    items=[dict(model=m) for m in ["cow", "pig", "duck", "cat", "dog"]],
    show={**{f"a{i}": dict(mode="solo", item=i, text=n) for i, n in enumerate(["MOO!", "OINK!", "QUACK!", "MEOW!", "WOOF!"])},
          "ch_farm": dict(mode="row", items=[0,1,2,3,4], text="FARM!"),
          "ch_all": dict(mode="row", items=[0,1,2,3,4], hl=True, text="")})

# ---------------- ABC ----------------
SP = dict(A="ay", B="bee", C="see", D="dee", E="ee", F="eff", G="gee", H="aitch", I="eye", J="jay", K="kay", L="el", M="em", N="en",
          O="oh", P="pee", Q="cue", R="are", S="ess", T="tee", U="you", V="vee", W="double_you", X="ex", Y="why", Z="zee")
def letters(tag, chars, notes, last=1):
    specs = [f"{c}|{SP[c]} {n}:{last if k == len(chars) - 1 else 1}" for k, (c, n) in enumerate(zip(chars, notes))]
    return line(tag, *specs)
B1 = letters("l1", "ABCDEFG", ["C4","D4","E4","F4","G4","A4","G4"])
B2 = letters("l2", "HIJKLMN", ["F4","E4","D4","E4","F4","G4","E4"])
B3 = letters("l3", "OPQRSTU", ["C5","B4","A4","G4","A4","B4","C5"])
B4 = letters("l4", "VWXYZ", ["G4","G4","A4","B4","C5"], last=2)
B5 = line("ch_az", "A|ay E4:1", "to G4:1", "Z, C5:2", "sing B4:1", "with A4:1", "me! G4:2")
B6 = line("ch_fun", "Letters E4:.5 F4:.5", "are G4:1", "so A4:1", "fun! C5:3")
abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SONGS["abc"] = dict(
    title="ABC Song!", bpm=120, theme="day", lines=[B1, B2, B3, B4, B5, B6] * 3,
    chords=[["C","F","G","C"]] + [["C","C","F","C"], ["F","C","G","C"], ["C","G","F","C"], ["C","C","G","C"], ["C","C","G","C"], ["C","F","F","C"]] * 3,
    items=[dict(model="letter", ch=c, color=R[i % 8]) for i, c in enumerate(abc)],
    show={"l1": dict(mode="perWord", items=list(range(0, 7)), words=list("ABCDEFG")),
          "l2": dict(mode="perWord", items=list(range(7, 14)), words=list("HIJKLMN")),
          "l3": dict(mode="perWord", items=list(range(14, 21)), words=list("OPQRSTU")),
          "l4": dict(mode="perWord", items=list(range(21, 26)), words=list("VWXYZ")),
          "ch_az": dict(mode="grid", items=list(range(26)), text="A to Z!"),
          "ch_fun": dict(mode="grid", items=list(range(26)), text="FUN!")})

# ---------------- Vehicles ----------------
V = [line("v0", "The C4:.5", "car E4:.5", "goes G4:1", "beep, C5:1", "beep, C5:1", "beep! C5:2"),
     line("v1", "The C4:.5", "bus E4:.5", "goes G4:1", "honk, A4:1", "honk, A4:1", "honk! A4:2"),
     line("v2", "The C4:.5", "train E4:.5", "goes G4:1", "choo, B4:1", "choo, B4:1", "choo! G4:2"),
     line("v3", "The C4:.5", "plane F4:.5", "goes A4:1", "zoom, C5:1", "zoom, B4:1", "zoom! A4:2"),
     line("v4", "The D4:.5", "boat G4:.5", "goes F4:1", "toot, E4:1", "toot, D4:1", "toot! C4:2"),
     line("ch_go", "Go, E4:1", "go, F4:1", "go! G4:1", "Here A4:1", "we B4:1", "go! C5:2"),
     line("ch_all", "Car, C5:1", "bus, A4:1", "train, G4:1", "plane, E4:1", "boat! C5:2")]
SONGS["vehicles"] = dict(
    title="Things That Go!", bpm=112, theme="day", lines=V * 2,
    chords=SONGS["animals"]["chords"],
    items=[dict(model=m) for m in ["car", "bus", "train", "plane", "boat"]],
    show={**{f"v{i}": dict(mode="solo", item=i, text=n) for i, n in enumerate(["BEEP!", "HONK!", "CHOO CHOO!", "ZOOM!", "TOOT!"])},
          "ch_go": dict(mode="row", items=[0,1,2,3,4], text="GO GO GO!"),
          "ch_all": dict(mode="row", items=[0,1,2,3,4], hl=True, text="")})

# ---------------- Planets ----------------
P = [line("p1", "Mercury, E4:.5 G4:.5", "Venus, A4:.5 G4:.5", "Earth C5:1", "and B4:1", "Mars! A4:2"),
     line("p2", "Jupiter, F4:.5 A4:.5", "Saturn, B4:.5 A4:.5", "round C5:1", "and B4:1", "round! G4:2"),
     line("p3", "Uranus, E4:.5 G4:.5", "Neptune, A4:.5 G4:.5", "far C5:1", "away! B4:1 C5:2"),
     line("p4", "Eight G4:1", "planets A4:.5 G4:.5", "in E4:1", "the D4:1", "sky! C4:2"),
     line("ch_zoom", "Zoom, E4:1", "zoom, G4:1", "into C5:.5 B4:.5", "space! C5:3"),
     line("ch_blast", "Three, G4:1", "two, E4:1", "one, C4:1", "blast G4:1", "off! C5:2")]
SONGS["planets"] = dict(
    title="Planets Song!", bpm=104, theme="space", lines=P * 2,
    chords=[["C","F","G","C"]] + [["C","F","C","F"], ["F","F","C","G"], ["C","F","C","C"], ["C","F","G","C"], ["C","C","G","C"], ["C","C","G","C"]] * 2,
    items=[dict(model="planet", kind=k) for k in ["mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune"]],
    show={"p1": dict(mode="perWord", items=[0, 1, 2, -1, 3], words=["MERCURY", "VENUS", "EARTH", None, "MARS"]),
          "p2": dict(mode="perWord", items=[4, 5, -1, -1, -1], words=["JUPITER", "SATURN", None, None, None], keep=[0,1,2,3]),
          "p3": dict(mode="perWord", items=[6, 7, -1, -1], words=["URANUS", "NEPTUNE", None, None], keep=[0,1,2,3,4,5]),
          "p4": dict(mode="row", items=list(range(8)), text="8 PLANETS!"),
          "ch_zoom": dict(mode="rocket", items=[], text="ZOOM!"),
          "ch_blast": dict(mode="blast", items=[], text="")})

if __name__ == "__main__":
    for sid, s in SONGS.items():
        d = pathlib.Path(f"build_{sid}"); d.mkdir(exist_ok=True)
        assert len(s["chords"]) == len(s["lines"]) + 1, (sid, len(s["chords"]), len(s["lines"]))
        json.dump(s["lines"], open(d / "song_in.json", "w"))
        json.dump(s["chords"], open(d / "chords.json", "w"))
        json.dump({k: s[k] for k in ("title", "theme", "items", "show")}, open(d / "vis.json", "w"))
        (d / "bpm").write_text(str(s["bpm"]))
        print(sid, len(s["lines"]), "lines", round((8 + 8 * len(s["lines"])) * 60 / s["bpm"], 1), "s")
