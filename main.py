from config import Config

from .cli import parse_args
from .app import run


def main() -> None:
    args = parse_args()
    config = Config(
        input=args.input,
        output=args.output,
        base_url=args.base_url,
        model=args.model,
        max_pages=args.max_pages,
        strategy=args.strategy,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )
    run(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
