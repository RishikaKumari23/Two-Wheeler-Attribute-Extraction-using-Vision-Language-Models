import csv
from collections import defaultdict

gt_path = '/Users/rishika/Downloads/Ground_Truth_Annotation_1080_Completed.csv'
pred_path = '/Users/rishika/Downloads/Image/Gemini_Predictions_990.csv'
out_report = '/Users/rishika/Downloads/Image/VLM_Benchmark_Evaluation_Report.md'

with open(gt_path) as f:
    gt_rows = {r['Image_File']: r for r in csv.DictReader(f)}

with open(pred_path) as f:
    pred_rows = {r['Image_File']: r for r in csv.DictReader(f)}

def calc_metrics(y_true, y_pred, labels):
    classes = sorted(list(labels))
    tp = defaultdict(int)
    fp = defaultdict(int)
    fn = defaultdict(int)
    total_correct = 0
    total = len(y_true)
    
    for t, p in zip(y_true, y_pred):
        if t == p:
            total_correct += 1
            tp[t] += 1
        else:
            fp[p] += 1
            fn[t] += 1
            
    acc = total_correct / total if total > 0 else 0
    class_metrics = {}
    f1_list = []
    
    for c in classes:
        p = tp[c] / (tp[c] + fp[c]) if (tp[c] + fp[c]) > 0 else 0
        r = tp[c] / (tp[c] + fn[c]) if (tp[c] + fn[c]) > 0 else 0
        f1 = (2 * p * r) / (p + r) if (p + r) > 0 else 0
        class_metrics[c] = {'precision': p, 'recall': r, 'f1': f1, 'count': tp[c] + fn[c]}
        f1_list.append(f1)
        
    macro_f1 = sum(f1_list) / len(f1_list) if f1_list else 0
    return acc, macro_f1, class_metrics

vt_true, vt_pred = [], []
riders_true, riders_pred = [], []
r_helm_true, r_helm_pred = [], []
p_helm_true, p_helm_pred = [], []
lug_true, lug_pred = [], []
gen_true, gen_pred = [], []

for img, gt in gt_rows.items():
    if img not in pred_rows:
        continue
    p = pred_rows[img]
    
    if gt.get('Vehicle_Type') and p.get('Gemini_Vehicle_Type'):
        vt_true.append(gt['Vehicle_Type'])
        vt_pred.append(p['Gemini_Vehicle_Type'])
        
    if gt.get('Number_of_Riders') and p.get('Gemini_Number_of_Riders'):
        riders_true.append(gt['Number_of_Riders'])
        riders_pred.append(p['Gemini_Number_of_Riders'])
        
    if gt.get('Rider_Helmet') and p.get('Gemini_Rider_Helmet'):
        r_helm_true.append(gt['Rider_Helmet'])
        r_helm_pred.append(p['Gemini_Rider_Helmet'])
        
    if gt.get('Pillion_Helmet') and p.get('Gemini_Pillion_Helmet'):
        p_helm_true.append(gt['Pillion_Helmet'])
        p_helm_pred.append(p['Gemini_Pillion_Helmet'])
        
    if gt.get('Luggage') and p.get('Gemini_Luggage'):
        lug_true.append(gt['Luggage'])
        lug_pred.append(p['Gemini_Luggage'])
        
    if gt.get('Rider_Gender') and p.get('Gemini_Rider_Gender'):
        gen_true.append(gt['Rider_Gender'])
        gen_pred.append(p['Gemini_Rider_Gender'])

attributes = [
    ('Vehicle Type (Motorcycle vs Scooter)', vt_true, vt_pred),
    ('Rider Helmet Compliance (Driver)', r_helm_true, r_helm_pred),
    ('Number of Riders (Solo, Double, Triple)', riders_true, riders_pred),
    ('Pillion Helmet Compliance', p_helm_true, p_helm_pred),
    ('Rider Gender', gen_true, gen_pred),
    ('Luggage / Cargo Detection', lug_true, lug_pred)
]

report_lines = [
    "# 🏍️ VLM Validation Benchmark Evaluation Report (N = 990)",
    "",
    "**Model:** Google Gemini (Zero-Shot with Structured JSON Context)",
    "**Ground Truth:** Human-labeled dataset (990 stratified highway frames)",
    "",
    "## 🏆 Executive Summary: Macro Performance",
    "",
    "| Attribute | Overall Accuracy | Macro F1-Score | Evaluated Sample Size (N) | Evaluation Status |",
    "| :--- | :---: | :---: | :---: | :---: |"
]

for name, yt, yp in attributes:
    labels = set(yt).union(set(yp))
    acc, f1, _ = calc_metrics(yt, yp, labels)
    status = "🌟 Exceptional (>95%)" if acc >= 0.95 else ("✅ High (>90%)" if acc >= 0.90 else "⚠️ Moderate (~80%)")
    report_lines.append(f"| **{name}** | **{acc*100:.2f}%** | **{f1*100:.2f}%** | {len(yt)} | {status} |")

report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("## 🔍 Detailed Class-Level Performance")
report_lines.append("")

for name, yt, yp in attributes:
    labels = set(yt).union(set(yp))
    acc, f1, cm = calc_metrics(yt, yp, labels)
    report_lines.append(f"### 📌 {name}")
    report_lines.append(f"- **Overall Accuracy:** {acc*100:.2f}%")
    report_lines.append(f"- **Macro F1-Score:** {f1*100:.2f}%")
    report_lines.append("")
    report_lines.append("| Class | Support (Ground Truth) | Precision | Recall | F1-Score |")
    report_lines.append("| :--- | :---: | :---: | :---: | :---: |")
    for c, m in cm.items():
        report_lines.append(f"| **{c}** | {m['count']} | {m['precision']*100:.1f}% | {m['recall']*100:.1f}% | {m['f1']*100:.1f}% |")
    report_lines.append("")

with open(out_report, 'w') as f:
    f.write('\n'.join(report_lines))

print(f"Report written to: {out_report}")
