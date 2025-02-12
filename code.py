import pandas as pd
import os
import subprocess
import sys
import datetime

def get_user_input(prompt):
    """Функция для запроса ввода у пользователя."""
    return input(prompt).strip()

def log_message(message, log_file):
    """Функция для записи логов в файл."""
    print(message)
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(message + "\n")

def find_file_by_keyword(directory, keyword):
    """Ищет файл в папке, содержащий заданное ключевое слово в названии."""
    matching_files = [f for f in os.listdir(directory) if keyword.lower() in f.lower() and f.endswith('.csv')]
    if len(matching_files) == 1:
        return os.path.join(directory, matching_files[0])
    elif len(matching_files) > 1:
        return get_user_input(f"Введите полный путь к нужному файлу {keyword}: ")
    else:
        return get_user_input(f"Введите полный путь к файлу {keyword}: ")

def main():
    # Создаем лог-файл
    script_dir = os.path.dirname(sys.argv[0])
    log_filename = f"logs_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}.txt"
    log_file = os.path.join(script_dir, log_filename)
    
    log_message("Выберите вариант фильтрации:", log_file)
    log_message("1. iOS и Android", log_file)
    log_message("2. Комбинированная ОС", log_file)
    filter_choice = get_user_input("Введите 1 или 2: ")
    while filter_choice not in ["1", "2"]:
        log_message("Ошибка: выберите 1 или 2.", log_file)
        filter_choice = get_user_input("Введите 1 или 2: ")
    
    log_message("Сохранять ли список удаленных id с указанием файлов, из которых они были удалены", log_file)
    log_message("y. Да", log_file)
    log_message("n. Нет", log_file)
    save_removed = get_user_input("Введите y или n: ")
    while save_removed not in ["y", "n"]:
        log_message("Ошибка: выберите y или n.", log_file)
        save_removed = get_user_input("Введите y или n: ")
    
    folder_path = get_user_input("Введите путь к папке с файлами для сравнения: ")
    while not os.path.isdir(folder_path):
        log_message("Ошибка: указанная папка не существует.", log_file)
        folder_path = get_user_input("Введите корректный путь к папке: ")
    
    update_folder_path = get_user_input("Введите путь к папке с файлами для обновления: ")
    while not os.path.isdir(update_folder_path):
        log_message("Ошибка: указанная папка не существует.", log_file)
        update_folder_path = get_user_input("Введите корректный путь к папке с файлами для обновления: ")
    
    updated_folder = os.path.join(update_folder_path, "updated")
    os.makedirs(updated_folder, exist_ok=True)
    
    if filter_choice == "1":
        file_ios_path = find_file_by_keyword(update_folder_path, "ios")
        file_android_path = find_file_by_keyword(update_folder_path, "Andr")
        data_ios = pd.read_csv(file_ios_path)
        data_android = pd.read_csv(file_android_path)
    else:
        file_combined_path = find_file_by_keyword(update_folder_path, "combined")
        data_combined = pd.read_csv(file_combined_path)
    
    removed_rows_file = os.path.join(updated_folder, "removed.txt") if save_removed == "y" else None
    
    if removed_rows_file:
        f = open(removed_rows_file, "w", encoding="utf-8")
    
    for i, file_name in enumerate(os.listdir(folder_path), 1):
        if not file_name.endswith('.csv'):
            continue
        file_path = os.path.join(folder_path, file_name)
        log_message(f"Обрабатываем файл {i}: {file_name}...", log_file)
        
        data = pd.read_csv(file_path)
        rows_set = set(data.apply(tuple, axis=1))
        
        if filter_choice == "1":
            data_ios = data_ios.loc[~data_ios.apply(tuple, axis=1).isin(rows_set)]
            data_android = data_android.loc[~data_android.apply(tuple, axis=1).isin(rows_set)]
        else:
            data_combined = data_combined.loc[~data_combined.apply(tuple, axis=1).isin(rows_set)]
        
        log_message(f"Файл {file_name} обработан.", log_file)
    
    if removed_rows_file:
        f.close()
    
    if filter_choice == "1":
        data_ios.to_csv(os.path.join(updated_folder, os.path.basename(file_ios_path).replace(".csv", "_updated.csv")), index=False)
        data_android.to_csv(os.path.join(updated_folder, os.path.basename(file_android_path).replace(".csv", "_updated.csv")), index=False)
    else:
        data_combined.to_csv(os.path.join(updated_folder, os.path.basename(file_combined_path).replace(".csv", "_updated.csv")), index=False)
    
    log_message("Обновленные файлы сохранены. Открываем папку...", log_file)
    subprocess.Popen(f'explorer "{updated_folder}"', shell=True)
    
if __name__ == "__main__":
    main()
