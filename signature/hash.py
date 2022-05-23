import argparse
import helpers


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    parser.add_argument("--type", required=True, choices=["256", "512"])
    parser.add_argument("--hash-path", required=True)
    args = parser.parse_args()

    helpers.hash_of_file(args.path, args.hash_path, args.type)
    with open(args.hash_path, "r") as f:
        print("Hash of file contents is: {}".format(f.read()))


if __name__ == "__main__":
    main()
