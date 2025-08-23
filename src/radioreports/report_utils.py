import os

def reverse_time(old:str, sep:str) -> str:
    
    parts = old.split(sep)
    new = f'{parts[2]}{sep}{parts[1]}{sep}{parts[0]}'
    
    return  new


def get_description_time(file_name:str) -> str:
    
    # print(f'get description date from {file_name}')
    
    date_start = get_date_start(file_name)
    time_start = get_time_start(file_name)
    date_end = get_date_end(file_name)
    time_end = get_time_end(file_name)

    date_1 = reverse_time(date_start, '.')
    date_2 = reverse_time(date_end, '.')
    
    desc = f'(з {time_start} {date_1} по {time_end} {date_2} року)'
    # print(f' return desc {desc}')
        
    return desc


def get_start_hour(file_name:str) -> str:
    
    time_start = get_time_start(file_name)
    
    return time_start[:2]


def get_foler_name_part(file_name:str) -> str:
    
    start = get_time_start_norm(file_name) + '_' + str(get_time_start(file_name)).replace(':', '-') 
    end = get_time_end_norm(file_name) +'_' + str(get_time_end(file_name)).replace(':', '-')
    
    return f'{start} - {end}'


def get_date_start(file_name:str) -> str:
    
    return str(file_name[7:17]).replace('-', '.')


def get_time_start(file_name:str) -> str:
    
    return str(file_name[18:23]).replace('-', ':')


def get_date_end(file_name:str) -> str:
    
    return str(file_name[24:34]).replace('-', '.')


def get_time_end(file_name:str) -> str:
    
    return str(file_name[35:40]).replace('-', ':')


def get_time_start_norm(file_name:str) -> str:
    
    date_start = get_date_start(file_name)
    
    return reverse_time(date_start, '.')

    
def get_time_end_norm(file_name:str) -> str:
    
    date_end = get_date_end(file_name)
    
    return reverse_time(date_end, '.')

def move_files_to_archive(folder_path: str, file_mask:str):
    
    archive_path = folder_path + r'/archive'
    
    if not os.path.exists(archive_path):
        os.makedirs(archive_path)
           
    for count, obj_name in enumerate(os.listdir(folder_path)):

        src = f"{folder_path}/{obj_name}"
        src_arch = f'{archive_path}/{obj_name}'

        if not os.path.isdir(src):
            try:
                if os.path.exists(src_arch):
                    os.remove(src_arch)
                # print(f'check {obj_name} and {file_mask} | {file_mask in obj_name}')
                if file_mask in obj_name:
                    os.rename(src, src_arch)
            except:
                print('File already exists or is open')