import requests
import os

def get_snapshots(url):
    cdx_api = "http://web.archive.org/cdx/search/cdx"
    params = {
        'url': url,
        'output': 'json',
        'collapse': 'timestamp:6'  # группировка по дате (до минуты)
    }
    
    try:
        response = requests.get(cdx_api, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data or len(data) < 2:
            return None
            
        timestamps = [entry[1] for entry in data[1:]]  # извлекаем таймстампы
        return sorted(list(set(timestamps)), reverse=True)  # сортируем по убыванию
        
    except Exception as e:
        print(f"Error getting snapshots for {url}: {e}")
        return None

def download_snapshot(url, timestamp):
    archive_url = f"https://web.archive.org/web/{timestamp}/{url}"
    try:
        response = requests.get(archive_url)
        response.raise_for_status()
        
        # Создаем имя файла
        filename = url.replace("://", "_").replace("/", "_")[:100] + f"_{timestamp}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        return filename
        
    except Exception as e:
        print(f"Error downloading {archive_url}: {e}")
        return None

def main():
    # Читаем список URL из файла
    with open('links.txt', 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    for url in urls:
        print(f"\n{'=' * 50}")
        print(f"Processing URL: {url}")
        
        # Получаем список доступных снапшотов
        timestamps = get_snapshots(url)
        
        if not timestamps:
            print("No snapshots found")
            continue
            
        # Показываем последние 10 снапшотов
        print(f"Last {len(timestamps[:10])} snapshots available:")
        for idx, ts in enumerate(timestamps[:10]):
            print(f"{idx + 1}. {ts[:4]}-{ts[4:6]}-{ts[6:8]} {ts[8:10]}:{ts[10:12]}")
        
        # Выбор снапшота
        while True:
            choice = input("Enter snapshot number (1-10), 'all' for all, 'skip' to skip: ").strip().lower()
            
            if choice == 'skip':
                break
                
            if choice == 'all':
                # Скачать все доступные версии
                for ts in timestamps:
                    filename = download_snapshot(url, ts)
                    if filename:
                        print(f"Downloaded: {filename}")
                break
                
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(timestamps[:10]):
                    filename = download_snapshot(url, timestamps[choice_idx])
                    if filename:
                        print(f"Downloaded: {filename}")
                    break
                else:
                    print("Invalid number. Try again.")
            except ValueError:
                print("Invalid input. Try again.")

if __name__ == "__main__":
    main()