"""公式ノート mhealth_stageN.ipynb 相当の学習データ生成スクリプト(自動生成)。
MHealth を取得して ./MHEALTHDATASET/ に展開し、./data 配下に pkl + QA-JSON を出力する。"""
import os, io, zipfile, urllib.request
if not os.path.isdir("MHEALTHDATASET"):
    print("[prep] downloading MHealth ...", flush=True)
    with urllib.request.urlopen("https://archive.ics.uci.edu/static/public/319/mhealth+dataset.zip", timeout=180) as r:
        zipfile.ZipFile(io.BytesIO(r.read())).extractall(".")
os.makedirs("data/train", exist_ok=True); os.makedirs("data/test", exist_ok=True)

import numpy as np
from scipy.io import loadmat
import random
import os
import re
import pickle
import torch
import pandas as pd

def check_label_continuity(df):
    continuity_segments = {}

    for subject in df['subject'].unique():
        subject_data = df[df['subject'] == subject]
        assert subject_data.index[0]==0

        for label in subject_data['activity'].unique():
            label_data = subject_data[subject_data['activity'] == label]

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

def split_sequences(sequences, window_size, stride):
    assert len(sequences[0]) == 15
    has_null = any(any(pd.isnull(item) or item == '' for item in sublist) for sublist in sequences) # 输出结果
    if has_null:
        raise ValueError("Has null values")

    segments = []
    labels = []

    num_complete_segments = (len(sequences) - window_size) // stride + 1

    for i in range(num_complete_segments):
        start = i * stride
        end = start + window_size
        segment = sequences[start:end]
        assert len(segment) == window_size
        segments.append(np.array(segment))
        labels.append([start, end-1])

    if labels[-1][1] < len(sequences) - 1:
        start = len(sequences) - window_size
        end = len(sequences)
        segment = sequences[start:end]
        assert len(segment) == window_size
        segments.append(np.array(segment))
        labels.append([start, end-1])
    assert len(labels) == len(segments)
    print(f"sequence length: {len(sequences)}\nsegments: {len(segments)}")
    pd.set_option('display.max_columns', None)
    print(labels[:5])
    print(labels[-5:])
    return segments, labels

activity_map = {
    1: 'Standing still (1 min)',
    2: 'Sitting and relaxing (1 min)',
    3: 'Lying down (1 min)',
    4: 'Walking (1 min)',
    5: 'Climbing stairs (1 min)',
    6: 'Waist bends forward (20x)',
    7: 'Frontal elevation of arms (20x)',
    8: 'Knees bending (crouching) (20x)',
    9: 'Cycling (1 min)',
    10: 'Jogging (1 min)',
    11: 'Running (1 min)',
    12: 'Jump front & back (20x)'
}
test_id = ['subject1', 'subject3', 'subject6']
window_size=100
stride=50

all_train_segments = []
all_test_segments = []
all_train_labels = []
all_test_labels = []

for i in range(1, 11):
    df = pd.read_csv(f'./MHEALTHDATASET/mHealth_subject{i}.log', header=None, sep='\t')
    # Note: Excluding the ECG data collected with the chest sensor
    df = df.loc[:, [0, 1, 2, 5, 6, 7, 8, 9, 10, 14, 15, 16, 17, 18, 19, 23]].rename(columns= {
        0: 'acc_ch_x',
        1: 'acc_ch_y',
        2: 'acc_ch_z',
        5: 'acc_la_x',
        6: 'acc_la_y',
        7: 'acc_la_z',
        8: 'gyr_la_x',
        9: 'gyr_la_y',
        10: 'gyr_la_z',
        14: 'acc_rw_x',
        15: 'acc_rw_y',
        16: 'acc_rw_z',
        17: 'gyr_rw_x',
        18: 'gyr_rw_y',
        19: 'gyr_rw_z',
        23: 'activity'
    })
    df['subject'] = f'subject{i}'
    continuity_segments = check_label_continuity(df)
    for key, value in continuity_segments.items():
        if key[1] == 0: # class != 1
            continue
        print(f"Subject: {key[0]} Activity: {key[1]}")
        for segment in value:
            # 划分时间序列数据为片段
            rows = df.loc[segment[0]:segment[1]]

            assert len(rows['subject'].unique()) == 1
            assert rows['subject'].unique()[0] == key[0]
            assert len(rows['activity'].unique()) == 1, f"Subject {key[0]}, activity {key[1]} but has {rows['activity'].unique()},  {segment[0]} 到 {segment[1]}"
            assert rows['activity'].unique()[0] == key[1]

            subject_activity_df = rows.iloc[:, ~rows.columns.isin(['subject', 'activity'])]
            subject_activity_series = subject_activity_df.values.tolist()

            if key[0] not in test_id:
                segments, labels = split_sequences(subject_activity_series, window_size, stride)
                all_train_segments.extend(segments)
            else:
                segments, labels = split_sequences(subject_activity_series, window_size, stride)
                all_test_segments.extend(segments)

            for label in labels:
                label_dict = {
                    "subject": key[0],
                    "activity_name": activity_map[key[1]],
                    "activity": key[1]-1,
                    "segments": label
                }
                if key[0] not in test_id:
                    all_train_labels.append(label_dict)
                else:
                    all_test_labels.append(label_dict)
        print("------"*10)

print(f"all_train_segments: {len(all_train_segments)}")
print(f"all_train_labels: {len(all_train_labels)}")
print(f"all_test_segments: {len(all_test_segments)}")
print(f"all_test_labels: {len(all_test_labels)}")

output_path = "./whole_data"

with open(os.path.join(output_path, 'train', 'mhealth_train_data_stage2.pkl'), 'wb') as f:
    pickle.dump(all_train_segments, f)

with open(os.path.join(output_path, 'test', 'mhealth_test_data_stage2.pkl'), 'wb') as f:
    pickle.dump(all_test_segments, f)

with open(os.path.join(output_path, 'train', 'mhealth_train_labels_stage2.pkl'), 'wb') as f:
    pickle.dump(all_train_labels, f)

with open(os.path.join(output_path, 'test', 'mhealth_test_labels_stage2.pkl'), 'wb') as f:
    pickle.dump(all_test_labels, f)

import pickle
import random
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from statsmodels.tsa.stattools import acf
import json
import re

PROMPT_DICT = {
    "trend_synonyms": {
        "upward": "downward",
        "ascending": "descending",
        "rising": "falling",
        "increasing": "decreasing"
    },
    "steady_synonyms": [
        "steady",
        "constant",
        "stable"
    ],
    "gen_summary_1": [
        "The provided {data_name} are the 2-second time-series recordings of six sensor channels.",
        "The given {data_name} represent the 2-second time-series data from six sensor channels.",
        "{data_name} consist of 2-second time-series measurements from six sensor channels.",
        "{data_name} include 2-second time-series readings from six sensor channels.",
        "The supplied {data_name} are the 2-second time-series values of six sensor channels.",
        "The 2-second time-series data of six sensor channels are provided in {data_name}.",
        "Contained within {data_name} are the 2-second time-series readings of six sensor channels.",
        "The dataset {data_name} comprises 2-second time-series observations from six sensor channels.",
        "In {data_name}, you will find 2-second time-series data recorded from six sensor channels.",
        "{data_name} hold the 2-second time-series measurements from six distinct sensor channels.",
        "The {data_name} data set includes 2-second time-series readings from six sensors.",
        "{data_name} captures the 2-second time-series outputs from six sensor channels.",
        "2-second time-series information from six sensor channels is contained within {data_name}.",
        "Included in {data_name} are the 2-second time-series sensor readings from six channels.",
        "The {data_name} file contains 2-second time-series data for six different sensor channels.",
        "Within {data_name} are 2-second time-series recordings from six sensor channels.",
        "{data_name} encapsulates 2-second time-series data collected from six sensor channels.",
        "The 2-second time-series readings from six sensor channels are found in {data_name}.",
        "The time-series data in {data_name} spans 2 seconds from six sensor channels.",
        "{data_name} contains 2-second recordings of time-series data from six sensor channels.",
        "Included in {data_name} are the time-series readings over 2 seconds from six sensors.",
        "{data_name} comprises 2-second time-series records from six sensor channels.",
        "The 2-second data from six sensor channels is included in {data_name}.",
        "You can find 2-second time-series readings from six sensors in {data_name}.",
        "The {data_name} dataset contains six channels of 2-second time-series data.",
        "2-second measurements from six sensor channels are provided in {data_name}.",
        "{data_name} includes 2-second observations from six different sensor channels.",
        "The {data_name} resource holds 2-second time-series data from six sensor channels.",
        "{data_name} features 2-second time-series recordings from six sensor channels."
    ],
    "gen_summary_2": [
        "First, let's analyze the trend changes in each channel's data:\n",
        "To begin with, let's examine the trend variations in the data for each channel:\n",
        "Let's start by looking at the trend changes across each channel's data:\n",
        "Initially, let's analyze the trend shifts in the data for each channel:\n",
        "First of all, let's delve into the trend variations in each channel's data:\n",
        "Let's kick off by analyzing how the trends change in each channel's data:\n",
        "Starting with an analysis, let's observe the trend changes in each channel's data:\n",
        "Let's commence by examining the trend shifts in each channel's data:\n",
        "First, let's take a look at the trend alterations in the data for each channel:\n",
        "Let's begin by analyzing the trend changes for each channel's data:\n",
        "Initially, let's take a closer look at the trend changes in each channel's data:\n",
        "To start, let's explore the trend variations in the data from each channel:\n",
        "Let's first analyze the trends in each channel's data:\n",
        "First, let's examine how the trends vary across each channel's data:\n",
        "Let's begin with an analysis of the trend changes in each channel's data:\n",
        "Starting off, let's look at the trend changes in each channel's data:\n",
        "To kick things off, let's analyze the trend variations in each channel's data:\n",
        "First, let's delve into the changes in trends for each channel's data:\n",
        "Let's initiate our analysis by looking at the trend changes in each channel's data:\n",
        "First up, let's examine the trend changes across each channel's data:\n",
        "Let's get started by analyzing the trend shifts in each channel's data:\n",
        "At the outset, let's explore the trend changes in the data for each channel:\n",
        "First, let's focus on the trend variations in each channel's data:\n",
        "To start with, let's examine the trend changes in each channel's data:\n",
        "Initially, let's look into the trend changes within each channel's data:\n",
        "Let's start our analysis by checking the trend changes in each channel's data:\n",
        "To begin, let's analyze the trend modifications in the data of each channel:\n",
        "Firstly, let's explore the trend differences across each channel's data:\n",
        "Let's begin our examination by looking at the trend changes in each channel's data:\n",
        "Let's start by analyzing how the trends in each channel's data change:\n",
        "First, let's observe the trend variations in the data for each channel:\n",
        "Let's initially delve into the trend changes in each channel's data:\n",
        "To begin our analysis, let's look at the trend shifts in each channel's data:\n",
        "Let's start off by examining the trend changes in the data for each channel:\n"
    ],
    "gen_summary_3_2": [
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
        "{trend_num} trend is present in the data."
    ],
    "gen_summary_3": [
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
        "The data mirrors {trend_num} different development tendencies, while also illustrating that the trend has changed {change_num} times in total.",
        "From a holistic perspective, the data presents {trend_num} unique trend forms, which have undergone {change_num} changes throughout the process.",
        "The data indicates {trend_num} primary shifting trends, with these trends transforming a total of {change_num} times.",
        "Parsing through the data, we discover {trend_num} distinct trend features, with the trend varying {change_num} times over the entire period.",
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
        "Across {trend_num} trends, the data shows {change_num} occurrences of trend shifts."
    ],
    "gen_summary_4": [
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
        "Summarily, a {trend_type} direction was evident across {total_time} seconds of data"
    ],
    "gen_summary_5": [
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
        "a sequence of {trend_type} occurring over {total_time} seconds"
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
        "Trend overview: {overall_trend}."
    ],
    "conclude": [
        "Therefore, the human activity represented by the given data should be {activity}.",
        "Hence, the human activity indicated by the provided data should be {activity}.",
        "Thus, the human activity shown by the given data is likely to be {activity}.",
        "As a result, the human activity reflected in the provided data should be {activity}.",
        "Consequently, the human activity depicted by the given data should be {activity}.",
        "In conclusion, the human activity represented by the provided data should be {activity}.",
        "Therefore, the human activity inferred from the given data should be {activity}.",
        "Thus, the human activity suggested by the given data should be {activity}.",
        "As a result, the human activity described by the provided data should be {activity}.",
        "Hence, the human activity reflected by the given data should be {activity}.",
        "Therefore, it can be concluded that the human activity represented by the given data should be {activity}.",
        "Thus, the human activity implied by the provided data should be {activity}.",
        "Consequently, the human activity indicated by the given data should be {activity}.",
        "In summary, the human activity represented by the provided data should be {activity}.",
        "Therefore, the human activity portrayed by the given data should be {activity}.",
        "As a result, the human activity identified from the given data should be {activity}.",
        "Thus, the human activity manifested by the provided data should be {activity}.",
        "Hence, the human activity captured by the given data should be {activity}.",
        "Consequently, the human activity revealed by the given data should be {activity}.",
        "Therefore, the human activity suggested by the provided data should be {activity}.",
        "In conclusion, the human activity inferred from the given data should be {activity}.",
        "Thus, the human activity shown by the provided data should be {activity}.",
        "As a result, the human activity evidenced by the given data should be {activity}.",
        "Therefore, the human activity illustrated by the provided data should be {activity}.",
        "Hence, the human activity indicated by the given data should be {activity}."
    ]


}

Q_TEMPLATES = [
    "Which human activity does this {data_name} segment, consisting of {channel_num} channels, represent?",
    "What human activity is captured in this {data_name} segment with {channel_num} channels?",
    "Which human action is depicted in this {channel_num}-channel {data_name} segment?",
    "Can you identify the human activity represented in this {channel_num}-channel {data_name} segment?",
    "What human behavior is showcased in this {data_name} that includes {channel_num} channels?",
    "Reading this {channel_num}-channel {data_name} segment, what human activity is being performed?",
    "Analyze this {data_name} containing {channel_num} channels. What human action does it portray?",
    "Examine this {data_name} segment with {channel_num} channels. Which human activity does it illustrate?",
    "Looking at this {channel_num}-channel {data_name}, can you determine the human activity it represents?",
    "What human task is being carried out in this {data_name} that features {channel_num} channels?",
    "Considering this {data_name} with {channel_num} channels, what human behavior is being demonstrated?",
    "Analyzing this {data_name} that contains {channel_num} channels, what human action can you discern?",
    "Based on the {channel_num} channels {data_name}, which human activity is being exhibited?",
    "Can you identify the human behavior portrayed in this {channel_num}-channel {data_name} segment?",
    "Considering the {channel_num} channels {data_name} segment, what human task is being performed?",
    "Examine this {data_name} consisting of {channel_num} channels. What human activity does it showcase?",
    "Given this {data_name} segment with {channel_num} channels, can you determine the human action it represents?",
    "Read this {channel_num}-channel {data_name}. Which human behavior is being demonstrated?",
    "Look at this {data_name} featuring {channel_num} channels. What human activity is being carried out?",
    "Study this {channel_num}-channel {data_name} segment. Can you identify the human task it portrays?",
    "What human action is being showcased in this {data_name} segment that includes {channel_num} channels?",
    "Which human behavior can you discern from this {channel_num}-channel {data_name}?",
    "Analyzing the {channel_num} channels {data_name}, what human activity is being exhibited?",
    "Based on this {data_name} consisting of {channel_num} channels, can you identify the human task being performed?",
    "Considering this {data_name} segment with {channel_num} channels, which human action is being represented?",
    "Examine the {channel_num} channels {data_name}. What human behavior does it showcase?",
    "What human activity does this {data_name} segment, with {channel_num} channels, depict?",
    "Can you identify the human activity represented by this {data_name}, which has {channel_num} channels?",
    "Please determine the human activity depicted in this {data_name} segment, comprising {channel_num} channels.",
    "Identify the human activity captured in this {data_name}, made up of {channel_num} channels.",
    "What is the human activity shown in this {data_name} segment, containing {channel_num} channels?",
    "What human activity is being depicted in this {data_name}, featuring {channel_num} channels?",
    "Can you determine the human activity portrayed in this {data_name} segment, with {channel_num} channels?",
    "Please identify the human activity captured in this {data_name}, including {channel_num} channels.",
    "Describe the human activity shown in this {data_name} segment, composed of {channel_num} channels.",
    "What is the human activity being shown in this {data_name}, involving {channel_num} channels?",
    "Which human activity does this {data_name} segment, recorded across {channel_num} channels, represent?",
    "Can you discern the human activity depicted in this {data_name}, with {channel_num} channels involved?",
    "What activity is being portrayed in this {data_name} segment, spanning {channel_num} channels?",
    "Please determine the human activity captured in this {data_name}, with {channel_num} channels utilized.",
    "Identify the human activity depicted in this {data_name} segment, across {channel_num} channels.",
    "What is the human activity shown in this {data_name}, utilizing {channel_num} channels?",
    "From the {channel_num} channels {data_name}, what human activity can you infer?",
    "Given the {channel_num} channels segments of the {data_name}, which human behavior is being portrayed?",
    "Inspect this {data_name} segment that has {channel_num} channels. Can you identify the human action it represents?",
    "Observing this {channel_num}-channel {data_name}, what human action can you discern?",
    "Study the {channel_num} channels segments of the {data_name}. Which human activity is being demonstrated?",
    "Analyzing this {data_name} with {channel_num} channels, what human behavior can you infer?",
    "Based on the {channel_num} channels {data_name}, can you identify the human action being performed?",
    "Considering the {channel_num} channels {data_name} segment, what human behavior is being showcased?",
    "Based on the {channel_num} channels {data_name}, what human activity can you deduce?",
    "Considering the {channel_num} channels {data_name} segment, what human activity can be inferred?",
    "Given the {channel_num} channels {data_name}, what human activity can you speculate?",
    "With the {channel_num} channels {data_name} segment, what human activity can you conclude?",
    "In light of the {channel_num} channels {data_name}, what human activity can you determine?"
]

def num_to_words(num):
    units = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
    teens = ['ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen',
             'nineteen']
    tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
    scales = ['', 'thousand', 'million', 'billion']

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
            return num_to_words(num // (1000 ** i)) + " " + scale + (
                " " + num_to_words(num % (1000 ** i)) if num % (1000 ** i) != 0 else "")


def convert_number(num):
    if '.' in str(num):
        whole, decimal = str(num).split('.')
        if decimal == '0':
            return num_to_words(int(num))
        else:
            return num_to_words(int(whole)) + " point " + " ".join([num_to_words(int(digit)) for digit in decimal])
    else:
        return num_to_words(int(num))


def capitalize_first_letter(string):
    if len(string) == 0:
        return string
    else:
        return string[0].upper() + string[1:]


def check_a_an(sentence):
    words = re.findall(r'\b\w+\b', sentence)
    vowels = 'aeiouAEIOU'
    corrected_sentence = sentence

    for i in range(len(words)):
        if words[i] in ['a', 'an', 'A', 'An']:
            if i + 1 < len(words):
                next_word = words[i + 1]
                if words[i] == 'a' and next_word[0] in vowels:
                    corrected_sentence = corrected_sentence.replace(f' a {next_word}', f' an {next_word}', 1)
                elif words[i] == 'A' and next_word[0] in vowels:
                    corrected_sentence = corrected_sentence.replace(f' A {next_word}', f' An {next_word}', 1)
                elif words[i] == 'an' and next_word[0] not in vowels:
                    corrected_sentence = corrected_sentence.replace(f' an {next_word}', f' a {next_word}', 1)
                elif words[i] == 'An' and next_word[0] not in vowels:
                    corrected_sentence = corrected_sentence.replace(f' An {next_word}', f' A {next_word}', 1)

    return corrected_sentence


def analyze_trend(time_series, sample_rate, start_point=0):
    """
    Analyze the trend of a {data}.

    Parameters:
    - time_series (list): A list of time series data points.
    - duration (int): The duration over which the data was collected.
    - threshold (float): The minimum difference between values to consider a change in trend.

    Returns:
    - DataFrame: A DataFrame with columns: from_time, to_time, from_value, to_value, trend.
    """
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
            trend_type = 'steady'
        elif start_val < end_val:
            trend_type = 'increase'
        else:
            trend_type = 'decrease'

        # Append the results to the lists
        from_time.append(start_time)
        to_time.append(end_time)
        from_value.append(start_val)
        to_value.append(end_val)
        trend.append(trend_type)

    # Create a DataFrame from the results
    result_df = pd.DataFrame({
        'from_time': from_time,
        'to_time': to_time,
        'from_value': from_value,
        'to_value': to_value,
        'trend': trend
    })

    return result_df


def merge_adjacent_rows(df):
    """
    Merge adjacent rows with the same trend into a new dataframe.

    Parameters:
    - df (DataFrame): A DataFrame with columns: from_time, to_time, from_value, to_value, trend.

    Returns:
    - DataFrame: A merged DataFrame with columns: from_time, to_time, from_value, to_value, trend, values.
    """
    # List to store the merged rows
    merged_rows = []

    # Variables to store the start of the current segment
    current_start_time = df.iloc[0]['from_time']
    current_start_value = df.iloc[0]['from_value']
    current_trend = df.iloc[0]['trend']
    current_values = [current_start_value]

    for index, row in df.iterrows():
        if row['trend'] == current_trend:
            # Continue accumulating values
            current_values.append(row['to_value'])
        else:
            # Close the current segment and start a new one
            merged_rows.append({
                'start_time': current_start_time,
                'end_time': df.iloc[index - 1]['to_time'],
                'start_value': current_start_value,
                'end_value': df.iloc[index - 1]['to_value'],
                'trend': current_trend,
                'values': current_values.copy()
            })
            current_start_time = row['from_time']
            current_start_value = row['from_value']
            current_trend = row['trend']
            current_values = [current_start_value, row['to_value']]

    # Append the last segment
    merged_rows.append({
        'start_time': current_start_time,
        'end_time': df.iloc[-1]['to_time'],
        'start_value': current_start_value,
        'end_value': df.iloc[-1]['to_value'],
        'trend': current_trend,
        'values': current_values
    })

    # Create a DataFrame from the merged rows
    merged_df = pd.DataFrame(merged_rows)

    return merged_df


def calculate_total_time(df):
    """
    Calculate the total duration for each trend in the dataframe.

    Parameters:
    - df (DataFrame): A DataFrame with columns: from_time, to_time, trend.

    Returns:
    - DataFrame: A DataFrame with columns: trend, total_time.
    """
    # Group by the trend and sum the duration for each trend
    total_time_by_trend = df.groupby('trend').apply(
        lambda x: round((x['end_time'] - x['start_time']).sum(), 2)).reset_index(
        name='total_time')

    return total_time_by_trend

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


def choose_decimal_places(std_dev):
    if std_dev < 0.01:
        return 6
    elif std_dev < 0.1:
        return 4
    elif std_dev < 1:
        return 3
    else:
        return 2


def generate_correlation_text(correlation_df):
    text = "Pearson Correlation Matrix for each channel:\n"
    for row in correlation_df.index:
        for col in correlation_df.columns:
            if row < col:  # 只考虑上三角矩阵的元素
                correlation_value = correlation_df.loc[row, col]
                if correlation_value >= 0.7:
                    correlation_description = "strongly positively correlated"
                elif correlation_value >= 0.3:
                    correlation_description = "moderately positively correlated"
                elif correlation_value >= 0.1:
                    correlation_description = "weakly positively correlated"
                elif correlation_value <= -0.7:
                    correlation_description = "strongly negatively correlated"
                elif correlation_value <= -0.3:
                    correlation_description = "moderately negatively correlated"
                elif correlation_value <= -0.1:
                    correlation_description = "weakly negatively correlated"
                else:
                    correlation_description = "not significantly correlated"

                text += f"The correlation between {row} and {col} is {correlation_description}.\n"
    return text


def round_to_8_decimals(number):
    return f'{number:.8f}'.rstrip('0').rstrip('.')


def gen_reason(d, pair_list, data_type):
    assert len(d[0])==15
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
    reading_list = [c_acc_x, c_acc_y, c_acc_z, la_acc_x, la_acc_y, la_acc_z, la_gs_x, la_gs_y, la_gs_z, rla_acc_x, rla_acc_y, rla_acc_z, rla_gs_x, rla_gs_y, rla_gs_z]
    reading_name = ["chest x-axis accelerometer", "chest y-axis accelerometer", "chest z-axis accelerometer",
                    "left-ankle x-axis accelerometer", "left-ankle y-axis accelerometer", "left-ankle z-axis accelerometer",
                    "left-ankle x-axis gyroscope", "left-ankle y-axis gyroscope", "left-ankle z-axis gyroscope",
                    "right-lower-arm x-axis accelerometer", "right-lower-arm y-axis accelerometer", "right-lower-arm z-axis accelerometer",
                    "right-lower-arm x-axis gyroscope", "right-lower-arm y-axis gyroscope", "right-lower-arm z-axis gyroscope"]

    info = {
        reading_name[0]: {},
        reading_name[1]: {},
        reading_name[2]: {},
        reading_name[3]: {},
        reading_name[4]: {},
        reading_name[5]: {},
        reading_name[6]: {},
        reading_name[7]: {},
        reading_name[8]: {},
        reading_name[9]: {},
        reading_name[10]: {},
        reading_name[11]: {},
        reading_name[12]: {},
        reading_name[13]: {},
        reading_name[14]: {}
    }

    smry_text=[]
    trend_text = []
    corr_text = []
    smry_text.append("Statistics for each channel:\n")

    for r, n in zip(reading_list, reading_name):
        data_df = merge_adjacent_rows(analyze_trend(r, sr))
        total_time_df = calculate_total_time(data_df)
        trend_text.append(n + ": ")

        info[n]["trend_num"] = len(total_time_df)
        info[n]["total_change_num"] = len(data_df)

        prompts_templates3 = PROMPT_DICT["gen_summary_3"]
        prompts_templates3_2 = PROMPT_DICT["gen_summary_3_2"]
        prompts_templates4 = PROMPT_DICT["gen_summary_4"]
        prompts_templates5 = PROMPT_DICT["gen_summary_5"]
        selected_template3_2 = random.choice(prompts_templates3_2)
        selected_template3 = random.choice(prompts_templates3)
        selected_template4 = random.choice(prompts_templates4)
        selected_template5 = random.choice(prompts_templates5)

        if info[n]["trend_num"] == 1:
            trend_text.append(capitalize_first_letter(
                selected_template3_2.format(trend_num=random.choice([info[n]["trend_num"], convert_number(info[n]["trend_num"])]))))
        else:
            trend_text.append(capitalize_first_letter(
                selected_template3.format(trend_num=random.choice([info[n]["trend_num"], convert_number(info[n]["trend_num"])]),
                                          change_num=random.choice([info[n]["total_change_num"], convert_number(info[n]["total_change_num"])]))))

        if 'trend_total_time' not in info[n]:
            info[n]['trend_total_time'] = {}

        for index, t in total_time_df.iterrows():
            info[n]["trend_total_time"][t["trend"]] = t['total_time']

        i_t = 0
        for index, t in total_time_df.iterrows():
            if i_t == 0:
                if len(total_time_df) == 1:
                    trend_text.append(capitalize_first_letter(
                        selected_template4.format(trend_type=choose_word(t["trend"], pair_list),
                                                  total_time=f"{t['total_time']:.2f}")) + ".")
                else:
                    trend_text.append(capitalize_first_letter(
                        selected_template4.format(trend_type=choose_word(t["trend"], pair_list),
                                                  total_time=f"{t['total_time']:.2f}")) + ",")
            elif i_t < len(total_time_df) - 1:
                trend_text.append(
                    selected_template5.format(
                        trend_type=choose_word(t["trend"], pair_list),
                        total_time=f"{t['total_time']:.2f}") + ",")
            else:
                trend_text.append(
                    "and " + selected_template5.format(trend_type=choose_word(t["trend"], pair_list),
                                                       total_time=f"{t['total_time']:.2f}") + ".")
            i_t += 1

        differences = np.diff(r)
        sum_of_differences = np.sum(differences)
        if sum_of_differences > 0:
            info[n]["overall_trend"] = "upward"
        elif sum_of_differences < 0:
            info[n]["overall_trend"] = "downward"
        else:
            info[n]["overall_trend"] = "steady"

        if info[n]["total_change_num"] > 1:
            prompts_templates7 = PROMPT_DICT["gen_summary_6"]
            selected_template7 = random.choice(prompts_templates7)

            trend_text.append(capitalize_first_letter(
                selected_template7.format(overall_trend=info[n]["overall_trend"]))+'\n')

        info[n]["min"] = np.min(r)
        info[n]["max"] = np.max(r)
        info[n]["median"] = np.median(r)
        info[n]["mean"] = np.mean(r)
        info[n]["std_dev"] = np.std(r)

        decimal_places = choose_decimal_places(info[n]["std_dev"])
        smry_text.append(f"{n}: Mean={round_to_8_decimals(info[n]['mean'])}, StdDev={round_to_8_decimals(info[n]['std_dev'])}\n")

        trend_counts = data_df['trend'].value_counts()

        if 'trend_total_changes' not in info[n]:
            info[n]['trend_total_changes'] = {}

        for i_n in range(len(trend_counts)):
            info[n]["trend_total_changes"][trend_counts.index[i_n]] = trend_counts.values[i_n]

    correlation_matrix = np.corrcoef(np.array(reading_list).T, rowvar=False)
    correlation_df = pd.DataFrame(correlation_matrix, columns=reading_name, index=reading_name)

    corr_text.append(generate_correlation_text(correlation_df))

    return {
        'smry_text': ' '.join(smry_text),
        'trend_text': ' '.join(trend_text),
        'corr_text': ' '.join(corr_text)
    }


def QA_gen(label_dict, data, pair_list):
    channel_num = data.shape[1]
    prompts_templates = Q_TEMPLATES
    selected_template = random.choice(prompts_templates)

    data_types = ["time series data", "sensor data", "normalized time series data", "normalized sensor data"]
    selected_data_type = random.choice(data_types)

    c = random.choice([channel_num, convert_number(channel_num)])

    question = selected_template.format(data_name=selected_data_type, channel_num=c)
    reason = gen_reason(data, pair_list, selected_data_type)

    gt = ACTIVITIES[int(label_dict['activity'])]

    return {
        "Q": question,
        "smry": reason['smry_text'],
        "trend_text": reason['trend_text'],
        "corr_text": reason['corr_text'],
        "A": gt
    }

ACTIVITIES = {
    0: 'Standing still (1 min)',
    1: 'Sitting and relaxing (1 min)',
    2: 'Lying down (1 min)',
    3: 'Walking (1 min)',
    4: 'Climbing stairs (1 min)',
    5: 'Waist bends forward (20x)',
    6: 'Frontal elevation of arms (20x)',
    7: 'Knees bending (crouching) (20x)',
    8: 'Cycling (1 min)',
    9: 'Jogging (1 min)',
    10: 'Running (1 min)',
    11: 'Jump front & back (20x)'
}

sr = 50

output_path = './whole_data'
split = "train"

output_path = os.path.join(output_path, split)
if not os.path.exists(output_path):
    os.makedirs(output_path)
    print(f"Directory '{output_path}' has created.")
else:
    print(f"Directory '{output_path}' exists.")

qa_dict = {
        "author": "",
        "version": "",
        "date": str(datetime.now().date()),
        "dataset": []
    }

for idx, (l, d) in enumerate(zip(all_train_labels, all_train_segments)):
    assert d.shape[0] == 100
    assert d.shape[1] == 15
    trend_pair_list = select_random_pair()
    data_dict = {
        "index": idx,
        "qa_pair": QA_gen(l, d, trend_pair_list)
    }
    qa_dict["dataset"].append(data_dict)
    if idx < 10:
        print(data_dict["qa_pair"])
    idx += 1
    print(f"{idx} finished")
with open(os.path.join(output_path, f"mhealth_{split}_qa_stage2_cls.json"), 'w') as f:
    json.dump(qa_dict, f, indent=2)
print(len(qa_dict["dataset"]), len(all_train_labels))



output_path = './whole_data'
split = "test"

output_path = os.path.join(output_path, split)
if not os.path.exists(output_path):
    os.makedirs(output_path)
    print(f"Directory '{output_path}' has created.")
else:
    print(f"Directory '{output_path}' exists.")

qa_dict = {
        "author": "",
        "version": "",
        "date": str(datetime.now().date()),
        "dataset": []
    }

for idx, (l, d) in enumerate(zip(all_test_labels, all_test_segments)):
    assert d.shape[0] == 100
    assert d.shape[1] == 15
    trend_pair_list = select_random_pair()
    data_dict = {
        "index": idx,
        "qa_pair": QA_gen(l, d, trend_pair_list)
    }
    qa_dict["dataset"].append(data_dict)
    if idx < 10:
        print(data_dict["qa_pair"])
    idx += 1
    print(f"{idx} finished")
with open(os.path.join(output_path, f"mhealth_{split}_qa_stage2_cls.json"), 'w') as f:
    json.dump(qa_dict, f, indent=2)
print(len(qa_dict["dataset"]), len(all_test_labels))
