# Exemplo de teste rápido

from app.models.dataModel import AnaliseRequest
from app.services.coleta_dados_service import coletar_dados_historicos

dados_simulacao = AnaliseRequest(
    tipoAnalise="previsao",
    dataIncio="2025-10-23",
    metricaAnalisar="Total de Alertas",
    fkEmpresa= 1, 
    fkMaquina= None,
    dataPrevisao="2025-12-23",
    componente=None,
)

try:
    dados_do_banco = coletar_dados_historicos(
        dados_simulacao, 
        agrupar_por="HORA", 
    )

    print(dados_do_banco)
    
    if dados_do_banco:
        print("✅ Sucesso! Dados brutos coletados (amostra):")
        for i in range(min(5, len(dados_do_banco))):
            print(dados_do_banco[i])
    else:
        print("❌ Falha! Retornou lista vazia. Verifique as credenciais ou a Stored Procedure.")

except RuntimeError as e:
    print(f"❌ Erro de Runtime na conexão ou SQL: {e}")