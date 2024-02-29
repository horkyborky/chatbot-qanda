import csv
import re
import openai

openai.api_key = "sk-xxxxxx"  # replace with your key...

# This assumes that you already have a file generated for Q&A in Excel, and that the column structure/header row is:
# question, answer, notes (optional)
# Download a sheet at a time and save to your local as a CSV


def read_questions_from_csv(filename):
    data_rows = []
    with open(filename, "r") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader)  # Skip the header row
        for row in reader:
            if not any(row):
                print("Encountered a blank row. Stopping.")
                break

            print(f"Read row: {row}")  # For debugging purposes

            if len(row) > 0:  # Ensure the row is not empty
                data_rows.append(row)

    print(f"Read {len(data_rows)} rows from the CSV file.")
    return data_rows


# The actual ChatGPT call, including system prompt and the ability to build out the prompt and stub in the question
# dynamically
# Adjust your prompt as you see fit to reflect your use case and audience specifically; this results in better questions
def chatgpt_api_call(prompt):
    messages = [
        {
            "role": "system",
            "content": "You are a writer who is helping low-income people with limited literacy apply for benefits. Provide exactly 10 alternate ways to ask the following question, ensuring they directly relate to the topic and are simplified for a sixth-grade reading level. Sentences should be short and simple and should not include answer text.",
        },
        {"role": "user", "content": prompt},
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-0613", messages=messages # can swap to the model of your choice - GPT-3.5 does a reasonably good job for cheap
        )
        assistant_message = response.choices[0].message.content
        
        print(
            "System message:", messages[0]["content"]
        )  # Get system message directly from messages list
        print("User message:", prompt)  # Print the prompt as user message
        print("Raw Response:", assistant_message)  # For debugging purposes
        alternatives = [
            alt.strip() for alt in assistant_message.split("\n") if alt.strip()
        ]  # split them out into separate strings

        return alternatives
    except Exception as e:
        print(f"Error during API call: {e}")
        return []


def get_alternative_questions(data_rows):
    alternatives = {}
    for row in data_rows:
        question = row[0]
        alternate_questions = chatgpt_api_call(question)
        alternatives[question] = alternate_questions
    return alternatives


def clean_alternate_question(question):
    question = re.sub(
        r"^\d+\.\s*", "", question
    )  # Remove starting numbers with periods (in case of formatting like "1. Here is an alternate.")
    question = question.replace('"', "")  # Remove double quotes
    question = question.replace("'", "")  # Remove single quotes
    question = question.replace(
        ",", ";"
    )  # Replace commas with semicolons (was screwing up writing out to CSV/TSV)
    question = re.sub(
        r"\s{2,}", " ", question
    )  # Replace 2+ spaces with a single space (spacing was odd on some answers)

    # Log the cleaned alternate question
    print(f"Cleaned Alt: {question}")

    return question


def main_execution_flow():
    global num
    data_rows = read_questions_from_csv(input_file)
    questions = [row[0] for row in data_rows]
    alternatives = get_alternative_questions(data_rows)

    for question in questions:
        num += 1
        print(
            f"Question {num}: {question}"
        )  # The print statements here are to help debug/validate output
        alt_questions = alternatives.get(question, [])
        print(f"Number of Alternates: {len(alt_questions)}")
        for alt in alt_questions:
            cleaned_alt = clean_alternate_question(alt)
            print(f"- {cleaned_alt}")
        print("\n")

    user_input = (
        input(
            "Have you reviewed the cleaned questions? Do you want to proceed with writing to the file? (yes/no): "
        )
        .strip()
        .lower()
    )  # Check the answers look ok before writing out to file

    if user_input == "yes" or user_input == "y":
        with open(outtie, "w", newline="") as output_file:
            tsv_writer = csv.writer(
                output_file, delimiter="\t", quoting=csv.QUOTE_MINIMAL
            )  # writing out as TSV here because CSV had formatting issues with spaces and commas
            new_headers = ["Question", "Answer", "Notes"] + [
                f"Answer{i+1}" for i in range(10)
            ]
            tsv_writer.writerow(new_headers)

            for original_row in data_rows:
                question = original_row[0]
                cleaned_alternates = [
                    clean_alternate_question(alt)
                    for alt in alternatives.get(question, [])
                ]
                # Ensure the list has exactly 10 items
                while len(cleaned_alternates) < 10:
                    cleaned_alternates.append("")

                if (
                    len(original_row) == 2
                ):  # If only "Question" and "Answer" are present, add an empty string for "Notes"
                    original_row.append("")

                new_row = original_row + cleaned_alternates
                tsv_writer.writerow(new_row)

        print("File written successfully!")
    else:
        print("Aborted writing to file.")


# Main loop
num = 0
input_file = "your_input_file.csv"
outtie = "your_output_file.tsv"
main_execution_flow()
