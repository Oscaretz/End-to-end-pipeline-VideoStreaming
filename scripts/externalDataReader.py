from pathlib import Path
import json
import pandas as pd

def get_base_dir():
    return Path(__file__).resolve().parent.parent

def read_json_file(filename: str) -> dict:
    # Paths to the SQL scripts.
    BASE_DIR = get_base_dir()
    # Change path for the one with the correct folder when needed.
    file_path = BASE_DIR / "data" / "portfolio" / filename

    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def read_csv_file(filename: str) -> pd.DataFrame:
    # Paths to the SQL scripts.
    BASE_DIR = get_base_dir()
    # Change path for the one with the correct folder when needed.
    file_path = BASE_DIR / "data" / "portfolio" / filename

    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    return pd.read_csv(file_path)

def main():
    # Example usage
    json_data = read_json_file("content.json")
    print("JSON content:", json_data)

    csv_data = read_csv_file("users.csv")
    print("\nCSV content (head):")
    print(csv_data.head())

    csv_data = read_csv_file("viewing_sessions.csv")
    print("\nCSV content (head):")
    print(csv_data.head())

if __name__ == "__main__":
    main()