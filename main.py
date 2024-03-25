from pathlib import Path
import os
from argparse import ArgumentParser


def setup_parser():
    help_text = """
    Command list:\n
        -f = File to be  processed. [ -f File/path.txt ]\n
        -s = A single line comment delimiter to use.  [ -s "#" ]\n
        -b = The beginning of a multi-line comment delimiter pair to use. [ -b "/*" ]\n
        -e = The ending of a multi-line comment delimiter pair to use. [ -e "*/" ]\n
    """
    parser = ArgumentParser(description='Removes text based on the submitted delimiter(s).', add_help=False)
    parser.add_argument('-f', '--File', action='append',
                        help='File to be processed.')
    parser.add_argument('-s', '--Single', action='append',
                        help='Text on a line starting with this delimiter will be removed.')
    parser.add_argument('-b', '--Beginning', action='append',
                        help='Starting with this delimiter, text will be removed until the ending delimiter is found.')
    parser.add_argument('-e', '--Ending', action='append',
                        help='All text and this delimiter will be removed if proceeded by a beginning delimiter.')
    parser.add_argument('-r', '--Replace', action='store_true',
                        help='Replace the original file')
    return parser


def main() -> int:

    parser = setup_parser()
    args = parser.parse_args()

    if args.File is not None:
        original = args.File[0]


        # Create the output file
        suffix = Path(original).suffix
        temp = original.replace(suffix, ('-Temp' + suffix))

        # Determine if we need a working copy.
        if args.Replace:
            changed = original
        else:
            changed = args.File[0].replace(suffix, ('-Changed' + suffix))
            changed_file = open(changed, 'w')
            original_file = open(original, 'r')
            for line in original_file.readlines():
                changed_file.write(line)
            original_file.close()
            changed_file.close()


        # Remove single line comments
        if args.Single is not None:
            changed_file = open(changed, 'r')
            temp_file = open(temp, 'w')

            for line in changed_file.readlines():
                split = line.split(args.Single[0])
                temp_file.write(split[0])

            temp_file.close()
            changed_file.close()
            os.remove(changed)
            os.rename(temp, changed)

        # Remove comments that are bracketed
        if (args.Beginning is not None) & (args.Ending is not None):
            begin = args.Beginning[0]
            end = args.Ending[0]

            # Remove comments that are bracket on one line
            changed_file = open(changed, 'r')
            temp_file = open(temp, 'w')

            for line in changed_file.readlines():
                while True:
                    if (begin in line) and (end in line):
                        before = line.split(begin)[0]
                        after = before[1].split(end)[0]
                        removed = before + after
                        temp_file.write(removed)
                    else:
                        break

            temp_file.close()
            changed_file.close()
            os.remove(changed)
            os.rename(temp, changed)

            # Remove comments across multiple lines
            changed_file = open(changed, 'r')
            temp_file = open(temp, 'w')
            comment = False
            for line in changed.readlines():

                # If a comment starts, write the prior text just in case.
                if begin in line:
                    comment = True
                    before = line.split(begin)[0]
                    temp_file.write(before)

                # If not in a comment write the whole line, otherwise skip.
                if not comment:
                    temp_file.write(line)

                # If a comment ends, write ending text of the line just in case.
                if end in line:
                    comment = False
                    after = line.split(begin)[1]
                    temp_file.write(after)

                temp_file.close()
                changed_file.close()
                os.remove(changed)
                os.rename(temp, changed)

    return 0


if __name__ == '__main__':
    main()
