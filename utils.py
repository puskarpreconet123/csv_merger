import pandas as pd
import re
import os

PHONE_ALIASES = {
    "phone",
    "phone number",
    "phone_number",
    "mobile",
    "mobile number",
    "mobile_number",
    "contact",
    "contact no",
    "contact_no",
    "contact number"
}

def find_phone_column(columns):
    for col in columns:
        if col in PHONE_ALIASES:
            return col
    return None

def format_phone(value):
    if pd.isna(value):
        return None
    
    digits = re.sub(r"\D", "", str(value))

    if len(digits) == 10:
        digits = "91" + digits

    if len(digits) == 12 and digits.startswith("91"):
        return int(digits)

    return None


def merge_csv(files, final_columns, output_path):
    all_dataframes = []

    final_columns = [c.lower() for c in final_columns]
    for file in files:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.lower()
        phone_output_col = None
        for col in final_columns:
            if col in PHONE_ALIASES:
                phone_output_col = col
                break

        phone_col = find_phone_column(df.columns)

        if phone_col:
            df[phone_output_col] = df[phone_col].apply(format_phone)

        for col in final_columns:
            if col not in df.columns:
                df[col] = "not available"

        df = df[final_columns]
        all_dataframes.append(df)

    merged_df = pd.concat(all_dataframes, ignore_index=True)

    # remove full duplicate rows
    merged_df = merged_df.drop_duplicates()

    output_file = os.path.join(output_path, "merged_output.csv")
    merged_df.to_csv(output_file, index=False)

    return output_file
