class ResultController:

    def __init__(self, resultado):
        self.resultado = resultado

    def texto_resultado(self):

        if self.resultado.empate:
            return "Empate!"

        return f"Vencedor: {self.resultado.vencedor.nome}"

    def vencedor(self):
        return self.resultado.vencedor