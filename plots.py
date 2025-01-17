import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

OUTPUT_PATH = "output/"
os.makedirs(OUTPUT_PATH, exist_ok=True)

sns.set(style="whitegrid")

df = pd.read_csv('resultados.csv')
otimos_df = pd.read_csv('otimos.csv')

numeric_cols = ['tempo_branch_and_bound', 'custo_branch_and_bound', 
                'tempo_2_tree', 'custo_2_tree', 
                'tempo_christofides', 'custo_christofides']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['Qtd_Cidades'] = df['id_instancia'].str.extract(r'(\d+)').astype(int)
df = pd.merge(df, otimos_df, on='id_instancia', how='left')

df['Erro_2_Tree (%)'] = 100 * (df['custo_2_tree'] - df['custo_otimo']) / df['custo_otimo']
df['Erro_Christofides (%)'] = 100 * (df['custo_christofides'] - df['custo_otimo']) / df['custo_otimo']

plt.figure(figsize=(12, 6))
mask = (df['tempo_2_tree'] <= 1600) & (df['tempo_christofides'] <= 1600)
df_filtrado = df[mask]
plt.plot(df_filtrado['Qtd_Cidades'], df_filtrado['tempo_2_tree'], marker='s', linestyle='', label='Twice Around Tree')
plt.plot(df_filtrado['Qtd_Cidades'], df_filtrado['tempo_christofides'], marker='^', linestyle='', label='Christofides')
plt.xlabel('Quantidade de Cidades')
plt.ylabel('Tempo de Execução')
plt.title('Relação entre Qtd_Cidades e Tempo de Execução para cada Algoritmo')
plt.legend()
plt.grid(True)
plt.savefig(f'{OUTPUT_PATH}cidades_exec.png')
plt.clf()

plt.figure(figsize=(12, 6))
mask = (df['tempo_2_tree'] <= 1600) & (df['tempo_christofides'] <= 1600)
df_filtrado = df[mask]
plt.plot(df_filtrado['Qtd_Cidades'], df_filtrado['Erro_2_Tree (%)'], marker='s', linestyle='', label='Erro 2 Tree')
plt.plot(df_filtrado['Qtd_Cidades'], df_filtrado['Erro_Christofides (%)'], marker='^', linestyle='', label='Erro Christofides')
plt.xlabel('Quantidade de Cidades')
plt.ylabel('Erro Relativo (%)')
plt.title('Erro Percentual em relação ao Custo Ótimo')
plt.legend()
plt.grid(True)
plt.savefig(f'{OUTPUT_PATH}erro.png')
plt.clf()

tempos_df = pd.melt(df, id_vars=['id_instancia', 'Qtd_Cidades'], 
                    value_vars=['tempo_branch_and_bound', 'tempo_2_tree', 'tempo_christofides'],
                    var_name='Algoritmo', value_name='Tempo (s)')

algoritmo_map = {
    'tempo_2_tree': 'Twice Around Tree',
    'tempo_christofides': 'Christofides'
}
tempos_df['Algoritmo'] = tempos_df['Algoritmo'].map(algoritmo_map)

tempos_df_filtrado = tempos_df[tempos_df['Tempo (s)'] <= 1600]

plt.figure(figsize=(10, 6))
sns.boxplot(x='Algoritmo', y='Tempo (s)', data=tempos_df_filtrado)
plt.title('Distribuição dos Tempos de Execução por Algoritmo (≤ 1600s)')
plt.savefig(f'{OUTPUT_PATH}dist_exec.png')
plt.clf()

scatter_df = df[(df['tempo_2_tree'] <= 1600) & (df['tempo_christofides'] <= 1600)]

plt.figure(figsize=(12, 6))
plt.scatter(scatter_df['tempo_2_tree'], scatter_df['Erro_2_Tree (%)'], 
            alpha=0.7, label='Twice Around Tree')
plt.scatter(scatter_df['tempo_christofides'], scatter_df['Erro_Christofides (%)'], 
            alpha=0.7, label='Christofides', marker='^')
plt.xlabel('Tempo de Execução (s)')
plt.ylabel('Erro Relativo (%)')
plt.title('Relação entre Tempo de Execução e Erro Relativo')
plt.legend()
plt.grid(True)
plt.savefig(f'{OUTPUT_PATH}scatter_tempo_erro.png')
plt.clf()