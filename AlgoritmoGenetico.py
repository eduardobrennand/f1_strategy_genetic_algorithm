from collections import Counter
from Circuito import Circuito
import pandas as pd
import numpy as np
import random


class BuscaGenetica:
    def __init__(self, populacao, mutacao_pb,
                 cruzamento_pb, geracoes, elitismo_pp,
                 pais):
        self.populacao = populacao
        self.mutacao_pb = mutacao_pb
        self.cruzamento_pb = cruzamento_pb
        self.geracoes = geracoes
        self.elitismo_pp = elitismo_pp
        self.circuito = Circuito(pais)

    def inicializarBuscaGenetica(self):
        """Inicializa o algoritmo genético."""
        # Gera a primeira população totalmente randomica
        populacao = self.gerarPopulacao()
        print(50 * '-')
        print("INIIALZIZANDO ALGORITMO GENÉTICO")
        print(50 * '-')
        for p in range(self.geracoes):
            # 1. Elitismo
            selecionados_elitismo = self.selecionarMelhoresIndividuos(
                populacao=populacao)

            # 2. Seleção Geral
            selecionados = self.selecaoPorRoleta(
                populacao=populacao)

            # 3. Cruzamento
            selecionados, total_individuos_cruzados = self.cruzarIndividuos(
                populacao=selecionados)

            # 4. Mutação
            selecionados, total_individuos_mutados = self.mutarIndividuos(
                populacao=selecionados)

            # 5. Concatenar os indivíduos do elitismo com os da seleção geral

            selecionados = np.append(selecionados, selecionados_elitismo)
            populacao = selecionados
        
            melhor_individuo = min(populacao, key=lambda x: x['Tempo'])

            # print("MELHOR INDIVIDUO DA GERAÇÃO " + str(p))
            # print(melhor_individuo)

        return populacao, melhor_individuo

    def selecaoPorRoleta(self, populacao):
        """Método de seleção por roleta."""
        populacao = sorted(populacao, key=lambda x: x['Tempo'])
        lista_avaliacoes = [individuo['Tempo'] for individuo in populacao]
        soma_avaliacoes = sum(lista_avaliacoes)
        soma_avaliacoes = np.array(soma_avaliacoes)

        probabilidade = ((soma_avaliacoes/lista_avaliacoes) / (sum(soma_avaliacoes/lista_avaliacoes)))
        for i, individuo in enumerate(populacao):
            individuo['Probabilidade'] = str(round(probabilidade[i] * 100, 2)) + '%'

        # Devemos retornar a populacao menos o numero dos individuos do elitismo,
        # pois os individuos do elitismo vao preencher o total da populacao.
        n_populacao = int(((1 - self.elitismo_pp) * len(populacao)))

        selecionados = np.random.choice(populacao, size=n_populacao, p=probabilidade)

        return selecionados

    def selecaoPorTorneio(self, geracao, selecionados_pp):
        """Método de seleção por torneio."""
        # Determinamos o numero total dos individuos que serao
        # selecionados para proxima geracao
        num_selecionados = int(selecionados_pp * len(geracao))
        selecionados = []

        for _ in range(num_selecionados):
            # Pegamos uma amostra randomica de dois individuos
            # para competirem entre si
            competidores = random.sample(geracao, 2)

            # O melhor individuo é selecionado baseado no menor tempo
            melhor_individuo = min(competidores, key=lambda x: x['Tempo'])
            selecionados.append(melhor_individuo)

        return selecionados

    def gerarPopulacao(self):
        """Método para gerar uma população aleatória."""
        populacao = []

        for _ in range(self.populacao):
            populacao.append(self.gerarIndividuo())

        return populacao

    def gerarIndividuo(self):
        """Gera um indivíduo aleatoriamente."""
        individuo = {'OrdemCompostos': [],
                     'PitStops': []}

        # Comecamos colocando um composto inicial
        composto = self.escolherCompostoAleatorio()
        individuo['OrdemCompostos'].append(composto)

        # Agora vamos montar a estrategia completa
        for volta in range(1, self.circuito.total_voltas):
            novoComposto = random.choices([False, True], weights=(95, 5), k=1)

            if novoComposto[0]:
                composto = self.escolherCompostoAleatorio()
                individuo['OrdemCompostos'].append(composto)
                individuo['PitStops'].append(volta)

        individuo['Tempo'] = self.avaliarIndividuo(individuo)

        return individuo

    def avaliarIndividuo(self, individuo):
        """Método para prever o tempo total de corrida do indivíduo
        de acordo com a estratégia utilizada."""
        contador_composto = 0
        composto_atual = individuo['OrdemCompostos'][contador_composto]
        tempo_total = 0
        voltas_composto = 1 # variável que define quantas voltas o pneu atual rodou

        # Verifica se só utilizou um tipo de pneu
        if (len(set(individuo['OrdemCompostos'])) == 1):
            tempo_total += 3600

        # Verifica se não houveram pitstops
        if (len(individuo['PitStops']) == 0):
            tempo_total += 3600

        # Verifica se algum tipo de composto é usado mais de três vezes
        frequencia_compostos = Counter(individuo['OrdemCompostos'])
        for composto, frequencia in frequencia_compostos.items():
            if frequencia > 3:
                tempo_total += 3600

        # Verifica se houve mais de um pitstop na mesma volta
        frequencia_pitstops = Counter(individuo['PitStops'])
        for pitstop, frequencia in frequencia_pitstops.items():
            if frequencia > 1:
                tempo_total += 3600

        for volta in range(1, self.circuito.total_voltas):
            tempo_volta = self.estimarTempoVolta(composto_atual, voltas_composto)
            tempo_total += tempo_volta
            voltas_composto += 1
            if volta in individuo['PitStops']:
                tempo_total += self.circuito.media_tempo_pitstop
                contador_composto += 1
                composto_atual = individuo['OrdemCompostos'][contador_composto]
                voltas_composto = 1

        return round(tempo_total, 2)

    def escolherCompostoAleatorio(self):
        """Escolhe um composto aleatório."""
        return random.choice(['SOFT', 'MEDIUM', 'HARD'])

    def estimarTempoVolta(self, composto, volta):
        """Estima o tempo médio de volta de acordo com o tipo de pneu
        e degradação."""
        media_tempos_voltas = self.circuito.medias_tempos_voltas

        if volta < len(media_tempos_voltas[composto]):
            media_tempo_volta = media_tempos_voltas[composto][volta]
        else:
            diferenca_volta = volta - len(media_tempos_voltas[composto])
            # Adicionamos 0.1s a cada volta que não temos mapeada no dicionario
            media_tempo_volta = media_tempos_voltas[composto][-1] + (
                0.1 * diferenca_volta)

        return media_tempo_volta

    def selecionarMelhoresIndividuos(self, populacao):
        """Seleciona os x% melhores indivíduos da população."""
        populacao = sorted(populacao, key=lambda x: x['Tempo'])

        n_individuos_selecionados = int(len(populacao) * self.elitismo_pp)

        selecionados_elitismo = populacao[:n_individuos_selecionados]

        return selecionados_elitismo

    def cruzarIndividuos(self, populacao):
        """Método para fazer o crossover entre indíviduos."""
        selecionados = []
        total_individuos_cruzados = 0
        while len(selecionados) < self.populacao:
            parente1 = random.choice(populacao).copy()
            parente2 = random.choice(populacao).copy()
            ponto_corte_compostos = random.randint(0, min(len(parente1['OrdemCompostos']), len(parente2['OrdemCompostos'])))
            ponto_corte_pitstops = random.randint(0, min(len(parente1['PitStops']), len(parente2['PitStops'])))
            parente1.pop('Tempo')
            parente2.pop('Tempo')
            print('Ponto de corte para o cruzamento dos compostos')
            print(ponto_corte_compostos)

            print('Ponto de corte para o cruzamento dos pitstops')
            print(ponto_corte_pitstops)

            print('Pai 1')
            print(parente1)

            print('Pai 2')
            print(parente2)

            filho1 = {
                'OrdemCompostos': parente1['OrdemCompostos'][:ponto_corte_compostos] + parente2['OrdemCompostos'][ponto_corte_compostos:],
                'PitStops': sorted(parente1['PitStops'][:ponto_corte_pitstops] + parente2['PitStops'][ponto_corte_pitstops:])
            }

            filho2 = {
                'OrdemCompostos': parente2['OrdemCompostos'][:ponto_corte_compostos] + parente1['OrdemCompostos'][ponto_corte_compostos:],
                'PitStops': sorted(parente2['PitStops'][:ponto_corte_pitstops] + parente1['PitStops'][ponto_corte_pitstops:])
            }

            print('Filho gerado 1:')
            print(filho1)

            print('Filho gerado 2:')
            print(filho2)

            break

            filho1['Tempo'] = self.avaliarIndividuo(filho1)
            filho2['Tempo'] = self.avaliarIndividuo(filho2)

            cruzamento_pp = random.random()

            # Vamos verificar se vai ocorrer cruzamento ou não
            if cruzamento_pp <= self.cruzamento_pb:
                selecionados.append(filho1)
                selecionados.append(filho2)
                total_individuos_cruzados += 1
            else:
                selecionados.append(parente1)
                selecionados.append(parente2)

        return selecionados, total_individuos_cruzados

    def mutarIndividuos(self, populacao):
        """Método para realizar a mutação em um indíviduo."""
        selecionados = []
        total_individuos_mutados = 0

        for individuo in populacao:
            mutacao_pp = random.random()

            # 1. Mutação dos pneus
            if mutacao_pp <= self.mutacao_pb:
                indice_pneu = random.randint(0, len(individuo['OrdemCompostos']) - 1)
                novo_pneu = self.escolherCompostoAleatorio()
                individuo['OrdemCompostos'][indice_pneu] = novo_pneu
                total_individuos_mutados += 1
                individuo['Tempo'] = self.avaliarIndividuo(individuo)
                selecionados.append(individuo)
            # 2. Mutação da volta do pitstop
            elif mutacao_pp <= self.mutacao_pb:
                if len(individuo['PitStops']) > 0:
                    print(individuo)
                    indice_volta = random.randint(0, len(individuo['PitStops']) - 1)
                    novo_pitstop = random.randint(1, self.circuito.total_voltas)
                    individuo['PitStops'][indice_volta] = novo_pitstop
                    print(individuo)
                else:
                    pitstop = random.randint(1, self.circuito.total_voltas)
                    individuo['PitStops'].append(pitstop)
                    individuo['OrdemCompostos'].append(self.escolherCompostoAleatorio())

                total_individuos_mutados += 1
                individuo['Tempo'] = self.avaliarIndividuo(individuo)
                selecionados.append(individuo)   
            # 3. Mutação para adicionar ou remover pitstops
            elif mutacao_pp <= self.mutacao_pb:
                if len(individuo['PitStops']) < 5:
                    indice_volta = random.randint(0, len(individuo['PitStops']) - 1)
                    novo_pitstop = random.randint(1, self.circuito.total_voltas)
                    novo_pneu = self.escolherCompostoAleatorio()
                    individuo['PitStops'][indice_volta] = novo_pitstop
                    individuo['OrdemCompostos'].append(novo_pneu)
                elif len(individuo['PitStops']) > 2:
                    indice_remover = random.randint(0, len(individuo['PitStops']) - 1)
                    individuo['PitStops'].pop(indice_remover)
                    individuo['OrdemCompostos'].pop(indice_remover + 1)

                total_individuos_mutados += 1
                individuo['Tempo'] = self.avaliarIndividuo(individuo)
                selecionados.append(individuo)
            else:
                selecionados.append(individuo)

        return selecionados, total_individuos_mutados
   
# Configuração teste
ga1 = BuscaGenetica(500, 0.01, 0.1, 500, 0.1, 'Italy')

# Melhor configuração encontrada pelo Analise.py:
ga2 = BuscaGenetica(50, 0.5, 0.5, 300, 0.1, 'Italy')

pop = ga2.gerarPopulacao()

ga2.cruzarIndividuos(pop)

# ga2.mutarIndividuos(pop)

