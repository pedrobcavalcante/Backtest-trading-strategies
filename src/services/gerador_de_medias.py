
def calcularMedias(estrategysAll, parametros):
    funcMedia = []

    def lambdaFunction(x, parametro):
        if x['results'][parametro] == None:
            return 0
        else:
            return x['results'][parametro]

    for parametro in parametros:
        estrategysFiltered = filter(
            lambda x: x['results'][parametro] != None, estrategysAll)
        sublist = list(
            map(lambda x: lambdaFunction(x, parametro), estrategysFiltered))
        media = sum(sublist) / len(sublist)
        funcMedia.append({
            "parametro": parametro,
            "media": media
        })
    return funcMedia


def inserirMedias(tabelaDeMedias, resultado):
    parametrosKeys = []
    for media in tabelaDeMedias.all():
        parametrosKeys.append(media["parametro"])
    for media in resultado:
        if media['parametro'] in parametrosKeys:
            # print("Atualizando parametro: " + media['parametro'])
            tabelaDeMedias.update(media)
        else:
            # print("Adicionando parametro: " + media['parametro'])
            tabelaDeMedias.insert(media)
