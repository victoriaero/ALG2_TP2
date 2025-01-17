# TSP Algoritmos II

Este repositório contém um script em Python para executar três algoritmos de resolução, ótimos e aproximativos, do Problema do Caixeiro Viajante (TSP) em lote sobre instâncias do TSPLIB. Os algoritmos implementados são:

- Branch-and-Bound (exato, com limite de tempo)
- Twice Around the Tree (aproximação)
- Christofides (aproximação)

## Estrutura do Projeto

- `main.py`: Contém a implementação dos algoritmos, funções de parsing das instâncias TSP, execução em lote e escrita dos resultados em CSV.
- `resultados.csv`: Arquivo gerado após a execução do script, contendo tempos e custos obtidos para cada instância e algoritmo.
- Instâncias TSP no formato `.tsp` organizadas no diretório `instancias_tsp`

## Requisitos

- Python 3.11
- Bibliotecas Python:
  - `networkx`
  - `matplotlib`
  - `seaborn`
  - `pandas`
  - Outras bibliotecas padrão: `os`, `math`, `time`, `csv`, `heapq`

Para instalar as bibliotecas necessárias, execute:
```bash
pip install networkx matplotlib seaborn pandas
```

As bibliotecas matplotlib, pandas e seaborn foram utilizadas apenas para geração de visualizações.

## Descrição do Código

### Parsing da Instância TSP
- **`parse_tsplib(file_path)`**: Lê um arquivo `.tsp` no formato TSPLIB e extrai:
  - Nome da instância
  - Dimensão (número de nós)
  - Coordenadas (x, y) de cada nó

- **`build_distance_matrix(coords)`**: Constrói uma matriz de distâncias euclidianas a partir das coordenadas fornecidas.

### Implementação dos Algoritmos

- **`twice_around_tree(dist_matrix)`**: Executa a aproximação TSP "twice-around-the-tree" usando MST e passeio Euleriano.
  
- **`christofides(dist_matrix)`**: Executa a aproximação do TSP com o algoritmo de Christofides:
  1. Calcula o MST.
  2. Encontra vértices de grau ímpar.
  3. Calcula o matching perfeito mínimo nos vértices ímpares.
  4. Constrói um grafo Euleriano.
  5. Encontra um ciclo hamiltoniano aproximado.

- **`branch_and_bound(dist_matrix, time_limit)`**: Resolve o TSP exatamente utilizando branch-and-bound com um limite de tempo. Se o tempo limite for ultrapassado, retorna "NA" para custo.

### Execução em Lote

- **`run_algorithms_on_folder(folder_path, output_csv)`**:
  - Itera sobre todos os arquivos `.tsp` em uma pasta especificada.
  - Para cada instância:
    - Faz o parsing e constrói a matriz de distâncias.
    - Executa os três algoritmos (Branch-and-Bound, Twice Around the Tree, Christofides).
    - Coleta tempo de execução e custo obtido.
  - Salva os resultados em um arquivo CSV (`resultados.csv` por padrão) com as colunas:
    - `id_instancia`
    - `tempo_branch_and_bound`, `custo_branch_and_bound`
    - `tempo_2_tree`, `custo_2_tree`
    - `tempo_christofides`, `custo_christofides`

### Execução do Script

1. **Executar o script:**
   - No terminal, execute:
     ```bash
     python main.py
     ```
   - O script processará cada instância encontrada na pasta especificada, executará os algoritmos e salvará os resultados em `resultados.csv`.

2. **Verificar resultados:**
   - Após a execução, abra o arquivo `resultados.csv` para revisar os tempos e custos obtidos para cada instância e algoritmo.
  
3. **Soluções ótimas**
   - Se encontram no csv `otimos.csv`
   
## Notas e Considerações

- **Limite de Tempo:** 
  - O algoritmo Branch-and-Bound possui um limite de tempo configurável (`time_limit=1800` segundos). Se ultrapassar esse tempo, o algoritmo interrompe e retorna "NA" para custo, registrando o tempo transcorrido até então.

- **Dependências do NetworkX:**
  - Os algoritmos utilizam a biblioteca NetworkX para cálculos de MST, matching perfeito e circuitos Eulerianos. Certifique-se de que a versão instalada é compatível com as funções utilizadas.

- **Performance:**
  - O Branch-and-Bound pode ser computacionalmente intensivo para instâncias grandes do TSP. O limite de tempo ajuda a evitar execuções muito longas.

Este script é útil para comparar o desempenho de diferentes abordagens de solução do TSP em lote, oferecendo insights sobre tempos de execução e qualidade das soluções aproximadas versus exatas.
