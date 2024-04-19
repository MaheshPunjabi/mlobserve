from pynvml import nvmlDeviceGetMemoryInfo, nvmlDeviceGetUtilizationRates, nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex, nvmlInit, nvmlShutdown, nvmlDeviceGetName
import atexit
import logging
import os
import subprocess
import json
import csv
import time
import datetime
logger = logging.getLogger(__name__)

def getGpuStats() -> dict:
    gpu_stats = dict()
    device_count = nvmlDeviceGetCount()
    for i in range(device_count):
        handle = nvmlDeviceGetHandleByIndex(i)
        gpu_mem_info = nvmlDeviceGetMemoryInfo(handle)
        gpu_util_info = nvmlDeviceGetUtilizationRates(handle)
        cur_device_name = nvmlDeviceGetName(handle)
        gpu_stats[cur_device_name] = dict()
        gpu_stats[cur_device_name]["util"] = gpu_util_info.gpu
        gpu_stats[cur_device_name]["memory"] = round((gpu_mem_info.used/gpu_mem_info.total)*100)
        logger.info(f'GPU {i}({cur_device_name}):')
        logger.info(f'\tMemory usage : {gpu_stats[cur_device_name]["memory"]}%')
        logger.info(f'\tUtilization: {gpu_stats[cur_device_name]["util"]}%')
    
    return gpu_stats

def getCpuLoad() -> int:
    logger.info(f"CPU load average(last minute): {round(os.getloadavg()[0],1)}")
    logger.info(f"CPU core count: {os.cpu_count()}")
    return round(os.getloadavg()[0]/os.cpu_count(),1)

def getIoStatOutput() -> json:
    try:
        iostat_output_bytes = subprocess.check_output(['iostat', '-x', '-o', 'JSON'])
        iostat_output_raw = iostat_output_bytes.decode("utf-8")
        # cleanup the output, previously pretty printed
        iostat_output = iostat_output_raw.replace('\n','')
        iostat_output = iostat_output.replace('\t','')
    except subprocess.CalledProcessError as e:
        logger.info(f"failed in iostat: {e.stderr}")

    try:
        iostat_data = json.loads(iostat_output)
    except:
        logger.info(f'failed to decode iostat output string: {iostat_output}')

    return iostat_data

def getIoStats() -> dict:
    iostat_data = getIoStatOutput()
    io_stats = dict()
    iowait = iostat_data['sysstat']['hosts'][0]['statistics'][0]['avg-cpu']['iowait']
    util_by_disk:dict = {i['disk_device']:i['util'] for i in iostat_data['sysstat']['hosts'][0]['statistics'][0]['disk']}
    logger.info(f'iowait: {iowait}, util: {util_by_disk}')
    io_stats["cpu_iowait"] = iowait
    io_stats["disks"] = util_by_disk
    return io_stats

def writeStatsToCsv(stats: dict):
    mode = 'a' if os.path.exists('data.csv') else 'w'
    field_names = ['time', 'CPU-load-avg', 'CPU-IOwait']
    field_names = field_names + [gpu_name+'-utilization' for gpu_name in stats['gpu_stats']]
    field_names = field_names + [gpu_name+'-memory' for gpu_name in stats['gpu_stats']]
    field_names = field_names + [disk_name for disk_name in stats['io_stats']['disks']]
    
    with open('data.csv', mode) as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
        if mode == 'w': #new file
            csv_writer.writeheader()
        
        #TODO: What if rows changed/missing?
        row = dict()
        row['time'] = datetime.datetime.now().strftime('%H:%M:%S')
        for gpu_name in stats['gpu_stats']:
            row[gpu_name+'-utilization'] = stats['gpu_stats'][gpu_name]['util']
            row[gpu_name+'-memory'] = stats['gpu_stats'][gpu_name]['memory']
        row['CPU-load-avg'] = stats['cpu_stats']
        row['CPU-IOwait'] = stats['io_stats']['cpu_iowait']
        for disk_name in stats['io_stats']['disks']:
            row[disk_name] = stats['io_stats']['disks'][disk_name]
        csv_writer.writerow(row)
        

def getStats() -> dict:
    stats = dict()
    stats['gpu_stats'] = getGpuStats()
    stats['cpu_stats'] = getCpuLoad()
    stats['io_stats'] = getIoStats()
    return stats

def main():
    nvmlInit()
    atexit.register(nvmlShutdown)
    logging.basicConfig(filename='observe.log', 
                        level=logging.INFO,
                        format='%(asctime)s %(name)s %(levelname)-s %(message)s'
                        )
    logger.info(f'Started at {datetime.datetime.now()}')
    
    while True:
        stats = getStats()
        writeStatsToCsv(stats)
        time.sleep(10)

if __name__ == "__main__":
    main()