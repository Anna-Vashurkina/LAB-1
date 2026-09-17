import pandas as pd

print("1. Загружаем основные таблицы...")
sightings = pd.read_csv('../data/sightings.csv')
crimes = pd.read_csv('../data/crime_incidents.csv')
locations = pd.read_csv('../data/locations.csv')
weather = pd.read_csv('../data/weather.csv')

# Превращаем timestamp в datetime, чтобы можно было вытащить дату и час для связи с погодой
sightings['timestamp'] = pd.to_datetime(sightings['timestamp'])
sightings['date'] = sightings['timestamp'].dt.date
sightings['hour'] = sightings['timestamp'].dt.hour

print("2. Выполняем соединения (joins)...")

# А. Присоединяем ближайшее преступление (из sightings.nearest_crime_id к crimes.crime_id)
# Используем suffixes, чтобы не запутаться, если названия колонок (например, latitude/longitude) совпадут
merged_df = sightings.merge(
    crimes, 
    left_on='nearest_crime_id', 
    right_on='crime_id', 
    how='left', 
    suffixes=('', '_crime')
)

# Б. Присоединяем информацию о локации/районе (по полю district)
merged_df = merged_df.merge(
    locations, 
    on='district', 
    how='left', 
    suffixes=('', '_loc')
)

# В. Присоединяем погоду по дате и часу
merged_df = merged_df.merge(
    weather, 
    on=['date', 'hour'], 
    how='left', 
    suffixes=('', '_weather')
)

print("3. Проверяем результат:")
print(f"Размер итогового датасета: {merged_df.shape[0]} строк, {merged_df.shape[1]} признаков.")

# Сохраняем результат в файл
merged_df.to_csv('../data/full_dataset.csv', index=False)
print("Готово! Объединенный файл сохранен как full_dataset.csv")
