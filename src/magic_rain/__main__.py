import argparse
from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Magiskt regn")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--demo", action="store_true", help="Starta med simulerad sensor")
    mode.add_argument("--doctor", action="store_true", help="Testa Kinect-djup i 60 s")
    parser.add_argument(
        "--windowed", action="store_true", help="Kör demon i ett fönster"
    )
    args = parser.parse_args(argv)

    if args.windowed and not args.demo:
        parser.error("--windowed kräver --demo")
    if not args.demo:
        from .diagnostics import DOCTOR_DURATION_S, check_depth

        return check_depth(DOCTOR_DURATION_S if args.doctor else 0)

    from .app import run_demo

    print("Magic Rain · Simulerad sensor · F11: helskärm · Esc: avsluta", flush=True)
    return run_demo(windowed=args.windowed)


if __name__ == "__main__":
    raise SystemExit(main())
