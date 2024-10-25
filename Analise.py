from AlgoritmoGenetico import BuscaGenetica
from itertools import product
import numpy as np

# Função para buscar os melhores parâmetros para BuscaGenetica
def buscarMelhoresParametros():
    """Método para tentar encontrar a melhor configuração de parâmetros do AG."""
    # Definindo os valores para os parâmetros da classe BuscaGenetica
    populacoes = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]  # Tamanhos de população
    mutacao_pbs = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5]  # Probabilidades de mutação
    cruzamento_pbs = [0.1, 0.2, 0.3, 0.4, 0.5]  # Probabilidades de cruzamento
    geracoes = [50, 100, 150, 200, 250, 300]  # Número de gerações
    elitismo_pps = [0.01, 0.05, 0.1, 0.15]  # Proporção de elitismo
    paises = ['Italy']  # País de exemplo

    # Produto cartesiano de todas as combinações possíveis de parâmetros
    combinacoes_parametros = product(populacoes, mutacao_pbs, cruzamento_pbs, geracoes, elitismo_pps, paises)

    melhor_tempo = float('inf')
    melhor_configuracao = None

    # Métrica adicional: média de desempenho de toda a população
    melhor_media_populacao = float('inf')

    for parametros in combinacoes_parametros:
        # Descompactando a combinação de parâmetros
        populacao, mutacao_pb, cruzamento_pb, geracoes, elitismo_pp, pais = parametros

        # Criando a instância da classe BuscaGenetica com os parâmetros atuais
        busca_genetica = BuscaGenetica(
            populacao=populacao,
            mutacao_pb=mutacao_pb,
            cruzamento_pb=cruzamento_pb,
            geracoes=geracoes,
            elitismo_pp=elitismo_pp,
            pais=pais
        )

        # Inicializando a busca genética
        populacao, melhor_individuo =  busca_genetica.inicializarBuscaGenetica()

        # Avaliar a melhor solução desta rodada
        melhor_individuo_atual = min(populacao, key=lambda x: x['Tempo'])
        tempo_atual = melhor_individuo_atual['Tempo']
        media_populacao_atual = np.mean([individuo['Tempo'] for individuo in populacao])

        # Comparando o tempo e a média para salvar a melhor configuração
        if tempo_atual < melhor_tempo and media_populacao_atual < melhor_media_populacao:
            melhor_tempo = tempo_atual
            melhor_media_populacao = media_populacao_atual
            melhor_configuracao = parametros

    print(f"Melhor configuração encontrada: {melhor_configuracao}")
    print(f"Melhor tempo: {melhor_tempo}")
    print(f"Melhor média de tempo da população: {melhor_media_populacao}")

# Chamada da função para buscar os melhores parâmetros
buscarMelhoresParametros()
