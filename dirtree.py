import os
import argparse

# Tree components (can be customized)
PREFIX_MIDDLE = "├── "
PREFIX_LAST = "└── "
PREFIX_PARENT_MIDDLE = "│   "
PREFIX_PARENT_LAST = "    "

def generate_tree(directory, prefix="", level=-1, limit_depth=None,
                  show_hidden=False, dir_only=False, ignore_list=None):
    """
    Generates and prints the directory tree structure.

    Args:
        directory (str): The path to the directory to scan.
        prefix (str): The prefix string for the current level (for tree drawing).
        level (int): Current depth level. -1 for the root.
        limit_depth (int, optional): Maximum depth to display. None for no limit.
        show_hidden (bool): Whether to show hidden files/directories (starting with '.').
        dir_only (bool): If True, only show directories.
        ignore_list (list, optional): A list of names to ignore.
    """
    if ignore_list is None:
        ignore_list = []

    if level == -1: # Root call
        print(os.path.basename(os.path.abspath(directory)))
        level = 0 # Start actual depth counting

    if limit_depth is not None and level >= limit_depth:
        return 0, 0 # dir_count, file_count

    try:
        # Get all items, then filter
        all_items = os.listdir(directory)
        items = []
        for item_name in all_items:
            if not show_hidden and item_name.startswith('.'):
                continue
            if item_name in ignore_list:
                continue
            items.append(item_name)
        items.sort() # Sort for consistent output
    except PermissionError:
        print(f"{prefix}{PREFIX_MIDDLE}[Error: Permission Denied for {os.path.basename(directory)}]")
        return 0, 0
    except FileNotFoundError:
        print(f"{prefix}{PREFIX_MIDDLE}[Error: Directory Not Found: {os.path.basename(directory)}]")
        return 0,0

    dir_count = 0
    file_count = 0
    pointers = [PREFIX_MIDDLE] * (len(items) - 1) + [PREFIX_LAST]

    for pointer, item_name in zip(pointers, items):
        path = os.path.join(directory, item_name)
        is_dir = os.path.isdir(path)

        if dir_only and not is_dir:
            continue # Skip files if only directories are requested

        print(f"{prefix}{pointer}{item_name}")

        if is_dir:
            dir_count += 1
            # Determine the new prefix for children
            extension = PREFIX_PARENT_MIDDLE if pointer == PREFIX_MIDDLE else PREFIX_PARENT_LAST
            # Recursively call for subdirectories
            sub_d_count, sub_f_count = generate_tree(
                path,
                prefix + extension,
                level + 1,
                limit_depth,
                show_hidden,
                dir_only,
                ignore_list
            )
            dir_count += sub_d_count
            file_count += sub_f_count
        else:
            file_count += 1
            
    return dir_count, file_count

def main():
    parser = argparse.ArgumentParser(
        description="Generate a directory tree structure.",
        formatter_class=argparse.RawTextHelpFormatter # For better help text formatting
    )
    parser.add_argument(
        "directory",
        nargs="?", # Makes the argument optional
        default=".", # Default to current directory
        help="The directory to scan (default: current directory)."
    )
    parser.add_argument(
        "-L", "--level",
        type=int,
        metavar="DEPTH",
        help="Descend only DEPTH levels deep."
    )
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Show all files (including hidden ones starting with '.')."
    )
    parser.add_argument(
        "-d", "--dir-only",
        action="store_true",
        help="List directories only."
    )
    parser.add_argument(
        "-I", "--ignore",
        metavar="PATTERN",
        action="append", # Allows multiple -I arguments
        default=[],
        help="Do not list files/directories that match PATTERN.\n"
             "Can be used multiple times (e.g., -I __pycache__ -I .git)."
    )
    parser.add_argument(
        "--no-indent", # Example of a less common option
        action="store_true",
        help="Turn off tree indent characters (useful for simple lists)."
    )

    args = parser.parse_args()

    if args.no_indent:
        global PREFIX_MIDDLE, PREFIX_LAST, PREFIX_PARENT_MIDDLE, PREFIX_PARENT_LAST
        PREFIX_MIDDLE = ""
        PREFIX_LAST = ""
        PREFIX_PARENT_MIDDLE = ""
        PREFIX_PARENT_LAST = ""


    target_dir = os.path.abspath(args.directory)

    if not os.path.isdir(target_dir):
        print(f"Error: '{target_dir}' is not a valid directory.")
        return

    print(f"Generating tree for: {target_dir}")
    print("-" * 30)

    dir_count, file_count = generate_tree(
        target_dir,
        limit_depth=args.level,
        show_hidden=args.all,
        dir_only=args.dir_only,
        ignore_list=args.ignore
    )

    print("-" * 30)
    summary = []
    if not args.dir_only:
        summary.append(f"{dir_count} director{'y' if dir_count == 1 else 'ies'}")
        summary.append(f"{file_count} file{'s' if file_count != 1 else ''}")
    else:
        summary.append(f"{dir_count} director{'y' if dir_count == 1 else 'ies'}")
    
    print(", ".join(summary))


if __name__ == "__main__":
    main()