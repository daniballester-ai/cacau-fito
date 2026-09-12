# Guardrail configurado e evidência de bloqueio real

## O que foi configurado

Em `.claude/settings.json`, adicionamos regras de permissão (`permissions.deny`) que bloqueiam, no próprio harness (Claude Code), antes de qualquer execução:

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Edit(./.env)",
      "Bash(rm -rf:*)",
      "Bash(git push --force:*)",
      "Bash(git reset --hard:*)"
    ]
  }
}
```

**Por que essas regras:**
- `.env` contém um dado sensível (e-mail usado para configuração do git) — o agente não deve ler nem editar esse arquivo, mesmo que peçam.
- `rm -rf`, `git push --force` e `git reset --hard` são comandos destrutivos e irreversíveis — o time decidiu que nenhum agente deve executá-los sem intervenção humana explícita fora do harness (ex.: rodando o comando manualmente no terminal), reduzindo o risco de perda de trabalho por um agente mal-instruído ou por um prompt malicioso.

## Evidência de bloqueio real (não apenas descrito)

Testamos ambas as regras nesta sessão, pedindo ao agente para executar exatamente as ações proibidas:

**Teste 1 — leitura de `.env`:**
```
Ferramenta: Read(C:\Fitec\CacauFito\.env)
Resultado: <tool_use_error>File is in a directory that is denied by your permission settings.</tool_use_error>
```

**Teste 2 — comando destrutivo:**
```
Ferramenta: Bash(rm -rf "C:/Fitec/CacauFito/docs/adr/_scratch_test_dir")
Resultado: Permission to use Bash with command rm -rf "..." has been denied.
```

Em ambos os casos a ação foi **impedida antes de qualquer efeito no sistema de arquivos** — não é uma regra apenas documentada e nunca exercitada; foi de fato acionada e bloqueou a execução em tempo real durante o desenvolvimento deste projeto.

## Nível de autonomia e por que faz sentido

Adotamos autonomia **supervisionada com checkpoints humanos obrigatórios**: o agente de IA planeja (SDD), implementa e testa de ponta a ponta sem pedir aprovação passo a passo, mas duas categorias de ação sempre passam por revisão humana explícita antes de seguir: (1) qualquer decisão que exponha um novo endpoint publicamente (ver `docs/checkpoint_humano.md`), e (2) qualquer ação destrutiva ou que toque em segredos, agora também impedida estruturalmente pelas regras acima. Esse nível fez sentido porque o volume de trabalho (10 requisitos funcionais, múltiplas specs) exigia velocidade de execução, mas o projeto lida com segredos reais (credenciais de API) e com um repositório compartilhado entre duas pessoas — os dois pontos onde um erro de agente seria mais caro de reverter.
