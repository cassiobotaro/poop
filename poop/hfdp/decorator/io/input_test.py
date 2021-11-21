from poop.hfdp.decorator.io.lower_case_input_stream import LowerCaseInputStream


def main() -> None:
    try:
        with open("test.txt", "w") as input_file:

            while entry := input():
                input_file.write(entry + "\n")

        with LowerCaseInputStream(open("test.txt", "r")) as output_file:
            for line in output_file:
                print(line.rstrip())

    except IOError as e:
        print(e)
