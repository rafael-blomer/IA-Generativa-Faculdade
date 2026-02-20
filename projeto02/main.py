from classifier import classificar_mensagem

temperaturas = [0.2, 0.6, 1.0]

mensagens_cliente = [
    "Quero contratar o plano premium",
    "O sistema está com erro",
    "Quero cancelar minha assinatura",
    "Quero falar com um atendente",
    "Preciso de ajuda com meu pagamento",
    "Gostaria de atualizar minhas informações de conta",
    "Vocês trabalham no sabado?"
]

for temperatura in temperaturas:
    for mensagem in mensagens_cliente:
        resposta = classificar_mensagem(mensagem, temperature=temperatura)
        print(f"Temperatura: {temperatura}")
        print(f"Cliente: {mensagem}")
        print(f"Resposta: {resposta}\n")