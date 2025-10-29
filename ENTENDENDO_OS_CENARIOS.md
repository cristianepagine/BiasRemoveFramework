# 📊 Entendendo os Cenários de Análise

## 🎯 Objetivo do Framework

Este framework tem como objetivo **DETECTAR E CORRIGIR** viés de gênero em avaliações de RH.

## 📝 Como Funciona

### 1. Dados Originais (Cenário 1 - 0% Correção)

Os dados mockados são gerados **PROPOSITALMENTE COM VIÉS** para simular um cenário real onde:
- Mulheres recebem avaliações sistematicamente mais baixas
- Homens recebem avaliações sistematicamente mais altas
- **Diferença média: ~0.56 pontos**
- **P-value < 0.0001** (viés estatisticamente significativo)

**Isto é INTENCIONAL** - estamos simulando um problema real de viés que precisa ser corrigido!

### 2. Correção Progressiva (Cenários 2-6)

O framework aplica diferentes níveis de correção:

| Cenário | Correção | O que acontece |
|---------|----------|----------------|
| **Cenário 1** | 0% | Dados originais COM viés |
| **Cenário 2** | 17% | Correção mínima aplicada |
| **Cenário 3** | 33% | Correção parcial |
| **Cenário 4** | 50% | Correção moderada |
| **Cenário 5** | 67% | Correção forte |
| **Cenário 6** | 83% | Correção quase total |
| **Cenário 7** | 100% | Correção TOTAL - sem viés |

### 3. Resultado Esperado

✅ **CORRETO**:
- Cenário 1 TEM viés (p-value < 0.05)
- Cenários intermediários mostram REDUÇÃO progressiva do viés
- Cenário 7 NÃO TEM viés (p-value > 0.05)

❌ **INCORRETO** seria:
- Cenário 1 SEM viés
- Cenário 7 COM viés

## 🔬 Interpretação dos Resultados

### Cenário 1 - Sem Correção (0%)
```
Média Feminino: 7.14
Média Masculino: 7.70
Diferença: 0.560
P-value: < 0.0001
Status: ⚠️ VIÉS DETECTADO
```

**Interpretação**: Este é o **PROBLEMA**. Há uma diferença estatisticamente significativa entre as avaliações de homens e mulheres. Mulheres estão sendo sistematicamente subavaliadas.

### Cenário 4 - Correção Moderada (50%)
```
Média Feminino: 7.42
Média Masculino: 7.70
Diferença: 0.280
P-value: 0.0002
Status: ⚠️ VIÉS AINDA PRESENTE
```

**Interpretação**: A correção de 50% **REDUZIU** o viés, mas ainda não é suficiente. A diferença caiu de 0.56 para 0.28, mas ainda é estatisticamente significativa.

### Cenário 7 - Correção Total (100%)
```
Média Feminino: 7.70
Média Masculino: 7.70
Diferença: 0.000
P-value: 0.9970
Status: ✅ SEM VIÉS
```

**Interpretação**: **SUCESSO**! A correção total eliminou o viés. As médias estão praticamente iguais e não há diferença estatística significativa.

## 💡 Por Que Isso É Importante?

### Sem Correção (Cenário 1):
- Mulheres recebem scores mais baixos injustamente
- Isso afeta promoções, aumentos e oportunidades
- Perpetua desigualdade de gênero

### Com Correção (Cenário 7):
- Avaliações são justas e baseadas em mérito
- Oportunidades iguais para todos
- Decisões de RH são mais equitativas

## 🎓 Metodologia Técnica

### Detecção de Viés

1. **Teste t de Student**: Compara médias entre grupos
2. **P-value < 0.05**: Indica diferença estatisticamente significativa
3. **Diferença de médias**: Quantifica a magnitude do viés

### Correção de Viés

1. **Reponderação**: Ajusta scores para equalizar médias
2. **Preserva distribuição**: Mantém variância e ranking relativo
3. **Progressiva**: Permite diferentes níveis de correção

## ❓ FAQ

**P: Por que o Cenário 1 tem viés se os dados são mockados?**
R: PROPOSITALMENTE! Estamos simulando um problema real para demonstrar como o framework o detecta e corrige.

**P: O correto não seria o Cenário 1 sem viés?**
R: Não! O objetivo é mostrar a **JORNADA** de correção. Começamos com um problema (viés) e mostramos como corrigi-lo.

**P: Como saber qual nível de correção usar?**
R: Depende da política da empresa. Recomendamos:
- **67-83%**: Equilíbrio entre correção e preservação de diferenças legítimas
- **100%**: Máxima equidade, mas pode sobre-corrigir

**P: E se os dados reais não tiverem viés?**
R: Ótimo! O framework detectará (p-value > 0.05) e não aplicará correção desnecessária.

## 🚀 Próximos Passos

1. **Analise seus dados reais**: Use o framework com avaliações verdadeiras
2. **Verifique se há viés**: Veja o Cenário 1
3. **Escolha o nível de correção**: Baseado em suas políticas
4. **Monitore continuamente**: Viés pode ressurgir ao longo do tempo

---

**Lembre-se**: O framework é uma FERRAMENTA de equidade. O objetivo não é "forçar" igualdade, mas REMOVER vieses sistemáticos que prejudicam grupos específicos.
