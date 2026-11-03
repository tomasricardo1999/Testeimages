# Configuração de publicação no Instagram

O workflow **Aprovar e publicar no Instagram** só publica quando a execução manual é iniciada com a confirmação explícita **PUBLICAR**. A opção predefinida é **NAO**, que termina sem publicar.

## Pré-requisitos Meta

1. Criar uma conta Instagram profissional (Business ou Creator).
2. Associá-la a uma Página Facebook, caso utilize o fluxo de autenticação Facebook Login.
3. Configurar uma app Meta e obter permissões de publicação para a conta. No fluxo Facebook Login, é necessária a permissão `instagram_content_publish`.
4. Obter o Instagram Professional Account ID e um Page Access Token válido com as permissões necessárias.

A Meta só consegue obter imagens alojadas num endereço público. Este repositório é público; o workflow converte os 11 PNGs aprovados em JPEGs e guarda-os no repositório antes de chamar a API. Não guardar tokens nos ficheiros do repositório.

## Configurar GitHub Secrets

No repositório, abrir **Settings → Secrets and variables → Actions → New repository secret** e criar:

- `IG_USER_ID`: ID da conta Instagram profissional.
- `IG_ACCESS_TOKEN`: token de acesso com permissões de publicação.

Opcionalmente, em **Settings → Secrets and variables → Actions → Variables**, criar:

- `IG_GRAPH_API_BASE`: URL base da Graph API. Se omitido, é usado `https://graph.facebook.com/v25.0` (fluxo Facebook Login).

Nunca partilhar o token no chat, em issues ou em commits. Se um token for exposto, revogá-lo na Meta.

## Como aprovar e publicar

1. Abrir o separador **Actions** do GitHub.
2. Escolher **Aprovar e publicar no Instagram**.
3. Clicar em **Run workflow**.
4. Selecionar ticker e estilo que foram revistos.
5. Só se quiser publicar, escolher **PUBLICAR** na confirmação e executar o workflow. **NAO** cancela sem publicar.

A aprovação é por execução, ticker e estilo. Os workflows de geração automática nunca publicam.

## Nota importante: 11 slides

A API do Instagram limita um carrossel a 10 itens. Para preservar os 11 slides atuais, a automação publica o carrossel com os slides 1–10 e publica o slide 11 como uma segunda publicação individual. Ambas usam a legenda aprovada; a segunda é identificada como continuação.

A API pode rejeitar a publicação se a conta, as permissões, o token ou a configuração da app Meta não estiverem corretos. Nenhum conteúdo é publicado até à execução manual com **PUBLICAR**.
