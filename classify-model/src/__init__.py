from src.__00__paths import data_dir_list, model_dir

for path in data_dir_list + [model_dir]:
    path.mkdir(parents=True, exist_ok=True)
    print(f'✔️ Created Directory: {'/'.join(path.parts[-2:])}')
