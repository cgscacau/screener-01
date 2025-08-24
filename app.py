import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import AverageTrueRange
from datetime import datetime, timedelta
import json
import warnings
from streamlit_option_menu import option_menu
from pathlib import Path

warnings.filterwarnings('ignore')

# **Configuração da página**
st.set_page_config(
    page_title="🇧🇷 Screener Pro BR v2.0",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# **CSS personalizado com tema brasileiro**
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #228B22 0%, #32CD32 50%, #FFD700 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(34, 139, 34, 0.3);
        border: 3px solid #FFD700;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.8rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
        font-size: 1.2rem;
        font-weight: 500;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.8rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border-left: 5px solid #228B22;
        margin: 1rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 45px rgba(0,0,0,0.15);
    }
    
    .signal-forte-compra {
        background: linear-gradient(135deg, #228B22 0%, #32CD32 100%);
        color: white;
        padding: 0.7rem 1.4rem;
        border-radius: 25px;
        font-weight: 700;
        text-align: center;
        display: inline-block;
        font-size: 0.95rem;
        box-shadow: 0 4px 15px rgba(34, 139, 34, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .signal-compra {
        background: linear-gradient(135deg, #32CD32 0%, #90EE90 100%);
        color: #006400;
        padding: 0.7rem 1.4rem;
        border-radius: 25px;
        font-weight: 700;
        text-align: center;
        display: inline-block;
        font-size: 0.95rem;
        box-shadow: 0 4px 15px rgba(50, 205, 50, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .signal-neutro {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #8B4513;
        padding: 0.7rem 1.4rem;
        border-radius: 25px;
        font-weight: 700;
        text-align: center;
        display: inline-block;
        font-size: 0.95rem;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .signal-venda {
        background: linear-gradient(135deg, #FF6347 0%, #FF4500 100%);
        color: white;
        padding: 0.7rem 1.4rem;
        border-radius: 25px;
        font-weight: 700;
        text-align: center;
        display: inline-block;
        font-size: 0.95rem;
        box-shadow: 0 4px 15px rgba(255, 99, 71, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .signal-forte-venda {
        background: linear-gradient(135deg, #DC143C 0%, #B22222 100%);
        color: white;
        padding: 0.7rem 1.4rem;
        border-radius: 25px;
        font-weight: 700;
        text-align: center;
        display: inline-block;
        font-size: 0.95rem;
        box-shadow: 0 4px 15px rgba(220, 20, 60, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #228B22 0%, #32CD32 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.8rem 2.5rem;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(34, 139, 34, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(34, 139, 34, 0.5);
        background: linear-gradient(135deg, #32CD32 0%, #228B22 100%);
    }
    
    .category-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 2px solid #228B22;
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .category-card:hover {
        border-color: #32CD32;
        box-shadow: 0 5px 20px rgba(34, 139, 34, 0.2);
    }
    
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid #2196f3;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .success-box {
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
        border-left: 4px solid #228B22;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-left: 4px solid #ff9800;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class GerenciadorAtivos:
    """Gerenciador de base de dados de ativos"""
    
    def __init__(self, arquivo_db="assets_database.json"):
        self.arquivo_db = arquivo_db
        self.dados = self.carregar_dados()
    
    def carregar_dados(self):
        """Carrega dados do arquivo JSON"""
        try:
            with open(self.arquivo_db, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.criar_base_inicial()
    
    def salvar_dados(self):
        """Salva dados no arquivo JSON"""
        with open(self.arquivo_db, 'w', encoding='utf-8') as f:
            json.dump(self.dados, f, ensure_ascii=False, indent=2)
    
    def criar_base_inicial(self):
        """Cria base inicial de dados"""
        dados_iniciais = {
            "acoes_brasileiras": {
                "nome": "Ações Brasileiras (B3)",
                "descricao": "Principais ações da Bolsa Brasileira",
                "tickers": [
                    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA",
                    "WEGE3.SA", "MGLU3.SA", "ELET3.SA", "SUZB3.SA", "RENT3.SA"
                ]
            },
            "acoes_americanas": {
                "nome": "Ações Americanas",
                "descricao": "Principais ações do mercado americano",
                "tickers": [
                    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX"
                ]
            },
            "criptomoedas": {
                "nome": "Criptomoedas",
                "descricao": "Principais criptomoedas",
                "tickers": [
                    "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD"
                ]
            }
        }
        
        self.salvar_dados_iniciais(dados_iniciais)
        return dados_iniciais
    
    def salvar_dados_iniciais(self, dados):
        """Salva dados iniciais no arquivo"""
        with open(self.arquivo_db, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    
    def obter_categorias(self):
        """Retorna lista de categorias disponíveis"""
        return list(self.dados.keys())
    
    def obter_tickers_categoria(self, categoria):
        """Retorna tickers de uma categoria"""
        return self.dados.get(categoria, {}).get('tickers', [])
    
    def obter_info_categoria(self, categoria):
        """Retorna informações de uma categoria"""
        return self.dados.get(categoria, {})
    
    def adicionar_ticker(self, categoria, ticker):
        """Adiciona ticker a uma categoria"""
        if categoria in self.dados:
            if ticker not in self.dados[categoria]['tickers']:
                self.dados[categoria]['tickers'].append(ticker.upper())
                self.salvar_dados()
                return True
        return False
    
    def remover_ticker(self, categoria, ticker):
        """Remove ticker de uma categoria"""
        if categoria in self.dados:
            if ticker in self.dados[categoria]['tickers']:
                self.dados[categoria]['tickers'].remove(ticker)
                self.salvar_dados()
                return True
        return False

class ScreenerAvancado:
    """Sistema de screener avançado"""
    
    def __init__(self):
        self.criterios_pesos = {
            'tendencia_ema': 0.25,
            'rsi': 0.20,
            'macd': 0.15,
            'pe_ratio': 0.15,
            'roe': 0.15,
            'liquidez': 0.10
        }
    
    @st.cache_data(ttl=1800, show_spinner=False)
    def obter_dados_acao(_self, ticker, periodo="1y"):
        """Obtém dados históricos e fundamentais com cache"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=periodo, auto_adjust=True, timeout=10)
            info = stock.info
            
            if hist.empty or len(hist) < 50:
                return None, None
            
            return hist, info
        except Exception:
            return None, None
    
    def calcular_indicadores(self, df):
        """Calcula indicadores técnicos"""
        df = df.copy()
        
        try:
            # EMAs
            for periodo in [9, 21, 50, 200]:
                df[f'EMA_{periodo}'] = EMAIndicator(df['Close'], window=periodo).ema_indicator()
            
            # RSI
            df['RSI'] = RSIIndicator(df['Close'], window=14).rsi()
            
            # MACD
            macd = MACD(df['Close'])
            df['MACD'] = macd.macd()
            df['MACD_Signal'] = macd.macd_signal()
            df['MACD_Histogram'] = macd.macd_diff()
            
            # ATR
            df['ATR'] = AverageTrueRange(df['High'], df['Low'], df['Close'], window=14).average_true_range()
            
        except Exception as e:
            st.error(f"Erro ao calcular indicadores: {e}")
        
        return df
    
    def avaliar_acao(self, ticker):
        """Avalia uma ação completa"""
        df, info = self.obter_dados_acao(ticker)
        
        if df is None or info is None:
            return None
        
        df = self.calcular_indicadores(df)
        ultimo = df.iloc[-1]
        
        # Inicializar resultado
        resultado = {
            'ticker': ticker,
            'nome': info.get('longName', ticker)[:40] + "..." if len(info.get('longName', ticker)) > 40 else info.get('longName', ticker),
            'preco': ultimo['Close'],
            'criterios': {},
            'score_total': 0.0,
            'gestao_risco': {}
        }
        
        score_total = 0.0
        
        # **1. Tendência EMA**
        preco = ultimo['Close']
        ema9 = ultimo.get('EMA_9', preco)
        ema21 = ultimo.get('EMA_21', preco)
        ema50 = ultimo.get('EMA_50', preco)
        
        if preco > ema9 > ema21 > ema50:
            ema_score = 1.0
            ema_sinal = "Forte Compra"
        elif preco > ema21:
            ema_score = 0.5
            ema_sinal = "Compra"
        elif preco < ema9 < ema21 < ema50:
            ema_score = -1.0
            ema_sinal = "Forte Venda"
        elif preco < ema21:
            ema_score = -0.5
            ema_sinal = "Venda"
        else:
            ema_score = 0.0
            ema_sinal = "Neutro"
        
        score_total += ema_score * self.criterios_pesos['tendencia_ema']
        resultado['criterios']['tendencia_ema'] = {
            'sinal': ema_sinal,
            'score': ema_score,
            'detalhes': f"Preço: R$ {preco:.2f}"
        }
        
        # **2. RSI**
        rsi = ultimo.get('RSI', 50)
        if rsi < 30:
            rsi_score = 1.0
            rsi_sinal = "Forte Compra"
        elif rsi > 70:
            rsi_score = -1.0
            rsi_sinal = "Forte Venda"
        elif 30 <= rsi <= 45:
            rsi_score = 0.5
            rsi_sinal = "Compra"
        elif 55 <= rsi <= 70:
            rsi_score = -0.5
            rsi_sinal = "Venda"
        else:
            rsi_score = 0.0
            rsi_sinal = "Neutro"
        
        score_total += rsi_score * self.criterios_pesos['rsi']
        resultado['criterios']['rsi'] = {
            'sinal': rsi_sinal,
            'score': rsi_score,
            'valor': rsi
        }
        
        # **3. MACD**
        macd_line = ultimo.get('MACD', 0)
        macd_signal = ultimo.get('MACD_Signal', 0)
        macd_hist = ultimo.get('MACD_Histogram', 0)
        
        if macd_line > macd_signal and macd_hist > 0:
            macd_score = 1.0
            macd_sinal = "Compra"
        elif macd_line < macd_signal and macd_hist < 0:
            macd_score = -1.0
            macd_sinal = "Venda"
        else:
            macd_score = 0.0
            macd_sinal = "Neutro"
        
        score_total += macd_score * self.criterios_pesos['macd']
        resultado['criterios']['macd'] = {
            'sinal': macd_sinal,
            'score': macd_score
        }
        
        # **4. P/E Ratio**
        pe_ratio = info.get('trailingPE', None)
        if pe_ratio and pe_ratio > 0:
            if 8 <= pe_ratio <= 18:
                pe_score = 1.0
                pe_sinal = "Compra"
            elif pe_ratio > 30:
                pe_score = -1.0
                pe_sinal = "Venda"
            else:
                pe_score = 0.0
                pe_sinal = "Neutro"
        else:
            pe_score = 0.0
            pe_sinal = "Sem Dados"
            pe_ratio = "N/A"
        
        score_total += pe_score * self.criterios_pesos['pe_ratio']
        resultado['criterios']['pe_ratio'] = {
            'sinal': pe_sinal,
            'score': pe_score,
            'valor': pe_ratio
        }
        
        # **5. ROE**
        roe = info.get('returnOnEquity', None)
        if roe and roe > 0:
            roe_pct = roe * 100
            if roe_pct >= 15:
                roe_score = 1.0
                roe_sinal = "Compra"
            elif roe_pct < 8:
                roe_score = -1.0
                roe_sinal = "Venda"
            else:
                roe_score = 0.0
                roe_sinal = "Neutro"
        else:
            roe_score = 0.0
            roe_sinal = "Sem Dados"
            roe_pct = "N/A"
        
        score_total += roe_score * self.criterios_pesos['roe']
        resultado['criterios']['roe'] = {
            'sinal': roe_sinal,
            'score': roe_score,
            'valor': roe_pct if roe_pct != "N/A" else "N/A"
        }
        
        # **6. Liquidez**
        volume_medio = df['Volume'].tail(20).mean()
        if volume_medio >= 1000000:
            liq_score = 0.5
            liq_sinal = "Alta"
        elif volume_medio >= 100000:
            liq_score = 0.0
            liq_sinal = "Média"
        else:
            liq_score = -0.5
            liq_sinal = "Baixa"
        
        score_total += liq_score * self.criterios_pesos['liquidez']
        resultado['criterios']['liquidez'] = {
            'sinal': liq_sinal,
            'score': liq_score,
            'volume_medio': volume_medio
        }
        
        # **Decisão final**
        resultado['score_total'] = score_total
        
        if score_total >= 0.6:
            resultado['decisao'] = "Forte Compra"
        elif score_total >= 0.2:
            resultado['decisao'] = "Compra"
        elif score_total <= -0.6:
            resultado['decisao'] = "Forte Venda"
        elif score_total <= -0.2:
            resultado['decisao'] = "Venda"
        else:
            resultado['decisao'] = "Neutro"
        
        # **Gestão de risco**
        atr = ultimo.get('ATR', 0)
        stop_loss = preco - (2.5 * atr)
        take_profit = preco + (4 * atr)
        volatilidade_pct = (atr / preco) * 100 if preco > 0 else 0
        
        resultado['gestao_risco'] = {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'atr': atr,
            'volatilidade_pct': volatilidade_pct,
            'volume_medio': volume_medio
        }
        
        return resultado
    
    def executar_screener(self, tickers):
        """Executa screener otimizado"""
        resultados = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, ticker in enumerate(tickers):
            status_text.text(f"🔍 Analisando {ticker} ({i+1}/{len(tickers)})")
            progress_bar.progress((i + 1) / len(tickers))
            
            resultado = self.avaliar_acao(ticker)
            if resultado:
                resultados.append(resultado)
        
        progress_bar.empty()
        status_text.empty()
        
        return sorted(resultados, key=lambda x: x['score_total'], reverse=True)

def criar_grafico_brasileiro(ticker, df):
    """Cria gráfico técnico com tema brasileiro"""
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(
            f'{ticker} - Análise Técnica Completa',
            'RSI (14)',
            'MACD',
            'Volume'
        ),
        row_heights=[0.5, 0.2, 0.2, 0.1]
    )
    
    # Candlestick com cores brasileiras
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Preço',
            increasing_line_color='#228B22',
            decreasing_line_color='#DC143C'
        ),
        row=1, col=1
    )
    
    # EMAs
    ema_config = [
        (9, '#32CD32', 2),
        (21, '#FFD700', 2),
        (50, '#FF6347', 2),
        (200, '#4169E1', 3)
    ]
    
    for periodo, cor, largura in ema_config:
        if f'EMA_{periodo}' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[f'EMA_{periodo}'],
                    mode='lines',
                    name=f'EMA {periodo}',
                    line=dict(color=cor, width=largura),
                    opacity=0.8
                ),
                row=1, col=1
            )
    
    # RSI
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['RSI'],
            mode='lines',
            name='RSI',
            line=dict(color='#8A2BE2', width=2)
        ),
        row=2, col=1
    )
    
    fig.add_hline(y=70, line_dash="dash", line_color="#DC143C", opacity=0.7, row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#228B22", opacity=0.7, row=2, col=1)
    
    # MACD
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MACD'],
            mode='lines',
            name='MACD',
            line=dict(color='#4169E1', width=2)
        ),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MACD_Signal'],
            mode='lines',
            name='Signal',
            line=dict(color='#DC143C', width=2)
        ),
        row=3, col=1
    )
    
    # Histograma MACD
    colors = ['#228B22' if x >= 0 else '#DC143C' for x in df['MACD_Histogram']]
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['MACD_Histogram'],
            name='Histogram',
            marker_color=colors,
            opacity=0.6
        ),
        row=3, col=1
    )
    
    # Volume
    volume_colors = ['#228B22' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#DC143C' 
                     for i in range(len(df))]
    
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=volume_colors,
            opacity=0.7
        ),
        row=4, col=1
    )
    
    # Layout brasileiro
    fig.update_layout(
        height=800,
        showlegend=True,
        template="plotly_white",
        title_x=0.5,
        font=dict(family="Inter", size=12),
        plot_bgcolor='rgba(248, 249, 250, 0.8)'
    )
    
    return fig

def formatar_sinal_html(decisao):
    """Formata sinais com CSS brasileiro"""
    classes = {
        "Forte Compra": "signal-forte-compra",
        "Compra": "signal-compra",
        "Neutro": "signal-neutro",
        "Venda": "signal-venda",
        "Forte Venda": "signal-forte-venda"
    }
    
    emojis = {
        "Forte Compra": "🚀",
        "Compra": "📈",
        "Neutro": "⚖️",
        "Venda": "📉",
        "Forte Venda": "💥"
    }
    
    classe = classes.get(decisao, "signal-neutro")
    emoji = emojis.get(decisao, "⚖️")
    
    return f'<div class="{classe}">{emoji} {decisao}</div>'

def formatar_valor_brasileiro(valor, tipo='real'):
    """Formata valores no padrão brasileiro"""
    if valor == 'N/A' or valor is None:
        return 'N/A'
    
    try:
        if tipo == 'real':
            return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        elif tipo == 'percentual':
            return f"{valor:.2f}%".replace('.', ',')
        elif tipo == 'volume':
            if valor >= 1e6:
                return f"{valor/1e6:.1f}M".replace('.', ',')
            elif valor >= 1e3:
                return f"{valor/1e3:.1f}K".replace('.', ',')
            else:
                return f"{valor:.0f}"
    except:
        return str(valor)

def main():
    """Função principal da aplicação"""
    
    # Header brasileiro
    st.markdown("""
    <div class="main-header">
        <h1>🇧🇷 Screener Pro BR v2.0</h1>
        <p>Sistema Avançado de Análise de Investimentos | Mercado Brasileiro e Internacional</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar gerenciadores
    gerenciador_ativos = GerenciadorAtivos()
    screener = ScreenerAvancado()
    
    # Menu principal
    selected = option_menu(
        menu_title=None,
        options=["🎯 Screener", "📊 Gerenciar Ativos", "📚 Guia Rápido"],
        icons=["search", "gear", "book"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f8f9fa"},
            "icon": {"color": "#228B22", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "--hover-color": "#e8f5e8"},
            "nav-link-selected": {"background-color": "#228B22"},
        }
    )
    
    if selected == "🎯 Screener":
        # **PÁGINA PRINCIPAL - SCREENER**
        
        # Sidebar
        with st.sidebar:
            st.markdown("### ⚙️ Configurações do Screener")
            
            # Seleção de categoria
            categorias = gerenciador_ativos.obter_categorias()
            categoria_opcoes = {}
            
            for cat in categorias:
                info = gerenciador_ativos.obter_info_categoria(cat)
                categoria_opcoes[info.get('nome', cat)] = cat
            
            categoria_selecionada_nome = st.selectbox(
                "📂 Selecione a Categoria:",
                options=list(categoria_opcoes.keys()),
                index=0
            )
            
            categoria_selecionada = categoria_opcoes[categoria_selecionada_nome]
            info_categoria = gerenciador_ativos.obter_info_categoria(categoria_selecionada)
            
            st.markdown(f"""
            <div class="info-box">
                <strong>{info_categoria.get('nome', 'Categoria')}</strong><br>
                {info_categoria.get('descricao', 'Sem descrição')}
            </div>
            """, unsafe_allow_html=True)
            
            # Tickers da categoria
            tickers_categoria = gerenciador_ativos.obter_tickers_categoria(categoria_selecionada)
            
            # Seleção de tickers
            tickers_selecionados = st.multiselect(
                f"📊 Selecione os ativos ({len(tickers_categoria)} disponíveis):",
                options=tickers_categoria,
                default=tickers_categoria[:10] if len(tickers_categoria) > 10 else tickers_categoria
            )
            
            # Ticker personalizado
            st.markdown("---")
            st.markdown("### ➕ Adicionar Ticker Personalizado")
            ticker_personalizado = st.text_input("Digite o ticker:", placeholder="Ex: PETR4.SA, AAPL, BTC-USD")
            
            if st.button("Adicionar à Análise") and ticker_personalizado:
                if ticker_personalizado.upper() not in tickers_selecionados:
                    tickers_selecionados.append(ticker_personalizado.upper())
                    st.success(f"✅ {ticker_personalizado.upper()} adicionado!")
            
            # Filtros
            st.markdown("---")
            st.markdown("### 🔧 Filtros Avançados")
            
            col1, col2 = st.columns(2)
            with col1:
                min_volume = st.number_input("Volume mín. (mil):", value=100, step=50)
                min_price = st.number_input("Preço mín. (R$):", value=1.0, step=0.5)
            
            with col2:
                max_pe = st.number_input("P/E máx.:", value=50, step=5)
                min_score = st.slider("Score mínimo:", -3.0, 3.0, -1.0, 0.1)
            
            # Botão principal
            st.markdown("---")
            executar = st.button("🚀 Executar Análise Completa", type="primary")
        
        # Área principal
        if not executar:
            # Página inicial
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown("""
                <div class="success-box" style="text-align: center; padding: 3rem;">
                    <h2>🎯 Bem-vindo ao Screener Pro BR v2.0</h2>
                    <p>Selecione os ativos na barra lateral e clique em <strong>"Executar Análise Completa"</strong> para começar.</p>
                    <br>
                    <p><strong>🇧🇷 Novidades da v2.0:</strong></p>
                    <ul style="text-align: left; display: inline-block;">
                        <li>✨ Interface com design brasileiro</li>
                        <li>📊 Base completa de ações da B3</li>
                        <li>🏠 Fundos Imobiliários (FIIs)</li>
                        <li>💰 Criptomoedas e commodities</li>
                        <li>📈 Gestão avançada de risco</li>
                        <li>🔄 Sistema de watchlists editáveis</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        
        else:
            # Executar análise
            if not tickers_selecionados:
                st.error("❌ Selecione pelo menos um ativo para análise!")
                return
            
            st.markdown(f"""
            <div class="success-box">
                <strong>🔍 Iniciando análise de {len(tickers_selecionados)} ativos...</strong><br>
                Categoria: {info_categoria.get('nome')}<br>
                Filtros: Volume mín. {min_volume}K, Preço mín. {formatar_valor_brasileiro(min_price)}, Score mín. {min_score}
            </div>
            """, unsafe_allow_html=True)
            
            # Executar screener
            with st.spinner("🔄 Processando análise completa..."):
                resultados = screener.executar_screener(tickers_selecionados)
            
            if not resultados:
                st.error("❌ Não foi possível analisar nenhum ativo. Verifique os tickers selecionados.")
                return
            
            # Aplicar filtros
            resultados_filtrados = []
            for r in resultados:
                volume_ok = r['gestao_risco']['volume_medio'] >= (min_volume * 1000)
                preco_ok = r['preco'] >= min_price
                score_ok = r['score_total'] >= min_score
                pe_ok = True
                
                if r['criterios']['pe_ratio']['valor'] != 'N/A':
                    try:
                        pe_ok = float(r['criterios']['pe_ratio']['valor']) <= max_pe
                    except:
                        pe_ok = True
                
                if volume_ok and preco_ok and score_ok and pe_ok:
                    resultados_filtrados.append(r)
            
            st.success(f"✅ Análise concluída! {len(resultados_filtrados)} ativos aprovados nos filtros de {len(resultados)} analisados.")
            
            if not resultados_filtrados:
                st.warning("⚠️ Nenhum ativo passou nos filtros aplicados. Tente relaxar os critérios.")
                return
            
            # **DASHBOARD DE RESULTADOS**
            
            # Métricas resumo
            st.markdown("### 📊 Dashboard de Resultados")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("📈 Total", len(resultados_filtrados))
            
            with col2:
                forte_compra = len([r for r in resultados_filtrados if r['decisao'] == 'Forte Compra'])
                st.metric("🚀 Forte Compra", forte_compra)
            
            with col3:
                compra = len([r for r in resultados_filtrados if r['decisao'] == 'Compra'])
                st.metric("📈 Compra", compra)
            
            with col4:
                neutro = len([r for r in resultados_filtrados if r['decisao'] == 'Neutro'])
                st.metric("⚖️ Neutro", neutro)
            
            with col5:
                score_medio = np.mean([r['score_total'] for r in resultados_filtrados])
                st.metric("⭐ Score Médio", f"{score_medio:.2f}")
            
            # Gráfico de distribuição
            st.markdown("### 📊 Distribuição dos Sinais")
            
            decisoes = [r['decisao'] for r in resultados_filtrados]
            df_decisoes = pd.DataFrame({'Decisão': decisoes})
            contagem = df_decisoes['Decisão'].value_counts()
            
            fig_pie = px.pie(
                values=contagem.values,
                names=contagem.index,
                title="Distribuição das Recomendações",
                color_discrete_map={
                    'Forte Compra': '#228B22',
                    'Compra': '#32CD32',
                    'Neutro': '#FFD700',
                    'Venda': '#FF6347',
                    'Forte Venda': '#DC143C'
                }
            )
            fig_pie.update_layout(font=dict(family="Inter"))
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.markdown("### 🏆 Top 5 Oportunidades")
                for i, r in enumerate(resultados_filtrados[:5], 1):
                    st.markdown(f"""
                    <div class="metric-card">
                        <strong>{i}. {r['ticker']}</strong><br>
                        {formatar_sinal_html(r['decisao'])}<br>
                        <small>Score: {r['score_total']:.2f} | {formatar_valor_brasileiro(r['preco'])}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Tabela principal
            st.markdown("### 📋 Ranking Completo")
            
            dados_tabela = []
            for r in resultados_filtrados:
                dados_tabela.append({
                    'Pos.': len(dados_tabela) + 1,
                    'Ticker': r['ticker'],
                    'Nome': r['nome'],
                    'Preço': formatar_valor_brasileiro(r['preco']),
                    'Score': f"{r['score_total']:.2f}",
                    'Decisão': r['decisao'],
                    'RSI': f"{r['criterios']['rsi']['valor']:.1f}",
                    'P/E': f"{r['criterios']['pe_ratio']['valor']}" if r['criterios']['pe_ratio']['valor'] != "N/A" else "N/A",
                    'ROE': f"{r['criterios']['roe']['valor']:.1f}%" if r['criterios']['roe']['valor'] != "N/A" else "N/A",
                    'Volume': formatar_valor_brasileiro(r['gestao_risco']['volume_medio'], 'volume'),
                    'Stop Loss': formatar_valor_brasileiro(r['gestao_risco']['stop_loss']),
                    'Take Profit': formatar_valor_brasileiro(r['gestao_risco']['take_profit'])
                })
            
            df_display = pd.DataFrame(dados_tabela)
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # Análise individual detalhada
            st.markdown("---")
            st.markdown("### 🔍 Análise Detalhada Individual")
            
            ticker_selecionado = st.selectbox(
                "Selecione um ativo para análise completa:",
                options=[r['ticker'] for r in resultados_filtrados],
                index=0
            )
            
            resultado_detalhado = next(r for r in resultados_filtrados if r['ticker'] == ticker_selecionado)
            
            # Layout detalhado
            col_info, col_grafico = st.columns([1, 2])
            
            with col_info:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📊 {resultado_detalhado['ticker']}</h3>
                    <h4>{resultado_detalhado['nome']}</h4>
                    <p><strong>Preço Atual:</strong> {formatar_valor_brasileiro(resultado_detalhado['preco'])}</p>
                    <p><strong>Score Total:</strong> {resultado_detalhado['score_total']:.2f}/3.0</p>
                    {formatar_sinal_html(resultado_detalhado['decisao'])}
                </div>
                """, unsafe_allow_html=True)
                
                # Gestão de risco
                st.markdown("#### 🛡️ Gestão de Risco")
                risco = resultado_detalhado['gestao_risco']
                
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    st.metric("Stop Loss", formatar_valor_brasileiro(risco['stop_loss']))
                    st.metric("Volatilidade", f"{risco['volatilidade_pct']:.1f}%")
                
                with col_r2:
                    st.metric("Take Profit", formatar_valor_brasileiro(risco['take_profit']))
                    st.metric("R/R Ratio", "1:1.6")
                
                # Critérios detalhados
                st.markdown("#### 📊 Detalhamento dos Critérios")
                
                for criterio, dados in resultado_detalhado['criterios'].items():
                    nome_criterio = criterio.replace('_', ' ').title()
                    
                    # Barra de progresso para score
                    score_normalizado = (dados['score'] + 1) / 2
                    
                    st.markdown(f"**{nome_criterio}:**")
                    st.progress(score_normalizado)
                    
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        st.markdown(f"- **Sinal:** {dados['sinal']}")
                    with col_c2:
                        st.markdown(f"- **Score:** {dados['score']:.2f}")
                    
                    if 'valor' in dados and dados['valor'] != "N/A":
                        st.markdown(f"- **Valor:** {dados['valor']}")
                    
                    st.markdown("---")
            
            with col_grafico:
                # Gráfico técnico brasileiro
                st.markdown("#### 📈 Análise Técnica")
                
                df_grafico, _ = screener.obter_dados_acao(ticker_selecionado, "6mo")
                if df_grafico is not None and len(df_grafico) > 50:
                    df_grafico = screener.calcular_indicadores(df_grafico)
                    fig = criar_grafico_brasileiro(ticker_selecionado, df_grafico)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("❌ Não foi possível carregar dados para o gráfico.")
            
            # Export de dados
            st.markdown("---")
            st.markdown("### 💾 Exportar Resultados")
            
            col_exp1, col_exp2, col_exp3 = st.columns(3)
            
            with col_exp1:
                csv_completo = pd.DataFrame(dados_tabela).to_csv(index=False)
                st.download_button(
                    label="📥 Baixar Completo (CSV)",
                    data=csv_completo,
                    file_name=f"screener_completo_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
            
            with col_exp2:
                forte_compra_data = [d for d in dados_tabela if d['Decisão'] == 'Forte Compra']
                if forte_compra_data:
                    csv_forte_compra = pd.DataFrame(forte_compra_data).to_csv(index=False)
                    st.download_button(
                        label="🚀 Apenas Forte Compra",
                        data=csv_forte_compra,
                        file_name=f"forte_compra_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )
            
            with col_exp3:
                resumo = f"""
SCREENER PRO BR v2.0 - RELATÓRIO
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

RESUMO EXECUTIVO:
- Total analisado: {len(resultados_filtrados)}
- Forte Compra: {len([r for r in resultados_filtrados if r['decisao'] == 'Forte Compra'])}
- Compra: {len([r for r in resultados_filtrados if r['decisao'] == 'Compra'])}
- Score médio: {score_medio:.2f}

TOP 5 OPORTUNIDADES:
{chr(10).join([f"{i+1}. {r['ticker']} - {r['decisao']} (Score: {r['score_total']:.2f})" for i, r in enumerate(resultados_filtrados[:5])])}
                """
                
                st.download_button(
                    label="📄 Relatório Resumido",
                    data=resumo,
                    file_name=f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain"
                )
    
    elif selected == "📊 Gerenciar Ativos":
        # **PÁGINA DE GERENCIAMENTO**
        
        st.markdown("### 📊 Gerenciamento de Watchlists")
        
        tab1, tab2 = st.tabs(["📝 Editar Listas", "📋 Visualizar Todas"])
        
        with tab1:
            st.markdown("#### Editar Listas Existentes")
            
            categorias = gerenciador_ativos.obter_categorias()
            categoria_edit = st.selectbox(
                "Selecione a categoria para editar:",
                options=categorias
            )
            
            if categoria_edit:
                info_cat = gerenciador_ativos.obter_info_categoria(categoria_edit)
                tickers_atuais = gerenciador_ativos.obter_tickers_categoria(categoria_edit)
                
                st.markdown(f"""
                <div class="info-box">
                    <strong>{info_cat.get('nome', categoria_edit)}</strong><br>
                    {info_cat.get('descricao', 'Sem descrição')}<br>
                    <small>Total de ativos: {len(tickers_atuais)}</small>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**➕ Adicionar Ticker:**")
                    novo_ticker = st.text_input("Ticker:", key=f"add_{categoria_edit}")
                    
                    if st.button("Adicionar", key=f"btn_add_{categoria_edit}"):
                        if novo_ticker:
                            if gerenciador_ativos.adicionar_ticker(categoria_edit, novo_ticker):
                                st.success(f"✅ {novo_ticker.upper()} adicionado!")
                                st.rerun()
                            else:
                                st.error("❌ Erro ao adicionar ticker.")
                
                with col2:
                    st.markdown("**➖ Remover Ticker:**")
                    if tickers_atuais:
                        ticker_remover = st.selectbox(
                            "Selecione para remover:",
                            options=tickers_atuais,
                            key=f"remove_{categoria_edit}"
                        )
                        
                        if st.button("Remover", key=f"btn_remove_{categoria_edit}"):
                            if gerenciador_ativos.remover_ticker(categoria_edit, ticker_remover):
                                st.success(f"✅ {ticker_remover} removido!")
                                st.rerun()
                
                # Lista atual
                if tickers_atuais:
                    st.markdown("**📋 Tickers Atuais:**")
                    
                    # Mostrar em colunas
                    num_cols = 4
                    cols = st.columns(num_cols)
                    
                    for i, ticker in enumerate(tickers_atuais):
                        with cols[i % num_cols]:
                            st.markdown(f"• {ticker}")
        
        with tab2:
            st.markdown("#### Visualizar Todas as Categorias")
            
            categorias = gerenciador_ativos.obter_categorias()
            
            for categoria in categorias:
                info = gerenciador_ativos.obter_info_categoria(categoria)
                tickers = gerenciador_ativos.obter_tickers_categoria(categoria)
                
                with st.expander(f"{info.get('nome', categoria)} ({len(tickers)} ativos)"):
                    st.markdown(f"**Descrição:** {info.get('descricao', 'Sem descrição')}")
                    
                    if tickers:
                        # Mostrar em colunas
                        num_cols = 4
                        cols = st.columns(num_cols)
                        
                        for i, ticker in enumerate(tickers):
                            with cols[i % num_cols]:
                                st.markdown(f"• {ticker}")
                    else:
                        st.markdown("*Nenhum ativo cadastrado*")
    
    elif selected == "📚 Guia Rápido":
        # **PÁGINA EDUCACIONAL**
        
        st.markdown("### 📚 Guia Rápido de Uso")
        
        tab1, tab2, tab3 = st.tabs(["🎯 Como Usar", "📊 Indicadores", "❓ FAQ"])
        
        with tab1:
            st.markdown("""
            ## 🎯 Como Usar o Screener Pro BR v2.0
            
            ### **Passo a Passo:**
            
            **1. Seleção de Ativos** 🎯
            - Escolha uma categoria na barra lateral (Ações BR, FIIs, Cripto, etc.)
            - Selecione os ativos específicos que deseja analisar
            - Adicione tickers personalizados se necessário
            
            **2. Configuração de Filtros** ⚙️
            - Volume mínimo: Garante liquidez adequada
            - Preço mínimo: Evita penny stocks
            - P/E máximo: Filtra ações muito caras
            - Score mínimo: Define qualidade mínima
            
            **3. Execução da Análise** 🚀
            - Clique em "Executar Análise Completa"
            - Aguarde o processamento
            - Analise os resultados no dashboard
            
            **4. Interpretação dos Resultados** 📊
            - **Score Total**: -3.0 (péssimo) a +3.0 (excelente)
            - **Sinais**: Forte Venda → Venda → Neutro → Compra → Forte Compra
            - **Gestão de Risco**: Stop loss e take profit automáticos
            """)
        
        with tab2:
            st.markdown("""
            ## 📊 Guia de Indicadores Técnicos
            
            ### **Médias Móveis Exponenciais (EMAs)**
            - **EMA 9**: Tendência de curtíssimo prazo
            - **EMA 21**: Tendência de curto prazo  
            - **EMA 50**: Tendência de médio prazo
            
            **Interpretação:**
            - Preço acima de todas EMAs = Tendência de alta forte
            - EMAs alinhadas = Confirmação de tendência
            
            ### **RSI (Relative Strength Index)**
            - **RSI < 30**: Possível sobrevenda (oportunidade)
            - **RSI > 70**: Possível sobrecompra (cuidado)
            - **RSI 45-55**: Zona neutra
            
            ### **MACD**
            - Linha MACD acima da linha de sinal = Momentum de alta
            - Histograma crescente = Força aumentando
            
            ### **Análise Fundamentalista**
            - **P/E Ratio**: 8-18 = bom valor
            - **ROE**: >15% = gestão eficiente
            """)
        
        with tab3:
            st.markdown("""
            ## ❓ Perguntas Frequentes
            
            **P: O que significa o Score Total?**
            R: É uma nota de -3.0 a +3.0 que combina análise técnica e fundamentalista. Scores positivos indicam oportunidades de compra.
            
            **P: Posso confiar 100% nos sinais?**
            R: Não! O screener é uma ferramenta de apoio. Sempre faça sua própria análise.
            
            **P: Como adicionar ações brasileiras?**
            R: Use o sufixo .SA (ex: PETR4.SA, VALE3.SA)
            
            **P: E criptomoedas?**
            R: Use o sufixo -USD (ex: BTC-USD, ETH-USD)
            
            **P: Os dados estão atualizados?**
            R: Os dados vêm do Yahoo Finance em tempo real, com possível atraso de 15-20 minutos.
            
            **P: Posso salvar minhas configurações?**
            R: Sim! Use a aba "Gerenciar Ativos" para criar e editar suas watchlists personalizadas.
            """)
        
        # Footer brasileiro
        st.markdown("---")
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #228B22 0%, #32CD32 50%, #FFD700 100%); border-radius: 15px; color: white; margin-top: 2rem;">
            <h3>🇧🇷 Screener Pro BR v2.0</h3>
            <p>Desenvolvido com ❤️ para investidores brasileiros</p>
            <small>Versão 2.0.0 | Última atualização: {datetime.now().strftime('%d/%m/%Y')}</small>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
