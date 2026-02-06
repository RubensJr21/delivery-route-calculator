import sys
from typing import List, Tuple
import numpy as np
import pandas as pd
import requests

from _config import DEPOT_COORDS

def read_coordinates_from_csv(
  csv_path: str,
  lat_col: str = "latitude",
  lon_col: str = "longitude",
  sep: str = ",",
  depot: Tuple[float, float] = (DEPOT_COORDS["lat"], DEPOT_COORDS["lon"]),
) -> List[Tuple[float, float]]:
  """
  Lê coordenadas de um CSV e retorna lista de (lon, lat) no formato OSRM.
  """
  df = pd.read_csv(csv_path, sep=sep, decimal=",")  # decimal=',' para vírgula BR
  coords = [depot]
  for _, row in df.iterrows():
    lon = float(row[lon_col])
    lat = float(row[lat_col])
    coords.append((lon, lat))
  return coords

def build_osrm_table_url(coords: List[Tuple[float, float]], sep: str = ",") -> str:
  """
  Constrói a URL do OSRM Table API a partir das coordenadas.
  Formato: /table/v1/driving/lon1,lat1;lon2,lat2;...
  """
  coord_str = ";".join([f"{lon},{lat}" for lon, lat in coords])
  return f"https://router.project-osrm.org/table/v1/driving/{coord_str}?annotations=distance,duration"

def main(input_path, output_path):
  coordinates = read_coordinates_from_csv(input_path)

  url = build_osrm_table_url(coordinates)
  print(f"URL gerada: {url}")

  response = requests.get(url)
  if response.status_code == 200:
    data = response.json()

    """
    distances é a distância em metros de um ponto até outro
    durations é o tempo em segundos de um ponto até outro
    """

    SCALE = 10  # ou 100, se quiser ainda mais precisão

    raw = np.array(data["distances"], dtype=float)  # matriz NxN de float
    distance_matrix = np.rint(raw * SCALE).astype(int)
    np.savetxt(output_path, distance_matrix, fmt="%d", delimiter=",")

    print(f"Matriz salva no arquivo {output_path}")
  else:
    print(f"Erro: {response.status_code} - {response.text}")


if __name__ == "__main__":
  # sys.argv[0] é o nome do script
  args = sys.argv[1:]

  if len(args) > 2:
    print("Usage: python script.py [--input=<path>] [--output=<path>]")
    sys.exit(1)

  input_path = "addresses.csv"
  output_path = "costs_matrix.csv"

  for arg in args:
    if arg.startswith("--input="):
      input_path = arg.split("=", 1)[1]
    elif arg.startswith("--output="):
      output_path = arg.split("=", 1)[1]
    else:
      print(f"Unknown argument: {arg}")
      print("Usage: python script.py [--input=<path>] [--output=<path>]")
      sys.exit(1)

  main(input_path, output_path)
