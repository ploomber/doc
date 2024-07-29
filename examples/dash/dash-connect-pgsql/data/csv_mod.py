import pandas as pd

csv_mods = {
    "student-mat.csv": "student-mat-min.csv",
    "student-por.csv": "student-por-min.csv"
}

for csv_cur, csv_conv in csv_mods.items():
    df = pd.read_csv(csv_cur, sep=";")

    # Select rows to keep
    df = df[["school", "sex", "romantic_status", "age", 
        "mother_occupation", "father_occupation", 
            "health", "study_time", "absences", "final_grade"]]
    df.to_csv(csv_conv)
    

