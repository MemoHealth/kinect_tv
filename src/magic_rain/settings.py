import json
import os
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from tempfile import NamedTemporaryFile

FUNHOUSE_STRENGTH = {"Lustiga huset · Konvex": -0.37, "Lustiga huset · Konkav": 0.44}
PAINT_SCENE = "Ljusmåleri"
PAINT_EXPLOSION = "Paint Explosion"
GALAXY_SCENE = "Galaxy Mirror"
AQUARIUM_SCENE = "Living Aquarium"
HALF_LIVES = {"Kort": 1.5, "Normal": 3.0, "Lång": 6.0}
PALETTES = {
    "Norrsken": ((84, 221, 204), (255, 152, 135), (174, 155, 250)),
    "Solnedgång": ((255, 199, 104), (242, 121, 171), (119, 190, 251)),
    "Havsglas": ((149, 234, 164), (95, 171, 247), (247, 151, 130)),
}

OPTIONS = {
    "scene": (
        "Regn", "Snö", *FUNHOUSE_STRENGTH, PAINT_SCENE, PAINT_EXPLOSION,
        GALAXY_SCENE, AQUARIUM_SCENE,
    ),
    "sound": ("Av", "Lågt", "Normal"),
    "intensity": ("Milt", "Normalt", "Livligt"),
    "mirror": ("På", "Av"),
    "zone": ("Bred", "Centrerad"),
    "distance": ("Normalt", "Nära"),
    "color_assist": ("På", "Av"),
    "paint_fade": tuple(HALF_LIVES),
    "paint_palette": tuple(PALETTES),
}


@dataclass(frozen=True)
class Settings:
    scene: str = "Regn"
    sound: str = "Lågt"
    intensity: str = "Normalt"
    mirror: str = "På"
    zone: str = "Bred"
    distance: str = "Normalt"
    color_assist: str = "På"
    paint_fade: str = "Normal"
    paint_palette: str = "Norrsken"

    def change(self, key: str, delta: int) -> "Settings":
        values = OPTIONS[key]
        index = (values.index(getattr(self, key)) + delta) % len(values)
        return replace(self, **{key: values[index]})


def settings_path() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    return base / "Magic Rain" / "settings.json"


def load_settings(path: Path) -> Settings:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return Settings()
    if not isinstance(data, dict) or type(data.get("version")) is not int:
        return Settings()
    if data["version"] != 1:
        return Settings()
    valid = {
        key: data[key] for key, values in OPTIONS.items() if data.get(key) in values
    }
    if valid.get("scene") in FUNHOUSE_STRENGTH:
        valid.pop("scene")
    return Settings(**valid)


def save_settings(path: Path, settings: Settings) -> bool:
    temporary: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as output:
            temporary = Path(output.name)
            values = asdict(settings)
            if settings.scene in FUNHOUSE_STRENGTH:
                values["scene"] = "Regn"
            json.dump({"version": 1, **values}, output, ensure_ascii=False)
        temporary.replace(path)
        return True
    except OSError:
        return False
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
