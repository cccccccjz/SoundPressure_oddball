from psychopy import visual, event, sound, core, prefs, monitors
import random
import numpy as np
import time
import os
import csv
from neuracle_lib.triggerBox import TriggerBox, PackageSensorPara, TriggerIn
from glob import glob
from itertools import product


# 主实验
def run_experiment():
    # 初始化窗口
    win = visual.Window(
        size=(1280, 720),
        fullscr=False,
        allowGUI=True,
        monitor='testMonitor',
        units='pix'
    )

    # 参数配置
    BASE_PATH = 'F:\资料文件\实验程序\SoundPressure_oddball\Sound'  # 更改为你的文件夹路径

    # 创建CSV日志文件
    with open('trigger_log.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # 写入CSV头部
        writer.writerow(['timestamp', 'trigger_value', 'status', 'sound_type',
                         'freq_level', 'db_level', 'block', 'trial_index'])

        # 映射关系
        STATUS_MAP = {
            'start': 0b10000000,
            'end': 0b00000000
        }
        SOUND_MAP = {
            '钢琴': 0b00000000,
            '小提琴': 0b00100000,
            '水声': 0b01000000
        }

        FREQ_MAP = {
            '低': 0b00000000,
            '中': 0b00001000,
            '高': 0b00010000
        }

        LEVEL_MAP = {
            20: 0b00000001,
            35: 0b00000010,
            50: 0b00000011,
            65: 0b00000100,
            80: 0b00000101
        }

        # 生成试次序列
        def create_trials(trial_nums):
            n_50 = int(trial_nums * 0.7)
            n_others = int(trial_nums * 0.3 / 4)
            trials = [50] * n_50
            for l in [20, 35, 65, 80]:
                trials += [l] * n_others
            random.shuffle(trials)
            return trials

        # 显示指导语
        instruction = visual.TextStim(win, text="请保持放松，注意听声音\n准备好后按空格键开始实验", height=40)
        instruction.draw()
        win.flip()
        event.waitKeys(keyList=['space'])

        # 倒计时
        for i in range(5, 0, -1):
            countdown = visual.TextStim(win, text=str(i), height=60)
            countdown.draw()
            win.flip()
            core.wait(1)

        # 主实验流程
        for block in range(3):
            # 生成音色频率组合
            combinations = list(product(
                ['钢琴', '小提琴', '水声'],
                ['低', '中', '高']
            ))
            random.shuffle(combinations)

            # 遍历每个音色频率组合
            for combo_idx, (sound_type, freq) in enumerate(combinations):
                folder_name = f"{sound_type}{freq}"
                sound_code = SOUND_MAP[sound_type]
                freq_code = FREQ_MAP[freq]

                # 发送组合开始trigger
                combo_start = STATUS_MAP['start'] ^ sound_code ^ freq_code
                # triggerbox.output_event_data(combo_start)
                writer.writerow([
                    time.time(), combo_start, 'block_start',
                    sound_type, freq, None, block, None
                ])

                # 生成试次序列
                trials = create_trials(120)  # 注意此处参数可能需要调整
                for trial_idx, level in enumerate(trials):
                    # 发送试次开始trigger
                    trigger_on = STATUS_MAP['start'] ^ sound_code ^ freq_code ^ LEVEL_MAP[level]
                    # triggerbox.output_event_data(trigger_on)
                    writer.writerow([
                        time.time(), trigger_on, 'trial_start',
                        sound_type, freq, level, block, trial_idx
                    ])

                    # 播放音频
                    wav_path = os.path.join(
                        BASE_PATH,
                        folder_name,
                        f'{level}dB.wav'
                    )
                    if not os.path.exists(wav_path):
                        raise FileNotFoundError(f"文件不存在: {wav_path}")

                    s = sound.Sound(wav_path)
                    s.play()
                    core.wait(s.duration)

                    # 发送试次结束trigger
                    trigger_off = STATUS_MAP['end'] ^ sound_code ^ freq_code ^ LEVEL_MAP[level]
                    # triggerbox.output_event_data(trigger_off)
                    writer.writerow([
                        time.time(), trigger_off, 'trial_end',
                        sound_type, freq, level, block, trial_idx
                    ])
                    core.wait(1)

                # 发送组合结束trigger
                combo_end = STATUS_MAP['end'] ^ sound_code ^ freq_code
                # triggerbox.output_event_data(combo_end)
                writer.writerow([
                    time.time(), combo_end, 'block_end',
                    sound_type, freq, None, block, None
                ])

                # 显示继续提示
                instruction = visual.TextStim(win, text="准备好后按空格键继续实验", height=40)
                instruction.draw()
                win.flip()
                event.waitKeys(keyList=['space'])

                # 倒计时
                for i in range(5, 0, -1):
                    countdown = visual.TextStim(win, text=str(i), height=60)
                    countdown.draw()
                    win.flip()
                    core.wait(1)


if __name__ == "__main__":
    prefs.hardware['audioLib'] = ['ptb']  # 可选值: ['ptb', 'pyo', 'pygame']
    prefs.hardware['audioDevice'] = '耳机 (2- WH-CH720N)'  # 指定设备名称
    run_experiment()