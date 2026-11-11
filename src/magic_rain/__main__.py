import argparse
from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    from .settings import OPTIONS

    parser = argparse.ArgumentParser(description="Magiskt regn")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--demo", action="store_true", help="Starta med simulerad sensor")
    mode.add_argument("--doctor", action="store_true", help="Testa Kinect-djup i 60 s")
    mode.add_argument("--displays", action="store_true", help="Visa bildskärmar")
    parser.add_argument(
        "--windowed", action="store_true", help="Kör i ett fönster"
    )
    parser.add_argument("--display", type=int, metavar="N", help="Välj bildskärm N")
    parser.add_argument(
        "--scene", choices=OPTIONS["scene"], help="Välj bana i demoläget"
    )
    args = parser.parse_args(argv)

    if (args.doctor or args.displays) and (args.windowed or args.display is not None):
        parser.error("Bildskärmsval gäller endast när regnscenen startas")
    if args.display is not None and args.display < 1:
        parser.error("--display börjar på 1")
    if args.scene is not None and not args.demo:
        parser.error("--scene kräver --demo")
    if args.displays:
        from .render.output import list_displays

        return list_displays()
    if args.doctor:
        from .diagnostics import check_depth

        return check_depth()

    from .app import run_demo, run_live

    if args.demo:
        print(
            "Magic Rain · Simulerad sensor · F11: helskärm · Esc: avsluta",
            flush=True,
        )
        return run_demo(
            windowed=args.windowed, display=args.display, scene=args.scene or "Regn"
        )
    return run_live(windowed=args.windowed, display=args.display)


if __name__ == "__main__":
    raise SystemExit(main())
