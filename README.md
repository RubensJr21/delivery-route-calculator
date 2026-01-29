# Delivery Route Calculator (Calculador de rotas de entregas)

## Finalidade

Esse projeto foi desenvolvido como uma resposta a um problema identificado na escolha de visitas para entregas de cestas. Atualmente as 'rotas' são feitas manualmente, sem uma otimização metrificada. Por tanto esse projeto tenta mectrificar baseando-se na distância entre os pontos. Ainda está sendo desenvolvido e mesmo sendo possível obter uma solução viável, podem existir melhorias que ainda podem ser feitas.

## Cenário

O projeto foi pensado para o seguinte cenário:

* 3 carros
* X famílias (podendo variar a cada nova remessa de cestas que chegam)
* 6 cestas por carro

Esses valores podem ser alterados no script de [calc_routes.py](calc_routes.py). Além das coordenadas do ponto de origem/depósito no arquivo [_config.py](_config.py) que por padrão é ignorado pelo git, entretanto tendo um arquivo de exemplo disponível em [_config.example.py](_config.example.py)

## Problema do Caixeiro Viajante

Durante as minhas pesquisas eu busquei entender com 'o que eu estava mexendo', o que de fato eu precisava resolver para entender como eu iria resolver. Vou então que rememorando as aulas de Matemática Discreta recordei-me do problema do caixeiro de viajante que para não ocupar muito espaço explicarei brevemente.

---

### O Problema do Caixeiro Viajante (PCV), ou Traveling Salesman Problem (TSP), é um desafio clássico de otimização na computação e matemática

* O Objetivo: Encontrar a rota mais curta (menor distância ou custo) para um vendedor que precisa visitar um conjunto de cidades, visitando cada uma apenas uma vez e retornando à cidade de origem.
* O Desafio: Embora pareça simples, o número de rotas possíveis aumenta drasticamente com o número de cidades (complexidade fatorial).
* Complexidade: É classificado como NP-difícil, o que significa que, para um grande número de cidades, encontrar a rota absolutamente mais rápida é computacionalmente inviável, recorrendo-se a algoritmos heurísticos para encontrar soluções aproximadas.
* Aplicações: É fundamental na logística para planejar rotas de entrega, otimizar braços robóticos em fábricas e organizar circuitos eletrônicos.

Em resumo: Visitar todos os pontos uma vez e voltar ao início gastando o mínimo possível

### Execução dos passos

Para obter a solução é necessário a execução de 3 scripts:

1. [distances.py](distances.py) : responsável por ler um arquivo [addresses.csv] em um formato específico, adicionar as coordenadas do depósito e solicitar as distâncias (atualmente utilizando a api do <https://project-osrm.org/>). Posteriormente salvando essa matriz de distâncias em um aruqivo [costs_matrix.csv].
1. [cal_routes.py](calc_routes.py) : utilizando o arquivo da matrix de distâncias [costs_matrix.csv] ele executa o algoritmo que encontra uma candidata melhor solução para o problema e salva em um arquivo json [routes.json] que contém as visitas e os índices de cada ponto geográfico a ser visitado em uma rota específica, as rotas separadas por carros informando a quantidade total de cestas por rota (carga total por rota).
1. [resolve_rotes.py](resolve_routes.py) : já que a o algoritmo anterior retorna os íncides das coordenadas, é necessário 'resolver' esses índices, para seja possível identificar visualmente onde exatamente cada carro irá passar. Como o cenário tem a necessidade de priorizar as pessoas que acompanharão as entregas, ele também informa quantas cestas cada pessoa que está presente da rota possui, possibilitando assim a alocação das pessoas nos carros que tem maior número de pontos a serem visitados (isso não é uma regra de negócio, apenas uma informação para auxliar no cenário idealizado para o problema em questão).

**É importtante notar que os índices dos carros são 'normalizados' para não ser necessário a utilização de métodos mais complexos para viagens múltimplas.**

**Exemplo**: considere um conjunto de carros [0, 1, 2], cada carro pode levar 6 cestas, com isso a capacidade total é de 18 cestas. No cenário onde existem 20 cestas o algoritmo encontraria a solução, pois 2 cestas ficariam sobrando. Para isso foram criados o que apelidei de `virtual_vehivles` que consiste em simular veículos para que comportem a capacidaede necessária [veja no código](calc_routes.py#L24-l28). Então para o exemplo citado seria necessário adicionar um `virtual_vehivles`(carro virtual) que representaria uma rota extra para o carro 0 com apenas 2 cestas.
