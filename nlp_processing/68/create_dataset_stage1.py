"""公式ノート mhealth_stageN.ipynb 相当の学習データ生成スクリプト(自動生成)。
MHealth を取得して datasets/MHEALTHDATASET/ に展開し、datasets/mhealth_stage1/ に pkl + QA-JSON を出力する。"""

import io
import json
import os
import pickle
import random
import re
import urllib.request
import zipfile
from datetime import datetime

import numpy as np
import pandas as pd

# 生成物は 68/datasets/ 以下に集約する（以降の相対パスはこのディレクトリ基準）
os.makedirs("datasets", exist_ok=True)
os.chdir("datasets")

if not os.path.isdir("MHEALTHDATASET"):
    print("[prep] downloading MHealth ...", flush=True)
    with urllib.request.urlopen("https://archive.ics.uci.edu/static/public/319/mhealth+dataset.zip", timeout=180) as r:
        zipfile.ZipFile(io.BytesIO(r.read())).extractall(".")
os.makedirs("mhealth_stage1/train", exist_ok=True)
os.makedirs("mhealth_stage1/test", exist_ok=True)


def check_label_continuity(df):
    continuity_segments = {}

    for subject in df["subject"].unique():
        subject_data = df[df["subject"] == subject]
        assert subject_data.index[0] == 0

        for label in subject_data["activity"].unique():
            label_data = subject_data[subject_data["activity"] == label]

            indices = label_data.index
            segments = []
            start_idx = indices[0]

            for i in range(len(indices) - 1):
                if indices[i] + 1 != indices[i + 1]:
                    end_idx = indices[i]
                    segments.append((start_idx, end_idx))
                    start_idx = indices[i + 1]

            segments.append((start_idx, indices[-1]))

            if segments:
                continuity_segments[(subject, label)] = segments

    return continuity_segments


def generate_window_sizes(sequence_length, window_size_list):
    min_window_size, max_window_size = window_size_list[0], window_size_list[1]
    window_sizes = []
    remaining_length = sequence_length
    while remaining_length > 0:
        if remaining_length < min_window_size:
            if window_sizes:
                last_window_size = window_sizes.pop()
                remaining_length += last_window_size
                continue
            else:
                raise ValueError("没有之前生成的窗口大小")
        window_size = random.randint(min_window_size, min(max_window_size, remaining_length))
        window_sizes.append(window_size)
        remaining_length -= window_size
    return window_sizes


def split_sequences(sequences, window_size_list, n=1):
    assert len(sequences[0]) == 15
    # 检查是否存在空值
    has_null = any(any(pd.isnull(item) or item == "" for item in sublist) for sublist in sequences)

    # 输出结果
    if has_null:
        raise ValueError("Has null values。")

    sequence_length = len(sequences)
    segments = []
    labels_set = set()
    labels = []
    for _ in range(n):
        window_sizes = generate_window_sizes(sequence_length, window_size_list)

        start = 0
        for window_size in window_sizes:
            end = start + window_size
            if (start, end) not in labels_set:
                labels_set.add((start, end))
                segment = sequences[start:end]
                segments.append(np.array(segment))
                labels.append([start, end])
            start = end
    return segments, labels


activity_map = {
    1: "Standing still (1 min)",
    2: "Sitting and relaxing (1 min)",
    3: "Lying down (1 min)",
    4: "Walking (1 min)",
    5: "Climbing stairs (1 min)",
    6: "Waist bends forward (20x)",
    7: "Frontal elevation of arms (20x)",
    8: "Knees bending (crouching) (20x)",
    9: "Cycling (1 min)",
    10: "Jogging (1 min)",
    11: "Running (1 min)",
    12: "Jump front & back (20x)",
}
test_id = ["subject1", "subject3", "subject6"]
window_size = [5, 100]

all_train_segments = []
all_test_segments = []
all_train_labels = []
all_test_labels = []

for i in range(1, 11):
    df = pd.read_csv(f"./MHEALTHDATASET/mHealth_subject{i}.log", header=None, sep="\t")
    # Note: Excluding the ECG data collected with the chest sensor
    df = df.loc[:, [0, 1, 2, 5, 6, 7, 8, 9, 10, 14, 15, 16, 17, 18, 19, 23]].rename(
        columns={
            0: "acc_ch_x",
            1: "acc_ch_y",
            2: "acc_ch_z",
            5: "acc_la_x",
            6: "acc_la_y",
            7: "acc_la_z",
            8: "gyr_la_x",
            9: "gyr_la_y",
            10: "gyr_la_z",
            14: "acc_rw_x",
            15: "acc_rw_y",
            16: "acc_rw_z",
            17: "gyr_rw_x",
            18: "gyr_rw_y",
            19: "gyr_rw_z",
            23: "activity",
        }
    )
    df["subject"] = f"subject{i}"
    continuity_segments = check_label_continuity(df)
    for key, value in continuity_segments.items():
        if key[1] == 0:  # class != 1
            continue
        for segment in value:
            # 划分时间序列数据为片段
            rows = df.loc[segment[0] : segment[1]]

            assert len(rows["subject"].unique()) == 1
            assert rows["subject"].unique()[0] == key[0]
            assert (
                len(rows["activity"].unique()) == 1
            ), f"Subject {key[0]}, activity {key[1]} but has {rows['activity'].unique()},  {segment[0]} 到 {segment[1]}"
            assert rows["activity"].unique()[0] == key[1]

            subject_activity_df = rows.iloc[:, ~rows.columns.isin(["subject", "activity"])]
            subject_activity_series = subject_activity_df.values.tolist()

            if key[0] not in test_id:
                segments, labels = split_sequences(subject_activity_series, window_size, 2)
                all_train_segments.extend(segments)
            else:
                segments, labels = split_sequences(subject_activity_series, window_size, 1)
                all_test_segments.extend(segments)

            for label in labels:
                label_dict = {"subject": key[0], "activity_name": activity_map[key[1]], "activity": key[1] - 1, "segments": label}
                if key[0] not in test_id:
                    all_train_labels.append(label_dict)
                else:
                    all_test_labels.append(label_dict)

print(f"all_train_segments: {len(all_train_segments)}")
print(f"all_train_labels: {len(all_train_labels)}")
print(f"all_test_segments: {len(all_test_segments)}")
print(f"all_test_labels: {len(all_test_labels)}")

output_path = "./mhealth_stage1"

with open(os.path.join(output_path, "train", "mhealth_train_data_stage1.pkl"), "wb") as f:
    pickle.dump(all_train_segments, f)

with open(os.path.join(output_path, "test", "mhealth_test_data_stage1.pkl"), "wb") as f:
    pickle.dump(all_test_segments, f)

with open(os.path.join(output_path, "train", "mhealth_train_labels_stage1.pkl"), "wb") as f:
    pickle.dump(all_train_labels, f)

with open(os.path.join(output_path, "test", "mhealth_test_labels_stage1.pkl"), "wb") as f:
    pickle.dump(all_test_labels, f)

print(all_test_labels[0])

PROMPT_DICT = {
    "trend_synonyms": {"upward": "downward", "ascending": "descending", "rising": "falling", "increasing": "decreasing", "growing": "declining"},
    "steady_synonyms": ["steady", "constant", "stable", "consistent"],
    "gen_smry_q": [
        "Could you provide a summary of the main features of the input {data} and the distribution of the trends?",
        "Please give an overview of the essential attributes of the input {data} and the spread of the trends.",
        "I would appreciate if you could outline the primary characteristics of the input {data} and the distribution of the trends.",
        "Can you present a brief description of the fundamental properties of the input {data} and the allocation of the trends?",
        "Would you be able to summarize the significant aspects of the input {data} and the dispersion of the trends?",
        "I kindly request a concise report on the central qualities of the input {data} and the distribution of the trends.",
        "Please provide a succinct account of the crucial elements of the input {data} and the distribution of the trends.",
        "Please provide a summary of the main features of the input {data} and the trends observed in its distribution.",
        "Could you analyze the key aspects of the {data} input and outline the distribution trends?",
        "I need an overview of the primary characteristics of the input {data} and a description of the trend distribution.",
        "Summarize the essential elements of the input {data} and the patterns in its distribution.",
        "Explain the fundamental attributes of the {data} input and the distribution trends it exhibits.",
        "Can you break down the main features and distribution trends of the input {data}?",
        "Offer a concise summary of the input {data}'s key characteristics and how its trends distribute.",
        "Detail the core aspects and distribution patterns observed in the {data} input.",
        "Identify and describe the key features and trend distribution within the input {data}.",
        "Provide insights into the primary elements and distribution trends of the {data} input.",
        "Examine the principal attributes of the {data} input and report on the observed distribution trends.",
        "Highlight the significant characteristics of the input {data} and the nature of its trend distribution.",
        "Can you summarize the key aspects of {data} and the trend distribution?",
        "Please outline the primary characteristics of {data} and the trend patterns.",
        "Could you detail the main features of {data} and outline the trend distribution?",
        "I need a summary of {data}'s main elements and their trend distributions.",
        "Please provide insights into the core features of {data} and the distribution of trends.",
        "Can you highlight the principal components of {data} and their trend distribution?",
        "Summarize the essential aspects of {data} and the trends' distribution, please.",
        "Summarize the key features and trend distribution of the {data}.",
        "What are the main characteristics and trend patterns in the {data}?",
        "Describe the primary attributes and trend dispersion of the {data}.",
        "Provide an overview of the {data}'s main features and trend distribution.",
        "Explain the essential properties and trend spread of the {data}.",
        "Outline the principal aspects and trend allocation of the {data}.",
        "Summarize the {data}'s core features and trend dissemination.",
        "What are the fundamental traits and trend arrangement in the {data}?",
        "Give a summary of the {data}'s main elements and trend apportionment.",
        "Describe the salient features and trend distribution within the {data}.",
    ],
    "gen_summary_1": [
        "The given {data_name} representing the {sensor_name} sensor readings from {start_time}s to {end_time}s.",
        "The {data_name} represents readings taken from an {sensor_name} sensor between {start_time} and {end_time} seconds.",
        "This {data_name} comprises {sensor_name} sensor readings collected from {start_time} seconds to {end_time} seconds.",
        "The {sensor_name} sensor readings recorded within the {start_time} to {end_time} second timeframe are presented in this {data_name}.",
        "The {data_name} encapsulates {sensor_name} sensor readings from {start_time}s to {end_time}s.",
        "Readings from an {sensor_name} sensor, captured from {start_time} seconds to {end_time} seconds, are depicted in the given {data_name}.",
        "The {data_name} illustrates measurements from an {sensor_name} sensor between {start_time} and {end_time} seconds.",
        "Presented is a span of {data_name}, indicating readings from an {sensor_name} sensor taken within the {start_time} to {end_time} second "
        "timeframe.",
        "This {data_name} reflects the output from an {sensor_name} sensor, measured from {start_time} seconds to {end_time} seconds.",
        "The presented {data_name} depicts the measurements obtained from an {sensor_name} sensor between {start_time} and {end_time} seconds.",
        "The {data_name} provided represents the output of an {sensor_name} sensor recorded between {start_time}s and {end_time}s.",
        "The {data_name} corresponds to the readings collected from an {sensor_name} sensor between {start_time}s and {end_time}s.",
        "The {data_name} illustrates the {sensor_name} sensor's measurements captured from {start_time}s to {end_time}s.",
        "The given {data_name} represents the {sensor_name} sensor's output recorded between {start_time} and {end_time} seconds.",
        "The {data_name} showcases the {sensor_name} sensor's readings acquired between {start_time}s and {end_time}s.",
        "The {data_name} represent the {sensor_name} sensor's measurements taken from {start_time} seconds to {end_time} seconds.",
        "The {data_name} encapsulates the {sensor_name} sensor's output collected between {start_time} and {end_time} seconds.",
        "The {data_name} comprises the {sensor_name} sensor's readings gathered from {start_time}s to {end_time}s.",
        "The {data_name} exhibits the {sensor_name} sensor's measurements registered within the {start_time} to {end_time} second timeframe.",
        "The {data_name} displays readings obtained from an {sensor_name} sensor from {start_time} seconds to {end_time} seconds.",
        "Readings collected from an {sensor_name} sensor from {start_time}s to {end_time}s are documented in this {data_name}.",
        "This {data_name} encapsulates the readings from an {sensor_name} sensor between {start_time} and {end_time} seconds.",
        "The provided {data_name} captures the readings from an {sensor_name} sensor, recorded between {start_time} and {end_time} seconds.",
        "This {data_name} represents the readings from an {sensor_name} sensor between {start_time}s and {end_time}s.",
        "Readings from an {sensor_name} sensor between {start_time}s and {end_time}s are chronicled in the given {data_name}.",
        "The {data_name} illustrates {sensor_name} sensor readings between {start_time} and {end_time} seconds.",
        "Recordings from an {sensor_name} sensor, between {start_time} and {end_time} seconds, are conveyed in this {data_name}.",
        "The {data_name} provided is a representation of the {sensor_name} sensor's output recorded continuously within the {start_time} to "
        "{end_time} second timeframe.",
        "The presented {data_name} encapsulates the {sensor_name} sensor's readings collected sequentially between {start_time}s and {end_time}s.",
        "The {data_name} under consideration contains the {sensor_name} sensor's output captured from {start_time} seconds to {end_time} seconds.",
        "The provided {data_name} shows readings from the {sensor_name} sensor from {start_time}s to {end_time}s.",
        "The {data_name} contains {sensor_name} sensor data between {start_time}s and {end_time}s.",
        "Readings from the {sensor_name} sensor between {start_time}s and {end_time}s are in the {data_name}.",
        "{data_name} includes {sensor_name} sensor observations taken from {start_time} seconds to {end_time} seconds.",
        "The {data_name} shows {sensor_name} readings from {start_time}s to {end_time}s.",
        "{sensor_name} sensor data between {start_time}s and {end_time}s is represented in {data_name}.",
        "{data_name} presents {sensor_name} data collected between {start_time} and {end_time} seconds.",
        "{sensor_name} readings between {start_time}s and {end_time}s are displayed in {data_name}.",
        "{sensor_name} sensor readings are captured in {data_name} within the {start_time} to {end_time} second timeframe.",
        "From {start_time}s to {end_time}s, {sensor_name} data is showcased in the {data_name}.",
        "The {data_name} exhibits {sensor_name} readings from {start_time} seconds to {end_time} seconds.",
    ],
    "gen_summary_2": [
        "The data exhibits {trend_num} distinct trends, with a total of {change_num} changes in trend observed.",
        "Analysis reveals {trend_num} separate trends within the data, undergoing a cumulative total of {change_num} shifts in direction.",
        "There are {trend_num} unique trends identified in the data, which altogether have shifted direction {change_num} times.",
        "The data outlines {trend_num} different patterns, with these patterns changing direction a total of {change_num} times.",
        "{trend_num} varied trends have been observed in the data, which altogether experienced {change_num} transitions.",
        "The input data displays {trend_num} individual trends, with a comprehensive change count reaching {change_num}.",
        "In the data, {trend_num} distinct movement trends are evident, and there have been {change_num} total trend alterations.",
        "The data delineates {trend_num} unique trends, undergoing {change_num} total changes in these trends.",
        "{trend_num} separate trends can be discerned within the data, with a total of {change_num} instances of trend modification.",
        "The data shows {trend_num} different trajectories, with these trajectories having changed a total of {change_num} times.",
        "Analysis of the data shows {trend_num} main trend patterns, and the trend has undergone {change_num} shifts in total.",
        "The data highlights {trend_num} significant trends, while also indicating that the trend has changed {change_num} times overall.",
        "Overall, the data reflects {trend_num} different development trends, which have experienced {change_num} changes in total.",
        "The data demonstrates {trend_num} major trend types, with the trend undergoing {change_num} turning points during the entire period.",
        "Examining the data, we notice {trend_num} clear trend characteristics, with the trend fluctuating a total of {change_num} times.",
        "The data mirrors {trend_num} different development tendencies, while also illustrating that the trend has changed {change_num} times in "
        "total.",
        "From a holistic perspective, the data presents {trend_num} unique trend forms, which have undergone {change_num} changes throughout the "
        "process.",
        "The data indicates {trend_num} primary shifting trends, with these trends transforming a total of {change_num} times.",
        "Parsing through the data, we discover {trend_num} distinct trend features, with the trend varying {change_num} times over the entire "
        "period.",
        "There are {trend_num} unique trends and {change_num} total trend changes observed in the data.",
        "The data shows {trend_num} different trends, with {change_num} changes in these trends.",
        "Analysis reveals {trend_num} separate trends and a total of {change_num} shifts in trend direction.",
        "We identified {trend_num} distinct patterns, along with {change_num} overall changes in trends in the given data.",
        "The input data demonstrates {trend_num} unique trends, experiencing {change_num} trend alterations in total.",
        "Observation indicates {trend_num} different trends with {change_num} instances of trend changes.",
        "The analysis points to {trend_num} distinct trends and {change_num} changes in the trends.",
        "{trend_num} separate trends and {change_num} trend shifts are seen in the data.",
        "The data reveals {trend_num} distinct trends with {change_num} trend variations.",
        "The data displays {trend_num} individual trends and {change_num} trend fluctuations.",
        "{change_num} trend changes are observed across {trend_num} trends in the input data.",
        "The data contains {trend_num} trends, exhibiting {change_num} trend modifications.",
        "{trend_num} trends are present in the data, with {change_num} instances of trend changes.",
        "Across {trend_num} trends, the data shows {change_num} occurrences of trend shifts.",
    ],
    "gen_summary_2_2": [
        "The data exhibits {trend_num} distinct trend.",
        "Analysis reveals {trend_num} separate trend within the data.",
        "There is {trend_num} unique trend identified in the data.",
        "The data outlines {trend_num} pattern.",
        "{trend_num} varied trend has been observed in the data.",
        "The input data displays {trend_num} individual trend.",
        "In the data, {trend_num} distinct movement trend is evident.",
        "The data delineates {trend_num} unique trend.",
        "{trend_num} separate trend can be discerned within the data.",
        "The data shows {trend_num} different trajectory.",
        "Analysis of the data shows {trend_num} main trend pattern.",
        "The data highlights {trend_num} significant trend.",
        "Overall, the data reflects {trend_num} different development trend.",
        "The data demonstrates {trend_num} trend type.",
        "Examining the data, we notice {trend_num} clear trend characteristic.",
        "The data mirrors {trend_num} different development tendency.",
        "From a holistic perspective, the data presents {trend_num} unique trend form.",
        "The data indicates {trend_num} primary shifting trend.",
        "Parsing through the data, we discover {trend_num} distinct trend feature.",
        "There is {trend_num} unique trend observed in the data.",
        "The data shows {trend_num} different trend.",
        "Analysis reveals {trend_num} separate trend.",
        "We identified {trend_num} distinct pattern.",
        "The input data demonstrates {trend_num} unique trend.",
        "Observation indicates {trend_num} different trend.",
        "The analysis points to {trend_num} distinct trend.",
        "{trend_num} separate trend is seen in the data.",
        "The data reveals {trend_num} distinct trend.",
        "The data displays {trend_num} individual trend.",
        "{trend_num} trend is observed in the input data.",
        "The data contains {trend_num} trend.",
        "{trend_num} trend is present in the data.",
    ],
    "gen_summary_3": [
        "To sum up, the data exhibited a {trend_type} trend for a cumulative period of {total_time} seconds",
        "In conclusion, the overall timespan of the data's {trend_type} tendency amounted to {total_time} seconds",
        "Summarizing the findings, the aggregate time during which the data displayed a {trend_type} pattern was {total_time} seconds",
        "The analysis reveals that the data's {trend_type} inclination persisted for a total of {total_time} seconds",
        "To encapsulate, the data's {trend_type} trend spanned a combined duration of {total_time} seconds",
        "In summary, the data's {trend_type} behavior lasted for an accumulated time of {total_time} seconds",
        "Recapitulating, the data's {trend_type} tendency endured for an aggregate timeframe of {total_time} seconds",
        "The investigation concludes that the data's {trend_type} trend had a total lifespan of {total_time} seconds",
        "To epitomize, the data's {trend_type} characteristic persevered for a sum of {total_time} seconds",
        "Encapsulating the outcomes, the data's {trend_type} trend stretched across a total time of {total_time} seconds",
        "In a nutshell, the data's {trend_type} propensity persisted for an accumulated duration of {total_time} seconds",
        "Summarizing the results, the data's {trend_type} tendency spanned a total timeframe of {total_time} seconds",
        "The examination reveals that the data's {trend_type} inclination endured for an aggregate of {total_time} seconds",
        "To encapsulate the findings, the data's {trend_type} behavior lasted for a cumulative period of {total_time} seconds",
        "In essence, the data exhibited a {trend_type} pattern for a combined time of {total_time} seconds",
        "The analysis concludes that the data's {trend_type} trend had a total lifespan of {total_time} seconds",
        "In summary, the data displayed a {trend_type} behavior for an aggregate time of {total_time} seconds",
        "Overall, the data showed a {trend_type} trend over {total_time} seconds",
        "In summary, a {trend_type} trend was observed across the span of {total_time} seconds",
        "To conclude, the trend was {trend_type} over a period of {total_time} seconds",
        "Summarizing, there was a {trend_type} trend throughout {total_time} seconds",
        "Briefly, the data trended {trend_type} over the duration of {total_time} seconds",
        "In total, the data showed a {trend_type} trend lasting {total_time} seconds",
        "Concisely, the trend observed was {trend_type} for {total_time} seconds",
        "The input data exhibited a {trend_type} trend during the {total_time} second period",
        "Upon review, the data's trend was {trend_type} throughout the {total_time} seconds",
        "The analysis highlighted a {trend_type} trend over the span of {total_time} seconds",
        "Summarily, a {trend_type} direction was evident across {total_time} seconds of data",
    ],
    "gen_summary_4": [
        "a {trend_type} pattern for {total_time} seconds",
        "a {trend_type} trend for {total_time} seconds",
        "a {trend_type} pattern for a total of {total_time} seconds",
        "a {trend_type} trend for a total of {total_time} seconds",
        "a {trend_type} pattern for a sum of {total_time} seconds",
        "a {trend_type} trend for a sum of {total_time} seconds",
        "a {trend_type} pattern for a cumulative period of {total_time} seconds",
        "a {trend_type} trend for a cumulative period of {total_time} seconds",
        "a {trend_type} pattern for an accumulated time of {total_time} seconds",
        "a {trend_type} trend for an accumulated time of {total_time} seconds",
        "a {trend_type} pattern for an aggregate time of {total_time} seconds",
        "a {trend_type} trend for an aggregate time of {total_time} seconds",
        "a {trend_type} pattern for {total_time} seconds in total",
        "a {trend_type} trend for {total_time} seconds in total",
        "a pattern of {trend_type} for {total_time} seconds",
        "a trend of {trend_type} for {total_time} seconds",
        "a {trend_type} trend observed over {total_time} seconds",
        "a {trend_type} pattern observed over {total_time} seconds",
        "a {trend_type} trend within a span of {total_time} seconds",
        "a {trend_type} pattern within a span of {total_time} seconds",
        "a sequence of {trend_type} occurring over {total_time} seconds",
    ],
    "gen_summary_6": [
        "The overall trend is {overall_trend}.",
        "The general trend observed is {overall_trend}.",
        "Overall, the trend is {overall_trend}.",
        "The primary trend detected is {overall_trend}.",
        "In summary, the overall trend is {overall_trend}.",
        "The main direction we're seeing is {overall_trend}.",
        "The overarching trend is identified as {overall_trend}.",
        "Key observation: the overall trend is {overall_trend}.",
        "The general trend shows {overall_trend}.",
        "According to the analysis, the overall trend is {overall_trend}.",
        "The data reveals a {overall_trend} trend in general.",
        "The predominant trend is observed to be {overall_trend}.",
        "The overarching trend is determined to be {overall_trend}.",
        "After calculation, the primary trend is identified as {overall_trend}.",
        "The general trend is {overall_trend}.",
        "The prevailing trend is {overall_trend}.",
        "The trend overall is {overall_trend}.",
        "The dominant trend is {overall_trend}.",
        "In summary, the trend is {overall_trend}.",
        "Broadly, the movement is {overall_trend}.",
        "The main direction is {overall_trend}.",
        "The overarching trend is characterized as {overall_trend}.",
        "The trend direction is {overall_trend}.",
        "Looking at the big picture, the trend is {overall_trend}.",
        "Trend overview: {overall_trend}.",
    ],
    "gen_trend_q": [
        "Kindly provide a detailed analysis of the trend changes observed in the {data}.",
        "Please offer a comprehensive description of how the trends in the {data} have evolved.",
        "I would appreciate a thorough explanation of the trend fluctuations that occurred within the {data}.",
        "Could you please examine the {data} in depth and explain the trend shifts observed step by step?",
        "I kindly request a detailed analysis of the trend changes present in the {data}.",
        "Please evaluate the {data} trends and provide a detailed description of their development.",
        "I would be grateful if you could offer a comprehensive account of the trend alterations within the {data}.",
        "Could you kindly assess the {data} and provide a description of the trend transformations that took place step by step?",
        "Could you analyze the trends observed in the {data} over the specified period step by step?",
        "I’m interested in understanding how the {data} has evolved. Could you break down the trend changes for me in detail?",
        "Please explore the {data} for me, highlighting any significant trends and changes that have occurred.",
        "I’d appreciate a comprehensive overview of the trends within the {data}, with particular attention to any notable shifts or changes.",
        "Can you dissect the {data} and explain the trend changes in a detailed manner?",
        "I'm looking for an in-depth examination of the {data}. Could you elucidate the trends and pivotal changes?",
        "Please conduct a thorough analysis of the {data}, focusing on the evolution of trends over time.",
        "Could you delve into the {data} and provide a detailed synopsis of the trends and alterations observed?",
        "Please analyze the trend shifts in the {data}.",
        "I need an overview of changes in {data} trends.",
        "Can you summarize trend fluctuations in the {data}?",
        "Offer insights into the trend alterations within the {data}.",
        "Detail the {data}'s trend transitions.",
        "Examine the evolution of trends in the {data}.",
        "Explore the changes in trends for the {data}.",
        "Give a brief analysis of {data} trend developments.",
        "Please analyze the trend changes in the {data}.",
        "Describe the trend shifts observed in the {data}.",
        "Examine how trends in the {data} have evolved.",
        "What trend changes can be seen in the {data}?",
        "Identify the trend variations within the {data}.",
        "Explain the trend developments in the {data}.",
        "Provide an overview of the trend patterns in the {data}.",
        "Detail the significant trend modifications in the {data}.",
        "Analyze the main trend alterations observed in the {data}.",
    ],
    "gen_trend_1": [
        "Between {start_time} and {end_time} seconds, the data exhibited a {trend} trend.",
        "The data showed a {trend} trend from {start_time} to {end_time} seconds.",
        "A {trend} trend was observed in the data spanning {start_time} to {end_time} seconds.",
        "The time period from {start_time} to {end_time} seconds was characterized by a {trend} trend in the data.",
        "Over the course of {start_time} to {end_time} seconds, the data displayed a {trend} trend.",
        "The data followed a {trend} trend during the time frame of {start_time} to {end_time} seconds.",
        "From {start_time}s to {end_time}s, a {trend} trend was evident in the data.",
        "The data manifested a {trend} trend within the {start_time} to {end_time} second range.",
        "Throughout the {start_time} to {end_time} second interval, the data demonstrated a {trend} trend.",
        "Data analysis from {start_time}s to {end_time}s indicated a {trend} trend.",
        "In the timeframe from {start_time}s to {end_time}s, the data presented a {trend} trend.",
        "Observing the data between {start_time} and {end_time} seconds revealed a {trend} trend.",
        "The data, from {start_time}s to {end_time}s, revealed a {trend} trend.",
        "From {start_time} to {end_time} seconds, there's a {trend} trend indicated by the data.",
        "During the period from {start_time}s to {end_time}s, the data exhibited a {trend} trend.",
        "Between {start_time} and {end_time} seconds, we observed a {trend} trend in the data.",
        "The data from {start_time} to {end_time} seconds showed a {trend} trend.",
        "A {trend} trend was evident in the data spanning from {start_time}s to {end_time}s.",
        "The data displayed a {trend} trend during the period between {start_time}s and {end_time}s.",
        "Within the {start_time} to {end_time} second range, the data presented a {trend} trend.",
        "The data revealed a {trend} trend spanning from {start_time} to {end_time} seconds.",
        "The data showcased a {trend} trend within the timeframe of {start_time}s to {end_time}s.",
        "Between {start_time} and {end_time} seconds, the data showed a {trend} trend.",
        "From {start_time} to {end_time} seconds, there was a {trend} trend observed in the data.",
        "The data demonstrated a {trend} trend from {start_time}s to {end_time}s.",
        "A {trend} trend in the data was evident between {start_time} and {end_time} seconds.",
        "Observations from {start_time} to {end_time} seconds indicated a {trend} trend in the data.",
        "Data between {start_time} seconds and {end_time} seconds revealed a {trend} trend.",
        "From {start_time}s to {end_time}s, the trend in the data was {trend}.",
        "The period from {start_time} to {end_time} seconds showed a {trend} trend in the data.",
    ],
    "gen_trend_2": [
        "Subsequently, a {trend} trend was observed until {end_time}s.",
        "Following this, the data showed a {trend} trend lasting up to {end_time} seconds.",
        "Afterward, a {trend} trend emerged and continued until {end_time}s.",
        "The previous trend was succeeded by a {trend} trend, which persisted up to {end_time} seconds.",
        "A {trend} trend then followed, extending to {end_time}s.",
        "The data then exhibited a {trend} trend, which carried on until {end_time} seconds.",
        "After the previous trend, a {trend} trend was noted, lasting until {end_time}s.",
        "The subsequent trend was {trend}, and it remained until {end_time} seconds.",
        "The {trend} trend continued until {end_time} seconds.",
        "The data maintained a {trend} trend through {end_time}s.",
        "Up to {end_time} seconds, the data persisted in a {trend} trend.",
        "The {trend} trend carried on till {end_time} seconds.",
        "A {trend} trend was sustained by the data up to {end_time} seconds.",
        "The data upheld a {trend} trend leading up to {end_time}s.",
        "Until {end_time}s, the data prolonged its {trend} trend.",
        "The {trend} trend in the data endured up until {end_time} seconds.",
        "The data perpetuated a {trend} trend all the way to {end_time}s.",
        "Extending to {end_time}s, the data maintained its {trend} trend.",
        "This was succeeded by a {trend} trend until {end_time} seconds.",
        "Subsequently, a {trend} trend was observed up to {end_time} seconds.",
        "Following this, the data exhibited a {trend} trend up to {end_time}s.",
        "Thereafter, a {trend} trend continued until {end_time} seconds.",
        "Afterwards, the trend shifted to {trend} until {end_time} seconds.",
        "The situation then transitioned into a {trend} trend up to {end_time} seconds.",
        "Subsequently, the trend moved to {trend} lasting until {end_time} seconds.",
        "This period was marked by a {trend} trend up until {end_time} seconds.",
        "Following that period, a {trend} trend was evident until {end_time}s.",
        "The data then exhibit a {trend} trend until reaching {end_time}s.",
        "The trend then shifted to a {trend} direction, lasting until {end_time}s.",
        "What followed was a {trend} trend, extending to {end_time} seconds.",
        "The data then entered a {trend} phase, which lasted until {end_time} seconds.",
        "Next, the trend took a {trend} turn, continuing up to {end_time}s.",
        "This phase was characterized by a {trend} trend until {end_time} seconds.",
        "It was then that the trend veered towards {trend}, which persisted until {end_time}s.",
        "Subsequently, the {trend} trend became apparent, prevailing until {end_time} seconds.",
        "The trend subsequently morphed into a {trend} pattern, holding until {end_time} seconds.",
        "Following this phase, the trend evolved into a {trend} trajectory until {end_time} seconds.",
        "Thereafter, the sequence of events led to a {trend} trend, which concluded at {end_time}s.",
        "Continuing onwards, a {trend} trend was observed through to {end_time} seconds.",
        "The trend subsequently evolved into a {trend} mode, prevailing up until {end_time} seconds.",
        "After that, the {trend} trend became the dominant pattern until {end_time} seconds.",
        "The pattern then entered a {trend} phase, which sustained up to {end_time}s.",
        "Following this development, the trend solidified into a {trend} direction, continuing until {end_time} seconds.",
        "The data then aligned with a {trend} trend, which was maintained up to {end_time} seconds.",
        "Subsequent observations indicated a {trend} trend, lasting until {end_time}s.",
        "The period following showed a sustained {trend} trend up to {end_time} seconds.",
        "The subsequent phase was defined by a {trend} trend, enduring until {end_time}s.",
        "The trend then progressed to a {trend} state, concluding at {end_time} seconds.",
        "Following this interval, the trend gravitated towards {trend}, persisting through {end_time} seconds.",
        "Subsequently, the trend shifted into a {trend} trend, which lasted till {end_time} seconds.",
        "In the next phase, a clear {trend} trend was evident, continuing right up to {end_time}s.",
        "The data's trajectory shifted towards a {trend} trend, lasting up until {end_time}s.",
        "After these developments, the {trend} trend took hold, extending to {end_time} seconds.",
        "The sequence of events led to a {trend} trend, which remained until {end_time}s.",
        "Then, a {trend} trend until {end_time}s.",
        "A {trend} trend followed, through {end_time} seconds.",
        "{trend} trend up to {end_time} seconds.",
        "Next, {trend} until {end_time}s.",
        "Followed by {trend} to {end_time}s.",
        "{trend} persisted until {end_time} seconds.",
        "Then, {trend} through {end_time} seconds.",
        "Subsequently, {trend} till {end_time}s.",
        "{trend} until {end_time} seconds.",
        "Afterward, {trend} to {end_time}s.",
        "Continues {trend} until {end_time} seconds.",
        "Trended {trend} until {end_time}s.",
        "Showed {trend} until {end_time} seconds.",
        "Until {end_time} seconds, we observed a {trend} trend.",
        "As of {end_time}s, the trend was {trend}.",
        "By {end_time} seconds, there was a noticeable {trend} trend.",
        "By the time it reached {end_time}s, a {trend} trend was evident.",
    ],
    "gen_trend_3": [
        "Ultimately, a {trend} trend was seen in the data up until {end_time} seconds.",
        "The data concluded with a {trend} trend, lasting up to {end_time} seconds.",
        "The final trend observed in the data was {trend}, which continued up to {end_time} seconds.",
        "In the end, the data displayed a {trend} trend that lasted up to {end_time}s.",
        "The concluding trend in the data was {trend}, which persevered up until {end_time}s.",
        "Up to {end_time}s, the data finished with a {trend} trend.",
        "The data's final trend was {trend}, which was maintained up to {end_time}s.",
        "Lastly, a {trend} trend was noted in the data, enduring until {end_time} seconds.",
        "The data's concluding trend was {trend}, which persisted up to {end_time} seconds.",
        "At the end, the data exhibited a {trend} trend that carried on until {end_time}s.",
        "The terminal trend in the data was {trend}, which held fast up to {end_time} seconds.",
        "In conclusion, the data demonstrated a {trend} trend that continued up to {end_time} seconds.",
        "Up until {end_time} seconds, the final trend {trend} was noted.",
        "The final trend had been {trend} up to {end_time}s.",
        "Continuing until {end_time}s, the trend was decidedly {trend}.",
        "Ultimately, by {end_time} seconds, a {trend} trend had been observed.",
        "Conclusively, up to {end_time}s, the data showed a {trend} trend.",
        "In the end, until {end_time}s, there was an observable {trend} trend.",
        "To conclude, by {end_time}s, a {trend} trend was noted in the data.",
        "The observation concluded with a {trend} trend by {end_time}s.",
        "Finishing at {end_time} seconds, the data revealed a {trend} trend.",
        "The concluding observation in the data was a {trend} trend, persisting up to {end_time} seconds.",
        "The data's final chapter was characterized by a {trend} trend, lasting up to {end_time}s.",
        "The data's end was marked by a {trend} trend, which sustained its direction up to {end_time}s.",
        "The final data trend, {trend}, stayed its course to {end_time} seconds.",
        "The data's final trend, {trend}, persisted up to {end_time} seconds.",
        "The data ended with a {trend} trend up to {end_time}s.",
        "The data's end saw a {trend} trend, enduring to {end_time} seconds.",
        "The data's end was {trend}, a trend that held to {end_time} seconds.",
    ],
    "gen_trend_4": [
        "In summary, the data contains a total of {upward_num} segments with continuous {upward_trend} trends",
        "Overall, the data shows {upward_num} {upward_trend} trends",
        "The data reveals a total of {upward_num} segments exhibiting continuous {upward_trend} trends",
        "Summarizing the data, there are {upward_num} ongoing {upward_trend} trends",
        "In essence, the dataset comprises {upward_num} segments with persistent {upward_trend} trends",
        "The summary indicates that the data includes {upward_num} segments with {upward_trend} trends",
        "In brief, the dataset shows {upward_num} segments with {upward_trend} trends",
        "To sum up, the data contains {upward_num} uninterrupted {upward_trend} trends",
        "The analysis indicates that there are {upward_num} segments with continuous {upward_trend} trends",
        "In short, the data reveals {upward_num} segments with {upward_trend} trends",
        "According to the data, there are {upward_num} segments showing continuous {upward_trend} trends",
        "In summary, the analysis found {upward_num} {upward_trend} trends",
        "The summary reveals {upward_num} segments with {upward_trend} trends",
    ],
    "gen_trend_5": [
        "{downward_num} segments with continuous {downward_trend} trends",
        "{downward_num} {downward_trend} trends",
        "{downward_num} segments exhibiting continuous {downward_trend} trends",
        "{downward_num} ongoing {downward_trend} trends",
        "{downward_num} segments with persistent {downward_trend} trends",
        "{downward_num} segments with {downward_trend} trends",
        "{downward_num} segments with {downward_trend} trends",
        "{downward_num} uninterrupted {downward_trend} trends",
        "{downward_num} segments with continuous {downward_trend} trends",
        "{downward_num} segments with {downward_trend} trends",
        "{downward_num} segments showing continuous {downward_trend} trends",
        "{downward_num} {downward_trend} trends",
        "{downward_num} segments with {downward_trend} trends",
    ],
    "gen_trend_6": [
        "and {stable_num} segments with {stable_trend} trends",
        "and {stable_num} {stable_trend} trends",
        "and {stable_num} segments exhibiting {stable_trend} trends",
        "and {stable_num} {stable_trend} trends",
        "and {stable_num} segments with {stable_trend} trends",
        "and {stable_num} segments with {stable_trend} trends",
        "and {stable_num} segments with {stable_trend} trends",
        "and {stable_num} uninterrupted {stable_trend} trends",
        "and {stable_num} segments with continuous {stable_trend} trends",
        "and {stable_num} segments with {stable_trend} trends",
        "and {stable_num} segments showing {stable_trend} trends",
        "and {stable_num} {stable_trend} trends",
        "and {stable_num} segments with {stable_trend} trends",
    ],
    "gen_subtrend_q": [
        "Please describe how the input {data}'s trends changed from {start_time}s to {end_time}s.",
        "Kindly analyze the {data} trend variations between {start_time} and {end_time} seconds.",
        "Please provide an overview of how the {data} trends evolved from {start_time} seconds to {end_time} seconds.",
        "I would appreciate if you could describe the {data} trend fluctuations that occurred within the {start_time} to {end_time} second "
        "timeframe.",
        "Could you please examine the {data} and explain the trend shifts observed from {start_time}s until {end_time}s?",
        "I kindly request an analysis of the {data} trend changes spanning the period between {start_time} and {end_time} seconds.",
        "Please evaluate the {data} trends and describe how they developed from {start_time} seconds to {end_time} seconds.",
        "I would be grateful if you could provide a description of the {data} trend alterations that took place from {start_time}s to {end_time}s.",
        "Could you kindly assess the {data} trend transformations occurring within the {start_time} to {end_time} second range?",
        "Please analyze the trend of the {data} from {start_time} seconds to {end_time} seconds.",
        "Could you describe how the {data} trend changes between {start_time}s and {end_time}s?",
        "I'm interested in the input {data}'s trend from {start_time} to {end_time} seconds. Can you break it down for me?",
        "Can you provide an analysis of the {data} trend from {start_time} seconds to {end_time} seconds?",
        "Would you be able to detail the trend changes in the given {data} from {start_time} to {end_time} seconds?",
        "I'd like an overview of how the input {data} evolves between {start_time} and {end_time} seconds. Can you help?",
        "Please give me an insight into the {data}'s progression from {start_time}s to {end_time}s.",
        "Could you examine the shift in {data} trends from {start_time} seconds to {end_time} seconds?",
        "I'm looking for a summary of the {data} trends between {start_time} and {end_time} seconds. What can you tell me?",
        "Can you explore the changes in the {data}'s trend from {start_time} to {end_time} seconds?",
        "Describe the trend of {data} from {start_time}s to {end_time}s.",
        "How did the {data} trend evolve from {start_time} to {end_time} seconds?",
        "Please outline the change in {data}'s trend between {start_time}s and {end_time}s.",
        "Can you detail the shift in {data} from {start_time} seconds to {end_time} seconds?",
        "Explain the transition in {data} from {start_time} to {end_time} seconds.",
        "Describe the {data}'s trend changes from {start_time} seconds to {end_time} seconds.",
        "How did the {data}'s trends evolve between {start_time} and {end_time} seconds?",
        "Explain the {data}'s trend shifts from {start_time}s to {end_time}s.",
        "Analyze the {data}'s trend variations between {start_time}s and {end_time}s.",
        "What were the {data}'s trend modifications from {start_time} to {end_time} seconds?",
        "Summarize the {data}'s trend developments between {start_time} and {end_time} seconds.",
        "Detail the {data}'s trend fluctuations from {start_time} to {end_time} seconds.",
        "Examine the {data}'s trend patterns between {start_time}s and {end_time}s.",
        "Describe how the {data}'s trends altered from {start_time} to {end_time} seconds.",
        "Provide an overview of the {data}'s trend changes between {start_time} seconds and {end_time} seconds.",
    ],
}


def capitalize_first_letter(string):
    if len(string) == 0:
        return string
    else:
        return string[0].upper() + string[1:]


def check_a_an(sentence):
    words = re.findall(r"\b\w+\b", sentence)
    vowels = "aeiouAEIOU"
    corrected_sentence = sentence

    for i in range(len(words)):
        if words[i] in ["a", "an", "A", "An"]:
            if i + 1 < len(words):
                next_word = words[i + 1]
                if words[i] == "a" and next_word[0] in vowels:
                    corrected_sentence = corrected_sentence.replace(f" a {next_word}", f" an {next_word}", 1)
                elif words[i] == "A" and next_word[0] in vowels:
                    corrected_sentence = corrected_sentence.replace(f" A {next_word}", f" An {next_word}", 1)
                elif words[i] == "an" and next_word[0] not in vowels:
                    corrected_sentence = corrected_sentence.replace(f" an {next_word}", f" a {next_word}", 1)
                elif words[i] == "An" and next_word[0] not in vowels:
                    corrected_sentence = corrected_sentence.replace(f" An {next_word}", f" A {next_word}", 1)

    return corrected_sentence


def analyze_trend(time_series, sample_rate, start_point=0):
    # Calculate the time interval between data points
    time_interval = 1 / sample_rate

    # Initialize lists to store the analysis results
    from_time, to_time, from_value, to_value, trend = [], [], [], [], []

    # Analyze the trend between consecutive data points
    for i in range(len(time_series) - 1):
        start_time = round((start_point + i) * time_interval, 2)
        end_time = round((start_point + i + 1) * time_interval, 2)
        start_val = time_series[i]
        end_val = time_series[i + 1]

        # Determine the trend
        if start_val == end_val:
            trend_type = "steady"
        elif start_val < end_val:
            trend_type = "increase"
        else:
            trend_type = "decrease"

        # Append the results to the lists
        from_time.append(start_time)
        to_time.append(end_time)
        from_value.append(start_val)
        to_value.append(end_val)
        trend.append(trend_type)

    # Create a DataFrame from the results
    result_df = pd.DataFrame({"from_time": from_time, "to_time": to_time, "from_value": from_value, "to_value": to_value, "trend": trend})

    return result_df


def merge_adjacent_rows(df):
    # List to store the merged rows
    merged_rows = []

    # Variables to store the start of the current segment
    current_start_time = df.iloc[0]["from_time"]
    current_start_value = df.iloc[0]["from_value"]
    current_trend = df.iloc[0]["trend"]
    current_values = [current_start_value]

    for index, row in df.iterrows():
        if row["trend"] == current_trend:
            # Continue accumulating values
            current_values.append(row["to_value"])
        else:
            # Close the current segment and start a new one
            merged_rows.append(
                {
                    "start_time": current_start_time,
                    "end_time": df.iloc[index - 1]["to_time"],
                    "start_value": current_start_value,
                    "end_value": df.iloc[index - 1]["to_value"],
                    "trend": current_trend,
                    "values": current_values.copy(),
                }
            )
            current_start_time = row["from_time"]
            current_start_value = row["from_value"]
            current_trend = row["trend"]
            current_values = [current_start_value, row["to_value"]]

    # Append the last segment
    merged_rows.append(
        {
            "start_time": current_start_time,
            "end_time": df.iloc[-1]["to_time"],
            "start_value": current_start_value,
            "end_value": df.iloc[-1]["to_value"],
            "trend": current_trend,
            "values": current_values,
        }
    )

    # Create a DataFrame from the merged rows
    merged_df = pd.DataFrame(merged_rows)

    return merged_df


def df2mkd(df):
    header = "| " + " | ".join(df.columns) + " |"
    separator = "|---" * len(df.columns) + "|"

    rows = []
    for _, row in df.iterrows():
        row_str = "| " + " | ".join(str(value) for value in row) + " |"
        rows.append(row_str)

    markdown_table = "\n".join([header, separator] + rows)
    return markdown_table


def calculate_total_time(df):
    """
    Calculate the total duration for each trend in the dataframe.

    Parameters:
    - df (DataFrame): A DataFrame with columns: from_time, to_time, trend.

    Returns:
    - DataFrame: A DataFrame with columns: trend, total_time.
    """
    # Group by the trend and sum the duration for each trend
    total_time_by_trend = df.groupby("trend").apply(lambda x: round((x["end_time"] - x["start_time"]).sum(), 2)).reset_index(name="total_time")

    return total_time_by_trend


def num_to_words(num):
    units = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    teens = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    scales = ["", "thousand", "million", "billion"]

    if num < 0:
        return "minus " + num_to_words(abs(num))

    if num < 10:
        return units[int(num)]

    if num < 20:
        return teens[int(num) - 10]

    if num < 100:
        return tens[int(num) // 10] + (" " + num_to_words(num % 10) if num % 10 != 0 else "")

    if num < 1000:
        return units[int(num) // 100] + " hundred" + (" " + num_to_words(num % 100) if num % 100 != 0 else "")

    for i, scale in enumerate(scales[1:], 1):
        if num < 1000 ** (i + 1):
            return num_to_words(num // (1000**i)) + " " + scale + (" " + num_to_words(num % (1000**i)) if num % (1000**i) != 0 else "")


def convert_number(num):
    if "." in str(num):
        whole, decimal = str(num).split(".")
        if decimal == "0":
            return num_to_words(int(num))
        else:
            return num_to_words(int(whole)) + " point " + " ".join([num_to_words(int(digit)) for digit in decimal])
    else:
        return num_to_words(int(num))


def format_floart_2_int(num):
    if isinstance(num, float) and num.is_integer():
        return int(num)
    else:
        return num


def select_random_pair():
    word_pairs = PROMPT_DICT["trend_synonyms"]
    upward_word = random.choice(list(word_pairs.keys()))
    downward_word = word_pairs[upward_word]
    steady_word = random.choice(PROMPT_DICT["steady_synonyms"])
    return [upward_word, downward_word, steady_word]


def choose_word(input_trend, pair):
    if input_trend == "steady":
        return pair[2]
    elif input_trend == "increase" or input_trend == "upward":
        return pair[0]
    else:
        return pair[1]


def generate_smry_text(reading, data_df, sensor_type, pair_list):
    """
    Generate a text description of the data.

    Parameters:
    - data_df (DataFrame): A DataFrame with columns: from_time, to_time, from_value, to_value, trend, values.
    - total_time_df (DataFrame): A DataFrame with columns: trend, total_time.

    Returns:
    - str: A text description of the data.
    """
    total_time_df = calculate_total_time(data_df)
    total_time_mkd = df2mkd(total_time_df)
    connect_words = ["followed by ", "came after ", "and then ", "trailed by ", "which was followed by ", "succeeded by "]
    # Initialize a list to store the text description
    prompts_templates1 = PROMPT_DICT["gen_summary_1"]
    prompts_templates2 = PROMPT_DICT["gen_summary_2"]
    prompts_templates2_2 = PROMPT_DICT["gen_summary_2_2"]
    prompts_templates3 = PROMPT_DICT["gen_summary_3"]
    prompts_templates4 = PROMPT_DICT["gen_summary_4"]

    trend_num = len(total_time_df)
    change_num = len(data_df)
    data_types = ["time series data", "sensor data"]

    selected_data_type = random.choice(data_types)

    selected_template1 = random.choice(prompts_templates1)
    selected_template2 = random.choice(prompts_templates2)
    selected_template2_2 = random.choice(prompts_templates2_2)
    selected_template3 = random.choice(prompts_templates3)
    selected_template4 = random.choice(prompts_templates4)
    selected_template5 = random.choice(prompts_templates4)

    text = []
    text.append(
        capitalize_first_letter(
            selected_template1.format(
                data_name=selected_data_type,
                sensor_name=sensor_type,
                start_time=data_df["start_time"].iloc[0],
                end_time=data_df["end_time"].iloc[-1],
            )
        )
    )
    if trend_num == 1:
        text.append(capitalize_first_letter(selected_template2_2.format(trend_num=random.choice([trend_num, convert_number(trend_num)]))))
    else:
        text.append(
            capitalize_first_letter(
                selected_template2.format(
                    trend_num=random.choice([trend_num, convert_number(trend_num)]),
                    change_num=random.choice([change_num, convert_number(change_num)]),
                )
            )
        )

    i_t = 0
    for index, t in total_time_df.iterrows():
        if i_t == 0:
            if len(total_time_df) == 1:
                text.append(
                    capitalize_first_letter(
                        selected_template3.format(trend_type=choose_word(t["trend"], pair_list), total_time=f"{t['total_time']:.2f}")
                    )
                    + "."
                )
            else:
                text.append(
                    capitalize_first_letter(
                        selected_template3.format(trend_type=choose_word(t["trend"], pair_list), total_time=f"{t['total_time']:.2f}")
                    )
                    + ","
                )
        elif i_t < len(total_time_df) - 1:
            text.append(
                random.choice(connect_words)
                + selected_template4.format(trend_type=choose_word(t["trend"], pair_list), total_time=f"{t['total_time']:.2f}")
                + ","
            )
        else:
            text.append("and " + selected_template5.format(trend_type=choose_word(t["trend"], pair_list), total_time=f"{t['total_time']:.2f}") + ".")
        i_t += 1

    differences = np.diff(reading)
    sum_of_differences = np.sum(differences)
    if sum_of_differences > 0:
        overall_trend = choose_word("upward", pair_list)
    elif sum_of_differences < 0:
        overall_trend = choose_word("downward", pair_list)
    else:
        overall_trend = choose_word("steady", pair_list)

    if change_num > 1:
        prompts_templates7 = PROMPT_DICT["gen_summary_6"]
        selected_template7 = random.choice(prompts_templates7)

        text.append(capitalize_first_letter(selected_template7.format(overall_trend=overall_trend)))

    return check_a_an(" ".join(text)), total_time_mkd


def generate_trend_text(data_df, pair_list):
    text_detailed = []

    prompts_templates1 = PROMPT_DICT["gen_trend_1"]
    prompts_templates2 = PROMPT_DICT["gen_trend_2"]
    prompts_templates3 = PROMPT_DICT["gen_trend_3"]

    i_d = 0
    for index, d in data_df.iterrows():
        if i_d == 0:
            selected_template1 = random.choice(prompts_templates1)
            text_detailed.append(
                capitalize_first_letter(
                    selected_template1.format(start_time=d["start_time"], end_time=d["end_time"], trend=choose_word(d["trend"], pair_list))
                )
            )
        elif i_d < len(data_df) - 1:
            selected_template2 = random.choice(prompts_templates2)
            text_detailed.append(capitalize_first_letter(selected_template2.format(end_time=d["end_time"], trend=choose_word(d["trend"], pair_list))))
        else:
            selected_template3 = random.choice(prompts_templates3)
            text_detailed.append(capitalize_first_letter(selected_template3.format(end_time=d["end_time"], trend=choose_word(d["trend"], pair_list))))
        i_d += 1

    prompts_templates4 = PROMPT_DICT["gen_trend_4"]
    prompts_templates5 = PROMPT_DICT["gen_trend_5"]
    prompts_templates6 = PROMPT_DICT["gen_trend_6"]

    rdm_list = list(range(0, len(prompts_templates4)))
    selected_num = random.choice(rdm_list)

    selected_template4 = prompts_templates4[selected_num]
    selected_template5 = prompts_templates5[selected_num]
    selected_template6 = prompts_templates6[selected_num]

    trend_counts = data_df["trend"].value_counts()
    num_trends = len(trend_counts)

    for i_n in range(num_trends):
        if i_n == 0:
            if num_trends > 1:
                text_detailed.append(
                    capitalize_first_letter(
                        selected_template4.format(upward_num=trend_counts.values[i_n], upward_trend=choose_word(trend_counts.index[i_n], pair_list))
                    )
                    + ","
                )
        elif i_n < num_trends - 1:
            text_detailed.append(
                selected_template5.format(downward_num=trend_counts.values[i_n], downward_trend=choose_word(trend_counts.index[i_n], pair_list)) + ","
            )
        else:
            text_detailed.append(
                selected_template6.format(stable_num=trend_counts.values[i_n], stable_trend=choose_word(trend_counts.index[i_n], pair_list)) + "."
            )

    return check_a_an(" ".join(text_detailed))


def generate_simple_trend_text(data_df, pair_list):
    text_detailed = []

    prompts_templates = [
        "{start_time}s to {end_time}s: {trend}",
        "{start_time} seconds to {end_time} seconds: {trend}",
        "{start_time} to {end_time} seconds: {trend}",
        "{start_time}-{end_time} seconds: {trend}",
        "{start_time}-{end_time}s: {trend}",
        "{start_time}s-{end_time}s: {trend}",
    ]

    prompts_templates_2 = [
        "Number of {trend} trends: {num}",
        "Count of {trend} trends: {num}",
        "Total {trend} trends: {num}",
        "Number of {trend} segments: {num}",
        "Count of {trend} segments: {num}",
        "Total {trend} segments: {num}",
    ]

    selected_template = random.choice(prompts_templates)
    selected_template2 = random.choice(prompts_templates_2)

    for index, df in data_df.iterrows():
        text_detailed.append(
            selected_template.format(start_time=df["start_time"], end_time=df["end_time"], trend=choose_word(df["trend"], pair_list))
        )

    trend_counts = data_df["trend"].value_counts()
    num_trends = len(trend_counts)
    if num_trends > 1:
        for i_n in range(num_trends):
            text_detailed.append(selected_template2.format(trend=choose_word(trend_counts.index[i_n], pair_list), num=trend_counts.values[i_n]))

    return check_a_an("\n".join(text_detailed))


def dscb_trend(df, sensor_type, pair_list, whether_gpt=False, model_type="3.5"):
    data_types = ["time series data", "sensor data"]
    prompts_templates = PROMPT_DICT["gen_subtrend_q"]

    selected_data_type = random.choice(data_types)
    selected_template = random.choice(prompts_templates)

    question = selected_template.format(data=selected_data_type, start_time=df["start_time"].iloc[0], end_time=df["end_time"].iloc[-1])
    answer = generate_trend_text(df, pair_list)

    return {"Q": question, "A": answer, "type": "trend"}


def dscb_simple_trend(df, sensor_type, pair_list, whether_gpt=False, model_type="3.5"):
    data_types = ["time series data", "sensor data"]
    prompts_templates = PROMPT_DICT["gen_trend_q"]

    selected_data_type = random.choice(data_types)
    selected_template = random.choice(prompts_templates)

    question = selected_template.format(data=selected_data_type)

    answer = generate_simple_trend_text(df, pair_list)

    return {"Q": question, "A": answer, "type": "simple_trend"}


def QA_summary(reading, trend_df, sensor_type, pair_list, whether_gpt=False, model_type="3.5"):
    data_types = ["time series data", "sensor data"]
    prompts_templates = PROMPT_DICT["gen_subtrend_q"]

    selected_data_type = random.choice(data_types)
    selected_template = random.choice(prompts_templates)

    question = selected_template.format(data=selected_data_type, start_time=trend_df["start_time"].iloc[0], end_time=trend_df["end_time"].iloc[-1])

    answer, smry_mkd_df = generate_smry_text(reading, trend_df, sensor_type, pair_list)
    return {"Q": question, "A": answer, "smry_table": smry_mkd_df, "type": "summary"}


sr = 50
qa_dict = {"author": "", "version": "", "date": str(datetime.now().date()), "dataset": []}


i = 0
for d in all_train_segments:
    assert len(d[0]) == 15
    c_acc_x = d[:, 0]
    c_acc_y = d[:, 1]
    c_acc_z = d[:, 2]
    la_acc_x = d[:, 3]
    la_acc_y = d[:, 4]
    la_acc_z = d[:, 5]
    la_gs_x = d[:, 6]
    la_gs_y = d[:, 7]
    la_gs_z = d[:, 8]
    rla_acc_x = d[:, 9]
    rla_acc_y = d[:, 10]
    rla_acc_z = d[:, 11]
    rla_gs_x = d[:, 12]
    rla_gs_y = d[:, 13]
    rla_gs_z = d[:, 14]
    reading_list = [
        c_acc_x,
        c_acc_y,
        c_acc_z,
        la_acc_x,
        la_acc_y,
        la_acc_z,
        la_gs_x,
        la_gs_y,
        la_gs_z,
        rla_acc_x,
        rla_acc_y,
        rla_acc_z,
        rla_gs_x,
        rla_gs_y,
        rla_gs_z,
    ]
    reading_name = [
        "chest x-axis accelerometer",
        "chest y-axis accelerometer",
        "chest z-axis accelerometer",
        "left-ankle x-axis accelerometer",
        "left-ankle y-axis accelerometer",
        "left-ankle z-axis accelerometer",
        "left-ankle x-axis gyroscope",
        "left-ankle y-axis gyroscope",
        "left-ankle z-axis gyroscope",
        "right-lower-arm x-axis accelerometer",
        "right-lower-arm y-axis accelerometer",
        "right-lower-arm z-axis accelerometer",
        "right-lower-arm x-axis gyroscope",
        "right-lower-arm y-axis gyroscope",
        "right-lower-arm z-axis gyroscope",
    ]

    data_dict = {"index": i, "summaries": {}, "qa_pairs": {name: [] for name in reading_name}}

    for r, n in zip(reading_list, reading_name):
        normalized_n = "normalized " + n
        t_df = analyze_trend(r, sr)
        trend_dataframe = merge_adjacent_rows(t_df)

        trend_pair_list = select_random_pair()

        data_dict["summaries"][n] = QA_summary(r, trend_dataframe, normalized_n, trend_pair_list, whether_gpt=False, model_type="3.5")
        data_dict["qa_pairs"][n].append(dscb_simple_trend(trend_dataframe, normalized_n, trend_pair_list, whether_gpt=False, model_type="4"))
    qa_dict["dataset"].append(data_dict)
    print(f"{i} finished")
    i += 1


with open(os.path.join(output_path, "train", "mhealth_train_qa_stage1.json"), "w") as f:
    json.dump(qa_dict, f, indent=2)
print(len(qa_dict["dataset"]))

qa_dict = {"author": "", "version": "", "date": str(datetime.now().date()), "dataset": []}
i = 0
for d in all_test_segments:
    assert len(d[0]) == 15
    c_acc_x = d[:, 0]
    c_acc_y = d[:, 1]
    c_acc_z = d[:, 2]
    la_acc_x = d[:, 3]
    la_acc_y = d[:, 4]
    la_acc_z = d[:, 5]
    la_gs_x = d[:, 6]
    la_gs_y = d[:, 7]
    la_gs_z = d[:, 8]
    rla_acc_x = d[:, 9]
    rla_acc_y = d[:, 10]
    rla_acc_z = d[:, 11]
    rla_gs_x = d[:, 12]
    rla_gs_y = d[:, 13]
    rla_gs_z = d[:, 14]
    reading_list = [
        c_acc_x,
        c_acc_y,
        c_acc_z,
        la_acc_x,
        la_acc_y,
        la_acc_z,
        la_gs_x,
        la_gs_y,
        la_gs_z,
        rla_acc_x,
        rla_acc_y,
        rla_acc_z,
        rla_gs_x,
        rla_gs_y,
        rla_gs_z,
    ]
    reading_name = [
        "chest x-axis accelerometer",
        "chest y-axis accelerometer",
        "chest z-axis accelerometer",
        "left-ankle x-axis accelerometer",
        "left-ankle y-axis accelerometer",
        "left-ankle z-axis accelerometer",
        "left-ankle x-axis gyroscope",
        "left-ankle y-axis gyroscope",
        "left-ankle z-axis gyroscope",
        "right-lower-arm x-axis accelerometer",
        "right-lower-arm y-axis accelerometer",
        "right-lower-arm z-axis accelerometer",
        "right-lower-arm x-axis gyroscope",
        "right-lower-arm y-axis gyroscope",
        "right-lower-arm z-axis gyroscope",
    ]

    data_dict = {"index": i, "summaries": {}, "qa_pairs": {name: [] for name in reading_name}}

    for r, n in zip(reading_list, reading_name):
        normalized_n = "normalized " + n
        t_df = analyze_trend(r, sr)
        trend_dataframe = merge_adjacent_rows(t_df)

        trend_pair_list = select_random_pair()

        data_dict["summaries"][n] = QA_summary(r, trend_dataframe, normalized_n, trend_pair_list, whether_gpt=False, model_type="3.5")
        data_dict["qa_pairs"][n].append(dscb_simple_trend(trend_dataframe, normalized_n, trend_pair_list, whether_gpt=False, model_type="4"))
    qa_dict["dataset"].append(data_dict)
    print(f"{i} finished")
    i += 1

with open(os.path.join(output_path, "test", "mhealth_test_qa_stage1.json"), "w") as f:
    json.dump(qa_dict, f, indent=2)
print(len(qa_dict["dataset"]))
