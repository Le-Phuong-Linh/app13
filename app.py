import streamlit as st
import os
import re
import shutil
from pathlib import Path

# =====================================================
# STREAMLIT UI CONFIGURATION
# =====================================================
st.set_page_config(page_title="First Line Cleaner", page_icon="📝", layout="centered")

st.title("📝 First Line Chapter Title Cleaner")
st.write("Загрузите текстовые файлы глав (`.txt`). Приложение проверит первую строку каждого файла на наличие слова **«Глава»**, удалит её, если условие выполнено, и подготовит архив с очищенными файлами.")

# =====================================================
# FILE UPLOADERS
# =====================================================
st.subheader("Загрузка файлов")
uploaded_files = st.file_uploader("Загрузите `.txt` файлы глав", type=["txt"], accept_multiple_files=True)

# =====================================================
# PROCESSING LOGIC
# =====================================================
def clean_first_line(files):
    input_dir = Path("temp_input")
    output_dir = Path("temp_output")
    
    if input_dir.exists():
        shutil.rmtree(input_dir)
    if output_dir.exists():
        shutil.rmtree(output_dir)
        
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    for file in files:
        with open(input_dir / file.name, "wb") as f:
            f.write(file.getbuffer())
            
    chapter_pattern = re.compile(r'^\s*глава\b', re.IGNORECASE)
    encoding = "utf-8"
    
    all_files = [f.name for f in input_dir.iterdir() if f.name.lower().endswith('.txt')]
    
    cleaned_count = 0
    skipped_count = 0
    
    for filename in sorted(all_files):
        filepath = input_dir / filename
        out_filepath = output_dir / filename
        
        try:
            with open(filepath, "r", encoding=encoding) as f:
                lines = f.readlines()
            
            if lines:
                first_line = lines[0]
                if chapter_pattern.match(first_line):
                    # Записываем файл без первой строки
                    with open(out_filepath, "w", encoding=encoding) as f:
                        f.writelines(lines[1:])
                    cleaned_count += 1
                else:
                    # Если условие не выполнено, копируем файл целиком
                    with open(out_filepath, "w", encoding=encoding) as f:
                        f.writelines(lines)
                    skipped_count += 1
            else:
                # Если файл пустой
                with open(out_filepath, "w", encoding=encoding) as f:
                    f.writelines(lines)
                skipped_count += 1
        except Exception:
            skipped_count += 1

    shutil.make_archive("cleaned_first_line_archive", "zip", output_dir)
    return "cleaned_first_line_archive.zip", cleaned_count, skipped_count, len(all_files)

# =====================================================
# MAIN ACTION BUTTON
# =====================================================
if st.button("Очистить первые строки"):
    if not uploaded_files:
        st.error("Пожалуйста, загрузите хотя бы один `.txt` файл.")
    else:
        with st.spinner("Проверка и очистка файлов..."):
            try:
                zip_path, cleaned, skipped, total = clean_first_line(uploaded_files)
                st.success(f"Обработка завершена! Всего проверено файлов: {total}")
                st.info(f"Очищено (удалена 1-я строка со словом «Глава»): **{cleaned}**")
                st.warning(f"Пропущено (без изменений): **{skipped}**")
                
                with open(zip_path, "rb") as fp:
                    st.download_button(
                        label="📦 Скачать очищенные файлы (ZIP)",
                        data=fp,
                        file_name="cleaned_files.zip",
                        mime="application/zip"
                    )
            except Exception as e:
                st.error(f"Произошла ошибка при обработке: {e}")