<div align="center">
  <a href="https://github.com/devjohnatas/ReadStitch">
    <img alt="ReadStitch Logo" width="180" src="https://github.com/devjohnatas/ReadStitch/raw/dev/assets/ReadStitchLogo.png">
  </a>

  <h1>ReadStitch</h1>
  <p><strong>A fusão perfeita entre SmartStitch e Waifu2X</strong><br/>Baixe capítulos, processe com qualidade superior e tenha a melhor experiência de leitura.</p>

  <p>
    <a href="https://github.com/devjohnatas/ReadStitch/releases/latest"><img src="https://img.shields.io/github/v/release/devjohnatas/ReadStitch?label=release" alt="Latest Release"></a>
    <a href="https://github.com/devjohnatas/ReadStitch/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/devjohnatas/ReadStitch/ci.yml?label=ci" alt="CI"></a>
    <a href="https://github.com/devjohnatas/ReadStitch/actions/workflows/build.yml"><img src="https://img.shields.io/github/actions/workflow/status/devjohnatas/ReadStitch/build.yml?label=release" alt="Release Workflow"></a>
    <a href="https://github.com/devjohnatas/ReadStitch/releases"><img src="https://img.shields.io/github/downloads/devjohnatas/ReadStitch/total" alt="Downloads"></a>
    <a href="https://github.com/devjohnatas/ReadStitch/blob/dev/LICENSE"><img src="https://img.shields.io/github/license/devjohnatas/ReadStitch" alt="License"></a>
  </p>
</div>

---

## 📖 O que é o ReadStitch?

O **ReadStitch** nasceu da junção do poder de corte inteligente do **SmartStitch** com a melhoria de imagem do **Waifu2X**. 

Os usuários podem baixar capítulos diretamente de diversos sites (como plataformas de webtoons e mangás) e optar por lê-los normalmente, ou passá-los pelo **ReadStitch** para:
- **Juntar e Fatiar (Stitch + Slice)**: Múltiplas imagens curtas são unidas e depois cortadas perfeitamente para uma leitura vertical suave e sem quebras grotescas de arte.
- **Upscaling Inteligente**: Integrado com o Waifu2X para remover ruídos e aumentar significativamente a resolução dos painéis.

### 🎯 Principais Funcionalidades

- **Processamento em Massa**: Processe pastas inteiras de uma vez de forma super simples.
- **Detecção Inteligente**:
  - Comparação de pixels avançada para detectar bordas e não cortar balões de texto.
  - Slicing direto com configurações de tolerância.
- **Formatos Suportados**: Exportação flexível para `.png, .jpg, .webp, .bmp, .psd, .tiff, .tga`.
- **Watermark e Assinatura**:
  - Inserção de overlay, header (cabeçalho) e footer (rodapé).
- **Menu de Contexto no Windows**: Clique direito em qualquer pasta do seu computador e processe tudo instantaneamente!
- **Auto-Update**: O programa sincroniza automaticamente as atualizações direto do Git e realiza a atualização forçada de forma transparente para manter todos sempre na melhor versão.

---

## 🚀 Como Começar

### Usuários Comuns (Interface Visual)
1. Acesse a página de [Releases](https://github.com/devjohnatas/ReadStitch/releases) e baixe a versão mais recente.
2. Extraia o pacote em seu computador e execute o `ReadStitch.exe`.
3. Escolha a pasta onde você baixou os capítulos.
4. Ajuste os formatos de saída e, se desejar, ative a opção do *Waifu2X* para melhoria gráfica.
5. Clique em processar!

### Desenvolvedores (Rodando via Código-fonte)
1. Instale o Python 3.11+.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute a interface ou o console:
   ```bash
   # Para a interface gráfica:
   python ReadStitchGUI.py
   
   # Ou pelo console:
   python ReadStitchConsole.py -i "./chapter" -sh 7500 -t .png
   ```

---

## 🤝 Como Contribuir

O **ReadStitch** é um projeto focado na comunidade. **Os usuários podem e são extremamente encorajados a ajudar no projeto!**
Veja como você pode contribuir:
- **Reportando Bugs (Issues)**: Encontrou algum erro? Abra uma [Issue](https://github.com/devjohnatas/ReadStitch/issues) detalhando o problema. Forneça os passos para reproduzir e os logs gerados na pasta `__logs__`.
- **Sugerindo Melhorias**: Quer que a gente suporte outro formato ou ferramenta? Nos avise pelas Issues.
- **Enviando Código (Pull Requests)**: Se você é dev, sinta-se livre para implementar correções, criar novas funcionalidades e abrir um *Pull Request (PR)*!

---

## 📄 Licença

O ReadStitch é totalmente **Open-Source** e distribuído sob os termos do arquivo [LICENSE](LICENSE).
Sinta-se livre para usar, modificar e distribuir o código de acordo com as regras estabelecidas.
