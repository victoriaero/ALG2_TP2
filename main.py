import os
import math
import time
import csv
import networkx as nx
from heapq import heappush, heappop

###############################################################################
#                           Parsing da instância TSP                          #
###############################################################################
def parse_tsplib(file_path):
    """
    Faz o parsing de um arquivo .tsp no formato TSPLIB.
    Retorna:
        - instance_name (str): Nome da instância (NAME).
        - dimension (int): Dimensão do problema (número de nós).
        - coords (list of tuples): Lista com as coordenadas (x, y) de cada nó.
    """
    instance_name = None
    dimension = None
    coords = []

    with open(file_path, 'r') as f:
        lines = f.read().splitlines()

    # Lê informações do cabeçalho
    in_coord_section = False
    for line in lines:
        # Remover espaços extras
        line = line.strip()
        if line.startswith("NAME"):
            # Ex: "NAME : a280"
            instance_name = line.split(":")[1].strip()
        elif line.startswith("DIMENSION"):
            # Ex: "DIMENSION : 280"
            dimension = int(line.split(":")[1].strip())
        elif line.startswith("NODE_COORD_SECTION"):
            # Próximas linhas terão coordenadas
            in_coord_section = True
            continue
        elif line.startswith("EOF"):
            break

        # Se estamos lendo as coordenadas
        if in_coord_section:
            # Ex: "1 288 149"
            parts = line.split()
            if len(parts) == 3:
                # parts[0] é índice, parts[1] = x, parts[2] = y
                x = float(parts[1])
                y = float(parts[2])
                coords.append((x, y))

            # Se já lemos 'dimension' coordenadas, podemos parar
            if len(coords) == dimension:
                break

    return instance_name, dimension, coords

def build_distance_matrix(coords):
    """
    Constrói uma matriz de distâncias euclidianas a partir das coordenadas.
    coords[i] = (x_i, y_i)
    """
    n = len(coords)
    dist_matrix = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                (x1, y1) = coords[i]
                (x2, y2) = coords[j]
                dist_matrix[i][j] = math.dist((x1, y1), (x2, y2))
    return dist_matrix

###############################################################################
#                     Implementação dos três algoritmos TSP                   #
###############################################################################
def twice_around_tree(dist_matrix):
    """
    Aproximação do TSP usando o algoritmo twice-around-the-tree.
    Utiliza a biblioteca NetworkX para computar o MST e gerar o passeio Euleriano.
    """
    G = nx.complete_graph(len(dist_matrix))  # Grafo completo com n nós
    for i in range(len(dist_matrix)):
        for j in range(i + 1, len(dist_matrix)):
            G[i][j]['weight'] = dist_matrix[i][j]  # Adiciona os pesos das arestas

    # 1. Calcula a MST
    mst = nx.minimum_spanning_tree(G, weight='weight')

    # 2. Dobra as arestas para construir grafo Euleriano
    eulerian_multigraph = nx.MultiGraph(mst)
    for u, v, data in mst.edges(data=True):
        eulerian_multigraph.add_edge(u, v, weight=data['weight'])

    # 3. Computa o passeio Euleriano e remove os ciclos
    euler_tour = list(nx.eulerian_circuit(eulerian_multigraph))
    visited = []
    visited_set = set()
    for u, v in euler_tour:
        if u not in visited_set:
            visited.append(u)
            visited_set.add(u)
    visited.append(visited[0])  # Fecha o ciclo

    # 4. Calcula o custo do passeio
    cost = sum(dist_matrix[visited[i]][visited[i + 1]] for i in range(len(visited) - 1))
    return visited, cost

def christofides(dist_matrix):
    """
    Aproximação do TSP usando o algoritmo de Christofides.
    Utiliza a biblioteca NetworkX para computar MST, matching perfeito e passeio Euleriano.
    """
    G = nx.complete_graph(len(dist_matrix))
    for i in range(len(dist_matrix)):
        for j in range(i + 1, len(dist_matrix)):
            G[i][j]['weight'] = dist_matrix[i][j]

    # 1. Calcula a MST
    mst = nx.minimum_spanning_tree(G, weight='weight')

    # 2. Identifica vértices de grau ímpar
    odd_vertices = [v for v in mst.nodes if mst.degree(v) % 2 == 1]

    # 3. Cria subgrafo com os vértices de grau ímpar
    odd_subgraph = nx.Graph()
    for u in odd_vertices:
        for v in odd_vertices:
            if u < v:
                odd_subgraph.add_edge(u, v, weight=dist_matrix[u][v])

    # 4. Computa o matching perfeito mínimo
    matching = nx.algorithms.matching.min_weight_matching(odd_subgraph)


    # 5. Adiciona as arestas do matching ao MST para formar grafo Euleriano
    eulerian_multigraph = nx.MultiGraph(mst)
    for u, v in matching:
        eulerian_multigraph.add_edge(u, v, weight=dist_matrix[u][v])

    # 6. Computa o passeio Euleriano e remove os ciclos
    euler_tour = list(nx.eulerian_circuit(eulerian_multigraph))
    visited = []
    visited_set = set()
    for u, v in euler_tour:
        if u not in visited_set:
            visited.append(u)
            visited_set.add(u)
    visited.append(visited[0])  # Fecha o ciclo

    # 7. Calcula o custo do passeio
    cost = sum(dist_matrix[visited[i]][visited[i + 1]] for i in range(len(visited) - 1))
    return visited, cost

def branch_and_bound(dist_matrix, time_limit=1800):
    """
    Branch-and-Bound para TSP.
    Utiliza NetworkX para calcular o MST como limite inferior.
    """
    start_time = time.time()
    N = len(dist_matrix)

    def compute_bound(visited, current_node):
        """
        Calcula o bound (limite inferior) usando MST.
        Verifica o tempo limite a cada iteração.
        """
        if time.time() - start_time > time_limit:
            raise TimeoutError("Tempo limite excedido no cálculo do bound.")
        unvisited = [v for v in range(N) if v not in visited]
        subgraph = nx.Graph()
        for i in unvisited + [current_node]:
            for j in unvisited + [current_node]:
                if i < j:
                    subgraph.add_edge(i, j, weight=dist_matrix[i][j])
        mst_cost = nx.minimum_spanning_tree(subgraph, weight='weight').size(weight='weight')
        return mst_cost

    best_tour = None
    best_cost = float('inf')
    root = (0, 0, [0], set([0]))  # (bound, cost_so_far, path, visited)
    pq = []
    heappush(pq, root)

    try:
        while pq:
            if time.time() - start_time > time_limit:
                raise TimeoutError("Tempo limite excedido no Branch-and-Bound.")

            bound, cost_so_far, path, visited = heappop(pq)
            if bound >= best_cost:
                continue

            current_node = path[-1]
            if len(visited) == N:
                total_cost = cost_so_far + dist_matrix[current_node][0]
                if total_cost < best_cost:
                    best_cost = total_cost
                    best_tour = path + [0]
            else:
                for next_node in range(N):
                    if next_node not in visited:
                        new_cost = cost_so_far + dist_matrix[current_node][next_node]
                        new_visited = visited | {next_node}
                        new_path = path + [next_node]
                        new_bound = new_cost + compute_bound(new_visited, next_node)
                        if new_bound < best_cost:
                            heappush(pq, (new_bound, new_cost, new_path, new_visited))
    except TimeoutError:
        return None, "NA"

    return best_tour, best_cost


###############################################################################
#                           Execução em lote e CSV                            #
###############################################################################
def run_algorithms_on_folder(folder_path, output_csv="resultados.csv"):
    results = []

    for file_name in sorted(os.listdir(folder_path)):
        if file_name.lower().endswith(".tsp"):
            file_path = os.path.join(folder_path, file_name)

            instance_name, dimension, coords = parse_tsplib(file_path)
            if not instance_name:
                instance_name = file_name

            dist_matrix = build_distance_matrix(coords)
            print(f"\nIniciando processamento para a instância: {instance_name} ({file_name})")

            # Branch-and-Bound
            print("  Executando Branch-and-Bound...")
            start_bnb = time.time()
            tour_bnb, cost_bnb = branch_and_bound(dist_matrix, time_limit=1800)
            tempo_bnb = time.time() - start_bnb
            print(f"  Branch-and-Bound concluído em {tempo_bnb:.2f}s com custo {cost_bnb}")

            # Twice Around the Tree
            print("  Executando Twice Around the Tree...")
            start_2tree = time.time()
            _, cost_2tree = twice_around_tree(dist_matrix)
            tempo_2tree = time.time() - start_2tree
            print(f"  Twice Around the Tree concluído em {tempo_2tree:.2f}s com custo {cost_2tree}")

            # Christofides
            print("  Executando Christofides...")
            start_christo = time.time()
            _, cost_christo = christofides(dist_matrix)
            tempo_christo = time.time() - start_christo
            print(f"  Christofides concluído em {tempo_christo:.2f}s com custo {cost_christo}")

            if cost_bnb == "NA":
                tempo_bnb = "NA"

            results.append([
                instance_name,
                tempo_bnb, cost_bnb,
                tempo_2tree, cost_2tree,
                tempo_christo, cost_christo
            ])

    with open(output_csv, 'w', newline='', encoding='utf-8') as out:
        writer = csv.writer(out)
        writer.writerow([
            "id_instancia",
            "tempo_branch_and_bound", "custo_branch_and_bound",
            "tempo_2_tree", "custo_2_tree",
            "tempo_christofides", "custo_christofides"
        ])
        for row in results:
            writer.writerow(row)

    print(f"\nResultados salvos em: {output_csv}")

if __name__ == "__main__":
    pasta = "/scratch3/samiramalaquias/alg2/instancias_tsp"
    run_algorithms_on_folder(pasta, output_csv="resultados.csv")