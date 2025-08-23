import logging
import os
import shutil
from pathlib import Path

import pandas as pd
from docx import Document
from pandas import DataFrame

from . import settings

# DOWNLOADS_PATH = r'C:\Downloads'

log = logging.getLogger(__name__)


def get_list_from_folder(folder_path: str, name_mask: str) -> list:
    files = [rep for rep in Path(folder_path).glob(name_mask)]
    return files


def get_fresh_communitify_report(name_mask: str) -> str:
    """
    Повертає шлях до найновішого XLSX за маскою у DATA_DIR.
    Дає зрозумілу помилку, якщо теку/файли не знайдено.
    """
    folder_path = Path(settings.DATA_DIR)

    if not folder_path.exists():
        msg = f"DATA_DIR не існує: {folder_path}"
        log.error(msg)
        raise FileNotFoundError(msg)

    reports = [rep for rep in folder_path.glob(name_mask) if rep.is_file()]
    if not reports:
        msg = f"Не знайдено файлів за маскою '{name_mask}' у {folder_path}"
        log.error(msg)
        raise FileNotFoundError(msg)

    latest_file = max(reports, key=os.path.getctime)
    log.info("Обрано файл: %s", latest_file)
    return str(latest_file)


def simple_save(df: DataFrame, name: str):
    try:
        with pd.ExcelWriter(name) as writer:
            df.to_excel(writer, index=False)
    except Exception as e:
        print(f" Cannt save {name} (Its open?) {e}")


def save_all_data(df: DataFrame, update_name: str, change_index=True):
    file_name = f"formatted\\{update_name}.xlsx"
    print("--------- Save All Data -----------------------")
    print(df)
    if change_index:
        df.set_index("id", inplace=True)
    with pd.ExcelWriter(file_name) as writer:
        df.to_excel(writer, index=False)


def create_folder(folder_name: str) -> None:
    # checking if the directory demo_folder
    # exist or not.
    folder_path = f"..\\Reports\\{folder_name}"
    if not os.path.exists(folder_name):
        # if the demo_folder directory is not present
        # then create it.
        os.makedirs(folder_name)


def create_doc(config: dict) -> None:
    output_path = config.get("output_path")
    template_path = config.get("template_path")
    file_name = config.get("file_name")
    data = config.get("data")

    doc = Document(template_path)
    for paragraph in doc.paragraphs:
        for key, value in data.items():
            if key in paragraph.text:
                value = value.replace("-", ":")
                paragraph.text = paragraph.text.replace(key, value)

    try:
        doc.save(output_path)
    except Exception as e:
        print(f" Cannt save doc file (Its open?) {e}")


def get_df_from_xlsx(file_name: str) -> DataFrame:
    df = pd.read_excel(file_name)
    return df


def get_files_list_by_mask(path: str, mask: str):
    folder_path = Path(path)
    return [rep for rep in folder_path.glob(mask)]


def move_files_to_folder(list_of_files, folder):
    for file_path in list_of_files:
        file_name = os.path.basename(file_path)
        target_path = folder + r"\\" + file_name
        try:
            shutil.move(file_path, target_path)
        except Exception as e:
            print(f"Cannt move file {file_name}: {e} (Mayby file is opened)")
