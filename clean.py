import os
import re
import hashlib
from datetime import datetime
from collections import defaultdict

def extract_swf_name(filename):
    match = re.search(r'__mult_([^\_]+?)\.swf_', filename)
    return match.group(1) + ".swf" if match else None

def get_timestamp(filename):
    match = re.search(r'_(\d{14})\.html$', filename)
    return match.group(1) if match else None

def file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def process_files():
    files = [f for f in os.listdir() if os.path.isfile(f) and f.endswith('.html')]
    
    # Первый этап: группировка по содержимому и оригинальному имени
    content_map = defaultdict(list)
    
    for filename in files:
        # Извлекаем оригинальное имя и timestamp
        swf_name = extract_swf_name(filename)
        timestamp = get_timestamp(filename)
        
        if not swf_name or not timestamp:
            continue
            
        # Получаем хеш содержимого
        fhash = file_hash(filename)
        
        # Добавляем в словарь
        content_map[(swf_name, fhash)].append((filename, timestamp))

    # Второй этап: обработка дубликатов и переименование
    for (swf_name, fhash), versions in content_map.items():
        # Сортируем версии по дате (новые сначала)
        versions.sort(key=lambda x: datetime.strptime(x[1], "%Y%m%d%H%M%S"), reverse=True)
        
        # Сохраняем самую новую версию
        original_filename, timestamp = versions[0]
        new_name = swf_name
        
        # Переименовываем и удаляем дубликаты
        try:
            os.rename(original_filename, new_name)
            print(f"Renamed: {original_filename} -> {new_name}")
            
            # Удаляем остальные версии
            for file_to_delete, _ in versions[1:]:
                os.remove(file_to_delete)
                print(f"Deleted duplicate: {file_to_delete}")
                
        except Exception as e:
            print(f"Error processing {swf_name}: {str(e)}")

if __name__ == "__main__":
    print("Starting file organization...")
    process_files()
    print("Operation completed!")