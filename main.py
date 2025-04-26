import os
import sys
import shutil

import pikepdf
from pikepdf import ObjectStreamMode
from PyPDF2 import PdfMerger

# שמות התיקיות (קבועים)
INPUT_FOLDER = "pdf files"
TEMP_FOLDER = "temp files"
OUTPUT_FOLDER = "output file"

# שם הקובץ המאוחד הדיפולטיבי (כולל הסיומת)
DEFAULT_MERGED_FILENAME = "merged.pdf"


def ensure_dir(path: str) -> None:
    """יוצר את התיקייה אם היא לא קיימת."""
    os.makedirs(path, exist_ok=True)


def compress_pdf(input_path: str, output_path: str) -> None:
    """
    דוחס PDF על ידי:
      • compress_streams=True → דוחס זרמים לא־דחוסים
      • recompress_flate=True → עושה recompress לזרמים שכבר דחוסים
      • object_stream_mode=ObjectStreamMode.generate → יוצר object streams חדשים
    """
    with pikepdf.open(input_path) as pdf:
        pdf.save(
            output_path,
            compress_streams=True,
            recompress_flate=True,
            object_stream_mode=ObjectStreamMode.generate,
        )


def compress_and_merge(input_folder: str, temp_folder: str, output_path: str) -> None:
    """
    1. דוחס כל PDF מ-input_folder לתוך temp_folder
    2. ממזג את כולם ל־output_path
    """
    ensure_dir(temp_folder)
    merger = PdfMerger()

    pdf_files = sorted(
        f for f in os.listdir(input_folder) if f.lower().endswith(".pdf")
    )
    if not pdf_files:
        print("אין קבצי PDF בתיקיית המקור.")
        return

    for fname in pdf_files:
        src = os.path.join(input_folder, fname)
        dst = os.path.join(temp_folder, fname)
        print(f"דוחס: {src} → {dst}")
        compress_pdf(src, dst)
        merger.append(dst)

    print(f"ממזג → {output_path}")
    with open(output_path, "wb") as f_out:
        merger.write(f_out)
    merger.close()


if __name__ == "__main__":
    # 1. קבלת שם הקובץ השלישי כארגומנט (אם קיים)
    if len(sys.argv) > 1 and sys.argv[1].strip():
        base_name = sys.argv[1].strip()
    else:
        base_name = DEFAULT_MERGED_FILENAME

    # 2. הוספת .pdf אם המשתמש לא ציין סיומת
    if not base_name.lower().endswith(".pdf"):
        merged_filename = f"{base_name}.pdf"
    else:
        merged_filename = base_name

    # 3. בדיקת קיום תיקיית המקור
    if not os.path.isdir(INPUT_FOLDER):
        print(f"תקלה: לא נמצאה התיקייה '{INPUT_FOLDER}'.")
        sys.exit(1)

    # 4. וידוא יצירת תיקיות temp ו-output
    ensure_dir(TEMP_FOLDER)
    ensure_dir(OUTPUT_FOLDER)

    # 5. הרצת התהליך
    merged_path = os.path.join(OUTPUT_FOLDER, merged_filename)
    compress_and_merge(INPUT_FOLDER, TEMP_FOLDER, merged_path)

    # 6. מחיקת כל הקבצים בתיקיית temp (התיקייה עצמה נשארת)
    for fname in os.listdir(TEMP_FOLDER):
        path = os.path.join(TEMP_FOLDER, fname)
        if os.path.isfile(path):
            os.remove(path)
    print("כל הקבצים ב־temp נמחקו.")

    print("הפעולה הושלמה בהצלחה.")
