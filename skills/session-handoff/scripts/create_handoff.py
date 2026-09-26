"""Create a handoff draft in the selected project; never commit or push."""
from _handoff import main

if __name__ == "__main__":
    raise SystemExit(main("create"))
