import json
import re
from typing import List


with open("cards.json", "r") as f:
    raw_data = json.load(f)['dataset']

# step 1: drop entries with empty values
# for l,k in enumerate(raw_data):
#     for i,j in zip(k.keys(), k.values()):
#         if j==None:
#             print(raw_data.pop(l))

# step 2: convert data
def parse_fee(fee_str: str) -> int:
    fee_match = re.search(r"(\d[\d,]*)", fee_str)
    if fee_match:
        return int(fee_match.group(1).replace(",", ""))
    return 0

def parse_reward_rate(rate_str: str) -> List[float]:
    matches = re.findall(r"(\d+\.?\d*)%", rate_str)
    return [float(r) for r in matches] if matches else [0.0]

def parse_age(eligibility_str: str):
    if 'Age:' in eligibility_str:
        age_str = eligibility_str.split('Age:')[1].split(':')[0]
        age_match = re.findall(r"(\d[\d]*)", age_str)
        if not age_match:
            return [0]
        return [int(i) for i in age_match]
    return 0



# for i in range(20,12,-1):
#     print(raw_data[i]['joiningFee'], ':', parse_fee(raw_data[i]['joiningFee']))
#     print(raw_data[i]['eligibility'], ':', parse_age(raw_data[i]['eligibility']))
#     print(raw_data[i]['rewardRate'], ':', parse_reward_rate(raw_data[i]['rewardRate']))

transformed_data = []
for raw in raw_data:
    data = {
        "cardName": raw["cardName"],
        "minMonthlyIncome": raw["minMonthlyIncome"],
        "age": parse_age(raw["eligibility"]),
        "joiningFee": parse_fee(raw["joiningFee"]),
        "annualFee": parse_fee(raw["annualFee"]),
        "rewardType": raw["rewardType"],
        "rewardRate": parse_reward_rate(raw["rewardRate"]),
        "employmentType": raw["employmentType"],
        "eligibility": raw["eligibility"],
        "features": raw["pros"],
        "cardImage": raw["cardImage"]
    }
    transformed_data.append(data)

with open("transformed_cards.json", "w") as f:
    json.dump({"dataset": transformed_data}, f)

# types = set()
# for i in raw_data:
#     types.add(i['rewardType'])
# print(types)
