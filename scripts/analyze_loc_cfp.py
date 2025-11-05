#!/usr/bin/env python3
import csv, os, re

# --- Function to detect movements in Rust source ---
def count_movements(rs_file):
    e = x = r = w = 0
    try:
        with open(rs_file, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()

            # --- Remove async functions for simplicity ---
            code = re.sub(r'\basync fn\b.*?{.*?}', '', code, flags=re.DOTALL)

            # --- Entry points ---
            e += len(re.findall(r'\bpub fn\b', code))
            e += len(re.findall(r'#\[(get|post|put|delete)\]', code))  # web routes
            e += len(re.findall(r'Router::route', code))
            
            # --- Exits ---
            x += len(re.findall(r'-> .*', code))
            x += len(re.findall(r'println!', code))
            x += len(re.findall(r'HttpResponse::Ok', code))

            # --- Read/Write DB movements ---
            r += len(re.findall(r'\.fetch', code))
            r += len(re.findall(r'\.query', code))
            w += len(re.findall(r'\.execute', code))
            w += len(re.findall(r'\.insert_into', code))
            w += len(re.findall(r'\.update', code))

            # --- Structs in impl blocks ---
            structs = re.findall(r'\bstruct\s+(\w+)', code)
            for s in structs:
                impls = re.findall(r'impl\s+' + re.escape(s) + r'\s*{([^}]*)}', code, flags=re.DOTALL)
                for m in impls:
                    e += len(re.findall(r'\bfn\b', m))

    except:
        pass
    return e, x, r, w

# --- File paths ---
input_csv = "rust_loc_results.csv"
output_csv = "rust_loc_results_with_summary.csv"

total_eloc = 0
total_cfp = 0

with open(input_csv) as infile, open(output_csv, 'w', newline='') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ["Entry","Exit","Read","Write","CFP","eLOC_per_CFP"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        repo = row["repo"]
        repo_dir = os.path.join("work", repo.replace("/", "_"))
        e_total = x_total = r_total = w_total = 0

        if os.path.exists(repo_dir):
            for root, _, files in os.walk(repo_dir):
                for file in files:
                    if file.endswith(".rs"):
                        e, x, r, w = count_movements(os.path.join(root, file))
                        e_total += e
                        x_total += x
                        r_total += r
                        w_total += w

        cfp = e_total + x_total + r_total + w_total
        eloc = int(row.get("rust_code",0) or 0)
        ratio = round(eloc/cfp,2) if cfp>0 else 0

        total_eloc += eloc
        total_cfp += cfp

        row.update({
            "Entry": e_total,
            "Exit": x_total,
            "Read": r_total,
            "Write": w_total,
            "CFP": cfp,
            "eLOC_per_CFP": ratio
        })
        writer.writerow(row)

    avg_ratio = round(total_eloc/total_cfp,2) if total_cfp>0 else 0
    writer.writerow({
        "repo":"TOTAL SUMMARY",
        "rust_code":total_eloc,
        "Entry":"",
        "Exit":"",
        "Read":"",
        "Write":"",
        "CFP":total_cfp,
        "eLOC_per_CFP":avg_ratio
    })
