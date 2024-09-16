import os
import random
import re
from tqdm import tqdm
import difflib


def load_game_ids(file_path):
    game_ids = {}
    korean_prefixes = ('SLKA', 'SCKA')

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(" ", 1)
            if len(parts) == 2:
                code, name = parts
                if not code.startswith(korean_prefixes):
                    game_ids[name] = code
    return game_ids


def rename_files(directory, game_ids):
    files = [
        f for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
    ]
    renamed_count = 0
    progress_bar = tqdm(files, desc="Renaming files", unit="file")
    for filename in progress_bar:
        file_path = os.path.join(directory, filename)
        name_without_ext, ext = os.path.splitext(filename)
        best_match = None
        best_ratio = 0
        for game_name, game_code in game_ids.items():
            ratio = difflib.SequenceMatcher(
                None, name_without_ext.lower(), game_name.lower()
            ).ratio()
            if ratio > best_ratio and ratio > 0.8:  # Adjustable threshold
                best_ratio = ratio
                best_match = (game_name, game_code)

        if best_match:
            new_filename = f"{best_match[1]} {filename}"
            new_file_path = os.path.join(directory, new_filename)
            os.rename(file_path, new_file_path)
            renamed_count += 1
            progress_bar.set_postfix(renamed=renamed_count, refresh=True)

    print(f"Total files renamed: {renamed_count}")


def read_random_lines(filename, n):
    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()
    return random.sample(lines, min(n, len(lines)))


def create_iso_files(lines, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    for line in lines:
        game_info = line.split(" ", 1)[-1].strip()
        game_name = game_info
        game_name = re.sub(r'[<>:"/\\|?*]', "_", game_name)
        filename = f"{game_name}.iso"
        filepath = os.path.join(directory, filename)
        try:
            open(filepath, "w").close()
            print(f"Created: {filename}")
        except OSError as e:
            print(f"Error creating {filename}: {e}")


def rename_isos():
    game_ids_file = "gameid.txt"
    iso_directory = input("Enter the full path to your ISO directory: ")

    game_ids = load_game_ids(game_ids_file)

    try:
        rename_files(iso_directory, game_ids)

        remove_korean = input(
            "Do you want to remove Korean titles? (y/n): "
            ).lower()
        if remove_korean == 'y':
            remove_korean_titles(iso_directory)
    except FileNotFoundError:
        print(
            f"Error: The directory '{iso_directory}' was not found. Please check the path and try again."
        )
    except PermissionError:
        print(
            f"Error: You don't have permission to access the directory '{iso_directory}'. Please check your permissions and try again."
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def create_dummy_isos():
    gameid_file = "gameid.txt"
    iso_directory = "testISOs"
    num_files = input(
        "Enter the number of dummy ISO files to create (default is 100): "
    )
    num_files = int(num_files) if num_files.strip() else 100

    random_lines = read_random_lines(gameid_file, num_files)
    create_iso_files(random_lines, iso_directory)

    print(f"Created {num_files} random .iso files in {iso_directory}")


def display_menu():
    display_banner()
    print("ISO Renamer and Creator")
    print("1. Rename ISO files")
    print("2. Create dummy ISO files with names from GameIDs.txt")
    print("0. Exit")
    return input("Enter your choice (0-2): ")


def display_banner():
    banner = """
██╗███████╗ ██████╗ ███╗   ███╗ █████╗  ██████╗ ██╗ ██████╗
██║██╔════╝██╔═══██╗████╗ ████║██╔══██╗██╔════╝ ██║██╔════╝
██║███████╗██║   ██║██╔████╔██║███████║██║  ███╗██║██║
██║╚════██║██║   ██║██║╚██╔╝██║██╔══██║██║   ██║██║██║
██║███████║╚██████╔╝██║ ╚═╝ ██║██║  ██║╚██████╔╝██║╚██████╗
╚═╝╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝ ╚═════╝
    """
    print(banner)


def remove_korean_titles(directory):
    korean_prefixes = ('SLKA', 'SCKA')
    removed_count = 0

    files = [f for f in os.listdir(directory)
             if os.path.isfile(os.path.join(directory, f))]
    progress_bar = tqdm(files, desc="Removing Korean titles", unit="file")

    for filename in progress_bar:
        if filename[:4] in korean_prefixes:
            file_path = os.path.join(directory, filename)
            try:
                os.remove(file_path)
                removed_count += 1
            except Exception as e:
                print(f"Error removing {filename}: {e}")

        progress_bar.set_postfix(removed=removed_count, refresh=True)

    print(f"Total Korean titles removed: {removed_count}")


def main():
    while True:
        choice = display_menu()

        if choice == "1":
            rename_isos()
            print("Renaming operation completed. Exiting the program.")
            break
        elif choice == "2":
            create_dummy_isos()
        elif choice == "0":
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
