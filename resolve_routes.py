import json
import sys

import pandas as pd

from _config import DEPOT_ADDR

# Rotas do JSON
df_rotas = pd.read_json("routes.json")

# CSV dos pontos
df_pontos = pd.read_csv(
    "addresses.csv",
    sep=",",
    decimal=","
)  # decimal=',' para vírgula BR
# Nova linha como DataFrame (mesmas colunas)
nova_linha = pd.DataFrame([DEPOT_ADDR], columns=df_pontos.columns)

# Adiciona no INÍCIO
df_pontos = pd.concat([nova_linha, df_pontos], ignore_index=True)


def expandir_visita(rota):
  indices = rota["points"]
  pontos = df_pontos.iloc[indices]  # Pega exatamente essas linhas

  pontos_transformados = pontos[[
      "id", "analista", "bairro", "endereco_atualizado"]]

  # pega do índice 1 até o penúltimo
  sub = pontos_transformados.iloc[1:-1]

  contagem = sub["analista"].value_counts()
  analistas_info = (
      contagem
      .reset_index()
      .rename(columns={"index": "analista", "analista": "name"})
      .to_dict(orient="records")
  )

  rota_enriquecida = {
      # "vehicle_id": rota["vehicle_id"],
      "total_load": rota["total_load"],
      "pontos": pontos_transformados.to_dict("records"),
      "analistas": analistas_info,  # novo campo
  }

  return rota_enriquecida


rotas_expandidas = {}
for vehicle_id, vehicle_data in df_rotas.items():
  rotas_expandidas[vehicle_id] = [
      expandir_visita(visit) for visit in vehicle_data["routes"]
  ]

# print(rotas_expandidas)

# Exemplo saída para vehicle_id=3 (visit_order=[0,1,5,8,6,14,10,0])
print(json.dumps(rotas_expandidas, indent=2, ensure_ascii=False))

with open("resolved_routes.json", "w", encoding="utf-8") as f:
  json.dump(rotas_expandidas, f, indent=2, ensure_ascii=False)

# df_rotas_expandidas = pd.DataFrame(rotas_expandidas)
