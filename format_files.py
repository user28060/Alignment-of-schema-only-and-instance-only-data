import os
import subprocess


def format_files(directory="./src/"):
    """
    Traverse all .py and README.md files in the given directory and subdirectories,
    and format them using autoflake, isort, black, and mdformat.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)

            # Process Python files
            if file.endswith(".py"):
                print(f"Processing Python file: {file_path}")
                try:
                    # Remove unused variables and imports with autoflake
                    subprocess.run(
                        [
                            "poetry",
                            "run",
                            "autoflake",
                            "--in-place",
                            "--remove-unused-variables",
                            "--remove-all-unused-imports",
                            file_path,
                        ],
                        check=True,
                    )

                    # Sort imports with isort
                    subprocess.run(["poetry", "run", "isort", file_path], check=True)

                    # Format code with black
                    subprocess.run(["poetry", "run", "black", file_path], check=True)

                    print(f"Formatted Python file: {file_path}")
                except subprocess.CalledProcessError as e:
                    print(f"Error processing {file_path}: {e}")

            # Process Markdown files
            if file.lower() == "readme.md":
                print(f"Processing Markdown file: {file_path}")
                try:
                    # Format Markdown with mdformat
                    subprocess.run(["poetry", "run", "mdformat", file_path], check=True)
                    print(f"Formatted Markdown file: {file_path}")
                except subprocess.CalledProcessError as e:
                    print(f"Error processing {file_path}: {e}")


if __name__ == "__main__":
    format_files(".")
