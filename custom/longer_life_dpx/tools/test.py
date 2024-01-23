import os, sys
import pandas as pd
def read_csv_txt(csv_path):
    tfs = pd.read_csv(csv_path, encoding="utf8")
    return tfs

def save_map_to_csv(output_csv, key_to_vals_map, labels):
    # city = pd.DataFrame([['Sacramento', 'California'], ['Miami', 'Florida']], columns=['id', 'name'])
    pd_key_to_vals = pd.DataFrame({labels[0]: key_to_vals_map.keys(), labels[1]: key_to_vals_map.values()})
    pd_key_to_vals.to_csv(output_csv, index=False, header=True)

if __name__=="__main__":
    dir = os.path.dirname(__file__)
    src_dir = os.getcwd()
    print(sys.argv[0])
    print(__file__)
    print(dir)
    print(src_dir)
    dir = src_dir
    print("!!!")

    log_name_to_fail_reason_out = "output/log_name_to_fail_reason_out.csv"
    dataset_to_run = []
    if os.path.exists(log_name_to_fail_reason_out):
        dataset_to_run = read_csv_txt(log_name_to_fail_reason_out)["log_name"].to_list()
    print(len(dataset_to_run))
