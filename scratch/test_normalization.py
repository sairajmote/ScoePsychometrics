from backend.scoring_brain_dominance import score_brain_dominance

# Sample data mimicking the user's result (56% and 66% raw)
# 56% raw left = (sum - 20) / 80 * 100 => sum = 56 * 0.8 + 20 = 44.8 + 20 = 64.8
# 66% raw right = (sum - 20) / 80 * 100 => sum = 66 * 0.8 + 20 = 52.8 + 20 = 72.8

# Let's just create 20 items for each side and set options to match
scoring_data = []
# Left side: total sum needs to be around 65. With 20 questions, average ~3.25 (between C and D)
for i in range(20):
    scoring_data.append({"keyed": "L", "selected_option": "C" if i < 15 else "D"}) # 15*3 + 5*4 = 45 + 20 = 65

# Right side: total sum needs to be around 73. With 20 questions, average ~3.65
for i in range(20):
    scoring_data.append({"keyed": "R", "selected_option": "D" if i < 13 else "C"}) # 13*4 + 7*3 = 52 + 21 = 73

results = score_brain_dominance(scoring_data)

print(f"Normalized Left: {results['left']['score_pct']}%")
print(f"Normalized Right: {results['right']['score_pct']}%")
print(f"Total: {results['left']['score_pct'] + results['right']['score_pct']}%")
print(f"Dominance: {results['dominance']['label']}")
print(f"Left Intensity: {results['left']['descriptor']}")
print(f"Right Intensity: {results['right']['descriptor']}")
