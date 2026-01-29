import json
import sys

import numpy as np
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


def calc_route(costs_csv_path="costs_matrix.csv"):
  # PARAMS
  num_vehicles = 3
  vehicle_capacity = 6
  baskets_per_family = 1
  # END PARAMS

  distance_matrix = np.loadtxt(costs_csv_path, delimiter=",", dtype=int)
  print("Matriz carregada!")

  num_families = len(distance_matrix)
  total_demand = num_families * baskets_per_family
  total_capacity = num_vehicles * vehicle_capacity

  diff_demand_capacity = total_demand - total_capacity

  virtual_vehicles = num_vehicles
  if diff_demand_capacity > 0:
    virtual_vehicles += int(np.ceil(diff_demand_capacity / vehicle_capacity))

  vehicle_capacities = [vehicle_capacity] * virtual_vehicles
  depot = 0

  source = {}
  source["distance_matrix"] = distance_matrix
  source["demands"] = [0] + [baskets_per_family] * (num_families - 1)
  source["num_vehicles"] = virtual_vehicles
  source["vehicle_capacities"] = vehicle_capacities

  # Cria o gerenciador de índices
  manager = pywrapcp.RoutingIndexManager(num_families, virtual_vehicles, depot)

  # Cria o modelo de roteamento
  routing = pywrapcp.RoutingModel(manager)

  # Callback de custo (usa a matriz de distâncias)
  def distance_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return source["distance_matrix"][from_node][to_node]

  transit_callback_index = routing.RegisterTransitCallback(distance_callback)
  routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

  # Restrição de capacidade
  def demand_callback(from_index):
    from_node = manager.IndexToNode(from_index)
    return source["demands"][from_node]

  demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
  routing.AddDimensionWithVehicleCapacity(
      demand_callback_index,
      0,  # nenhum “slack”
      source["vehicle_capacities"],
      True,  # start cumulativo em zero
      "Capacity",
  )

  # Configura a busca
  search_parameters = pywrapcp.DefaultRoutingSearchParameters()

  # Testar PARALLEL_SAVINGS, SAVINGS, BEST_INSERTION, GLOBAL_CHEAPEST_ARC
  search_parameters.first_solution_strategy = (
      routing_enums_pb2.FirstSolutionStrategy.PARALLEL_SAVINGS
  )

  # Testar GUIDED_LOCAL_SEARCH e TABU_SEARCH (talvez o SIMULATED_ANNEALING)
  search_parameters.local_search_metaheuristic = (
      routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
  )

  search_parameters.time_limit.FromSeconds(10)  # por exemplo
  # opcional, para ver se está tentando:
  # search_parameters.log_search = True

  solution = routing.SolveWithParameters(search_parameters)

  # 1) Pré-processamento: cria esqueleto
  routes = {
      f"vehicle_{vehicle_id}": {"routes": []}
      for vehicle_id in range(num_vehicles)
  }

  for vehicle_id in range(len(source["vehicle_capacities"])):
    index = routing.Start(vehicle_id)
    route = []
    route_load = 0

    while not routing.IsEnd(index):
      node_index = manager.IndexToNode(index)
      route.append(node_index)
      route_load += source["demands"][node_index]
      index = solution.Value(routing.NextVar(index))

    # Fecha na Estação
    route.append(manager.IndexToNode(index))

    visit = {
        "points": route,  # ex.: [0, 2, 1, 3, 0]
        "total_load": route_load  # cestas
    }

    index_vehicle = f"vehicle_{int(vehicle_id) % num_vehicles}"

    routes[index_vehicle]["routes"].append(visit)

    print(f"Rota do vehicle {vehicle_id} finalizada!")

  with open("routes.json", "w", encoding="utf-8") as f:
    json.dump(routes, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
  # Check if enough arguments are provided (script name + 2 arguments = 3 items)
  num_args = len(sys.argv)
  if num_args > 2:
    print("Usage: python script.py <path_csv_location>")
    sys.exit(1)
  elif num_args == 2:
    calc_route(sys.argv[1])
  else:
    calc_route()
