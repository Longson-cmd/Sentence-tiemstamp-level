import json
with open('compare_result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

list_consecutive_nulls = []
i = 0
while i < len(data):
    if data[i]["has_timestamp"] == False:
        k = i 
        while k + 1 < len(data):
            if data[k+1]["has_timestamp"] == False:
                k += 1
            else:
                break
        list_consecutive_nulls.append((i, k))
        i = k + 1
    else:
        i += 1


for (first_null, final_null) in list_consecutive_nulls:
    if first_null > 0 and final_null < len(data) -1:
        before_item = data[first_null -1]
        after_item = data[final_null +1]
        number_consecutive_nulls = final_null - first_null + 1
        start_null_gap = before_item["end"]
        end_null_gap = after_item["start"]
        average_null_length = (end_null_gap - start_null_gap) / number_consecutive_nulls
        for k in range(0, number_consecutive_nulls):
            data[k + first_null]["start"] = round(start_null_gap + average_null_length * k, 2)
            data[k + first_null]["end"] = round(start_null_gap + average_null_length * (k+ 1), 2)
            data[first_null + k]["has_timestamp"] = True
            # print(data[k + first_null])


# GET SENTENCES'S TIMESTAMPS
words_in_a_sentence = []
idx_s = 0
list_words = []  
for i in range(len(data)):
    if data[i]["idx_s"] == idx_s:
        list_words.append(data[i])
    else:
        words_in_a_sentence.append(list_words)
        idx_s += 1
        list_words = [data[i]]
# Append the final sentence you collected
if list_words:
    words_in_a_sentence.append(list_words)

sentence_timestamps = [] 
for i, items in enumerate(words_in_a_sentence) :
    text = ''
    start, end = None, None
        # Find the first element with has_timestamp == False or None
    item_before = next((item for item in items if  item["has_timestamp"]), None)
    item_before = next((item for item in items if  item["has_timestamp"]), None)
    if item_before :
        start = item_before["end"] 
    # Find the last element with has_timestamp == False or None
   
    item_after = next((item for item in reversed(items) if  item["has_timestamp"]), None)
    if item_after:
        end = item_after["start"]

    for item in items:
        # print("item ",  item)
        text += ' ' + item["word"]
    sentence_timestamps.append({"start": start, "end" : end, "text" : text})
    print(f"start: {start:<6}- end: {end:<6} | text :{text}")
        

