<div align="center">
  <a href="https://github.com/devjohnatas/ReadStitch">
    <img alt="ReadStitch Logo" width="180" src="assets/ReadStitchLogo.png">
  </a>

  <h1>ReadStitch</h1>
  <p><strong>Stitch e Upscaling para Webtoons e Mangás</strong><br/>Baixe capítulos, processe imagens e melhore a qualidade de leitura.</p>

  <p>
    <a href="https://github.com/devjohnatas/ReadStitch/releases/latest"><img src="https://img.shields.io/github/v/release/devjohnatas/ReadStitch?label=release" alt="Latest Release"></a>
    <a href="https://github.com/devjohnatas/ReadStitch/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/devjohnatas/ReadStitch/ci.yml?label=ci" alt="CI"></a>
    <a href="https://github.com/devjohnatas/ReadStitch/actions/workflows/build.yml"><img src="https://img.shields.io/github/actions/workflow/status/devjohnatas/ReadStitch/build.yml?label=release" alt="Release Workflow"></a>
    <a href="https://github.com/devjohnatas/ReadStitch/releases"><img src="https://img.shields.io/github/downloads/devjohnatas/ReadStitch/total" alt="Downloads"></a>
    <a href="https://github.com/devjohnatas/ReadStitch/blob/master/LICENSE"><img src="https://img.shields.io/github/license/devjohnatas/ReadStitch" alt="License"></a>
  </p>
</div>

---

## O que é o ReadStitch?

O ReadStitch é uma ferramenta desenvolvida a partir da integração entre os projetos SmartStitch e Waifu2X. O objetivo principal é fornecer uma pipeline automatizada para edição e leitura de webtoons e mangás.

Com a ferramenta, é possível baixar capítulos de diversas fontes online, ler diretamente os arquivos originais ou processá-los com as seguintes funcionalidades:
- **Juntar e Fatiar (Stitch + Slice):** Imagens menores são combinadas e posteriormente fatiadas em dimensões ideais para leitura, evitando cortes no meio de painéis ou de caixas de texto.
- **Upscaling de Imagem:** Integração nativa com o Waifu2X para remoção de artefatos visuais e aumento de resolução.

### Principais Funcionalidades

- **Processamento em Lote:** Suporte para o processamento automático de múltiplas pastas simultaneamente.
- **Detecção Avançada:** Algoritmos de comparação de pixels para cortes inteligentes que não prejudicam a leitura.
- **Múltiplos Formatos:** Suporte completo para entrada e saída em formatos como `.png`, `.jpg`, `.webp`, `.bmp`, `.psd`, `.tiff` e `.tga`.
- **Marcas d'água:** Inserção configurável de overlay, cabeçalhos e rodapés automáticos nas imagens processadas.
- **Integração com o Sistema:** Opção de adicionar o ReadStitch diretamente ao menu de contexto do Windows.
- **Atualização Automática:** Sincronização direta com o repositório Git ou via pacotes de release para manter a ferramenta sempre atualizada.

---

## Como Utilizar

### Interface Gráfica (Releases)
1. Acesse a seção de [Releases](https://github.com/devjohnatas/ReadStitch/releases) e faça o download da versão mais recente.
2. Descompacte o arquivo e inicie o executável `ReadStitch.exe`.
3. Selecione o diretório contendo as imagens dos capítulos.
4. Configure as preferências de saída (como tamanho e formato) e marque a opção do Waifu2X caso deseje upscaling.
5. Inicie o processamento.

### Rodando via Código-fonte
1. Instale o Python 3.11 ou superior.
2. Clone o repositório e instale as dependências:
   ```bash
   git clone https://github.com/devjohnatas/ReadStitch.git
   cd ReadStitch
   pip install -r requirements.txt
   ```
3. Execute o programa:
   ```bash
   # Interface gráfica
   python ReadStitchGUI.py
   
   # Modo console
   python ReadStitchConsole.py -i "./chapter" -sh 7500 -t .png
   ```

---

## Comandos do Console (CLI)

O modo console é recomendado para integrações e rotinas de automação:
```text
python ReadStitchConsole.py [-h] -i INPUT_FOLDER -sh SPLIT_HEIGHT
                             [-t {.png,.jpg,.webp,.bmp,.psd,.tiff,.tga}]
                             [-cw CUSTOM_WIDTH]
                             [-dt {none,pixel}]
                             [-s [0-100]]
                             [-lq [1-100]]
                             [-ip IGNORABLE_PIXELS]
                             [-sl [1-100]]
```

---

## Como Contribuir

O ReadStitch é um projeto de código aberto. Toda contribuição é válida e ajuda a melhorar o projeto.
- **Relatar Problemas (Issues):** Caso encontre falhas, crie uma Issue descrevendo o problema, incluindo os passos de reprodução e anexando os registros da pasta `__logs__`.
- **Melhorias e Sugestões:** Sugestões para novas funcionalidades ou ajustes no código atual são sempre bem-vindas no painel de Issues.
- **Pull Requests (PR):** Contribuições diretas no código podem ser feitas através de Pull Requests na ramificação principal.

---

## Licença

Este software é distribuído sob a licença MIT. Para mais informações, consulte o arquivo [LICENSE](LICENSE).
