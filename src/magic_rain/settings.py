import json
import os
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from tempfile import NamedTemporaryFile

OPTIONS = {
    "scene": ("Regn", "Snö"),
    "sound": ("Av", "Lågt", "Normal"),
    "intensity": ("Milt", "Normalt", "Livligt"),
    "mirror": ("På", "Av"),
    "zone": ("Bred", "Centrerad"),
    "distance": ("Normalt", "Nära"),
}


@dataclass(frozen=True)
class Settings:
    scene: str = "Regn"
    sound: str = "Lågt"
    intensity: str = "Normalt"
    mirror: str = "På"
    zone: str = "Bred"
    distance: str = "Normalt"

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
    return Settings(**valid)


def save_settings(path: Path, settings: Settings) -> bool:
    temporary: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as output:
            temporary = Path(output.name)
            json.dump({"version": 1, **asdict(settings)}, output, ensure_ascii=False)
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
