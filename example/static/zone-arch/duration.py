from xyz import *
import os
import tqdm
import pandas as pd

tmpDir = 'tmp'
datas = []

def plot(df):
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Plot two figures, side by side, x is the baseline and y is ours
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    sns.scatterplot(data=df, x='count_baseline', y='count_ours', ax=axs[0])
    sns.scatterplot(data=df, x='depth_baseline', y='depth_ours', ax=axs[1])
    
    # plot redlines for x=y
    count_max = max(df['count_baseline'].max(), df['count_ours'].max())
    count_min = min(df['count_baseline'].min(), df['count_ours'].min())
    depth_max = max(df['depth_baseline'].max(), df['depth_ours'].max())
    depth_min = min(df['depth_baseline'].min(), df['depth_ours'].min())
    axs[0].plot([count_min, count_max], [count_min, count_max], 'r--')
    axs[1].plot([depth_min, depth_max], [depth_min, depth_max], 'r--')
    
    axs[0].set_title('CNOT Count')
    axs[1].set_title('Depth')
    plt.tight_layout()
    plt.savefig('result.png')
    
    # print average impr of count and depth
    df["count_impr"] = (df["count_baseline"] - df["count_ours"]) / df["count_baseline"]
    df["depth_impr"] = (df["depth_baseline"] - df["depth_ours"]) / df["depth_baseline"]
    
    print(f"Average improvement of CNOT count: {df['count_impr'].mean()}")
    print(f"Average improvement of depth: {df['depth_impr'].mean()}")
    
def state_generator():
    for i in range(10):
        for n in range(4, 8):
            m_list = [4, n, n**2]
            for m in m_list:
                m = min(m, 2**n)
                yield i, n, m
    
def prepareData():
    if not os.path.exists(tmpDir):
        os.makedirs(tmpDir)
        
    for i, n, m in tqdm.tqdm(state_generator(), total=10*4*3):
        state_vector = rand_state(n, m)
        state = quantize_state(state_vector)
        qc = sparse_state_synthesis(state, map_gates=False, depth_opt=False, verbose_level=0)
        qc_baseline = mapping_debug(qc)
        write_qasm(qc_baseline, f"{tmpDir}/circuit_{n}_{m}_baseline_{i}.qasm")

        # qc_ours = sparse_state_synthesis(state, map_gates=False, depth_opt=True, verbose_level=0)
        # qc_ours = mapping_debug(qc_ours, control_reorder=True)
        qc_ours = sparse_state_synthesis_ours(state, map_gates=True, depth_opt=True, verbose_level=0)
        # qc_ours = resynthesis(qc_ours)
        qc_ours = schedule_commutable_gates(qc_ours)
        if qc_ours.get_level() > qc_baseline.get_level():
            qc_ours = qc_baseline
        write_qasm(qc_ours, f"{tmpDir}/circuit_{n}_{m}_ours_{i}.qasm")
        
        datas.append({
            'n': n,
            'm': m,
            'count_baseline': qc_baseline.get_cnot_cost(),
            'count_ours': qc_ours.get_cnot_cost(),
            'depth_baseline': qc_baseline.get_level(),
            'depth_ours': qc_ours.get_level()
        })
        
        # verify the state vectors
        state_vector0 = simulate_circuit(qc_baseline)
        state_vector1 = simulate_circuit(qc_ours)
        if not np.allclose(state_vector0, state_vector1):
            print("state vectors are not equal")
            print(f"state_vector0 = {quantize_state(state_vector0)}")
            print(f"state_vector1 = {quantize_state(state_vector1)}")

    df = pd.DataFrame(datas)
    df.to_csv('result.csv', index=False)

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the DAC experiment')
    parser.add_argument('--force', action='store_true', help='Force to re-run the experiment')
    args = parser.parse_args()
    
    if not os.path.exists(tmpDir):
        os.makedirs(tmpDir)
    if not os.path.exists('result.csv') or args.force:
        prepareData()
    plot(pd.read_csv('result.csv'))