# Biblioteca para manipular o garfo
import networkx as nx
# Biblioteca para manipular o garfo
import random

# Classe caminhão
class Caminhao:
	def __init__(self, id, k, viagem, capacidade_total, num_compartimentos, capacidade_compartimento, horas_disponiveis, fator_custo):
		self.id = id
		self.k = k
		self.viagem = viagem
		self.capacidade_total = capacidade_total
		self.num_compartimentos = num_compartimentos
		self.capacidade_compartimento = capacidade_compartimento
		self.capacidade_atual = {'C'+str(i+1): capacidade_compartimento for i in range(num_compartimentos)} # [VFV 16/05] Era capacidade_total, alterei para capacidade_compartimento
		self.granja_alocada = {'C'+str(i+1): -1 for i in range(num_compartimentos)}
		self.carga_alocada = {'C'+str(i+1): 0 for i in range(num_compartimentos)}
		self.horas_disponiveis = horas_disponiveis
		self.capacidade_disponivel = capacidade_total
		self.fator_custo = fator_custo
		self.rotas = {}
		self.rotas['ingenua'] = {}
		self.rotas['ingenua']['sequencia'] = []
		self.rotas['ingenua']['tempo'] = 0
		self.rotas['ingenua']['distancia'] = 0
		self.rotas['ingenua']['custo'] = 0
		self.fechado = 0
		#self.viagem = 0 # [VFV 16/05]

# Função para ler a matriz de distâncias
def ler_matriz_distancias(arquivo):
	matriz_distancias = []
	with open(arquivo, 'r') as file:
		for line in file:
			row = [float(val) for val in line.strip().split()]
			matriz_distancias.append(row)
	return matriz_distancias

# Função para ler o arquivo de demandas
def ler_demandas(arquivo):
	demandas = {}
	with open(arquivo, 'r') as file:
		for line in file:
			vertice, demanda = line.strip().split()
			demandas[int(vertice)] = int(demanda)
	return demandas

# Função para construir o grafo
def construir_grafo(matriz_distancias, demandas):
	grafo = nx.Graph()
	num_vertices = len(matriz_distancias)
	
	for vertice, demanda in demandas.items():
		grafo.add_node(vertice, demanda=demanda)
	
	# Itera com base no número de vértices
	for i in range(num_vertices):
		for j in range(i + 1, num_vertices):
			distancia = matriz_distancias[i][j]
			if distancia != 0:
				# Adciona as arestas de cada vértice para cada vértice
				grafo.add_edge(i, j, weight=distancia)
	
	return grafo

# Função para gerar as rotas para os caminhões
def encontrar_rotas(grafo, caminhoes):
	rotas = []
	# Vértices não atendidos. Inicialmente todos são não atendidos, exceto o vértice 0, que representa a fábrica.
	vertices_nao_atendidos = set(grafo.nodes()) - {0}  # Todos os vértices, exceto o vértice 0
	
	# Itera com base no número de caminhões
	for caminhao in caminhoes:
		rota = [0]  # Todas as rotas começam no vértice 0
		# Capacidade e horas cheias, caminhões ainda estão no ponto 0
		capacidade_atual = caminhao.capacidade_total 
		horas_disponiveis = caminhao.horas_disponiveis
		
		# Enquanto houver vértices não atendidos
		while vertices_nao_atendidos:
			vizinhos = list(grafo.neighbors(rota[-1]))
			random.shuffle(vizinhos)  # Embaralha os vizinhos para selecionar aleatoriamente
			# Proximo vértice ainda não é definido
			proximo_vertice = None
			# Seleciona o próximo vértice
			for vizinho in vizinhos:
				# Se o próximo vértice já não estiver na rota e estiver na lista de não atendidos e as condições de demanda
				# e horas disponíveis forem satisfeitas, define o próximo vértice
				if vizinho not in rota and vizinho in vertices_nao_atendidos \
						and 'demanda' in grafo.nodes[vizinho] \
						and grafo.nodes[vizinho]['demanda'] <= capacidade_atual \
						and horas_disponiveis - grafo[rota[-1]][vizinho]['weight'] / 40 >= 0:  # Verifica se há horas suficientes
					proximo_vertice = vizinho
					break
			# Se não houver próximo vértice, encerre
			if proximo_vertice is None:
				break
			
			# Calcula a distância do vértice atual até o próximo
			distancia = grafo[rota[-1]][proximo_vertice]['weight']
			tempo_viagem = distancia / 40  # Tempo de viagem em horas (a 40 km/h)
			
			# Se não há horas suficientes para atender um próximo vértice, encerre
			if (horas_disponiveis - tempo_viagem) < tempo_viagem :  # Verifica se excede as horas disponíveis
				break
			
			# Atualiza as variáveis dos caminhões
			horas_disponiveis -= tempo_viagem
			capacidade_atual -= grafo.nodes[proximo_vertice].get('demanda', 0)
			rota.append(proximo_vertice)
			vertices_nao_atendidos.remove(proximo_vertice)
		
		if len(rota) > 1:  # Garante que há pelo menos um vértice além do vértice inicial na rota
			rota.append(0)  # Todas as rotas terminam no vértice 0
			rotas.append(rota)
		else:
			caminhao.horas_disponiveis = 0  # Define horas disponíveis como 0 se não houver rota viável
	
	return rotas

# Função para calcular o custo
def calcular_custo_rota(rota, grafo, velocidade):
	# ***Custo posteriormente será mudado de acordo com o tipo de caminhão
	custo = 0.36
	for i in range(len(rota) - 1):
		origem = rota[i]
		destino = rota[i + 1]
		if not grafo.has_edge(origem, destino):
			break
		distancia = grafo[origem][destino]['weight']
		custo += distancia
	tempo_total = custo / velocidade
	tempo_total = round(tempo_total, 2)
	custo = round(custo, 2)
	return custo, tempo_total
	
def atualizar_distancia_tempo_viagem(caminhao,matriz_distancias,tipo='ingenua'):
	
	
	velocidade = 60 # km/h
	
	#print("\n\n\n\n")
	
	#for compartimento in caminhao.granja_alocada:
	#	print("Compartimento:",compartimento,"/ Granja:",caminhao.granja_alocada[compartimento])
		
	sequencia_rota = []
	sequencia_rota.append(0)
	granjas_atendidas = list(set([caminhao.granja_alocada[compartimento] for compartimento in caminhao.granja_alocada]))
	try:
		granjas_atendidas.remove(-1)
	except ValueError:
		pass
	
	distancia_viagem = matriz_distancias[0][granjas_atendidas[0]]
	#print(distancia_viagem)
	for i in range(0,len(granjas_atendidas)-1,1):
		distancia_viagem += matriz_distancias[granjas_atendidas[i]][granjas_atendidas[i+1]]
		#print(distancia_viagem)
		sequencia_rota.append(granjas_atendidas[i])
	
	distancia_viagem += matriz_distancias[granjas_atendidas[-1]][0]
	sequencia_rota.append(granjas_atendidas[-1])
	sequencia_rota.append(0)
	
	
	tempo_viagem = distancia_viagem / velocidade
	caminhao.rotas['ingenua']['sequencia'] = sequencia_rota
	caminhao.rotas['ingenua']['tempo'] = tempo_viagem
	caminhao.rotas['ingenua']['distancia'] = distancia_viagem
	
	return distancia_viagem,tempo_viagem
	

def inicializar_frota_granjas(demandas,frota,matriz_distancias,info=0,tipo='ingenua'):
	# [VFV 16/05]
	
	if info == 1:
		print("\n\n")
	granjas_pendentes = list(demandas.keys())
	#print("Granjas pendentes:",granjas_pendentes)
	
	caminhoes_disponiveis = [frota[id_caminhao].id for id_caminhao in frota]
	#print("Caminhoes disponíveis:",caminhoes_disponiveis)
	ultimo_id = len(frota)
	
		
	# Selecionar uma granja aleatoriamente
	
	
	atribuicao_ok = 0
	while atribuicao_ok == 0:
		
		granja = random.choice(granjas_pendentes)
		
		if info == 1:
			print("============================")
			print("Granjas pendentes:",granjas_pendentes)
			print("Caminhoes disponíveis:",caminhoes_disponiveis)
			print("============================")
			print("\nGranja",granja,"com demanda",demandas[granja])
		
		granja_atendida_ok = 0
		# Vamos tentar alocar a demanda no mesmo caminhão, se possível.
		while granja_atendida_ok == 0:# and id_caminhao in caminhoes_disponiveis:
			
			
			id_caminhao = random.choice(caminhoes_disponiveis)
			if info == 1:
				print("Caminhão id =",id_caminhao,"( k =",frota[id_caminhao].k,")")
			
			compartimentos_disponiveis = [] # Essa lista vai receber os compartimentos disponíveis no caminhão selecionado
			for compartimento in frota[id_caminhao].capacidade_atual:
				if frota[id_caminhao].capacidade_atual[compartimento] > 0:
					compartimentos_disponiveis.append(compartimento)
			
			if info == 1:
				print("Compartimentos disponíveis:",compartimentos_disponiveis)
			
			while id_caminhao in caminhoes_disponiveis and granja_atendida_ok == 0:
			
				compartimento = random.choice(compartimentos_disponiveis)
				if info == 1:
					print("\tSelecionou compartimento:",compartimento)
				
				# Verificando quanto da carga vai ser alocado ao compartimento.
				if demandas[granja] <= frota[id_caminhao].capacidade_atual[compartimento]: # Se a capacidade do compartimento suportar toda a demanda, alocar
					carga_compartimento = demandas[granja]
				else: # Senão, vamos ter que atender apenas a capacidade do compartimento.
					carga_compartimento = frota[id_caminhao].capacidade_atual[compartimento]
					
				
				# Agora vamos alocar a granja ao compartimento, de fato.
				frota[id_caminhao].granja_alocada[compartimento] = granja # Aloca granja ao compartimento.
				frota[id_caminhao].carga_alocada[compartimento] = carga_compartimento # Aloca carga ao compartimento.
				frota[id_caminhao].capacidade_disponivel -= frota[id_caminhao].capacidade_compartimento # Reduz a capacidade do caminhão.
				frota[id_caminhao].capacidade_atual[compartimento] = 0
				# <=== Agora poderíamos reduzir as horas do caminhão, seria o mais adequado. (Mas vamos deixar pra fazer isso só quando o caminhão fechar)
				if info == 1:
					print("\t\tCarga:",carga_compartimento)
					print("\t\tGranja:",granja)
					print("\t\tCapacidade atualizada:",frota[id_caminhao].capacidade_disponivel)
				
				compartimentos_disponiveis.remove(compartimento)
				if info == 1:
					print("\t\tCompartimentos disponíveis atualizado:",compartimentos_disponiveis)
				if len(compartimentos_disponiveis) == 0:
					if info == 1:
						print("\t\t\tAbrindo uma nova viagem para o caminhão",frota[id_caminhao].k)
					caminhoes_disponiveis.remove(id_caminhao)
					
					# Vamos fechar o caminhão id_caminhao e atualizar as horas disponíveis
					distancia_viagem,tempo_viagem = atualizar_distancia_tempo_viagem(frota[id_caminhao],matriz_distancias,tipo=tipo)
					frota[id_caminhao].horas_disponiveis -= tempo_viagem
					frota[id_caminhao].fechado = 1
					
					# Vou abrir uma nova viagem para o caminhão.
					if frota[id_caminhao].horas_disponiveis > 1:
						novo_id = ultimo_id + 1
						ultimo_id = novo_id
						nova_viagem = Caminhao(id=novo_id, k=frota[id_caminhao].k, viagem = frota[id_caminhao].viagem + 1, capacidade_total=frota[id_caminhao].capacidade_total, num_compartimentos=frota[id_caminhao].num_compartimentos, capacidade_compartimento=frota[id_caminhao].capacidade_compartimento, horas_disponiveis=frota[id_caminhao].horas_disponiveis, fator_custo=frota[id_caminhao].fator_custo)
						frota[novo_id] = nova_viagem
						caminhoes_disponiveis.append(novo_id)
						if info == 1:
							print("\t\t\tCriou uma nova viagem (=",frota[id_caminhao].viagem + 1,") para o caminhão k =",frota[id_caminhao].k)
					#end if
					else:
						if info == 1:
							print("\t\t\tNão foi possível criar uma nova viagem para o caminhão k =",frota[id_caminhao].k,"(horas esgotadas)")
				#end if
				
				demandas[granja] -= carga_compartimento # Retira a demanda da granja
				if info == 1:
					print("\t\tDemanda atualizada:",demandas[granja])
				if demandas[granja] == 0:
					granjas_pendentes.remove(granja)
					granja_atendida_ok = 1 # Resolveu o problema da granja. Podemos passar para a próxima.
				# end
				
				
				
			#end while id_caminhao
				
				
		#end while granja_atendida_ok
		
		if len(granjas_pendentes) == 0:
			atribuicao_ok = 1
		
	#end atribuicao_ok
	
	return frota
			 
#end

def calcular_custo(frota,matriz_distancias,info=0,tipo='ingenua'):
	
	custo_por_viagem = {}
	
	custo_total = 0
	for id_caminhao in frota:
		caminhao = frota[id_caminhao]
		if info == 1:
			print("=====================")
			print("Id:", caminhao.id)
			print("k:", caminhao.k)
			print("viagem:", caminhao.viagem)
			print("capacidade_total:", caminhao.capacidade_total)
			print("num_compartimentos:", caminhao.num_compartimentos)
			print("capacidade_compartimento:", caminhao.capacidade_compartimento)
			print("capacidade_atual:", caminhao.capacidade_atual)
			print("granja_alocada:", caminhao.granja_alocada)
			print("carga_alocada:", caminhao.carga_alocada)
			print("horas_disponiveis:", caminhao.horas_disponiveis)
			print("capacidade_disponivel:", caminhao.capacidade_disponivel)
		
		if tipo == 'ingenua':
			distancia = caminhao.rotas['ingenua']['distancia']
			#print(distancia)
			tempo = caminhao.rotas['ingenua']['tempo']
		
		if distancia < 60 and caminhao.fator_custo == 0.36:
			distancia = 60
		elif distancia < 45 and caminhao.fator_custo == 0.34:
			distancia = 45
			
		if caminhao.capacidade_disponivel == caminhao.capacidade_total:
			distancia = 0
		
		custo_viagem_atual = distancia * caminhao.fator_custo
		custo_por_viagem[id_caminhao] = custo_viagem_atual
		#if info == 1:
		print(custo_viagem_atual)
		custo_total += custo_viagem_atual
	
	
	return custo_total,custo_por_viagem
	
def exibir_info_frota(frota,tipo='ingenua'):
	
	custo_total = 0
	for id_caminhao in frota:
		caminhao = frota[id_caminhao]
		print("=====================")
		print("Id:", caminhao.id)
		print("K:", caminhao.k)
		print("Viagem:", caminhao.viagem)
		print("Capacidade total:", caminhao.capacidade_total)
		print("Número de compartimentos:", caminhao.num_compartimentos)
		print("Capacidade dos compartimentos:", caminhao.capacidade_compartimento)
		print("Capacidade atual:", caminhao.capacidade_atual)
		print("Granja alocada por compartimento:", caminhao.granja_alocada)
		print("Carga alocada por compartimento:", caminhao.carga_alocada)
		print("Capacidade disponível:", caminhao.capacidade_disponivel)
		print("Horas disponíveis (após viagem):", caminhao.horas_disponiveis)
		
		
		
		
		if tipo == 'ingenua':
			
			print("Rota ingênua:")
			print("\tSequência:",end=" ")
			#print(caminhao.rotas['ingenua']['sequencia'])
			for granja in caminhao.rotas['ingenua']['sequencia'][:-1]:
				print(granja,end=" => ")
			
			if len(caminhao.rotas['ingenua']['sequencia']) > 0:
				print(caminhao.rotas['ingenua']['sequencia'][-1])
			else:
				print("")
			distancia = caminhao.rotas['ingenua']['distancia']
			#print(distancia)
			tempo = caminhao.rotas['ingenua']['tempo']
		
		if distancia < 60 and caminhao.fator_custo == 0.36:
			distancia = 60
		elif distancia < 45 and caminhao.fator_custo == 0.34:
			distancia = 45
		if caminhao.capacidade_disponivel == caminhao.capacidade_total:
			distancia = 0
		custo_viagem_atual = distancia * caminhao.fator_custo
		
		
		if tipo == 'ingenua':
			print("\tDistância:",caminhao.rotas['ingenua']['distancia'])
			print("\tTempo:",caminhao.rotas['ingenua']['tempo'])
			print("\tCusto:",custo_viagem_atual)
		
		custo_total += custo_viagem_atual
		
	print("\nCusto total da solução:",custo_total)
		
		
def fechar_caminhoes(frota,matriz_distancias,tipo='ingenua'):
	
	for id_caminhao in frota:
		if frota[id_caminhao].fechado == 0:
			if frota[id_caminhao].capacidade_disponivel != frota[id_caminhao].capacidade_total:
				distancia_viagem,tempo_viagem = atualizar_distancia_tempo_viagem(frota[id_caminhao],matriz_distancias,tipo=tipo)
				frota[id_caminhao].horas_disponiveis -= tempo_viagem
			frota[id_caminhao].fechado = 1
		#end
	#end
#end

def atualizar_caminhao(caminhao,matriz_distancias,tipo='ingenua'):
	
	capacidade_total = caminhao.capacidade_total
	capacidade_compartimento = caminhao.capacidade_compartimento
	capacidade_disponivel = capacidade_total
	for compartimento in caminhao.granja_alocada:
		if caminhao.carga_alocada[compartimento] > 0:
			capacidade_disponivel -= capacidade_compartimento
			caminhao.capacidade_atual[compartimento] = 0
		#end
		else:
			caminhao.capacidade_atual[compartimento] = capacidade_compartimento
	#end
	caminhao.capacidade_disponivel = capacidade_disponivel
	distancia_viagem,tempo_viagem = atualizar_distancia_tempo_viagem(caminhao,matriz_distancias,tipo=tipo)
	
	caminhao.horas_disponiveis -= tempo_viagem 
	
		
		
	
#end

def reduzir_fracionamento_granja(frota,demandas,matriz_distancias,num_granjas,cap_maxima,tipo='ingenua'):
	
	granjas_viagens_dict = {}
	for granja in range(1,num_granjas+1,1):
		granjas_viagens_dict[granja] = {}
		granjas_viagens_dict[granja]['viagem'] = []
		granjas_viagens_dict[granja]['carga'] = []
		granjas_viagens_dict[granja]['num_viagens'] = 0
	#end
	
	for id_caminhao in frota:
		caminhao = frota[id_caminhao]
		granjas_viagens = set()
		for compartimento in caminhao.granja_alocada:
			if caminhao.granja_alocada[compartimento] != -1:
				granja = caminhao.granja_alocada[compartimento]
				granjas_viagens.add(caminhao.granja_alocada[compartimento])
				granjas_viagens_dict[granja]['viagem'].append(id_caminhao)
				granjas_viagens_dict[granja]['carga'].append(caminhao.carga_alocada[compartimento])
		#end
		
		for granja in granjas_viagens:
			if granja != -1: # -1 é compartimento vazio
				granjas_viagens_dict[granja]['num_viagens']+=1
		#end
		
		
	#end
	
	
	
	
	#print(granjas_viagens_dict)
	for i in granjas_viagens_dict:
		print(i,granjas_viagens_dict[i])
		
	# Temos a quantidade de caminhões que atende a cada granja.
	
	
	# Vamos montar uma lista das granjas candidatas a terem o fracionamento reduzido
	granjas_candidatas = []
	for granja in granjas_viagens_dict:
		#print("\nGranja:",granja,"| demandas[granja]: ",demandas[granja],"| granjas_viagens_dict[granja]:",granjas_viagens_dict[granja])
		if granjas_viagens_dict[granja]['num_viagens'] > 1:
			granjas_candidatas.append(granja)  # Uma granja que é atendida em uma só viagem já está OK e não precisa entrar nas candidatas.
		elif int(demandas[granja] / cap_maxima) > granjas_viagens_dict[granja]['num_viagens']: # A demanda das granjas deve ser capaz de ser atendida por um número de granjas menor do que o que já está sendo.
			granjas_candidatas.append(granja)
	
	
	# OK, temos as granjas candidatas a terem fracionamento reduzido.
	print(granjas_candidatas)
	if len(granjas_candidatas) == 0: # Não temos granjas candidatas a redução de fracionamento. Podemos sair da função.
		print("Não há granjas candidatas a redução de fracionamento.")
		return
	
	# Agora vamos aplicar uma perturbação usando essa categoria de vizinhança.
	
	
	quebra = 0
	perturbacao_ok = 0
	while perturbacao_ok == 0 and len(granjas_candidatas): # Vamos tentar com todas as granjas candidatas.
	
		perturbacao_granja_escolhida_ok = 0
		# Precisa tentar fazer tentativas com essa granja até que tenha sucesso.
		
		granja_escolhida = random.choice(granjas_candidatas) # Escolhemos uma granja para reduzir fracionamento
		###granja_escolhida = 1 # Apenas para teste controlado   ****** ALTERAR AQUI *******
		granjas_candidatas.remove(granja_escolhida) # Ela não é mais uma candidata de teste
		print("\nEscolhendo a granja",granja_escolhida)
			
		
		# Viagens que tentaremos eliminar. A medida em que formos tentando, vamos removendo dessa lista.
		viagens_candidatas_saida = list(set(granjas_viagens_dict[granja_escolhida]['viagem']))
		
		print("Viagens candidatas a saída (não vão mais existir para a granja):",viagens_candidatas_saida)
		
		# granja_escolhida será a granja na qual faremos a redução de fracionamento.
		while perturbacao_granja_escolhida_ok == 0 and len(viagens_candidatas_saida) > 0:
			
			# Vamos escolher uma para ser eliminada
			viagem_saida = random.choice(viagens_candidatas_saida)
			#viagem_saida = 2 # Apenas para teste controlado
			viagens_candidatas_saida.remove(viagem_saida)
			
			print("Viagem escolhida para saída:",viagem_saida)
			
			# Compartimentos da granja na viagem escolhida para ser eliminada
			compartimentos_granja_viagem_saida = frota[viagem_saida].granja_alocada
			# Esse é o número de compartimentos que a granja escolhida tem na viagem de saída
			num_compartimentos_granja_viagem_saida = list(frota[viagem_saida].granja_alocada.values()).count(granja_escolhida)
			
			print(num_compartimentos_granja_viagem_saida)
			
						
			# Vamos tentar fazer um swap com alguma viagem que esteja atendendo a granja escolhida. A medida em que formos tentando, vamos removendo dessa lista.
			viagens_candidatas_recebimento = list(set(granjas_viagens_dict[granja_escolhida]['viagem']))
			viagens_candidatas_recebimento.remove(viagem_saida) # A granja_saida não pode ser a do recebimento
			
			swap_ok = 0
			print("Viagens candidatas a recebimento:",viagens_candidatas_recebimento)
			
			
			while swap_ok == 0 and len(viagens_candidatas_recebimento) > 0: # Enquanto não resolver a situação, vamos tentando
				
				# viagem_recebimento é a viagem que receberá a granja
				
				# Uma candidata a recebimento das viagens da viagem_saida
				viagem_recebimento_aux = random.choice(viagens_candidatas_recebimento)
				viagens_candidatas_recebimento.remove(viagem_recebimento_aux)
				
				
				# Compartimentos existentes na viagem recebimento
				compartimentos_granja_viagem_recebimento = frota[viagem_recebimento_aux].granja_alocada
				
				# Agora vamos verificar se a viagem_recebimento_aux tem capacidade para receber os compartimentos
				# Número de compartimentos de outras granjas na viagem recebimento (que poderão ir para a viagem_saida)
				num_compartimentos_outras_granjas_viagem_recebimento_aux = frota[viagem_recebimento_aux].num_compartimentos - list(frota[viagem_recebimento_aux].granja_alocada.values()).count(granja_escolhida) 
				print(list(frota[viagem_recebimento_aux].granja_alocada.values()))
								
				# Os compartimentos da viagem_recebimento devem comportar os compartimentos da granja na viagem_saida
				if num_compartimentos_outras_granjas_viagem_recebimento_aux >= num_compartimentos_granja_viagem_saida:
					viagem_recebimento = viagem_recebimento_aux
					# OK, encontrou uma viagem_saida e uma viagem_recebimento. Agora é fazer o swap.
					
					print("ENTROU NO SWAPPPP")
					print("Fazendo o swap: sai da ",viagem_saida,"e vai pra viagem",viagem_recebimento,"( granja",granja_escolhida,")")
					
					
					# ******* O SWAP DEVE SER FEITO AQUI!!! *********
					
					#caminhao = frota[id_caminhao]
					#print("=====================")
					#print("Id:", caminhao.id)
					#print("k:", caminhao.k)
					#print("viagem:", caminhao.viagem)
					#print("capacidade_total:", caminhao.capacidade_total)
					#print("num_compartimentos:", caminhao.num_compartimentos)
					#print("capacidade_compartimento:", caminhao.capacidade_compartimento)
					#print("capacidade_atual:", caminhao.capacidade_atual)
					#print("granja_alocada:", caminhao.granja_alocada)
					#print("carga_alocada:", caminhao.carga_alocada)
					#print("horas_disponiveis:", caminhao.horas_disponiveis)
					#print("capacidade_disponivel:", caminhao.capacidade_disponivel)
					
					caminhao_saida = frota[viagem_saida]
					caminhao_recebimento = frota[viagem_recebimento]
					
					
					exibir_info_frota(frota,tipo='ingenua')
					
					
					"""
					print("\n\nANTES:\n\n")
					print("Caminhão saída:",caminhao_saida)
					print("Id:", caminhao_saida.id)
					print("k:", caminhao_saida.k)
					print("viagem:", caminhao_saida.viagem)
					print("capacidade_total:", caminhao_saida.capacidade_total)
					print("num_compartimentos:", caminhao_saida.num_compartimentos)
					print("capacidade_compartimento:", caminhao_saida.capacidade_compartimento)
					print("capacidade_atual:", caminhao_saida.capacidade_atual)
					print("granja_alocada:", caminhao_saida.granja_alocada)
					print("carga_alocada:", caminhao_saida.carga_alocada)
					print("horas_disponiveis:", caminhao_saida.horas_disponiveis)
					print("capacidade_disponivel:", caminhao_saida.capacidade_disponivel)
					
					print("\n")
					print("Caminhão recebimento:",caminhao_recebimento)
					print("Id:", caminhao_recebimento.id)
					print("k:", caminhao_recebimento.k)
					print("viagem:", caminhao_recebimento.viagem)
					print("capacidade_total:", caminhao_recebimento.capacidade_total)
					print("num_compartimentos:", caminhao_recebimento.num_compartimentos)
					print("capacidade_compartimento:", caminhao_recebimento.capacidade_compartimento)
					print("capacidade_atual:", caminhao_recebimento.capacidade_atual)
					print("granja_alocada:", caminhao_recebimento.granja_alocada)
					print("carga_alocada:", caminhao_recebimento.carga_alocada)
					print("horas_disponiveis:", caminhao_recebimento.horas_disponiveis)
					print("capacidade_disponivel:", caminhao_recebimento.capacidade_disponivel)
					"""
					
					
					
					
					
					
					distancia_viagem,tempo_viagem = atualizar_distancia_tempo_viagem(caminhao_saida,matriz_distancias,tipo=tipo)
					caminhao_saida.horas_disponiveis += tempo_viagem
					
					distancia_viagem,tempo_viagem = atualizar_distancia_tempo_viagem(caminhao_recebimento,matriz_distancias,tipo=tipo)
					caminhao_recebimento.horas_disponiveis += tempo_viagem
					
					
					for compartimento_saida in caminhao_saida.granja_alocada:
						if caminhao_saida.granja_alocada[compartimento_saida] == granja_escolhida:
							for compartimento_recebimento in caminhao_recebimento.granja_alocada:
								if caminhao_recebimento.granja_alocada[compartimento_recebimento] != granja_escolhida:
									granja_aux = caminhao_saida.granja_alocada[compartimento_saida]
									caminhao_saida.granja_alocada[compartimento_saida] = caminhao_recebimento.granja_alocada[compartimento_recebimento]
									caminhao_recebimento.granja_alocada[compartimento_recebimento] = granja_aux
									
									
									carga_aux = caminhao_saida.carga_alocada[compartimento_saida]
									caminhao_saida.carga_alocada[compartimento_saida] = caminhao_recebimento.carga_alocada[compartimento_recebimento]
									caminhao_recebimento.carga_alocada[compartimento_recebimento] = carga_aux
								#end
							#end
						#end
					#end
					
					
					
					
					atualizar_caminhao(caminhao_saida,matriz_distancias,tipo='ingenua')
					atualizar_caminhao(caminhao_recebimento,matriz_distancias,tipo='ingenua')
									
					"""
					print("\n\nDEPOIS:\n\n")
					print("Caminhão saída:",caminhao_saida)
					print("Id:", caminhao_saida.id)
					print("k:", caminhao_saida.k)
					print("viagem:", caminhao_saida.viagem)
					print("capacidade_total:", caminhao_saida.capacidade_total)
					print("num_compartimentos:", caminhao_saida.num_compartimentos)
					print("capacidade_compartimento:", caminhao_saida.capacidade_compartimento)
					print("capacidade_atual:", caminhao_saida.capacidade_atual)
					print("granja_alocada:", caminhao_saida.granja_alocada)
					print("carga_alocada:", caminhao_saida.carga_alocada)
					print("horas_disponiveis:", caminhao_saida.horas_disponiveis)
					print("capacidade_disponivel:", caminhao_saida.capacidade_disponivel)
					
					print("\n")
					print("Caminhão recebimento:",caminhao_recebimento)
					print("Id:", caminhao_recebimento.id)
					print("k:", caminhao_recebimento.k)
					print("viagem:", caminhao_recebimento.viagem)
					print("capacidade_total:", caminhao_recebimento.capacidade_total)
					print("num_compartimentos:", caminhao_recebimento.num_compartimentos)
					print("capacidade_compartimento:", caminhao_recebimento.capacidade_compartimento)
					print("capacidade_atual:", caminhao_recebimento.capacidade_atual)
					print("granja_alocada:", caminhao_recebimento.granja_alocada)
					print("carga_alocada:", caminhao_recebimento.carga_alocada)
					print("horas_disponiveis:", caminhao_recebimento.horas_disponiveis)
					print("capacidade_disponivel:", caminhao_recebimento.capacidade_disponivel)
					"""
									
							
								
					exibir_info_frota(frota,tipo='ingenua')
					
					
					
					
					print("^^^ FEZ UM SWAP")
					
					
							
					
					
					
					
					
					# *******      FIM DO SWAP   !!! *********
					
					"""
					# Não sei pq escrevi esse trecho... escrevi há muito tempo e não faço ideia ...
					cargas_saida = []
					for compartimento_granja,compartimento_carga in zip(frota[viagem_saida].granja_alocada,frota[viagem_saida].carga_alocada):
						if frota[viagem_saida].granja_alocada[compartimento_granja] == granja_escolhida:
							cargas_saida.append(frota[viagem_saida].carga_alocada[compartimento_carga])
							
					print(cargas_saida)
					
					exit()
					"""
					
					
					swap_ok = 1
					perturbacao_granja_escolhida_ok = 1
					perturbacao_ok = 1
					
				# end
				else:
					print("Não deu para fazer a troca com a viagem", viagem_recebimento_aux,".\n\n")
					quebra = 1
					# Vamos ter que tentar outra
			#end while swap_ok == 0 and len(viagens_candidatas_recebimento) > 0:
			
			if len(viagens_candidatas_recebimento) == 0 and swap_ok == 0:
				print("Não temos candidata a recebimento. Vamos ter que escolher outra de saída.")
			
			
				
				
				
		#end while perturbacao_granja_escolhida_ok == 0:
	#end while perturbacao_ok	
		
	
	print("OK, fim!")
	
	
	
	
	
	return granjas_viagens_dict
	
#end
	
def main():
	
	print("Leitura das demandas...", end = "")
	demandas = ler_demandas("demanda.txt")
	demandas_aux = demandas.copy()
	
	num_granjas = len(demandas)
	print("OK! (",num_granjas,"granjas )")
	
	print("Leitura da matriz de distâncias...", end = "")
	matriz_distancias = ler_matriz_distancias("matriz_distancias.txt")
	print("OK!")
	
	
	random.seed(10)
	
	print("Inicialização da solução inicial...", end = "")	
	frota = {}
	frota[1] = Caminhao(id=1, k=1, viagem = 0, capacidade_total=9, num_compartimentos=3, capacidade_compartimento=3, horas_disponiveis=16, fator_custo=0.36)
	frota[2] = Caminhao(id=2,  k=2, viagem = 0, capacidade_total=15, num_compartimentos=5, capacidade_compartimento=3, horas_disponiveis=16, fator_custo=0.36)
	frota[3] = Caminhao(id=3,  k=3, viagem = 0, capacidade_total=15, num_compartimentos=5, capacidade_compartimento=3, horas_disponiveis=16, fator_custo=0.36)
	frota[4] = Caminhao(id=4,  k=4, viagem = 0, capacidade_total=12, num_compartimentos=4, capacidade_compartimento=3, horas_disponiveis=16, fator_custo=0.36)
	frota[5] = Caminhao(id=5,  k=5, viagem = 0, capacidade_total=12, num_compartimentos=4, capacidade_compartimento=3, horas_disponiveis=16, fator_custo=0.36)
	frota[6] = Caminhao(id=6,  k=6, viagem = 0, capacidade_total=15, num_compartimentos=5, capacidade_compartimento=3, horas_disponiveis=16, fator_custo=0.34)
	frota[7] = Caminhao(id=7,  k=7, viagem = 0, capacidade_total=18, num_compartimentos=6, capacidade_compartimento=3, horas_disponiveis=16, fator_custo=0.34)
	frota[8] = Caminhao(id=8,  k=8, viagem = 0, capacidade_total=18, num_compartimentos=6, capacidade_compartimento=3, horas_disponiveis=16, fator_custo=0.34)
	
	frota = inicializar_frota_granjas(demandas_aux,frota,matriz_distancias,info=0,tipo='ingenua')
	print("OK!")
	
	
	
	print("\n")
	
	# Fechando os caminhões para atualizar valores das distâncias e custos.
	fechar_caminhoes(frota,matriz_distancias,tipo='ingenua') # Fechando os caminhões que estão abertos para que as rotas possam ser calculadas.
	
	print("Exibindo informações sobre a frota:\n")
	# Apenas exibição de informações. Nenhuma atualização de valores é feita por aqui.
	exibir_info_frota(frota,tipo='ingenua')
	
	cap_maxima = 18
	reduzir_fracionamento_granja(frota,demandas,matriz_distancias,num_granjas,cap_maxima,tipo='ingenua')
	
	
	
		
		
		
if __name__ == "__main__":
	main()
	
	
	
	
	
	
	
	

#[VFV 16/05] Não estou usando esse main
def main_old():
	# Entrada dos arquivos de dados
	
	demandas = ler_demandas("demanda.txt")
	
	
	
	# Chamada de função para gerar o grafo
	grafo = construir_grafo(matriz_distancias, demandas)
	
	caminhoes = [Caminhao(id=1, capacidade_total=9, num_compartimentos=3, capacidade_compartimento=3), 
				Caminhao(id=2, capacidade_total=15, num_compartimentos=5, capacidade_compartimento=3), 
				Caminhao(id=3, capacidade_total=15, num_compartimentos=5, capacidade_compartimento=3), 
				Caminhao(id=4, capacidade_total=12, num_compartimentos=4, capacidade_compartimento=3), 
				Caminhao(id=5, capacidade_total=12, num_compartimentos=4, capacidade_compartimento=3),
				Caminhao(id=6, capacidade_total=15, num_compartimentos=5, capacidade_compartimento=3), 
				Caminhao(id=7, capacidade_total=18, num_compartimentos=6, capacidade_compartimento=3),
				Caminhao(id=8, capacidade_total=18, num_compartimentos=6, capacidade_compartimento=3)]
				
				
				
				
	
	rotas = encontrar_rotas(grafo, caminhoes)
	
	vertices_atendidos = set()
	for rota in rotas:
		vertices_atendidos.update(rota)
	
	vertices_nao_atendidos = set(grafo.nodes()) - vertices_atendidos
	
	for caminhao, rota in zip(caminhoes, rotas):
		custo, tempo_total = calcular_custo_rota(rota, grafo, velocidade=40)
		print(f"Caminhao {caminhao.id}: {rota}, custo: {custo}, tempo total: {tempo_total} horas")
	
	if vertices_nao_atendidos:
		print("Vertices nao atendidos:", vertices_nao_atendidos)

