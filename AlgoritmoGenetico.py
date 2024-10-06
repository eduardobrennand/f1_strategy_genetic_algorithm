from Circuito import Circuito
import numpy as np
import pandas as pd
import random


class BuscaGenetica:
    def __init__(self, populacao, mutacao_pb,
                 crossover_pb, geracoes, pais):
        self.populacao = populacao
        self.mutacao_pb = mutacao_pb
        self.crossover_pb = crossover_pb
        self.geracoes = geracoes
        self.circuito = Circuito(pais)

    def gerarPopulacao(self):
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
        return individuo

    def avaliarIndividuo(self, individuo):
        contador_composto = 0
        composto_atual = individuo['OrdemCompostos'][contador_composto]
        tempo_total = self.estimarTempoVolta(composto_atual, 1)

        # Se so utilizar um tipo de composto ou não fizer pitstop,
        # devemos penalizar.
        if (len(set(individuo['OrdemCompostos'])) == 1) or (
                len(individuo['PitStops']) == 0):
            tempo_total += 3600

        for volta in range(1, self.circuito.total_voltas):
            tempo_total += self.estimarTempoVolta(composto_atual, volta)
            if volta in individuo['PitStops']:
                tempo_total += self.circuito.media_tempo_pitstop
                contador_composto += 1
                composto_atual = individuo['OrdemCompostos'][contador_composto]
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
            diferenca_volta = volta - len(media_tempo_volta[composto])
            # Adicionamos 0.5s a cada volta que não temos mapeada no dicionario
            media_tempo_volta = media_tempos_voltas[composto][-1] + (
                0.5 * diferenca_volta)

        return media_tempo_volta

    def cruzarIndividuos(self):
        ...

    def mutarIndividuo(self):
        ...
