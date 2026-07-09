import os
import re
import json

# ==============================================================================
# CONFIGURAÇÃO DE NOVAS FONTES E DIREÇÃO LINGUÍSTICA
# ==============================================================================
DIRECAO_ATUAL = "libras-pt"

novas_playlists = [
    "https://www.youtube.com/playlist?list=PL18ybxrEghTtRHxgWHKTZUrI8BfbtX5Hf"
]

videos_avulsos = []
ARQUIVO_BANCO = 'legendas_completo.json'

# ==============================================================================
# PROCESSO LOCAL
# ==============================================================================
if os.path.exists(ARQUIVO_BANCO):
    with open(ARQUIVO_BANCO, 'r', encoding='utf-8') as f:
        banco_dados = json.load(f)
    print(f"✅ Banco de dados existente carregado com sucesso. Contém {len(banco_dados)} trechos.")
else:
    banco_dados = []
    print("⚠️ Nenhum banco de dados prévio detectado na pasta. Criando um novo do zero.")

videos_processados = set(item['video_id'] for item in banco_dados)

def limpar_vtt(arquivo_vtt, video_id):
    trechos = []
    if not os.path.exists(arquivo_vtt): return trechos
    with open(arquivo_vtt, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    blocos = conteudo.split('\n\n')
    for bloco in blocos:
        linhas = bloco.strip().split('\n')
        if len(linhas) >= 2:
            tempo_match = re.search(r'(\d{2}):(\d{2}):(\d{2})[.,](\d{3})', linhas[0])
            if tempo_match:
                h, m, s, ms = map(int, tempo_match.groups())
                segundos = h * 3600 + m * 60 + s + ms / 1000.0
                texto = " ".join(linhas[1:])
                texto = re.sub(r'<[^>]*>', '', texto).strip()
                if texto and not texto.startswith('NOTE'):
                    trechos.append({
                        'video_id': video_id, 
                        'texto': texto, 
                        'tempo_inicio': segundos,
                        'direcao': DIRECAO_ATUAL
                    })
    return trechos

def processar_arquivos_baixados():
    novos_trechos_contador = 0
    arquivos_no_diretorio = os.listdir('.')
    for arquivo in arquivos_no_diretorio:
        if arquivo.endswith('.pt.vtt') or arquivo.endswith('.pt-BR.vtt'):
            video_id = arquivo.split('.pt')[0]
            if video_id in videos_processados:
                os.remove(arquivo)
                continue
            trechos_video = limpar_vtt(arquivo, video_id)
            banco_dados.extend(trechos_video)
            novos_trechos_contador += len(trechos_video)
            videos_processados.add(video_id)
            os.remove(arquivo)
    return novos_trechos_contador

# Processamento de Playlists locais (removido limite de downloads para rodar completa)
for playlist_url in novas_playlists:
    if "list=" in playlist_url:
        print(f"\nMinerando novas legendas da playlist ({DIRECAO_ATUAL})...")
        # Roda o comando nativo do sistema do seu computador
        os.system(f'yt-dlp --write-auto-subs --write-subs --sub-lang pt --skip-download --output "%(id)s.%(ext)s" "{playlist_url}"')
        adicionados = processar_arquivos_baixados()
        print(f"Concluído. {adicionados} novos trechos acoplados.")

if videos_avulsos:
    print(f"\nMinerando vídeos avulsos...")
    for vid in videos_avulsos:
        if vid in videos_processados: continue
        os.system(f'yt-dlp --write-auto-subs --write-subs --sub-lang pt --skip-download --output "{vid}.%(ext)s" "https://www.youtube.com/watch?v={vid}"')
        processar_arquivos_baixados()

with open(ARQUIVO_BANCO, 'w', encoding='utf-8') as f:
    json.dump(banco_dados, f, ensure_ascii=False, indent=4)

print(f"\n====================================================")
print(f"PROCESSO CONCLUÍDO!")
print(f"Volume total final do seu banco de dados local: {len(banco_dados)} trechos.")
print(f"====================================================")