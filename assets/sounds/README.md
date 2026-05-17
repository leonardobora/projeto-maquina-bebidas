# Sons da Máquina de Bebidas

Sons usados no projeto — todos do [freesound.org](https://freesound.org), preferencialmente CC0.

| Arquivo | Descrição | Origem sugerida | Licença | Autor |
|---|---|---|---|---|
| `tapa.wav` | Impacto seco na lateral metálica | https://freesound.org/people/newagesoup/sounds/369133/ | CC0 | newagesoup |
| `dispensar.wav` | Motor + lata caindo da máquina | https://freesound.org/people/Emma7073/sounds/250194/ | CC0 | Emma7073 |
| `bebida_gratis.wav` | Ding-ding curto de jackpot | https://freesound.org/people/MarcoConsoli/sounds/620132/ | verificar antes de baixar | MarcoConsoli |
| `quebra.wav` | Zap elétrico / curto-circuito | https://freesound.org/people/NachtmahrTV/sounds/556717/ | CC0 | NachtmahrTV |

## Como obter

1. Crie uma conta gratuita em freesound.org (download exige login).
2. Baixe cada arquivo das URLs acima.
3. Salve em `assets/sounds/` com o nome exato da primeira coluna (`tapa.wav`, etc.).
4. Se algum arquivo vier em MP3 ou outro formato, pode renomear pra `.wav` — `pygame.mixer` aceita ambos. Ou converter via Audacity pra garantir.

## Fallback

Se algum arquivo estiver ausente, o programa segue funcionando sem som (ver `audio.py`).

Pra rodar mudo intencionalmente: `MAQUINA_MUTE=1 python maquina.py` (PowerShell: `$env:MAQUINA_MUTE='1'; python maquina.py`)

## Trocar por outros sons

Sinta-se à vontade pra substituir qualquer arquivo por outro de sua preferência — só mantenha o nome do arquivo. Critérios sugeridos:
- duração < 2s (exceto `dispensar.wav`, até 3s)
- sem voz humana, sem música melódica
- volume normalizado
