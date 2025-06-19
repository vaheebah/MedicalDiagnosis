"""
Task 3: Knowledge File Reader
- Reads a text file (`Knowledge.txt`)
- Prints each line
"""
def read_knowledge_file(filename="Knowledge.txt"):

    try:
        with open(filename, 'r') as file:
            lines = file.readlines()

        cleaned_lines = [line.strip() for line in lines if line.strip()]
        print(f" Read {len(cleaned_lines)} lines from {filename}")
        return cleaned_lines

    except FileNotFoundError:
        print(f" Error: File '{filename}' not found.")
        return []


if __name__ == "__main__":
    knowledge = read_knowledge_file()
    for line in knowledge:
        print("Raw knowledge sentence:", line)
