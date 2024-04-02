import pandas as pd

df = pd.read_csv('resynthesis.csv')

# calculate the incr% of runtime
df['time_incr'] = (df['time_new']) / df['time_old'] * 100

# pivot using the n_qubits and m_state
pivot = df.pivot_table(index=['n_qubits', 'm_state'], values=['n_cnot_old', 'n_cnot_new', 'time_incr'], aggfunc='mean')

print(pivot)

pivot.to_csv('pivot.csv')